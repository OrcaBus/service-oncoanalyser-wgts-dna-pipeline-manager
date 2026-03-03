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
import logging
from jsonschema import ValidationError

from orcabus_api_tools.workflow import add_comment_to_workflow_run

# Type checking imports
if typing.TYPE_CHECKING:
    from mypy_boto3_schemas import SchemasClient
    from mypy_boto3_ssm import SSMClient

# Globals
SSM_REGISTRY_NAME_ENV_VAR = "SSM_REGISTRY_NAME"
SSM_SCHEMA_NAME_ENV_VAR = "SSM_SCHEMA_NAME"
WORKFLOW_NAME_ENV_VAR = "WORKFLOW_NAME"
COMMENT_AUTHOR = "{WORKFLOW_NAME}-workflow-validation-service"

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        json_body: str,
        workflow_run_id: str = None,
        comment_error: bool = False
) -> bool:
    """
    Download the draft schema, validate it against the current schema, and print the results.

    :param json_schema: The current schema as a JSON string.
    :param json_body: The draft schema as a JSON string.
    :param workflow_run_id: The workflow run ID to add comments to (if any).
    :param comment_error: Whether to add a comment to the workflow run on validation error.
    """
    try:
        jsonschema.validate(
            instance=json.loads(json_body),
            schema=json.loads(json_schema),
        )
    except ValidationError as e:
        logger.info(f"Failed validation, {e}")
        if comment_error:
            add_comment_to_workflow_run(
                workflow_run_orcabus_id=workflow_run_id,
                comment=f"Draft schema validation failed: {e.message} at \"{e.json_path}\"",
                author=COMMENT_AUTHOR.format(
                    WORKFLOW_NAME=environ.get(WORKFLOW_NAME_ENV_VAR)
                )
            )
        return False
    return True


def handler(event, context) -> Dict[str, bool]:
    """
    Given a draft schema, validate it against the current schema and print the results.
    :return:
    """
    # Get the event data
    payload_data = event.get('data')
    workflow_run_id = event.get("workflowRunId", "")
    comment_error = event.get("addCommentOnError", False)

    # Get the SSM parameters
    schema_registry = get_ssm_parameter_value(environ[SSM_REGISTRY_NAME_ENV_VAR])
    schema_name = json.loads(get_ssm_parameter_value(environ[SSM_SCHEMA_NAME_ENV_VAR]))['schemaName']

    # Get the current schema from the schema registry
    current_schema = get_schema_from_registry(
        registry_name=schema_registry,
        schema_name=schema_name
    )

    # Validate the draft schema against the current schema
    is_valid_schema = validate_draft_schema(
        current_schema,
        # Assuming the event contains the draft schema as a JSON string
        json.dumps(payload_data),
        workflow_run_id=workflow_run_id,
        comment_error=comment_error
    )

    # Return if the schema is not valid
    return {
        "isValid": is_valid_schema
    }
