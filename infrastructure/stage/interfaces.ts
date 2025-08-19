/*

Interfaces for the application

 */

import { SsmParameterPaths, SsmParameterValues } from './ssm/interfaces';

/**
 * Stateful application stack interface.
 */

export interface StatefulApplicationStackConfig {
  // Values
  // Detail
  ssmParameterValues: SsmParameterValues;

  // Keys
  ssmParameterPaths: SsmParameterPaths;
}

/**
 * Stateless application stack interface.
 */
export interface StatelessApplicationStackConfig {
  // Event Stuff
  eventBusName: string;

  // Workflow manager stuff
  isNewWorkflowManagerDeployed: boolean;
}

/* Set versions */
export type WorkflowVersionType = '2.0.0' | '2.1.0';

/* Set genomes */
export type GenomeType = 'GRCh38_umccr' | 'GRCh38_hmf';

export type NotInBuiltInHmfReferenceGenomesType = Exclude<GenomeType, 'GRCh38_hmf'>;

export interface Genome {
  fasta: string;
  fai: string;
  dict: string;
  img: string;
  bwamem2_index: string;
  gridss_index: string;
  star_index: string;
}
