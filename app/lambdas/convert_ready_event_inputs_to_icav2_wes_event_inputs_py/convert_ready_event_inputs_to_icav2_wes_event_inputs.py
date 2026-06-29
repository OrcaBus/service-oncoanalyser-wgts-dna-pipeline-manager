#!/usr/bin/env python3

"""
Given the inputs from a ready event, this script generates an ICAV2 WES event for the oncoanalyser workflow.

The data payload inputs should look like the following:
{
    "mode": "wgts",
    "groupId": "SBJ05828",
    "subjectId": "SBJ05828",
    "tumorDnaBamUri": "s3://path-to-tumor-bam",
    "normalDnaBamUri": "s3://path-to-normal-bam",
    "tumorDnaSampleId" "TUMOR_LIBRARY_ID",
    "normalDnaSampleId": "NORMAL_LIBRARY_ID",
    "genome": "GRCh38_umccr",
    "genomeVersion": "38",
    "genomeType": "alt",
    "forceGenome": True,
    "refDataHmfDataPath": "s3://path-to-reference-data/oncoanalyser/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.1.0--1/",
    "genomes": {
        "GRCh38_umccr": {
            "fasta": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/GRCh38_full_analysis_set_plus_decoy_hla.fa",
            "fai": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai",
            "dict": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.dict",
            "img": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/bwa_index_image/0.7.17-r1188/GRCh38_full_analysis_set_plus_decoy_hla.fa.img",
            "bwamem2Index": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/bwa-mem2_index/2.2.1/",
            "gridssIndex": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/gridss_index/2.13.2/",
            "starIndex": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/star_index/gencode_38/2.7.3a/"
        }
    }
}


To generate an output like the following

{
  "inputs": {
        "monochrome_logs": True,
        "mode": "wgts",
        "publish_dir_mode": "symlink",
        "outdir": "out",
        "samplesheet": [
            # Normal Bam
            {
                "group_id": "SBJ05828",
                "subject_id": "SBJ05828",
                "sample_id": "L2401540",
                "sample_type": "normal",
                "sequence_type": "dna",
                "filetype": "bam",
                "filepath": "s3://path/to/normal_bam",
            },
            # Normal Bam index
            {
                "group_id": "SBJ05828",
                "subject_id": "SBJ05828",
                "sample_id": "L2401540",
                "sample_type": "normal",
                "sequence_type": "dna",
                "filetype": "bai",
                "filepath": "s3://path/to/normal_bam.bai",
            },
            # Tumor Bam
            {
                "group_id": "SBJ05828",
                "subject_id": "SBJ05828",
                "sample_id": "L2401541",
                "sample_type": "tumor",
                "sequence_type": "dna",
                "filetype": "bam",
                "filepath": "s3://path/to/tumor_bam",
            },
            # Tumor Bam index
            {
                "group_id": "SBJ05828",
                "subject_id": "SBJ05828",
                "sample_id": "L2401541",
                "sample_type": "tumor",
                "sequence_type": "dna",
                "filetype": "bai",
                "filepath": "s3://path/to/tumor_bam.bai",
            },
        ],
        "genome": "GRCh38_umccr",
        "genome_version": "38",
        "genome_type": "alt",
        "force_genome": True,
        "ref_data_hmf_data_path": "s3://path-to-reference-data/oncoanalyser/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.1.0--1/",
        "genomes": {
            "GRCh38_umccr": {
                "fasta": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/GRCh38_full_analysis_set_plus_decoy_hla.fa",
                "fai": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai",
                "dict": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.dict",
                "img": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/bwa_index_image/0.7.17-r1188/GRCh38_full_analysis_set_plus_decoy_hla.fa.img",
                "bwamem2_index": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/bwa-mem2_index/2.2.1/",
                "gridss_index": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/gridss_index/2.13.2/",
                "star_index": "s3://path-to-reference-data/oncoanalyser/GRCh38_umccr/star_index/gencode_38/2.7.3a/"
            }
        }
    }
}
"""

# Typing imports
from typing import List, Dict, Union, cast, Literal, TypedDict
import pandas as pd

# Layer imports
from orcabus_api_tools.fastq.models import FastqListRowDict

