#!/usr/bin/env node
'use strict';

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

async function main() {
  const client = new Client({
    name: 'hbtrack-github-admin-smoke-test',
    version: '1.0.0'
  });

  const transport = new StdioClientTransport({
    command: 'node',
    args: ['scripts/mcp/github_admin_server.cjs'],
    cwd: process.cwd(),
    stderr: 'pipe'
  });

  if (transport.stderr) {
    transport.stderr.on('data', () => {
      // discard child stderr during smoke test
    });
  }

  await client.connect(transport);
  const toolsResult = await client.listTools();
  const toolNames = new Set(toolsResult.tools.map((tool) => tool.name));
  const expected = [
    'github_admin_whoami',
    'github_admin_request',
    'github_admin_get_branch_policy',
    'github_admin_list_actions_variables',
    'github_admin_set_actions_variable',
    'github_admin_delete_actions_variable',
    'github_admin_list_actions_secrets',
    'github_admin_set_actions_secret',
    'github_admin_delete_actions_secret'
  ];

  for (const name of expected) {
    if (!toolNames.has(name)) {
      throw new Error(`Tool ausente no server: ${name}`);
    }
  }

  const whoami = await client.callTool({
    name: 'github_admin_whoami',
    arguments: {
      repo_full_name: 'hbtrack/official'
    }
  });

  const result = {
    tools: expected,
    whoami: whoami.structuredContent
  };

  console.log(JSON.stringify(result, null, 2));
  await client.close();
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error));
  process.exit(1);
});
