import {
  PIPELINE_CACHE_BUCKET,
  PIPELINE_CACHE_PREFIX,
} from '@orcabus/platform-cdk-constructs/shared-config/s3';
import { StageName } from '@orcabus/platform-cdk-constructs/shared-config/accounts';

export function camelCaseToSnakeCase(camelCase: string): string {
  return camelCase.replace(/([A-Z])/g, '_$1').toLowerCase();
}

export function camelCaseToKebabCase(camelCase: string): string {
  return camelCase.replace(/([A-Z])/g, '-$1').toLowerCase();
}

export function substituteBucketConstants(uri: string, stage: StageName) {
  return uri
    .replace(/{__CACHE_BUCKET__}/g, PIPELINE_CACHE_BUCKET[stage])
    .replace(/{__CACHE_PREFIX__}/g, PIPELINE_CACHE_PREFIX[stage]);
}