# Globals
DEFAULT_MODE = "wgts"
DEFAULT_MONOCHROME_LOGS = True
DEFAULT_GENOME = "GRCh38_hmf"
DEFAULT_GENOME_VERSION = "38"
DEFAULT_GENOME_TYPE = "no_alt"
DEFAULT_PUBLISH_DIR_MODE = "symlink"
DEFAULT_OUTDIR = "out"

DEFAULT_SAMPLESHEET_COLUMNS = [
    "group_id",
    "subject_id",
    "sample_id",
    "sample_type",
    "sequence_type",
    "filetype",
    "filepath",
]

FASTQ_SAMPLESHEET_COLUMNS = [
    *DEFAULT_SAMPLESHEET_COLUMNS.copy(),
    "info"
]

# Models
SampleType = Literal["normal", "tumor"]
SequenceType = Literal["dna"]


class ReadyEventInputsBase(TypedDict):
    # Metadata
    groupId: str
    subjectId: str
    normalDnaSampleId: str
    tumorDnaSampleId: str


class ReadyEventInputsFastq(ReadyEventInputsBase):
    # FQLRs
    normalFastqListRows: List[FastqListRowDict]
    tumorFastqListRows: List[FastqListRowDict]


class ReadyEventInputsBam(ReadyEventInputsBase):
    normalDnaBamUri: str
    tumorDnaBamUri: str


ReadyEventInputsType = Union[ReadyEventInputsFastq, ReadyEventInputsBam]


def generate_samplesheet_from_inputs(
        ready_event_inputs: ReadyEventInputsType
) -> List[Dict[str, str]]:
    if ready_event_inputs.get('normalDnaBamUri') is not None:
        return generate_samplesheet_from_input_bams(cast(ReadyEventInputsBam, ready_event_inputs))
    else:
        return generate_samplesheet_from_input_fastqs(cast(ReadyEventInputsFastq, ready_event_inputs))


def generate_samplesheet_rows_from_fastqs(
        group_id: str,
        subject_id: str,
        sample_id: str,
        sample_type: SampleType,
        sequence_type: SequenceType,
        fastq_list_rows: List[FastqListRowDict],
) -> pd.DataFrame:
    """
    Given a list of fastq list rows, generate a list of samplesheet rows.
    Ensure that there are no duplicate lanes.
    :param group_id:
    :param subject_id:
    :param sample_id:
    :param sample_type:
    :param sequence_type:
    :param fastq_list_rows:
    :return:
    """

    # Set lanes used
    lanes_used = set()
    # Set list of series
    rows_series_list: List[pd.Series] = []

    # Ensure that there are no duplicate lanes
    for fastq_list_row_iter_ in fastq_list_rows.copy():
        # Continue to add lane ids to the lanes_used set until we find a lane that is not in the lanes_used set
        while fastq_list_row_iter_['lane'] in lanes_used:
            fastq_list_row_iter_['lane'] += 1
        # Add lane to lanes_used set
        lanes_used.add(fastq_list_row_iter_['lane'])
        rows_series_list.append(
            pd.Series(
                index=FASTQ_SAMPLESHEET_COLUMNS,
                data={
                    "group_id": group_id,
                    "subject_id": subject_id,
                    "sample_id": sample_id,
                    "sample_type": sample_type,
                    "sequence_type": sequence_type,
                    "filetype": "fastq",
                    "info": f"library_id:{fastq_list_row_iter_['rglb']};lane:{str(fastq_list_row_iter_['lane']).zfill(3)}",
                    "filepath": ";".join(list(filter(
                        lambda file_iter_: file_iter_ is not None,
                        [
                            fastq_list_row_iter_["read1FileUri"],
                            fastq_list_row_iter_.get("read2FileUri", None),
                        ]
                    )))
                }
            )
        )

    # Return the DataFrame
    return pd.DataFrame(rows_series_list)


def generate_samplesheet_from_input_fastqs(
        ready_event_inputs: ReadyEventInputsFastq
) -> List[Dict[str, str]]:
    samplesheet_df = pd.concat([
        # Normal fastqs
        generate_samplesheet_rows_from_fastqs(
            group_id=ready_event_inputs["groupId"],
            subject_id=ready_event_inputs["subjectId"],
            sample_id=ready_event_inputs["normalDnaSampleId"],
            sample_type="normal",
            sequence_type="dna",
            fastq_list_rows=ready_event_inputs['normalFastqListRows']
        ),
        # Tumor fastqs
        generate_samplesheet_rows_from_fastqs(
            group_id=ready_event_inputs["groupId"],
            subject_id=ready_event_inputs["subjectId"],
            sample_id=ready_event_inputs["tumorDnaSampleId"],
            sample_type="tumor",
            sequence_type="dna",
            fastq_list_rows=ready_event_inputs['tumorFastqListRows']
        )
    ])

    # Convert the DataFrame to a list of dictionaries
    return cast(List[Dict[str, str]], samplesheet_df.to_dict(orient='records'))


