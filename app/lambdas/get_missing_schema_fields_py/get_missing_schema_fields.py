#!/usr/bin/env python3

"""
Given a payload data object, validate it against the schema and return the list of missing/invalid fields.
"""

# Standard imports
import boto3
import json
import typing
import jsonschema
from pathlib import Path
from os import environ
from typing import List, Dict, Union, Any

if typing.TYPE_CHECKING:
    from mypy_boto3_schemas import SchemasClient
    from mypy_boto3_ssm import SSMClient

SSM_REGISTRY_NAME_ENV_VAR = "SSM_REGISTRY_NAME"
SSM_SCHEMA_PATH_ENV_VAR = "SSM_SCHEMA_PATH"
DEFAULT_PAYLOAD_VERSION_ENV_VAR = "DEFAULT_PAYLOAD_VERSION"


def get_ssm_parameter_value(parameter_name: str) -> str:
    ssm_client: "SSMClient" = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def get_schema_from_registry(registry_name: str, schema_name: str) -> str:
    schemas_client: "SchemasClient" = boto3.client("schemas")
    response = schemas_client.describe_schema(RegistryName=registry_name, SchemaName=schema_name)
    return response["Content"]


def resolve_schema_ref(schema: dict, ref: str) -> dict:
    """
    Resolve a local JSON schema $ref like '#/$defs/FastqInputs'.
    """
    if not ref.startswith("#/"):
        return {}

    resolved = schema
    for ref_part in ref.lstrip("#/").split("/"):
        resolved = resolved.get(ref_part, {})

    return resolved


def get_missing_required_fields_for_schema_option(
        schema_option: dict,
        instance: dict,
        path: str
) -> list[str]:
    """
    Given a resolved oneOf schema option, return the missing required field paths.
    """
    missing_fields = []

    for required_field in schema_option.get("required", []):
        if not isinstance(instance, dict) or required_field not in instance:
            field_path = f"{path}.{required_field}" if path else required_field
            missing_fields.append(field_path)

    return missing_fields


def get_one_of_missing_field_summaries(
        schema: dict,
        error: jsonschema.ValidationError,
        path: str
) -> list[dict[str, list[str]]]:
    """
    Summarise oneOf validation failures without exposing every nested conditional.

    Assumes oneOf options are $ref objects. For each referenced option, collect the
    missing required fields. Then pair equivalent missing fields into concise
    'either X or Y' messages.
    """
    missing_field_options = []

    for idx, option in enumerate(error.validator_value, start=1):
        missing_field_option_list = []
        if not (isinstance(option, dict) and "$ref" in option):
            continue

        resolved_option = resolve_schema_ref(schema, option["$ref"])
        option_missing_fields = get_missing_required_fields_for_schema_option(
            resolved_option,
            error.instance,
            path
        )

        if option_missing_fields:
            for field in option_missing_fields:
                missing_field_option_list.append(field)

        missing_field_options.append(
            {
                f"{path}: {option["$ref"].rsplit("/")[-1]} path": missing_field_option_list
            }
        )

    return missing_field_options


def handler(event, context):
    """
    Validate the data against the schema and return missing fields.

    Input:
    {
        "data": {...},
        "payloadVersion": "2025.08.05"  (optional)
    }

    Output:
    {
        "missingFields": ["inputs.sequenceData", "inputs.reference", ...]
    }
    """
    data = event.get("data", {})
    payload_version = event.get("payloadVersion", environ.get(DEFAULT_PAYLOAD_VERSION_ENV_VAR, ""))

    # Get schema
    schema_registry = get_ssm_parameter_value(environ[SSM_REGISTRY_NAME_ENV_VAR])
    schema_name = json.loads(get_ssm_parameter_value(
        str(Path(environ[SSM_SCHEMA_PATH_ENV_VAR]) / payload_version)
    ))["schemaName"]
    schema_content = get_schema_from_registry(registry_name=schema_registry, schema_name=schema_name)
    schema = json.loads(schema_content)

    # Validate and collect all errors
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(data))

    # Extract missing field paths
    missing_fields: List[Union[Dict[str, Any], str]] = []
    for error in errors:
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else ""
        if error.validator == "required":
            # For required errors, list each missing property
            for missing_prop in error.validator_value:
                if missing_prop not in error.instance:
                    field_path = f"{path}.{missing_prop}" if path else missing_prop
                    missing_fields.append(field_path)
        elif error.validator == "oneOf":
            missing_fields.append(
                {
                    "oneOf": get_one_of_missing_field_summaries(
                        schema,
                        error,
                        path
                    )
                }
            )
        else:
            # For other errors (type, pattern, etc.)
            if path:
                missing_fields.append(f"{path} ({error.message[:50]})")

    # Reduce string duplicates
    missing_fields_str = list(set(list(filter(
        lambda missing_field_iter: isinstance(missing_field_iter, str),
        missing_fields
    ))))

    missing_fields = missing_fields_str + list(filter(
        lambda missing_field_iter: isinstance(missing_field_iter, Dict),
        missing_fields
    ))

    return {"missingFields": missing_fields}
