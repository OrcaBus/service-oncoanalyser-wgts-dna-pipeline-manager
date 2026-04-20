#!/usr/bin/env python3

"""
Post schema validation for oncoanalyser wgts dna workflows

Performs the following steps:
* Validate inputs, ensure each uri is available in the project context.

* Validate engine parameters, ensure that the output / logs and cache uris
all start with the project prefix.
* Confirm that the pipeline is in the project
* Ensure that the output / logs and cache uris all end with the portal run id

Log any failures to the OrcaUI

"""

# Imports
from typing import Dict, Tuple
import logging
from os import environ

# Wrapica imports
from wrapica.project_data import coerce_data_id_or_uri_to_project_data_obj, get_project_data_obj_by_id
from libica.openapi.v3 import ApiException
from wrapica.storage_configuration import get_s3_key_prefix_by_project_id
from wrapica.project_pipelines import get_project_pipeline_obj

# Layer imports
from orcabus_api_tools.filemanager.errors import S3FileNotFoundError
from orcabus_api_tools.workflow import add_comment_to_workflow_run, get_workflow_run
from orcabus_api_tools.filemanager import get_s3_object_id_from_s3_uri

from icav2_tools import set_icav2_env_vars

# Globals
WORKFLOW_NAME_ENV_VAR = "WORKFLOW_NAME"
COMMENT_AUTHOR = "{WORKFLOW_NAME}-workflow-validation-service"
TEST_BUCKET_ENV_VAR = "TEST_DATA_BUCKET_NAME"
REF_DATA_BUCKET_ENV_VAR = "REF_DATA_BUCKET_NAME"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_engine_parameters(
        engine_parameters: Dict,
        workflow_run_id: str = None,
        project_prefix: str = None
) -> Tuple[bool, str]:
    """
    Validate the engine parameters.
    :param engine_parameters: The engine parameters to validate.
    :param workflow_run_id: The workflow run ID
    :param project_prefix: The project prefix
    :return: A tuple of (is_valid, comment)
    """
    # Get the project id
    project_id = engine_parameters.get("projectId")

    # Confirm that the outputUri and logsUri are a subset of the project prefix
    output_uri = engine_parameters.get("outputUri", "")
    logs_uri = engine_parameters.get("logsUri", "")
    cache_uri = engine_parameters.get("cacheUri", "")
    pipeline_id = engine_parameters.get("pipelineId", "")

    # Validate the uris are correct
    if not output_uri.startswith(project_prefix):
        return False, f"outputUri '{output_uri}' is not in the project context '{project_prefix}'"
    if not logs_uri.startswith(project_prefix):
        return False, f"logsUri '{logs_uri}' is not in the project context '{project_prefix}'"
    if not cache_uri.startswith(project_prefix):
        return False, f"cacheUri '{cache_uri}' is not in the project context '{project_prefix}'"

    # Ensure that the output uri, logs uri and cache uri aren't all the same
    if not (
            len(list({output_uri, logs_uri, cache_uri})) == len(list([output_uri, logs_uri, cache_uri]))
    ):
        return False, f"output uri, logs uri and cache uri must all be distinct"

    # Confirm the pipeline is in the project
    try:
        _ = get_project_pipeline_obj(
            project_id=project_id,
            pipeline_id=pipeline_id,
        )
    except ValueError as e:
        return False, f"The pipeline {pipeline_id} cannot be found in the project {project_id}"

    # Get the portal run id from the workflow run id
    portal_run_id = get_workflow_run(workflow_run_id)['portalRunId']

    # Confirm that the output uri, logs uri end with the portal run id
    if not output_uri.endswith(f"/{portal_run_id}/"):
        return False, f"outputUri '{output_uri}' does not end with the portal run id '{portal_run_id}'"
    if not logs_uri.endswith(f"/{portal_run_id}/"):
        return False, f"logsUri '{logs_uri}' does not end with the portal run id '{portal_run_id}'"
    if not cache_uri.endswith(f"/{portal_run_id}/"):
        return False, f"cacheUri '{cache_uri}' does not end with the portal run id '{portal_run_id}'"

    return True, ""


