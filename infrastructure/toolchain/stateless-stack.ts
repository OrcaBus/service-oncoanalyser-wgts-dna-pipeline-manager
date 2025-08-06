import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DeploymentStackPipeline } from '@orcabus/platform-cdk-constructs/deployment-stack-pipeline';
import { getStackProps } from '../stage/config';

export class StatelessStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new DeploymentStackPipeline(this, 'DeploymentPipeline', {
      githubBranch: 'main',
      githubRepo: /** TODO: Replace with string. Example: */ 'service-microservice-manager',
      stack: /** TODO: Replace with Stack (e.g. TheStatelessStack) */ undefined as unknown,
      stackName: /** TODO: Replace with string. Example: */ 'StatelessMicroserviceManager',
      stackConfig: {
        beta: getStackProps('BETA'),
        gamma: getStackProps('GAMMA'),
        prod: getStackProps('PROD'),
      },
      pipelineName: /** TODO: Replace with string. Example: */ 'OrcaBus-StatelessMicroservice',
      cdkSynthCmd: ['pnpm install --frozen-lockfile --ignore-scripts', 'pnpm cdk-stateless synth'],
    });
  }
}
