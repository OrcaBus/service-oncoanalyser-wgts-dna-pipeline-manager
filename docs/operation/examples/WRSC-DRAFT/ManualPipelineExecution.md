Manual Pipeline Execution (legacy)
================================================================================

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Procedure](#procedure)
- [Confirmation](#confirmation)


Introduction
--------------------------------------------------------------------------------

This Pipeline Manager manages the execution of the DRAGEN WGTS DNA pipeline. Here we describe the (legacy) procedure for manual execution of the pipeline.

> [!IMPORTANT]
> Please ensure you know which DRAFT events are required by the deployed version you are aiming for. Please check with Alexis if in doubt.

Requirements
--------------------------------------------------------------------------------

- appropriate AWS permissions
- AWS credentials set up in the local environment
- tools installed
  - AWS CLI
  - JQ

Procedure
--------------------------------------------------------------------------------

To initate a pipeline execution we need to generate an initial DRAFT event. For more details consult the main [README](../../../../README.md).
For convenience we provide a shell script that generates and optionally submits an appropriate event.

- familiarise yourself with the script: [generate-WRSC-draft.sh](./generate-WRSC-draft.sh)
  - especially check the settings in the `Globals` section
    - ensure the values are fit for your use case, e.g. for clinical samples match the accredited pipeline details
- in the `Glocals` section provide the Library IDs
  - set `LIBRARY_ID` to the Library ID of your normal / germline sample
  - set `TUMOR_LIBRARY_ID` to the Library ID of your matching tumor sample
    - the tumor can be omitted for germline only execution mode
- execute the script (e.g. `bash generate-WRSC-draft.sh`)
  - Note: AWS credentials need to set on the environment
  - make sure the `DRYRUN` variable at the start of the script is set to `true`
- the script should produce the JSON output of the DRAFT event that can be inspected to double check that reflects the intended request
  - take note of the generated `workflowRunName` or `portalRunId`
- if the DRAFT event is correct, update the `DRYRUN` variable to `false` and run the script again
- the script will now submit the DRAFT event and it should complete successfully


Confirmation
--------------------------------------------------------------------------------

The OrcaBus [Portal](https://portal.umccr.org/) can be used to check whether the event resulted in a WorkflowRun record.

- navigate to the Portal's WorkflowRun listing: https://portal.umccr.org/runs/workflow
- search for your WorkflowRun using the `workflowRunName` or `portalRunId`
- confirm that the WorkflowRun is listed and progressing as expected (check over time)
- once the WorkflowRun as `SUCCEEDED` the results should be available via the Portal's [Files](https://portal.umccr.org/files) view
  - simply filter by the `portalRunId`
