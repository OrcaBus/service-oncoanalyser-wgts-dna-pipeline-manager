#!/usr/bin/env python3

"""
1 Get the latest succeeded workflow for a given library id
2 Get the BAM file from that workflow
"""

# Standard imports
from typing import Optional, Literal, List

# Layer imports
from orcabus_api_tools.workflow import get_workflows_from_library_id, get_workflow_run
from orcabus_api_tools.filemanager import get_file_manager_request_response_results
from orcabus_api_tools.filemanager.models import FileObject

# Globals
DRAGEN_WGTS_DNA_WORKFLOW_RUN_NAME = "dragen-wgts-dna"
Phenotype = Literal["TUMOR", "NORMAL"]


def get_latest_dragen_workflow(
        tumor_library_id: str,
        normal_library_id: str
) -> Optional[str]:
    """
    Get the BAM file from the latest succeeded dragen workflow for a given library id
    :param tumor_library_id:
    :param normal_library_id:
    :return:
    """

    # Get workflows
    tumor_workflows = list(filter(
        lambda workflow_iter_: (
            workflow_iter_['workflow'].get('name', "") == DRAGEN_WGTS_DNA_WORKFLOW_RUN_NAME or
            # Prod workaround
            workflow_iter_['workflow'].get('workflowName', "") == DRAGEN_WGTS_DNA_WORKFLOW_RUN_NAME
        ),
        get_workflows_from_library_id(tumor_library_id)
    ))
    normal_workflows = list(filter(
        lambda workflow_iter_: (
            workflow_iter_['workflow'].get('name', "") == DRAGEN_WGTS_DNA_WORKFLOW_RUN_NAME or
            # Prod workaround
            workflow_iter_['workflow'].get('workflowName', "") == DRAGEN_WGTS_DNA_WORKFLOW_RUN_NAME
        ),
        get_workflows_from_library_id(normal_library_id)
    ))

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

    # Get the latest workflow by orcabusId
    latest_workflow = sorted(
        intersecting_workflows,
        key=lambda workflow_iter_: workflow_iter_['orcabusId'],
        reverse=True
    )[0]

    # Check the state of the latest workflow, if it is not succeeded we should not use it
    if not latest_workflow['currentState']['status'] == 'SUCCEEDED':
        return None

    return latest_workflow['portalRunId']


def get_bam_from_dragen_workflow(portal_run_id: str, phenotype: Phenotype) -> Optional[FileObject]:
    bam_file: FileObject
    if phenotype == 'TUMOR':
        bam_file = next(filter(
            lambda file_iter: file_iter['key'].endswith("_tumor.bam"),
            get_file_manager_request_response_results(
                endpoint="api/v1/s3/attributes",
                params={
                    "portalRunId": portal_run_id,
                }
            )
        ))
        return bam_file
    elif phenotype == 'NORMAL':
        bam_file = next(filter(
            lambda file_iter: file_iter['key'].endswith("_normal.bam"),
            get_file_manager_request_response_results(
                endpoint="api/v1/s3/attributes",
                params={
                    "portalRunId": portal_run_id,
                }
            )
        ))
        return bam_file
    raise ValueError("Phenotype must be either 'TUMOR' or 'NORMAL'")


def handler(event, context):
    """
    Given a normal and tumor library id, get the latest dragen workflow and return the bam files
    :param event:
    :param context:
    :return:
    """

    # Get the library ids from the event
    tumor_library_id = event.get('tumorLibraryId', None)
    normal_library_id = event.get('normalLibraryId', None)
    portal_run_id = event.get('portalRunId', None)
    phenotype: Phenotype = event.get('phenotype', None)

    # Get the latest dragen workflow for the tumor library id
    if (
            (
                    tumor_library_id is None or normal_library_id is None
            ) and
            (
                    portal_run_id is None or phenotype is None
            )
    ):
        raise ValueError("Either tumorLibraryId and normalLibraryId or portalRunId and phenotype must be provided")

    if portal_run_id is None:
        portal_run_id = get_latest_dragen_workflow(tumor_library_id, normal_library_id)

        if portal_run_id is None:
            return {}

        tumor_bam_file_obj = get_bam_from_dragen_workflow(portal_run_id, phenotype='TUMOR')
        normal_bam_file_obj = get_bam_from_dragen_workflow(portal_run_id, phenotype='NORMAL')

        # Return the bam file URIs
        # If weve set a phenotype, return only that bam, useful in the populate draft data step
        # Otherwise return both
        if phenotype == 'TUMOR':
            return {
                "bamUri": f"s3://{tumor_bam_file_obj['bucket']}/{tumor_bam_file_obj['key']}"
            }
        elif phenotype == 'NORMAL':
            return {
                "bamUri": f"s3://{normal_bam_file_obj['bucket']}/{normal_bam_file_obj['key']}"
            }
        return {
            "tumorDnaBamUri": f"s3://{tumor_bam_file_obj['bucket']}/{tumor_bam_file_obj['key']}",
            "normalDnaBamUri": f"s3://{normal_bam_file_obj['bucket']}/{normal_bam_file_obj['key']}",
        }

    else:
        return {
            "bamUri": get_bam_from_dragen_workflow(portal_run_id, phenotype=phenotype)
        }


if __name__ == "__main__":
    from os import environ
    import json

    environ['AWS_PROFILE'] = 'umccr-production'
    environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
    environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'

    print(json.dumps(
        handler(
            {
                "tumorLibraryId": "L2300943",
                "normalLibraryId": "L2300950"
            },
            None
        ),
        indent=4
    ))

# {
#     "tumorBamUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/analysis/dragen-wgts-dna/202509019aa880c3/L2300943__L2300950__hg38__linear__dragen_wgts_dna_somatic_variant_calling/L2300943_tumor.bam",
#     "normalBamUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/analysis/dragen-wgts-dna/202509019aa880c3/L2300943__L2300950__hg38__linear__dragen_wgts_dna_somatic_variant_calling/L2300950_normal.bam"
# }
