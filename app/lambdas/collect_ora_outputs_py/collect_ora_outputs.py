#!/usr/bin/env python3

"""
Given the decompressed outputs, update the fastq list rows to match the ora outputs

{
  "fileUriByFastqIdMap": {
    "fqr.01JN25MRV2622KBD073XGKVYQP": [
      "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R1_001.fastq.ora",
      "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R2_001.fastq.ora"
    ]
  }
  "decompressedFileList": "{% $states.input.decompressedFileList %}"
}

Output
{
  "fastqListRows": "{% $states.result.fastqListRows %}"
}


{
  "fileUriByFastqIdMap": {
    "fqr.01JN25MRV2622KBD073XGKVYQP": [
      "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R1_001.fastq.ora",
      "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R2_001.fastq.ora"
    ]
  },
  "fastqListRows": [
      {
        "rgid": "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7",
        "rglb": "L2300950",
        "rgsm": "L2300950",
        "lane": 2,
        "rgcn": "UMCCR",
        "rgds": "Library ID: L2300950 / Sequenced on 29 Jun 2023 at UMCCR / Phenotype: normal / Assay: TsqNano / Type: WGS",
        "rgdt": "2023-06-29",
        "rgpl": "Illumina",
        "read1FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R1_001.fastq.ora",
        "read2FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2300950/L2300950_S11_L002_R2_001.fastq.ora"
      }
  ],
  "decompressedFileList": [
    {
      "fastqId": "fqr.01JN25MRV2622KBD073XGKVYQP",
      "decompressedFileUriByOraFileIngestIdList": [
        {
          "ingestId": "0194d7a8-4a6a-7210-8ee9-9075cd1e24f6",
          "gzipFileUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-dna/20260509a27b96ef/230629_A01052_0154_BH7WF5DSX7/Samples/Lane_2/L2300950/L2300950_S11_L002_R1_001.fastq.gz"
        },
        {
          "ingestId": "0194d7a9-0174-7611-b121-28125db81967",
          "gzipFileUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-dna/20260509a27b96ef/230629_A01052_0154_BH7WF5DSX7/Samples/Lane_2/L2300950/L2300950_S11_L002_R2_001.fastq.gz"
        }
      ]
    }
  ]
}

And get the output

"fastqListRows": [
  {
    "rgid": "GGCATTCT+CAAGCTAG.2.230629_A01052_0154_BH7WF5DSX7",
    "rglb": "L2300950",
    "rgsm": "L2300950",
    "lane": 2,
    "rgcn": "UMCCR",
    "rgds": "Library ID: L2300950 / Sequenced on 29 Jun 2023 at UMCCR / Phenotype: normal / Assay: TsqNano / Type: WGS",
    "rgdt": "2023-06-29",
    "rgpl": "Illumina",
    "read1FileUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-dna/20260509a27b96ef/230629_A01052_0154_BH7WF5DSX7/Samples/Lane_2/L2300950/L2300950_S11_L002_R1_001.fastq.gz",
    "read2FileUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-dna/20260509a27b96ef/230629_A01052_0154_BH7WF5DSX7/Samples/Lane_2/L2300950/L2300950_S11_L002_R2_001.fastq.gz"
  }
]
"""
from copy import copy
# Standard imports
from typing import Dict, List, Union

# Layer imports
from orcabus_api_tools.filemanager import get_ingest_id_from_s3_uri


def get_fastq_id_by_uri(
        file_uri: str,
        file_uri_by_fastq_id_map: Dict[str, List[str]]
) -> str:
    for fastq_id, file_uri_list in file_uri_by_fastq_id_map.items():
        if file_uri in file_uri_list:
            return fastq_id
    raise ValueError(f"Cannot find {file_uri} in file uri map")


def get_decompressed_file_from_s3_uri_and_fastq_id(
        s3_uri: str,
        fastq_id: str,
        decompressed_file_list: List[Dict[str, Union[str, List[Dict[str, str]]]]],
) -> str:
    # Get the ingest id from the s3 uri
    ingest_id = get_ingest_id_from_s3_uri(s3_uri)

    for decompressed_file_obj in decompressed_file_list:
        if not decompressed_file_obj['fastqId'] == fastq_id:
            continue
        for ingest_obj_iter in decompressed_file_obj['decompressedFileUriByOraFileIngestIdList']:
            if not ingest_obj_iter['ingestId'] == ingest_id:
                continue
            return ingest_obj_iter['gzipFileUri']
    raise ValueError(f"Cannot find decompressed file for s3 uri {s3_uri} and fastq id {fastq_id} in decompressed file list")


def handler(event, context):
    """
    Given the new extracted file paths, collect each of the outputs
    :param event:
    :param context:
    :return:
    """

    # Collect the inputs
    file_uri_by_fastq_id_map = event.get("fileUriByFastqIdMap")
    fastq_list_rows = event.get("fastqListRows")
    decompressed_file_list = event.get("decompressedFileList")

    # Check all inputs are not none
    if file_uri_by_fastq_id_map is None or fastq_list_rows is None or decompressed_file_list is None:
        raise ValueError("Error! all of fileUriByFastqIdMap, fastqListRows and decompressedFileList must be valid inputs")

    # Iterate over each fastq list row
    new_fastq_list_rows = []
    for fastq_list_row in fastq_list_rows:
        # Copy over all elements
        new_fastq_list_row = copy(fastq_list_row)

        # Collect the fastq id
        fastq_id = get_fastq_id_by_uri(fastq_list_row['read1FileUri'], file_uri_by_fastq_id_map)

        # Create new read1FileUri from the cache dir
        new_fastq_list_row['read1FileUri'] = get_decompressed_file_from_s3_uri_and_fastq_id(
            fastq_list_row['read1FileUri'],
            fastq_id,
            decompressed_file_list
        )

        # Create new read1FileUri from the cache dir
        if 'read2FileUri' in fastq_list_row:
            new_fastq_list_row['read2FileUri'] = get_decompressed_file_from_s3_uri_and_fastq_id(
                fastq_list_row['read2FileUri'],
                fastq_id,
                decompressed_file_list
            )

        # Append to list
        new_fastq_list_rows.append(new_fastq_list_row)

    return {
        "fastqListRows": new_fastq_list_rows
    }
