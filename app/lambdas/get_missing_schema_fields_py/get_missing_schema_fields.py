#!/usr/bin/env python3

"""
Given a payload data object, validate it against the schema and return the list of missing/invalid fields.
"""

import boto3
import json
import typing
import jsonschema
from os import environ
from pathlib import Path

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
    missing_fields = []
    for error in errors:
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else ""
        if error.validator == "required":
            # For required errors, list each missing property
            for missing_prop in error.validator_value:
                if missing_prop not in error.instance:
                    field_path = f"{path}.{missing_prop}" if path else missing_prop
                    missing_fields.append(field_path)
        else:
            # For other errors (type, pattern, etc.)
            if path:
                missing_fields.append(f"{path} ({error.message[:50]})")

    return {"missingFields": missing_fields}
