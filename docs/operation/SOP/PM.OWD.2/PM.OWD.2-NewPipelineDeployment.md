# New Oncoanalyser WGTS DNA Pipeline Deployment

- Version: 1.0
- Contact: Alexis Lucattini, [alexisl@unimelb.edu.au](mailto:alexisl@unimelb.edu.au)

There may be times where we need to deploy a new version of the Oncoanalyser WGTS DNA pipeline.

In the SOP below we discuss the following scenarios:
* User wants to deploy a new version of the pipeline for testing purposes.
* User wants to make a new release of the pipeline for production use.

Throughout the SOP we make the following expectations:
* User is familiar with UMCCR's [cwl-ica repository][cwl_ica_repo] and has a working knowledge of CWL/Nextflow.
* User has access to the ICAv2 platform with at minimum 'Contributor level' permissions in at least one project.
* User has access to the appropriate AWS Account tied to the ICAv2 project.

- [Pipeline Summary](#pipeline-summary)
- [Setup](#setup)
- [Development Deployment](#development-deployment)
  - [Pipeline Creation](#pipeline-creation)
  - [Running the Pipeline](#running-the-pipeline)
- [Production Deployment](#production-deployment)
  - [GitHub Releases](#github-releases)
  - [Infrastructure Constants Updates](#infrastructure-constants-updates)
  - [Workflow Manager Updates](#workflow-manager-updates)
  - [Analysis Glue Updates](#analysis-glue-updates)


## Pipeline Summary

The Oncoanalyser WGTS DNA pipeline runs on ICAv2 using CWL/Nextflow. It performs somatic analysis including:
- SNV/indel calling (SAGE)
- Structural variant detection (GRIPSS/ESVEE)
- Copy number analysis (PURPLE)
- Tumour mutational burden estimation

The pipeline requires alignment BAM files from the upstream Dragen WGTS DNA pipeline as inputs.

## Setup

Ensure you have:
- ICAv2 CLI installed and configured
- AWS credentials for the target environment
- Access to the OrcaBus Portal

## Development Deployment

### Pipeline Creation

1. Package the workflow into a ZIP file for deployment into ICA.
2. Deploy into the development ICAv2 project:
   ```shell
   icav2 projects enter development
   icav2 projectpipelines create-cwl-pipeline-from-zip <workflow-zip>
   ```
3. Keep note of the pipeline ID.

### Running the Pipeline

Run the pipeline on a test dataset using [SOP 1][sop_1_rel_path], providing the new `pipelineId` in the engine parameters:

```json5
{
  "payload": {
    "version": "<DEFAULT_PAYLOAD_VERSION>",
    "data": {
      "engineParameters": {
        "pipelineId": "<THE PIPELINE ID YOU JUST CREATED>"
      }
    }
  }
}
```

## Production Deployment

### GitHub Releases

1. Push CWL changes to a branch, get reviewed and merged to main.
2. Create a new workflow release via the cwl-ica CLI.

### Infrastructure Constants Updates

Update `infrastructure/stage/constants.ts` to include the new pipeline ID in `WORKFLOW_VERSION_TO_DEFAULT_ICAV2_PIPELINE_ID_MAP`.

### Workflow Manager Updates

Register the new workflow version with the Workflow Manager:

```shell
make-new-workflow.sh \
  --workflow-name 'oncoanalyser-wgts-dna' \
  --workflow-version "<version>" \
  --executionEngine "ICA" \
  --executionEnginePipelineId "<pipeline-id>" \
  --codeVersion "$(cd <cwl-ica-repo> && git rev-parse --short=7 HEAD)" \
  --validationState "VALIDATED"
```

### Analysis Glue Updates

Update the [analysis-glue repository][analysis_glue_repo_link] constants to include the new workflow version.


[cwl_ica_repo]: https://github.com/umccr/cwl-ica
[sop_1_rel_path]: ../PM.OWD.1/PM.OWD.1-ManualPipelineExecution.md
[analysis_glue_repo_link]: https://github.com/OrcaBus/service-analysis-glue
