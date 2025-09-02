#!/usr/bin/env python3

"""
Compare the payload of the original portal run id and that of the new object

We dont want to accidentally end up in an infinite loop, so we only want to push a WRU / WRSC event if
the payload has changed
"""

# Standard library imports
from deepdiff import DeepDiff
from typing import Dict, Any
from requests import HTTPError

# Layer imports
from orcabus_api_tools.workflow import get_latest_payload_from_portal_run_id
from orcabus_api_tools.workflow.models import Payload


def handler(event, context):
    """
    Get the latest payload from the portal run id and compare it to the new object payload
    :param event:
    :param context:
    :return:
    """
    try:
        workflow_object_payload: Payload = get_latest_payload_from_portal_run_id(
            portal_run_id=event['portalRunId']
        )
    except HTTPError as e:
        # This will be fixed in the next platform constructs release
        workflow_object_payload = {}
    new_payload = event['newPayload']

    # Now no longer a valid payload object
    workflow_object_payload: Dict[str, Any]
    # Remove the payload ref id attribute along with the orcabus id
    if 'payloadRefId' in workflow_object_payload:
        del workflow_object_payload['payloadRefId']
    if 'orcabusId' in workflow_object_payload:
        del workflow_object_payload['orcabusId']

    if not DeepDiff(workflow_object_payload, new_payload):
        return {
            "hasChanged": False
        }
    return {
        "hasChanged": True
    }


# if __name__ == "__main__":
#     from os import environ
#     import json
#
#     environ['AWS_PROFILE'] = 'umccr-development'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#
#     print(json.dumps(
#         handler(
#             {
#                 "portalRunId": "202509020a4000ed",
#                 "newPayload": {
#                     "version": "2025.08.05",
#                     "data": {
#                         "inputs": {
#                             "mode": "wgts",
#                             "genome": "GRCh38_umccr",
#                             "genomeVersion": "38",
#                             "genomeType": "alt",
#                             "forceGenome": True,
#                             "genomes": {
#                                 "GRCh38Umccr": {
#                                     "fasta": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/GRCh38_full_analysis_set_plus_decoy_hla.fa",
#                                     "fai": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai",
#                                     "dict": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.dict",
#                                     "img": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.img",
#                                     "bwamem2Index": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/bwa-mem2_index/2.2.1/",
#                                     "gridssIndex": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/gridss_index/2.13.2/",
#                                     "starIndex": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/star_index/gencode_38/2.7.3a/"
#                                 }
#                             },
#                             "tumorDnaSampleId": "L2300943",
#                             "normalDnaSampleId": "L2300950",
#                             "refDataHmfDataPath": "s3://reference-data-503977275616-ap-southeast-2/refdata/hartwig/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.1.0--1/"
#                         },
#                         "engineParameters": {
#                             "logsUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-dna/202509020a4000ed/",
#                             "outputUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/analysis/oncoanalyser-wgts-dna/202509020a4000ed/",
#                             "projectId": "ea19a3f5-ec7c-4940-a474-c31cd91dbad4",
#                             "pipelineId": "ab6e1d62-1b5a-4b24-86b8-81ccf4bdc7a2"
#                         },
#                         "tags": {
#                             "libraryId": "L2300950",
#                             "subjectId": "HCC1395",
#                             "individualId": "SBJ00480",
#                             "fastqRgidList": [
#                                 "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7"
#                             ],
#                             "tumorLibraryId": "L2300943",
#                             "tumorFastqRgidList": [
#                                 "ACTAAGAT+CCGCGGTT.4.230602_A00130_0258_BH55TMDSX7",
#                                 "ACTAAGAT+CCGCGGTT.3.230602_A00130_0258_BH55TMDSX7"
#                             ]
#                         }
#                     }
#                 }
#             },
#             None
#         ),
#         indent=4
#     ))
#
# # {
# #     "tumorBamUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/analysis/dragen-wgts-dna/202509019aa880c3/L2300943__L2300950__hg38__linear__dragen_wgts_dna_somatic_variant_calling/L2300943_tumor.bam",
# #     "normalBamUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/analysis/dragen-wgts-dna/202509019aa880c3/L2300943__L2300950__hg38__linear__dragen_wgts_dna_somatic_variant_calling/L2300950_normal.bam"
# # }
