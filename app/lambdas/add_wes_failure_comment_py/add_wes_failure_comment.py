#!/usr/bin/env python3

"""
The ICA analysis has failed, we add a comment to the analysis
"""

# Standard imports
from os import environ

# Local imports
from orcabus_api_tools.workflow import (
    add_comment_to_workflow_run, get_workflow_run_from_portal_run_id
)

# Globals
WORKFLOW_NAME_ENV_VAR = "WORKFLOW_NAME"
COMMENT_AUTHOR = "{WORKFLOW_NAME}-icav2-wes-event-service"


def handler(event, context):
    """
    Add a comment to the ICA analysis indicating failure.

    """

    # Collect inputs
    error_type = event.get("errorType")
    error_message_uri = event.get("errorMessageUri")
    portal_run_id = event.get("portalRunId")
    execution_arn = event.get("executionArn", "")

    # Get the workflow run id from the portal run id
    workflow_run_id = get_workflow_run_from_portal_run_id(portal_run_id)["orcabusId"]

    # Construct the comment body
    body = f"The workflow has failed with error type '{error_type}', full traceback can be found at '{error_message_uri}'"
    footer = f"---\nStep Functions Execution: {execution_arn}"
    full_comment = f"{body}\n{footer}"

    # Enforce 1024 char limit
    max_length = 1024
    if len(full_comment) > max_length:
        truncation_suffix = "\n... [truncated, see execution ARN for full detail]"
        available = max_length - len(footer) - len(truncation_suffix) - 1
        full_comment = f"{body[:available]}{truncation_suffix}\n{footer}"

    # Construct the comment
    add_comment_to_workflow_run(
        workflow_run_orcabus_id=workflow_run_id,
        comment=full_comment,
        author=COMMENT_AUTHOR.format(
            WORKFLOW_NAME=environ.get(WORKFLOW_NAME_ENV_VAR)
        )
    )
