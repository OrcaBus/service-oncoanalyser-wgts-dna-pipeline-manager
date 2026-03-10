Manual Pipeline Execution
================================================================================
- Version: 2025.03.05
- Contact: Alexis Lucattini, [alexisl@unimelb.edu.au](mailto:alexisl@unimelb.edu.au)

Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Procedure](#procedure)
- [Confirmation](#confirmation)


Introduction
--------------------------------------------------------------------------------

This Pipeline Manager manages the execution of the ONCOANALYSER WGTS DNA pipeline.
Here we describe the SOP for manual execution of the pipeline.

Requirements
--------------------------------------------------------------------------------

- appropriate AWS permissions
- AWS credentials set up in the local environment
- Access to the OrcaBus Portal (i.e. a PORTAL_TOKEN set in the environment)
- tools installed
  - [aws](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) version 2 or higher
  - [jq](https://github.com/jqlang/jq) version 1.7 or higher
  - [curl](https://curl.se/download.html) version 7.76.0 or higher
  - [semver](https://github.com/fsaintjacques/semver-tool)


Procedure
--------------------------------------------------------------------------------

To initiate a pipeline execution we need to generate an initial DRAFT event. For more details consult the main [README](../../../../README.md).
For convenience, we provide a shell script that generates and optionally submits an appropriate event.

- Familiarise yourself with the script and its parameters: [generate-WRU-draft.sh --help](./generate-WRU-draft.sh)
  - especially check the settings in the `Globals` section
    - ensure the values are fit for your use case, e.g. for clinical samples match the accredited pipeline details
  - Set the engine parameters (if necessary) and library id(s) in the positional arguments.
- Execute the script (e.g. `bash generate-WRU-draft.sh --comment 'Manual rerun' <your_tn_library_id> <your_normal_library_id>`)
  - Note: AWS credentials need to be set on the environment as does your PORTAL_TOKEN (see the script for details)
  - Use the comment parameter to explain the reason for the manual run, this will be visible in the Portal and helpful for future reference.
- The script should produce the JSON output of the DRAFT event that can be inspected to double check that reflects the intended request
  - Take note of the generated `workflowRunName` or `portalRunId` and the URL to the OrcaBus Portal view of the workflow.
  - You can have the script save the output json file by using the `--save-draft-payload` method.

Confirmation
--------------------------------------------------------------------------------

The OrcaBus [Portal](https://portal.umccr.org/) can be used to check whether the event resulted in a WorkflowRun DRAFT record.
