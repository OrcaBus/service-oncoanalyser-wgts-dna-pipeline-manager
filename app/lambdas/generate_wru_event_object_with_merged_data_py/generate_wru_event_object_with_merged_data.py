#!/usr/bin/env python3

"""
Generate a WRU event object with merged data
"""
from typing import Dict, Any

# Layer imports
from orcabus_api_tools.workflow import (
    get_latest_payload_from_workflow_run,
    get_workflow_run_from_portal_run_id
)
from orcabus_api_tools.workflow.models import WorkflowRun, Payload


def handler(event, context):
    """
    Generate WRU event object with merged data
    :param event:
    :param context:
    :return:
    """

    # Get the event inputs
    # Get the event inputs
    portal_run_id = event.get("portalRunId", None)
    libraries = event.get("libraries", None)
    payload = event.get("payload", None)
    upstream_data = event.get("upstreamData", {})

    # Get the bam uris
    dragen_tumor_bam_uri = upstream_data.get('dragenTumorDnaBamUri', None)
    dragen_normal_bam_uri = upstream_data.get('dragenNormalDnaBamUri', None)

    # Create a copy of the oncoanalyser draft workflow run object to update
    oncoanalyser_draft_workflow_run = get_workflow_run_from_portal_run_id(
        portal_run_id=portal_run_id
    )

    # Make a copy
    oncoanalyser_draft_workflow_update = oncoanalyser_draft_workflow_run.copy()

    # Remove 'currentState' and replace with 'status'
    oncoanalyser_draft_workflow_update['status'] = oncoanalyser_draft_workflow_update.pop('currentState')['status']

    # Add in the libraries if provided
    if libraries is not None:
        oncoanalyser_draft_workflow_update["libraries"] = list(map(
            lambda library_iter: {
                "libraryId": library_iter['libraryId'],
                "orcabusId": library_iter['orcabusId'],
                "readsets": library_iter.get('readsets', [])
            },
            libraries
        ))

    # First check if the oncoanalyser draft workflow object has the fields we would update with the

    # Generate a workflow run update object with the merged data
    if (
            payload['data'].get("inputs", {}).get("tumorDnaBamUri", None) is not None or
            payload['data'].get("inputs", {}).get("normalDnaBamUri", None) is not None
    ):
        # Return the OG, we dont want to overwrite existing data
        oncoanalyser_draft_workflow_update["payload"] = {
            "version": payload['version'],
            "data": payload['data']
        }
        return {
            "oncoanalyserWgtsDnaWorkflowRunUpdate": oncoanalyser_draft_workflow_update
        }

    # Merge the data from the dragen draft payload into the oncoanalyser draft payload
    new_data_object = payload['data'].copy()
    if new_data_object.get("inputs", None) is None:
        new_data_object["inputs"] = {}
    new_data_object["inputs"]["tumorDnaBamUri"] = dragen_tumor_bam_uri
    new_data_object["inputs"]["normalDnaBamUri"] = dragen_normal_bam_uri

    # Update the inputs with the dragen draft payload data
    oncoanalyser_draft_workflow_update["payload"] = {
        "version": payload['version'],
        "data": new_data_object
    }

    return {
        "oncoanalyserWgtsDnaWorkflowRunUpdate": oncoanalyser_draft_workflow_update
    }
