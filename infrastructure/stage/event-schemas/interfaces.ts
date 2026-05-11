import { PayloadVersionType } from '../interfaces';

export type SchemaNames = 'completeDataDraft';

export const schemaNamesList: SchemaNames[] = ['completeDataDraft'];

export interface BuildSchemaProps {
  schemaName: SchemaNames;
  payloadVersion: PayloadVersionType;
}
