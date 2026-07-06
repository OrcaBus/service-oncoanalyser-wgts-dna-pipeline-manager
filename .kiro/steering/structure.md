# Project Structure

## Top-Level Layout

```
├── app/                        # Application logic (lambdas, step functions, schemas)
├── bin/deploy.ts               # CDK entry point — initialises stateless + stateful root stacks
├── infrastructure/             # CDK infrastructure code
│   ├── stage/                  # Per-environment application stacks
│   └── toolchain/              # CodePipeline stacks (deploy to beta/gamma/prod)
├── test/                       # CDK/cdk-nag compliance tests
├── docs/                       # Draw.io exports, SOPs, workflow studio exports
├── .kiro/steering/             # AI steering documents
├── cdk.json                    # CDK app config (entry: `pnpx ts-node bin/deploy.ts`)
├── package.json / pnpm-workspace.yaml
└── Makefile                    # Common developer commands
```

## `app/` — Application Logic

```
app/
├── event-schemas/              # JSON schemas for event validation (versioned directory structure)
│   └── complete-data-draft/
│       ├── 2025.08.05/
│       │   └── complete-data-draft-schema.json
│       └── 2026.04.16/
│           └── complete-data-draft-schema.json
├── lambdas/                    # Python Lambda functions
│   ├── collect_ora_outputs_py/
│   ├── compare_payload_py/
│   ├── convert_icav2_wes_event_to_wrsc_event_py/
│   ├── convert_ready_event_inputs_to_icav2_wes_event_inputs_py/
│   ├── determine_fastq_compression_type_py/
│   ├── find_latest_workflow_py/
│   ├── generate_fastq_uri_by_fastq_id_map_py/
│   ├── generate_wru_event_object_with_merged_data_py/
│   ├── get_analysis_storage_size_from_basecount_est_py/
│   ├── get_bam_from_latest_dragen_workflow_py/
│   ├── get_draft_payload_py/
│   ├── get_dragen_outputs_from_portal_run_id_py/
│   ├── get_fastq_id_list_from_rgid_list_py/
│   ├── get_fastq_list_rows_from_fastq_rgid_list_py/
│   ├── get_fastq_rgids_from_library_id_py/
│   ├── get_latest_payload_from_portal_run_id_py/
│   ├── get_libraries_py/
│   ├── get_metadata_tags_py/
│   ├── get_prefix_from_project_id_py/
│   ├── get_workflow_run_object_py/
│   ├── post_schema_validation_py/
│   └── validate_draft_data_complete_schema_py/
└── step-functions-templates/   # ASL JSON Step Functions definitions
    ├── glue_succeeded_events_to_draft_update_sfn_template.asl.json
    ├── icav2_wes_event_to_wrsc_event_sfn_template.asl.json
    ├── populate_draft_data_sfn_template.asl.json
    ├── ready_event_to_icav2_wes_request_event_sfn_template.asl.json
    └── validate_draft_data_and_put_ready_event_sfn_template.asl.json
```

### Lambda Naming Convention

Lambda directories use `snake_case` with a `_py` suffix (e.g. `get_libraries_py`). The CDK infrastructure converts camelCase names to snake_case automatically via `camelCaseToSnakeCase()`.

### Lambda Pattern

- Single file per Lambda, named `<function_name>.py`
- Must export `handler(event, context) -> Dict[str, Any]`
- Extensive docstrings describing input/output event shapes
- Business logic only — no AWS SDK calls for infrastructure wiring (IAM, SSM lookups are CDK-managed)
- Commented-out `if __name__ == "__main__"` blocks for local testing

### Event Schema Versioning (Reference Pattern)

This service is the reference implementation for versioned event schemas. Schemas are stored under `app/event-schemas/complete-data-draft/<payload-version>/`. Each version directory contains the complete JSON schema for that payload version. The CDK stateful stack reads the latest version directory to register the schema.

## `infrastructure/` — CDK Code

```
infrastructure/
├── stage/
│   ├── config.ts               # Environment configs (beta, gamma, prod)
│   ├── constants.ts            # All app constants (SSM paths, event names, workflow versions, S3 refs)
│   ├── interfaces.ts           # Shared TypeScript interfaces for the stack
│   ├── stateless-application-stack.ts
│   ├── stateful-application-stack.ts
│   ├── lambda/                 # Lambda construct builders
│   │   ├── index.ts            # buildAllLambdas() — iterates lambdaNameList
│   │   └── interfaces.ts       # Lambda name list + requirements map
│   ├── step-functions/         # Step Function construct builders
│   ├── event-rules/            # EventBridge rule builders
│   ├── event-targets/          # EventBridge target builders
│   ├── event-schemas/          # Schema registry construct builders
│   ├── ssm/                    # SSM parameter construct builders
│   └── utils/                  # Shared utilities (camelCase ↔ kebab/snake conversions)
└── toolchain/
    ├── constants.ts            # Toolchain-specific constants
    ├── stateless-stack.ts      # CodePipeline for stateless deployments
    └── stateful-stack.ts       # CodePipeline for stateful deployments
```

### Infrastructure Patterns

- Each resource type (lambda, step-functions, event-rules, etc.) has its own `index.ts` (builder) and `interfaces.ts` (types)
- All constants (SSM paths, event names, bucket names, workflow versions) live in `infrastructure/stage/constants.ts` — do not hardcode these elsewhere
- Lambdas are built with `PythonUvFunction` from `@orcabus/platform-cdk-constructs`
- IAM permissions are granted inline in `infrastructure/stage/lambda/index.ts` based on per-Lambda requirement flags in `interfaces.ts`
- `NagSuppressions` are added inline with justification comments wherever `cdk-nag` rules are suppressed

## Key Conventions

- **Event source**: `orcabus.oncoanalyserwgtsdna`
- **Event bus**: `OrcaBusMain`
- **SSM prefix**: `/orcabus/workflows/oncoanalyser-wgts-dna/`
- **Stack prefix**: `orca-oncoanalyser-wgts-dna`
- **Workflow name**: `oncoanalyser-wgts-dna`
- **Lambda runtime**: Python 3.14 on ARM64
- **Upstream workflow name**: `dragen-wgts-dna` (glue pattern dependency)
- When adding a new Lambda: add the directory under `app/lambdas/<name>_py/`, register it in `infrastructure/stage/lambda/interfaces.ts`, and declare its IAM requirement flags there
- When adding a new workflow version: update `WORKFLOW_VERSION_TO_DEFAULT_ICAV2_PIPELINE_ID_MAP` and related maps in `constants.ts`
