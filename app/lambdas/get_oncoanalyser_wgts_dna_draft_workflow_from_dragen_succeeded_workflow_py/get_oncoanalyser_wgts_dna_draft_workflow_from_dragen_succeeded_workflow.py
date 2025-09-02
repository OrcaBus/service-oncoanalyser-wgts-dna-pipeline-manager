#!/usr/bin/env python3

"""
Get oncoanalyser wgts dna draft event from dragen succeeded event.

Given a dragen portal run id, find any oncoanalyser wgts dna draft event
"""

# Standard imports
from typing import Optional, List

# Layer imports
from orcabus_api_tools.workflow import (
    get_workflows_from_library_id,
    get_workflow_run, get_workflow_run_from_portal_run_id
)
from orcabus_api_tools.workflow.models import WorkflowRunDetail


def get_latest_oncoanalyser_wgts_workflow(
        libraries_list: List[str],
) -> Optional[str]:
    """
    Get the BAM file from the latest succeeded dragen workflow for a given library id
    :param tumor_library_id:
    :param normal_library_id:
    :return:
    """

    # Get workflows for the given library ids
    # Doesnt matter which order the libraries are in, just need both
    tumor_workflows = get_workflows_from_library_id(libraries_list[0])
    normal_workflows = get_workflows_from_library_id(libraries_list[1])

    if len(tumor_workflows) == 0 or len(normal_workflows) == 0:
        return None

    # Get intersection of workflow IDs
    intersecting_workflow_ids = list(
        set(
            list(map(lambda workflow_iter_: workflow_iter_['orcabusId'], tumor_workflows))
        ).intersection(
            set(
                list(map(lambda workflow_iter_: workflow_iter_['orcabusId'], normal_workflows))
            )
        )
    )

    # If no intersecting workflows, return None
    if len(intersecting_workflow_ids) == 0:
        return None

    # Get the intersection of workflow objects
    intersecting_workflows = list(map(
        lambda workflow_iter_: get_workflow_run(workflow_iter_['orcabusId']),
        list(filter(
            lambda workflow_iter_: workflow_iter_['orcabusId'] in intersecting_workflow_ids,
            tumor_workflows
        ))
    ))

    # Get the latest draft oncoanalyser workflows for the given library id
    oncoanalyser_wgts_dna_draft_workflows: List[WorkflowRunDetail] = list(filter(
        lambda workflow_iter_: (
            workflow_iter_['workflow']['name'] == ONCOANALYSER_WGTS_DNA_WORKFLOW_RUN_NAME
            and workflow_iter_['currentState']['status'] == "DRAFT"
        ),
        intersecting_workflows
    ))

    # If no oncoanalyser workflows, return None
    if len(oncoanalyser_wgts_dna_draft_workflows) == 0:
        return None

    # Get the latest workflow by orcabusId
    latest_workflow = sorted(
        oncoanalyser_wgts_dna_draft_workflows,
        key=lambda workflow_iter_: workflow_iter_['orcabusId'],
        reverse=True
    )[0]

    return latest_workflow['portalRunId']


# Globals
ONCOANALYSER_WGTS_DNA_WORKFLOW_RUN_NAME = "oncoanalyser-wgts-dna"


def handler(event, context):
    """
    Get the oncoanalyser wgts dna draft payload from the dragen succeeded event.
    :param event:
    :param context:
    :return:
    """

    # Expect a portal run id as input
    portal_run_id = event.get("dragenWgtsDnaSucceededPortalRunId")

    # Get the workflow run for the dragen wgts dna workflow
    dragen_wgts_dna_workflow_run_obj = get_workflow_run_from_portal_run_id(
        portal_run_id,
    )

    # Get the libraries from the dragen workflow run
    libraries = dragen_wgts_dna_workflow_run_obj.get("libraries", [])

    # Expect two libraries (tumor and normal)
    if len(libraries) != 2:
        return None

    # Now get the portal run id for the latest oncoanalyser wgts dna draft workflow
    oncoanalyser_wgts_draft_portal_run_id = get_latest_oncoanalyser_wgts_workflow(
        libraries_list=list(map(
            lambda library_iter_: library_iter_['libraryId'],
            libraries
        ))
    )

    return {
        "oncoanalyserWgtsDnaDraftWorkflowRunObject": get_workflow_run_from_portal_run_id(oncoanalyser_wgts_draft_portal_run_id)
    }
