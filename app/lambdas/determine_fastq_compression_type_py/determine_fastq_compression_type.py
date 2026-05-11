#!/usr/bin/env python3

"""
Given an input of fastq list rows, determine the compression type

Return isOra: true if 'read1FileUri' endswith '.ora' otherwise isOra: false
"""

# Standard imports
import typing
from typing import List, TypedDict, Literal

if typing.TYPE_CHECKING:
    from orcabus_api_tools.fastq.models import FastqListRowDict

CompressionType = Literal[
    'ORA',
    'GZIP'
]


class CompressionTypeResponse(TypedDict):
    compressionType: CompressionType


def handler(event, context) -> CompressionTypeResponse:
    """
    Given an input of fastq list rows, determine the compression type
    """

    fastq_list_rows: List['FastqListRowDict'] = event.get("fastqListRows", [])

    if len(fastq_list_rows) == 0:
        raise ValueError("fastqListRows is required in the event payload and must be a non-empty list")

    # Check the first row's read1FileUri to determine if it's an .ora file
    first_row = fastq_list_rows[0]

    if first_row['read1FileUri'].endswith('.ora'):
        return {
            "compressionType": "ORA"
        }
    else:
        return {
            "compressionType": "GZIP"
        }
