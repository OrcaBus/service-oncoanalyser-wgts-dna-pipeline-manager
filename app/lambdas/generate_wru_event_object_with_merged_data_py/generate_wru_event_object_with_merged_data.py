#!/usr/bin/env python3

"""
Generate a WRU event object with merged data
"""

# Layer imports
from orcabus_api_tools.workflow import get_latest_payload_from_workflow_run
from orcabus_api_tools.workflow.models import WorkflowRun, Payload


def handler(event, context):
    """
    Generate WRU event object with merged data
    :param event:
    :param context:
    :return:
    """

    # Get the event inputs
    dragen_tumor_bam_uri: str = event['dragenTumorDnaBamUri']
    dragen_normal_bam_uri: str = event['dragenNormalDnaBamUri']
    oncoanalyser_draft_workflow_run_object: WorkflowRun = event['oncoanalyserWgtsDnaDraftWorkflowRunObject']

    # First check if the oncoanalyser draft workflow object has the fields we would update with the
    # dragen draft payload
    # If not, we should replace them and instead return the original values
    latest_oncoanalyser_payload: Payload = get_latest_payload_from_workflow_run(oncoanalyser_draft_workflow_run_object['orcabusId'])

    # Generate a workflow run update object with the merged data
    if (
            latest_oncoanalyser_payload['data'].get("inputs", {}).get("tumorDnaBamUri", None) is not None or
            latest_oncoanalyser_payload['data'].get("inputs", {}).get("normalDnaBamUri", None) is not None
    ):
        return {}

    oncoanalyser_draft_update = oncoanalyser_draft_workflow_run_object.copy()
    # Delete the currentState attribute from the API, all others can stay
    _ = oncoanalyser_draft_update.pop('currentState', None)

    # Merge the data from the dragen draft payload into the oncoanalyser draft payload
    new_data_object = latest_oncoanalyser_payload['data'].copy()
    if new_data_object.get("inputs", None) is None:
        new_data_object["inputs"] = {}
    new_data_object["inputs"]["tumorDnaBamUri"] = dragen_tumor_bam_uri
    new_data_object["inputs"]["normalDnaBamUri"] = dragen_normal_bam_uri

    # Update the inputs with the dragen draft payload data
    oncoanalyser_draft_update["payload"] = {
        "version": latest_oncoanalyser_payload['version'],
        "data": new_data_object
    }

    return {
        "oncoanalyserWgtsDnaDraftWorkflowRunUpdate": oncoanalyser_draft_update
    }
