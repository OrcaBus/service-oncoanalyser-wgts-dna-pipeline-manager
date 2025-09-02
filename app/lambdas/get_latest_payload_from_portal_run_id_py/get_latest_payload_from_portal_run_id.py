#!/usr/bin/env python3

"""
Get the dragen wgts dna succeeded event object
"""

# Layer imports
from orcabus_api_tools.workflow import get_latest_payload_from_portal_run_id


def handler(event, context):
    """
    Get the workflow run object
    :param event:
    :param context:
    :return:
    """
    # Get the portal run id from the event object
    portal_run_id = event['portalRunId']

    # Get the workflow run object
    workflow_payload = get_latest_payload_from_portal_run_id(portal_run_id)

    # Return the workflow payload object
    return {
        "payload": workflow_payload
    }

# if __name__ == "__main__":
#     from os import environ
#     import json
#     environ['AWS_PROFILE'] = 'umccr-production'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#
#     print(json.dumps(
#         handler(
#             {
#                 "portalRunId": "202509019aa880c3"
#             },
#             None
#         ),
#         indent=4
#     ))
#
# # {
# #     "payload": {
# #         "orcabusId": "pld.01K42RRMD5T5S0DKQNHP0KKXQB",
# #         "payloadRefId": "28ae3736-2ba5-427f-b7a0-a5349d5cb179",
# #         "version": "2025.06.04",
# #         "data": {
# #             "tags": {
# #                 "libraryId": "L2300950",
# #                 "subjectId": "HCC1395",
# #                 "individualId": "SBJ00480",
# #                 "fastqRgidList": [
# #                     "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7"
# #                 ],
# #                 "tumorLibraryId": "L2300943",
# #                 "tumorFastqRgidList": [
# #                     "ACTAAGAT+CCGCGGTT.4.230602_A00130_0258_BH55TMDSX7",
# #                     "ACTAAGAT+CCGCGGTT.3.230602_A00130_0258_BH55TMDSX7"
# #                 ],
# #                 "ntsmExternalPassing": true,
# #                 "preLaunchDupFracEst": 0.12,
# #                 "preLaunchCoverageEst": 72.17,
# #                 "preLaunchInsertSizeEst": 286,
# #                 "tumorNtsmInternalPassing": true,
# #                 "tumorPreLaunchDupFracEst": 0.13,
# #                 "tumorPreLaunchCoverageEst": 151.68,
# #                 "tumorPreLaunchInsertSizeEst": 286
# #             },
# #             "inputs": {
# #                 "reference": {
# #                     "name": "hg38",
# #                     "tarball": "s3://reference-data-503977275616-ap-southeast-2/refdata/dragen-hash-tables/v11-r5/hg38-alt_masked-cnv-graph-hla-methyl_cg-rna/hg38-alt_masked.cnv.graph.hla.methyl_cg.rna-11-r5.0-1.tar.gz",
# #                     "structure": "graph"
# #                 },
# #                 "sampleName": "L2300950",
# #                 "oraReference": "s3://reference-data-503977275616-ap-southeast-2/refdata/dragen-ora/v2/ora_reference_v2.tar.gz",
# #                 "sequenceData": {
# #                     "fastqListRows": [
# #                         {
# #                             "lane": 2,
# #                             "rgcn": "UMCCR",
# #                             "rgds": "Library ID: L2300950 / Sequenced on 29 Jun 2023 at UMCCR / Phenotype: normal / Assay: TsqNano / Type: WGS",
# #                             "rgdt": "2023-06-29",
# #                             "rgid": "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7",
# #                             "rglb": "L2300950",
# #                             "rgpl": "Illumina",
# #                             "rgsm": "L2300950",
# #                             "read1FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R1_001.fastq.ora",
# #                             "read2FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R2_001.fastq.ora"
# #                         }
# #                     ]
# #                 },
# #                 "tumorSampleName": "L2300943",
# #                 "alignmentOptions": {
# #                     "enableDuplicateMarking": true
# #                 },
# #                 "somaticReference": {
# #                     "name": "hg38",
# #                     "tarball": "s3://reference-data-503977275616-ap-southeast-2/refdata/dragen-hash-tables/v11-r5/hg38-alt_masked-cnv-hla-methyl_cg-methylated_combined/hg38-alt_masked.cnv.hla.methyl_cg.methylated_combined.rna-11-r5.0-1.tar.gz",
# #                     "structure": "linear"
# #                 },
# #                 "somaticMsiOptions": {
# #                     "msiCommand": "tumor-normal",
# #                     "msiCoverageThreshold": 40,
# #                     "msiMicrosatellitesFile": "s3://reference-data-503977275616-ap-southeast-2/refdata/dragen-msi/1-1-0/hg38/WGS_v1.1.0_hg38_microsatellites.list"
# #                 },
# #                 "somaticTmbOptions": {
# #                     "enableTmb": true
# #                 },
# #                 "tumorSequenceData": {
# #                     "fastqListRows": [
# #                         {
# #                             "lane": 4,
# #                             "rgcn": "UMCCR",
# #                             "rgds": "Library ID: L2300943 / Sequenced on 2 Jun 2023 at UMCCR / Phenotype: tumor / Assay: TsqNano / Type: WGS",
# #                             "rgdt": "2023-06-02",
# #                             "rgid": "ACTAAGAT+CCGCGGTT.4.230602_A00130_0258_BH55TMDSX7",
# #                             "rglb": "L2300943",
# #                             "rgpl": "Illumina",
# #                             "rgsm": "L2300943",
# #                             "read1FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300943/L2300943_S18_L004_R1_001.fastq.ora",
# #                             "read2FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300943/L2300943_S18_L004_R2_001.fastq.ora"
# #                         },
# #                         {
# #                             "lane": 3,
# #                             "rgcn": "UMCCR",
# #                             "rgds": "Library ID: L2300943 / Sequenced on 2 Jun 2023 at UMCCR / Phenotype: tumor / Assay: TsqNano / Type: WGS",
# #                             "rgdt": "2023-06-02",
# #                             "rgid": "ACTAAGAT+CCGCGGTT.3.230602_A00130_0258_BH55TMDSX7",
# #                             "rglb": "L2300943",
# #                             "rgpl": "Illumina",
# #                             "rgsm": "L2300943",
# #                             "read1FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300943/L2300943_S18_L003_R1_001.fastq.ora",
# #                             "read2FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300943/L2300943_S18_L003_R2_001.fastq.ora"
# #                         }
# #                     ]
# #                 },
# #                 "targetedCallerOptions": {
# #                     "enableTargeted": [
# #                         "cyp2d6"
# #                     ]
# #                 },
# #                 "somaticSvCallerOptions": {
# #                     "enableSv": true
# #                 },
# #                 "snvVariantCallerOptions": {
# #                     "qcDetectContamination": true,
# #                     "vcMnvEmitComponentCalls": true,
# #                     "vcCombinePhasedVariantsDistance": 2,
# #                     "vcCombinePhasedVariantsDistanceSnvsOnly": 2
# #                 },
# #                 "somaticCnvCallerOptions": {
# #                     "enableCnv": true,
# #                     "enableHrd": true,
# #                     "cnvUseSomaticVcBaf": true
# #                 },
# #                 "somaticNirvanaAnnotationOptions": {
# #                     "enableVariantAnnotation": true,
# #                     "variantAnnotationAssembly": "GRCh38"
# #                 }
# #             },
# #             "outputs": {
# #                 "multiQcOutputRelPath": "L2300943__L2300950__multiqc/",
# #                 "dragenSomaticVariantCallingOutputRelPath": "L2300943__L2300950__hg38__linear__dragen_somatic_variant_calling/",
# #                 "dragenGermlineVariantCallingOutputRelPath": "L2300950__hg38__graph__dragen_germline_variant_calling/"
# #             },
# #             "engineParameters": {
# #                 "logsUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/logs/dragen-wgts-dna/202509019aa880c3/",
# #                 "outputUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/analysis/dragen-wgts-dna/202509019aa880c3/",
# #                 "projectId": "eba5c946-1677-441d-bbce-6a11baadecbb",
# #                 "pipelineId": "e436c569-6022-4dfb-9692-3f265522a66f"
# #             }
# #         }
# #     }
# # }
