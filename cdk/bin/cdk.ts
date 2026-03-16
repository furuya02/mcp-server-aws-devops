#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { McpStack } from '../lib/mcp-stack';

const app = new cdk.App();
const projectName = app.node.tryGetContext('projectName') || 'mcp-server-sample';
const authType = app.node.tryGetContext('authType') || 'api-key';

// authType のバリデーション
if (authType !== 'api-key' && authType !== 'oauth') {
  throw new Error(`Invalid authType: ${authType}. Must be 'api-key' or 'oauth'`);
}

const region = app.node.tryGetContext('region') || 'ap-northeast-1';
const env = { account: process.env.CDK_DEFAULT_ACCOUNT, region };

new McpStack(app, `${projectName}-stack`, {
  projectName,
  authType: authType as 'api-key' | 'oauth',
  env,
});
