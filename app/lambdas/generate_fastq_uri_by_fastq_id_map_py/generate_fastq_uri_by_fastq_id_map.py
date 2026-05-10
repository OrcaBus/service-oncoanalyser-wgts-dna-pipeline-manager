#!/usr/bin/env python3

"""
Generate fastq uri by fastq id map

Given fastqIdList and fastqListRows, provide a dict of fastqIds to fileUris
"""

# Standard imports
from typing import Dict, List
import typing

# Layer imports
from orcabus_api_tools.fastq import get_fastq_by_rgid


# Type hints
if typing.TYPE_CHECKING:
    from orcabus_api_tools.fastq.models import FastqListRowDict

def handler(event, context) -> Dict[str, Dict[str, List[str]]]:
    """
    Generate the fastq id to uri map
    """

    # Inputs
    fastq_id_list: List[str] = event["fastqIdList"]
    fastq_list_rows: List['FastqListRowDict'] = event["fastqListRows"]

    # Generate the map
    file_uri_by_fastq_id_map = {}
    for fastq_list_row_iter_ in fastq_list_rows:
        # Match the fastq id
        fastq_id_iter: str = get_fastq_by_rgid(fastq_list_row_iter_['rgid'])['id']
        if fastq_id_iter not in fastq_id_list:
            raise ValueError(f"Fastq id {fastq_id_iter} from fastq list rows is not in the provided fastq id list")

        # Get the file uris
        file_uris_iter: List[str] = [fastq_list_row_iter_['read1FileUri']]

        # Get the read 2 file uri if it exists
        if fastq_list_row_iter_['read2FileUri'] is not None:
            file_uris_iter.append(fastq_list_row_iter_['read2FileUri'])

        file_uri_by_fastq_id_map[fastq_id_iter] = file_uris_iter

    return {
        "fileUriByFastqIdMap": file_uri_by_fastq_id_map
    }
