#!/usr/bin/env python3

"""
Given an upstream portal run id,
find the draft workflow object for sash

"""
# Standard imports
from typing import List

# Local imports
from orcabus_api_tools.workflow import (
    get_workflow_runs_from_metadata
)
from orcabus_api_tools.workflow.models import WorkflowRunDetail

# Globals
TERMINAL_DEPRECATED_STATES = [
    'DEPRECATED',
    'RESOLVED'
]


def handler(event, context):
    """
    Get the latest payload from the portal run id
    :param event:
    :param context:
    :return:
    """
    # Get the upstream events

    # Get the workflow type, name is mandatory
    workflow_name = event['workflowName']
    workflow_version = event.get('workflowVersion', None)

    # Workflow state
    workflow_status = event.get('status', None)

    # Get the libraries / and/or the analysis run id
    # The analysis run id takes preference when making queries
    analysis_run_id = event.get('analysisRunId', None)
    libraries = event.get('libraries', [])
    rgid_list = event.get('rgidList', None)

    # Now we have our workflows, filter to the correct workflow name (and version if provided)
    workflows_list: List[WorkflowRunDetail]
    workflows_list = get_workflow_runs_from_metadata(
        analysis_run_id=analysis_run_id,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
        library_id_list=list(map(
            lambda library_iter_: library_iter_['libraryId'],
            libraries
        )),
        rgid_list=rgid_list
    )

    # Filter to workflow state if provided
    if workflow_status is not None:
        # We need to make sure that we dont have any workflows that are still running
        # That were started AFTER the last succeeded one
        if (
            workflow_status == 'SUCCEEDED' and
            len(workflows_list) > 1
        ):

            # First remove DEPRECATED / RESOLVED runs from the list
            # Since the most recent appropriate run registered may not be the last
            workflows_list = list(filter(
                lambda workflow_run_iter: workflow_run_iter['currentState']['status'] not in TERMINAL_DEPRECATED_STATES,
                workflows_list
            ))

            # Now check the latest workflow is SUCCEEDED
            if not (
                    sorted(
                        workflows_list,
                        key=lambda workflow_iter_: workflow_iter_['orcabusId'],
                        reverse=True
                    )[0]['currentState']['status'] == workflow_status
            ):
                return {
                    "workflowRunObject": None
                }

        # Filter by status
        workflows_list = list(filter(
            lambda workflow_iter_: workflow_iter_['currentState']['status'] == workflow_status,
            workflows_list
        ))

    if len(workflows_list) == 0:
        return {
            "workflowRunObject": None
        }

    # Get the latest draft workflow for the given workflow name
    return {
        "workflowRunObject": sorted(
            workflows_list,
            key=lambda workflow_iter_: workflow_iter_['orcabusId'],
            reverse=True
        )[0]
    }
