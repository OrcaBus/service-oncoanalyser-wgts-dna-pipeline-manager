import * as schemas from 'aws-cdk-lib/aws-eventschemas';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { EVENT_SCHEMAS_DIR, SCHEMA_REGISTRY_NAME, SSM_SCHEMA_ROOT } from '../constants';
import * as path from 'path';
import * as fs from 'fs';
import { schemaNamesList, BuildSchemaProps } from './interfaces';
import { Construct } from 'constructs';
import { camelCaseToKebabCase } from '../utils';

export function buildRegistry(scope: Construct, registryName: string): schemas.CfnRegistry {
  return new schemas.CfnRegistry(scope, `${registryName}-registry`, {
    registryName: registryName,
  });
}

export function buildSchema(scope: Construct, props: BuildSchemaProps): schemas.CfnSchema {
  // Import the schema file from the schemas directory
  const schemaPath = path.join(
    EVENT_SCHEMAS_DIR,
    camelCaseToKebabCase(props.schemaName) + '-schema.json'
  );

  // Create a new schema in the Event Schemas service
  return new schemas.CfnSchema(scope, props.schemaName, {
    type: 'JSONSchemaDraft4',
    content: fs.readFileSync(schemaPath, 'utf-8'),
    registryName: props.registry.attrRegistryName,
  });
}

export function buildSchemasAndRegistry(scope: Construct) {
  // Build the registry
  const registryObj = buildRegistry(scope, SCHEMA_REGISTRY_NAME);

  // Add an ssm entry for the registry name
  new ssm.StringParameter(scope, `${SCHEMA_REGISTRY_NAME}-ssm`, {
    parameterName: path.join(SSM_SCHEMA_ROOT, 'registry'),
    stringValue: registryObj.attrRegistryName,
  });

  // Iterate over the schemas directory and create a schema for each file
  for (const schemaName of schemaNamesList) {
    const schemaObj = buildSchema(scope, {
      registry: registryObj,
      schemaName: schemaName,
    });
    // And also a latest ssm parameter for the schema
    // Likely the one most commonly used
    new ssm.StringParameter(scope, `${schemaName}-ssm-latest`, {
      parameterName: path.join(SSM_SCHEMA_ROOT, camelCaseToKebabCase(schemaName), 'latest'),
      stringValue: JSON.stringify({
        registryName: schemaObj.registryName,
        schemaName: schemaObj.attrSchemaName,
        schemaVersion: schemaObj.attrSchemaVersion,
      }),
    });
  }
}
