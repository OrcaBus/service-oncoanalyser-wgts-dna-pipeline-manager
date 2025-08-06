import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class DeployStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /**
     * Define your stack to be deployed in stages here
     *
     * TODO: Rename the class to match the service name and stateless/stateful stack
     */
  }
}
