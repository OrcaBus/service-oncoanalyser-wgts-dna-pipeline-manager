# Product: Oncoanalyser WGTS DNA Pipeline Manager

## Summary

This is an OrcaBus microservice that manages the lifecycle of the **Oncoanalyser WGTS DNA pipeline** — a comprehensive somatic analysis pipeline that performs SNV/indel calling, structural variant detection, copy number analysis, and tumour mutational burden estimation using the Oncoanalyser/LINX/PURPLE/SAGE toolchain on ICAv2.

The service handles orchestration on ICAv2 (Illumina Connected Analytics v2) via CWL workflows. It follows the standard ICAv2-centric Pipeline Architecture used across OrcaBus. This is a downstream service — it depends on the successful completion of the Dragen WGTS DNA pipeline (via a glue state machine) to obtain alignment BAM outputs as inputs.

This service is the **reference implementation for event schema versioning** — its versioned directory structure under `app/event-schemas/` is the canonical pattern that all other pipeline managers should follow.

## Core Responsibilities

- Accept `WorkflowRunStateChange` DRAFT events and validate/populate them into READY events
- Submit READY events to ICAv2 as `Icav2WesRequest` events via a Step Functions state machine
- Monitor ICAv2 analysis state changes and convert them to `WorkflowRunUpdate` events
- Validate draft schemas against a registered JSON schema before promotion
- React to upstream Dragen WGTS DNA SUCCEEDED events and update existing DRAFT runs with new alignment data (glue pattern)
- Perform post-schema validation of engine parameters and URI formats

## Event Flow

```
DRAFT event (WorkflowRunStateChange)
  → populate draft data (Step Functions)
  → validate draft schema
  → post-schema validation (engine params, URIs)
  → emit READY event
  → submit to ICAv2 WES
  → monitor ICAv2 state changes
  → emit WorkflowRunUpdate events

Upstream SUCCEEDED event (dragen-wgts-dna)
  → glue state machine
  → find matching DRAFT runs
  → merge upstream BAM outputs into DRAFT payload
  → emit WorkflowRunUpdate DRAFT event (if changed)
```

## Upstream / Downstream

- **Upstream**: Dragen WGTS DNA (provides alignment BAM outputs via glue state machine)
- **Downstream**: Oncoanalyser WGTS Both, Sash
- **Key dependencies**: ICAv2 WES Manager, Workflow Manager

## Environments

Deploys to `beta`, `gamma`, and `prod` via AWS CodePipeline. The toolchain account hosts the CodePipeline; application stacks deploy cross-account.
