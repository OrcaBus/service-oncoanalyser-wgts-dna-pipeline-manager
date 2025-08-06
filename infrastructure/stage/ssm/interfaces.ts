import { Genome } from '../interfaces';

export interface SsmParameterValues {
  // Payload defaults
  workflowName: string;
  payloadVersion: string;
  workflowVersion: string;

  // Input defaults
  inputsByWorkflowVersionMap: Record<string, object>;

  // Engine Parameter defaults
  pipelineIdsByWorkflowVersionMap: Record<string, string>;
  icav2ProjectId: string;
  logsPrefix: string;
  outputPrefix: string;
  cachePrefix: string;

  // Reference defaults
  hmfReferenceDataByWorkflowVersionMap: Record<string, string>;
  genomes: Record<string, Genome>;
}

export interface SsmParameterPaths {
  // Top level prefix
  ssmRootPrefix: string;

  // Payload defaults
  workflowName: string;
  payloadVersion: string;
  workflowVersion: string;

  // Input defaults
  prefixDefaultInputsByWorkflowVersion: string;

  // Engine Parameter defaults
  prefixPipelineIdsByWorkflowVersion: string;
  icav2ProjectId: string;
  logsPrefix: string;
  outputPrefix: string;
  cachePrefix: string;

  // Reference defaults
  hmfReferenceDataSsmRootPrefix: string;
  genomesSsmRootPrefix: string;
}

export interface BuildSsmParameterProps {
  ssmParameterValues: SsmParameterValues;
  ssmParameterPaths: SsmParameterPaths;
}
