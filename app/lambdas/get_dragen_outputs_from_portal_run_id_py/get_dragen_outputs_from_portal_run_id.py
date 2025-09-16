#!/usr/bin/env python3

"""
1 Get the latest succeeded workflow for a given library id
2 Get the BAM file from that workflow
"""

# Standard imports
from typing import Optional, Literal, List
from pathlib import Path

# Layer imports
from orcabus_api_tools.filemanager import get_file_manager_request_response_results
from orcabus_api_tools.filemanager.models import FileObject

# Globals
DRAGEN_WGTS_DNA_WORKFLOW_RUN_NAME = "dragen-wgts-dna"
Phenotype = Literal["TUMOR", "NORMAL"]
PHENOTYPE_LIST: List[Phenotype] = ["TUMOR", "NORMAL"]


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
            lambda file_iter: (
                file_iter['key'].endswith("_normal.bam")
            ),
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
    portal_run_id = event.get('portalRunId', None)
    phenotype: Phenotype = event.get('phenotype', None)

    if not phenotype in PHENOTYPE_LIST:
        raise ValueError(f"Phenotype must be one of {PHENOTYPE_LIST}")

    bam_file_obj = get_bam_from_dragen_workflow(portal_run_id, phenotype=phenotype)

    output_uri = f"s3://{bam_file_obj['bucket']}/{str(Path(bam_file_obj['key']))}"

    # Return the output
    if phenotype == 'TUMOR':
        return {
            "dragenTumorDnaBamUri": output_uri
        }

    return {
        "dragenNormalDnaBamUri": output_uri
    }