def validate_inputs(
        inputs: Dict,
        project_id: str,
        project_prefix: str,
) -> Tuple[bool, str]:
    """
    Validate the inputs.

    :param inputs: The inputs to validate.
    :param project_id: The ICAv2 project id to validate against.
    :param project_prefix: The ICAv2 project prefix
    """
    # Initalise the data uris list
    data_uris = []
    # Get all fastq uris from the inputs
    # (we will support oncoanalyser from fastq in a later iteration)
    for fastq_obj in inputs.get("fastqListRows", []):
        # We filter out 'None' values later
        data_uris.extend([
            fastq_obj.get("read1FileUri"),
            fastq_obj.get("read2FileUri")
        ])
    # Get all bam inputs
    for key in ["tumorDnaBamUri", "normalDnaBamUri"]:
        data_uris.append(inputs.get(key))

    # Remove empty / null values from list
    data_uris = list(filter(
        # Is not empty or None
        lambda uri_iter_: uri_iter_,
        data_uris
    ))

    # Confirm each data uri is available from the filemanager
    for data_uri in data_uris:
        # Try to get the object from the filemanager
        try:
            get_s3_object_id_from_s3_uri(data_uri)
        except S3FileNotFoundError as e:
            return False, f"Data uri '{data_uri}' cannot be found by the filemanager, are you sure it exists?"

    # Or externally mounted data uris (e.g. s3://reference-data-bucket/...)
    data_uris = list(filter(
        lambda uri_iter_: (
            # Doesn't belong to test-data bucket
            # Doesn't belong to the project bucket
            not (
                uri_iter_.startswith(f"s3://{environ[TEST_BUCKET_ENV_VAR]}/") or
                uri_iter_.startswith(f"s3://{environ[REF_DATA_BUCKET_ENV_VAR]}/") or
                uri_iter_.startswith(project_prefix)
            )
        ),
        data_uris
    ))

    # Validate each fastq uri
    for data_uri in data_uris:
        # Try get the icav2 object by uri
        try:
            project_data_obj = coerce_data_id_or_uri_to_project_data_obj(
                data_id_or_uri=data_uri,
            )
        except ValueError as e:
            return False, f"Data uri '{data_uri}' cannot be found in the project context '{project_id}'"

        # Then try get it in this context
        try:
            get_project_data_obj_by_id(
                project_id=project_id,
                data_id=project_data_obj.data.id
            )
        except ApiException as e:
            return False, f"Data uri '{data_uri}' cannot be found in the project context '{project_id}'"

    return True, ""


def handler(event, context) -> Dict[str, bool]:
    """
    Given a draft schema, validate it against the current schema and print the results.
    :return:
    """
    # We have a valid schema, lets confirm that the fastq uris are valid uris and in the appropriate project context
    # Set env vars
    set_icav2_env_vars()

    # Get the event data
    payload_data = event.get('data')
    workflow_run_id = event.get("workflowRunId", "")

    # Get the ICAv2 project id from the event
    engine_parameters = payload_data.get("engineParameters")

    # Get the project prefix
    project_prefix = get_s3_key_prefix_by_project_id(engine_parameters.get("projectId"))

    # Confirm the engine parameters match
    is_valid, comment = validate_engine_parameters(
        engine_parameters,
        workflow_run_id=workflow_run_id,
        project_prefix=project_prefix,
    )

    # Check if the inputs are also valid
    if is_valid:
        # Get the inputs and confirm that the fastq uris are valid
        # and are accessible in the right project context
        inputs = payload_data.get("inputs")
        # Validate the inputs
        is_valid, comment = validate_inputs(
            inputs,
            project_id=engine_parameters.get("projectId"),
            # Get the key prefix for the project
            project_prefix=get_s3_key_prefix_by_project_id(engine_parameters.get("projectId"))
        )

    # Somewhere along the way, the validation failed
    if not is_valid:
        add_comment_to_workflow_run(
            workflow_run_orcabus_id=workflow_run_id,
            comment=f"Post schema validation failed: {comment}",
            author=COMMENT_AUTHOR.format(
                WORKFLOW_NAME=environ.get(WORKFLOW_NAME_ENV_VAR)
            )
        )
        return {
            "isValid": False
        }

    return {
        "isValid": True
    }
