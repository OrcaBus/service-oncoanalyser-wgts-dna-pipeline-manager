import { LambdaInput, lambdaNameList, LambdaObject, lambdaRequirementsMap } from './interfaces';
import { PythonUvFunction } from '@orcabus/platform-cdk-constructs/lambda';
import {
  DEFAULT_PAYLOAD_VERSION,
  DEFAULT_WORKFLOW_VERSION,
  LAMBDA_DIR,
  SCHEMA_REGISTRY_NAME,
  SSM_SCHEMA_ROOT,
  TEST_DATA_BUCKET_NAME,
  REF_DATA_BUCKET_NAME,
  WORKFLOW_NAME,
} from '../constants';
import { REPO_NAME } from '../../toolchain/constants';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cdk from 'aws-cdk-lib';
import { Duration } from 'aws-cdk-lib';
import { NagSuppressions } from 'cdk-nag';
import { Construct } from 'constructs';
import { camelCaseToKebabCase, camelCaseToSnakeCase } from '../utils';
import * as path from 'path';
import { SchemaNames } from '../event-schemas/interfaces';

function buildLambda(scope: Construct, props: LambdaInput): LambdaObject {
  const lambdaNameToSnakeCase = camelCaseToSnakeCase(props.lambdaName);
  const lambdaRequirements = lambdaRequirementsMap[props.lambdaName];

  // Create the lambda function
  const lambdaFunction = new PythonUvFunction(scope, props.lambdaName, {
    entry: path.join(LAMBDA_DIR, lambdaNameToSnakeCase + '_py'),
    runtime: lambda.Runtime.PYTHON_3_14,
    architecture: lambda.Architecture.ARM_64,
    index: lambdaNameToSnakeCase + '.py',
    handler: 'handler',
    timeout: Duration.seconds(60),
    memorySize:
      lambdaRequirements.needsIcav2Tools || lambdaRequirements.needsHigherMemory ? 1024 : 512,
    includeOrcabusApiToolsLayer: lambdaRequirements.needsOrcabusApiTools,
    includeIcav2Layer: lambdaRequirements.needsIcav2Tools,
  });

  // AwsSolutions-L1 - Python 3.14 is not yet in the cdk-nag approved list but is our target runtime
  // AwsSolutions-IAM4 - Basic execution role provides CloudWatch Logs permissions needed by all Lambdas
  NagSuppressions.addResourceSuppressions(
    lambdaFunction,
    [
      {
        id: 'AwsSolutions-L1',
        reason:
          'Python 3.14 is not yet in the cdk-nag approved list but is our target runtime for ARM64 Lambda functions',
      },
      {
        id: 'AwsSolutions-IAM4',
        reason:
          'Basic execution managed policy provides CloudWatch Logs permissions required by all Lambda functions',
      },
    ],
    true
  );

  /*
    Add in SSM permissions for the lambda function
    */
  if (lambdaRequirements.needsSsmParametersAccess) {
    lambdaFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['ssm:GetParameter'],
        resources: [
          `arn:aws:ssm:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:parameter${path.join(SSM_SCHEMA_ROOT, '/*')}`,
        ],
      })
    );
    NagSuppressions.addResourceSuppressions(
      lambdaFunction,
      [
        {
          id: 'AwsSolutions-IAM5',
          reason:
            'Wildcard covers SSM parameters under the schema root path; specific parameter names include schema versions determined at runtime',
        },
      ],
      true
    );
  }

  /*
    For the schema validation lambdas we need to give them the access to the schema
    */
  if (lambdaRequirements.needsSchemaRegistryAccess) {
    // Add the schema registry access to the lambda function
    lambdaFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['schemas:DescribeRegistry', 'schemas:DescribeSchema'],
        resources: [
          `arn:aws:schemas:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:registry/${SCHEMA_REGISTRY_NAME}`,
          `arn:aws:schemas:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:schema/${path.join(SCHEMA_REGISTRY_NAME, '/*')}`,
        ],
      })
    );

    NagSuppressions.addResourceSuppressions(
      lambdaFunction,
      [
        {
          id: 'AwsSolutions-IAM5',
          reason:
            'Wildcard covers all schema versions in the registry; individual schema ARNs cannot be enumerated at deploy time because versions are created dynamically',
        },
      ],
      true
    );

    /*
    Special if the lambdaName needs schema registry access,
    we need to add in the ssm parameters
    to the REGISTRY_NAME and SCHEMA_PATH
   */
    const draftSchemaName: SchemaNames = 'completeDataDraft';
    lambdaFunction.addEnvironment('SSM_REGISTRY_NAME', path.join(SSM_SCHEMA_ROOT, 'registry'));
    lambdaFunction.addEnvironment(
      'SSM_SCHEMA_PATH',
      path.join(SSM_SCHEMA_ROOT, camelCaseToKebabCase(draftSchemaName))
    );
    /*
    Add DEFAULT_PAYLOAD_VERSION env var too
    */
    lambdaFunction.addEnvironment('DEFAULT_PAYLOAD_VERSION', DEFAULT_PAYLOAD_VERSION);
  }

  /*
    External bucket info, required by the post schema validation lambda to confirm inputs
    are legitimate
  */
  if (lambdaRequirements.needsExternalBucketInfo) {
    lambdaFunction.addEnvironment('TEST_DATA_BUCKET_NAME', TEST_DATA_BUCKET_NAME);
    lambdaFunction.addEnvironment('REF_DATA_BUCKET_NAME', REF_DATA_BUCKET_NAME);
  }

  /*
  Workflow info, usually for comment generation on the workflow run in the OrcaUI
   */
  if (lambdaRequirements.needsWorkflowInfo) {
    lambdaFunction.addEnvironment('WORKFLOW_NAME', WORKFLOW_NAME);
    lambdaFunction.addEnvironment('WORKFLOW_VERSION', DEFAULT_WORKFLOW_VERSION);
  }

  /*
  Repository GitHub URL, used in user-facing comments to link to the README
   */
  if (lambdaRequirements.needsRepoUrl) {
    lambdaFunction.addEnvironment(
      'REPOSITORY_GITHUB_URL',
      `https://github.com/OrcaBus/${REPO_NAME}`
    );
  }

  /* Return the function */
  return {
    lambdaName: props.lambdaName,
    lambdaFunction: lambdaFunction,
  };
}

export function buildAllLambdas(scope: Construct): LambdaObject[] {
  // Iterate over lambdaLayerToMapping and create the lambda functions
  const lambdaObjects: LambdaObject[] = [];
  for (const lambdaName of lambdaNameList) {
    lambdaObjects.push(
      buildLambda(scope, {
        lambdaName: lambdaName,
      })
    );
  }

  return lambdaObjects;
}
