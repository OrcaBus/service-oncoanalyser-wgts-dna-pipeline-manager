#!/usr/bin/env python3

"""
Download the draft schema, validate it against the current schema, and print the results.
"""

# Imports
import json
import boto3
import typing
import jsonschema
from os import environ
from typing import Dict

from jsonschema import ValidationError

# Type checking imports
if typing.TYPE_CHECKING:
    from mypy_boto3_schemas import SchemasClient
    from mypy_boto3_ssm import SSMClient

# Globals
SSM_REGISTRY_NAME_ENV_VAR = "SSM_REGISTRY_NAME"
SSM_SCHEMA_NAME_ENV_VAR = "SSM_SCHEMA_NAME"


def get_ssm_parameter_value(parameter_name: str) -> str:
    """
    Get the SSM parameter for the schema.
    :return: The SSM parameter value.
    """

    # Get the ssm client
    ssm_client: SSMClient = boto3.client("ssm")

    # Get the SSM parameter value
    response = ssm_client.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )

    return response["Parameter"]["Value"]


def get_schema_from_registry(
        registry_name: str,
        schema_name: str
) -> str:
    """
    Get the schema from the schema registry.
    :param registry_name: The name of the schema registry.
    :param schema_name: The name of the schema.
    :return: The schema as a string.
    """

    # Get the schemas client
    schemas_client: SchemasClient = boto3.client("schemas")

    # Get the schema from the registry
    response = schemas_client.describe_schema(
        RegistryName=registry_name,
        SchemaName=schema_name
    )

    return response["Content"]


def validate_draft_schema(
        json_schema: str,
        json_body: str
) -> bool:
    """
    Download the draft schema, validate it against the current schema, and print the results.
    """
    try:
        jsonschema.validate(
            instance=json.loads(json_body),
            schema=json.loads(json_schema)
        )
    except ValidationError:
        return False
    return True


def handler(event, context) -> Dict[str, bool]:
    """
    Given a draft schema, validate it against the current schema and print the results.
    :return:
    """
    # Get the SSM parameters
    schema_registry = get_ssm_parameter_value(environ[SSM_REGISTRY_NAME_ENV_VAR])
    schema_name = json.loads(get_ssm_parameter_value(environ[SSM_SCHEMA_NAME_ENV_VAR]))['schemaName']

    # Get the current schema from the schema registry
    current_schema = get_schema_from_registry(
        registry_name=schema_registry,
        schema_name=schema_name
    )

    # Get the draft schema from the schema registry
    return {
        "isValid": validate_draft_schema(
            current_schema,
            # Assuming the event contains the draft schema as a JSON string
            json.dumps(event)
        )
    }


# if __name__ == "__main__":
#     from os import environ
#     import json
#     environ['AWS_PROFILE'] = 'umccr-development'
#     environ["SSM_REGISTRY_NAME"] = '/orcabus/workflows/dragen-wgts-dna/schemas/registry'
#     environ["SSM_SCHEMA_NAME"] = '/orcabus/workflows/dragen-wgts-dna/schemas/dragen-wgts-dna-complete-data-draft/latest'
#     print(json.dumps(
#         handler({}, None),
#         indent=4
#     ))
