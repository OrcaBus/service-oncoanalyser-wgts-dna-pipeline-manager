#!/usr/bin/env python3

"""
Generate workflow run comments for the populate-draft-data state machine.

Provides commentary on state transitions during draft data population:
- When tags or engine parameters change (requiring a new DRAFT event)
- When inputs are being populated (which may take time)
- When payload is unchanged and missing fields are identified
"""

# Standard imports
from os import environ
from typing import Dict, Any

# Layer imports
from orcabus_api_tools.workflow import add_comment_to_workflow_run

# Globals
WORKFLOW_NAME_ENV_VAR = "WORKFLOW_NAME"
REPOSITORY_GITHUB_URL_ENV_VAR = "REPOSITORY_GITHUB_URL"
COMMENT_AUTHOR = "{workflow_name}-populate-draft-data-service"
MAX_COMMENT_LENGTH = 1024
TRUNCATION_SUFFIX = "\n... [truncated, see execution ARN for full detail]"

COMMENT_TEMPLATES = {
    "tags_changed": "Updating draft tags before proceeding to input population.",
    "engine_parameters_changed": "Updating draft engine parameters before proceeding to input population.",
    "both_changed": "Updating draft tags and engine parameters before proceeding to input population.",
    "updating_inputs": "Updating inputs — this may take time to complete if awaiting upstream data or unarchiving.",
    "no_change_missing_fields": "Draft payload has not changed since last population attempt. The following required schema fields are still missing or incomplete:\n{missing_fields_list}\n\nTo resolve this, either:\nA) Wait for upstream processes to complete (FASTQ data availability, unarchiving)\nB) Manually provide the missing attributes via a WorkflowRunUpdate event\n\nFor details on upstream dependencies and manual submission, see: {repo_url}",
}


def handler(event: Dict[str, Any], context) -> Dict[str, bool]:
    """
    Add a comment to the workflow run indicating the current populate-draft-data stage.

    Event shape:
    {
        "workflowRunId": "<orcabus-id>",
        "commentType": "tags_changed" | "engine_parameters_changed" | "both_changed" | "updating_inputs" | "no_change_missing_fields",
        "missingFields": ["inputs.sequenceData", ...],  // only for no_change_missing_fields
        "executionArn": "<step-functions-execution-arn>"
    }

    Returns:
    {
        "commentAdded": true
    }
    """
    workflow_run_id = event["workflowRunId"]
    comment_type = event["commentType"]
    execution_arn = event.get("executionArn", "")
    missing_fields = event.get("missingFields", [])

    workflow_name = environ.get(WORKFLOW_NAME_ENV_VAR, "unknown")
    author = COMMENT_AUTHOR.format(workflow_name=workflow_name)
    repo_url = environ.get(REPOSITORY_GITHUB_URL_ENV_VAR, "")

    # Build comment body
    body = COMMENT_TEMPLATES.get(comment_type, f"State update: {comment_type}")

    # Handle the no_change_missing_fields template specially
    if comment_type == "no_change_missing_fields" and missing_fields:
        missing_fields_list = "\n- ".join([""] + missing_fields)  # prefix each with \n-
        body = body.format(missing_fields_list=missing_fields_list, repo_url=repo_url)
    elif comment_type == "no_change_missing_fields":
        body = body.format(missing_fields_list="\n- (none detected)", repo_url=repo_url)

    footer = f"---\nStep Functions Execution: {execution_arn}"

    full_comment = f"{body}\n{footer}"

    # Enforce 1024 char limit
    if len(full_comment) > MAX_COMMENT_LENGTH:
        # Keep the footer, truncate the body
        available = MAX_COMMENT_LENGTH - len(footer) - len(TRUNCATION_SUFFIX) - 1  # -1 for newline
        full_comment = f"{body[:available]}{TRUNCATION_SUFFIX}\n{footer}"

    add_comment_to_workflow_run(
        workflow_run_orcabus_id=workflow_run_id,
        comment=full_comment,
        author=author,
    )

    return {"commentAdded": True}
