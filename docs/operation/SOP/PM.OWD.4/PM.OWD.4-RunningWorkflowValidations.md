# Running Workflow Validations

- Version: 2026.07.03
- Contact: Alexis Lucattini, [alexisl@unimelb.edu.au](mailto:alexisl@unimelb.edu.au)

This SOP describes how to run workflow validations for the Oncoanalyser WGTS DNA pipeline.

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Procedure](#procedure)
- [Expected Outputs](#expected-outputs)
- [Validation Criteria](#validation-criteria)


## Introduction

When deploying a new version of the Oncoanalyser WGTS DNA pipeline (new workflow version or parameter changes),
validation runs should be performed against known test datasets to confirm expected behaviour.

## Requirements

- AWS credentials for the beta/gamma environment
- Access to the OrcaBus Portal
- A known test dataset with expected outcomes (e.g. SEQC-II HCC1395 tumor/normal pair)
- The pipeline version to validate has been deployed (see [PM.OWD.2][sop_2_rel_path])

## Procedure

1. **Identify test libraries** — Use the standard validation libraries (e.g. L2300943 tumor / L2300950 normal for SEQC-II).

2. **Submit a validation DRAFT event** — Follow [PM.OWD.1][sop_1_rel_path] to submit a DRAFT event targeting the new pipeline version:
   ```json5
   {
     "payload": {
       "version": "<PAYLOAD_VERSION>",
       "data": {
         "engineParameters": {
           "pipelineId": "<NEW_PIPELINE_ID>"
         }
       }
     }
   }
   ```

3. **Monitor execution** — Track the workflow run through the OrcaBus Portal or AWS Step Functions console. Ensure it transitions through DRAFT → READY → SUBMITTED → SUCCEEDED.

4. **Compare outputs** — Compare the analysis outputs against the expected reference outputs for the test dataset.

## Expected Outputs

The Oncoanalyser WGTS DNA pipeline produces:
- SNV/indel VCF files (SAGE)
- Structural variant calls (GRIPSS/ESVEE)
- Copy number segments (PURPLE)
- TMB estimates
- LINX annotations and visualisations

## Validation Criteria

A validation run is considered successful when:
1. The workflow run reaches SUCCEEDED status without manual intervention.
2. All expected output files are present in the output URI.
3. Key metrics (variant counts, TMB values, purity estimates) are within acceptable ranges of the reference run.
4. No unexpected errors or warnings appear in the execution logs.

If validation fails, consult [PM.OWD.5 - Troubleshooting][sop_5_rel_path] for guidance.


[sop_1_rel_path]: ../PM.OWD.1/PM.OWD.1-ManualPipelineExecution.md
[sop_2_rel_path]: ../PM.OWD.2/PM.OWD.2-NewPipelineDeployment.md
[sop_5_rel_path]: ../PM.OWD.5/PM.OWD.5-TroubleShooting.md
