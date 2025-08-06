import * as schemas from 'aws-cdk-lib/aws-eventschemas';

export type SchemaNames = 'completeDataDraft';

export const schemaNamesList: SchemaNames[] = ['completeDataDraft'];

export interface BuildSchemaProps {
  registry: schemas.CfnRegistry;
  schemaName: SchemaNames;
}