def generate_samplesheet_from_input_bams(
        ready_event_inputs: ReadyEventInputsBam
) -> List[Dict[str, str]]:
    samplesheet_df_bams = pd.DataFrame(
        columns=DEFAULT_SAMPLESHEET_COLUMNS,
        data=[
            # Normal bam
            {
                "group_id": ready_event_inputs["groupId"],
                "subject_id": ready_event_inputs["subjectId"],
                "sample_id": ready_event_inputs["normalDnaSampleId"],
                "sample_type": "normal",
                "sequence_type": "dna",
                "filetype": "bam",
                "filepath": ready_event_inputs["normalDnaBamUri"],
            },
            # Tumor bam
            {
                "group_id": ready_event_inputs["groupId"],
                "subject_id": ready_event_inputs["subjectId"],
                "sample_id": ready_event_inputs["tumorDnaSampleId"],
                "sample_type": "tumor",
                "sequence_type": "dna",
                "filetype": "bam",
                "filepath": ready_event_inputs["tumorDnaBamUri"],
            },
        ]
    )

    # Generate BAM index entries from the BAM entries
    samplesheet_df_bam_indexes = samplesheet_df_bams.copy()
    samplesheet_df_bam_indexes.apply(
        lambda row: row.update({"filetype": "bai", "filepath": f"{row['filepath']}.bai"}),
        axis='columns'
    )

    # Join the BAM and BAM index entries
    samplesheet_df = pd.concat(
        [samplesheet_df_bams, samplesheet_df_bam_indexes],
        ignore_index=True
    )

    # Convert the DataFrame to a list of dictionaries
    return cast(List[Dict[str, str]], samplesheet_df.to_dict(orient='records'))


def genome_keys_to_snake_case(genome: Dict[str, str]) -> Dict[str, str]:
    """
    Input genome keys are in camelCase, this function converts them to snake_case.
    :param genome:
    :return:
    """
    return dict(map(
        lambda kv_iter_: (kv_iter_[0].replace("Index", "_index").lower(), kv_iter_[1]),
        genome.items()
    ))


def handler(event, context):
    """
    Given the inputs from a ready event, this script generates an ICAV2 WES event inputs for the oncoanalyser workflow.
    :param event:
    :param context:
    :return:
    """

    # Get the ready event inputs
    ready_event_inputs: ReadyEventInputsType = event.get("inputs", {})

    # Extract necessary fields from the ready event inputs
    return {
        "inputs": dict(filter(
            lambda kv_iter_: kv_iter_[1] is not None,
            {
                "mode": ready_event_inputs.get("mode", DEFAULT_MODE),
                "monochrome_logs": ready_event_inputs.get("monochromeLogs", DEFAULT_MONOCHROME_LOGS),
                "publish_dir_mode": ready_event_inputs.get("publishDirMode", DEFAULT_PUBLISH_DIR_MODE),
                "outdir": ready_event_inputs.get("outdir", DEFAULT_OUTDIR),
                "samplesheet": generate_samplesheet_from_inputs(ready_event_inputs),
                "genome": ready_event_inputs.get("genome", DEFAULT_GENOME),
                "genome_version": ready_event_inputs.get("genomeVersion", DEFAULT_GENOME_VERSION),
                "genome_type": ready_event_inputs.get("genomeType", DEFAULT_GENOME_TYPE),
                "force_genome": ready_event_inputs.get("forceGenome", None),
                "ref_data_hmf_data_path": ready_event_inputs["refDataHmfDataPath"],
                "genomes": (
                    dict(map(
                        lambda kv_iter_: (kv_iter_[0], genome_keys_to_snake_case(kv_iter_[1])),
                        ready_event_inputs.get("genomes").items()
                    ))
                    if ready_event_inputs.get("genomes") is not None
                    else None
                )
            }.items()
        ))
    }
