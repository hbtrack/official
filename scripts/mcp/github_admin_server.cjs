#!/usr/bin/env node
'use strict';

const { execFileSync, spawnSync } = require('node:child_process');
const { McpServer } = require('@modelcontextprotocol/sdk/server/mcp.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { z } = require('zod');

const DEFAULT_REPO = process.env.GITHUB_DEFAULT_REPO || 'hbtrack/official';
const API_BASE = 'https://api.github.com';
const GITHUB_API_VERSION = '2022-11-28';

const ALLOWED_SURFACE_PATTERNS = [
  /^\/rulesets(?:\/|$)/,
  /^\/rules\/branches\/[^/]+(?:\/|$)/,
  /^\/branches\/[^/]+\/protection(?:\/|$)/,
  /^\/environments(?:\/|$)/,
  /^\/actions\/variables(?:\/|$)/,
  /^\/actions\/secrets(?:\/|$)/
];

function parseRepoFullName(repoFullName) {
  const value = (repoFullName || DEFAULT_REPO).trim();
  const match = value.match(/^(?:[^/]+\/)?([^/]+)\/([^/]+)$/);
  if (!match) {
    throw new Error(`repo_full_name invalido: ${value}`);
  }
  return { owner: match[1], repo: match[2], normalized: `${match[1]}/${match[2]}` };
}

function normalizeSurface(surface) {
  if (!surface || typeof surface !== 'string') {
    throw new Error('surface deve ser uma string nao vazia.');
  }
  const trimmed = surface.trim();
  const normalized = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
  if (normalized.includes('..') || normalized.includes('?') || normalized.includes('#')) {
    throw new Error(`surface nao permitida: ${normalized}`);
  }
  return normalized;
}

function assertAllowedSurface(surface) {
  if (!ALLOWED_SURFACE_PATTERNS.some((pattern) => pattern.test(surface))) {
    throw new Error(
      `surface fora da allowlist administrativa: ${surface}. Permitido apenas para rulesets, branch policy, environments, actions variables e actions secrets.`
    );
  }
}

function getGitHubToken() {
  const fromEnv = process.env.GITHUB_TOKEN;
  if (fromEnv && fromEnv.trim()) {
    return fromEnv.trim();
  }
  try {
    return execFileSync('gh', ['auth', 'token'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe']
    }).trim();
  } catch (error) {
    const stderr = error && typeof error.stderr === 'string' ? error.stderr.trim() : '';
    throw new Error(stderr || 'Nao foi possivel obter token via gh auth token.');
  }
}

async function githubRequest({ repoFullName, method = 'GET', surface, body = undefined }) {
  const repo = parseRepoFullName(repoFullName);
  const normalizedSurface = normalizeSurface(surface);
  assertAllowedSurface(normalizedSurface);
  const url = `${API_BASE}/repos/${repo.normalized}${normalizedSurface}`;
  const headers = {
    Accept: 'application/vnd.github+json',
    Authorization: `Bearer ${getGitHubToken()}`,
    'X-GitHub-Api-Version': GITHUB_API_VERSION
  };

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    method: method.toUpperCase(),
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined
  });

  const text = await response.text();
  let payload;
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { raw: text };
  }

  if (!response.ok) {
    const message =
      payload && typeof payload === 'object' && payload.message
        ? payload.message
        : typeof payload.raw === 'string'
          ? payload.raw
          : JSON.stringify(payload);
    throw new Error(`${method.toUpperCase()} ${normalizedSurface} falhou (${response.status}): ${message}`);
  }

  return {
    repo_full_name: repo.normalized,
    method: method.toUpperCase(),
    surface: normalizedSurface,
    status: response.status,
    payload
  };
}

function runGhCommand(args, input = undefined) {
  const result = spawnSync('gh', args, {
    encoding: 'utf8',
    input,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || 'gh command failed').trim());
  }
  return (result.stdout || '').trim();
}

function sanitizeSecretResult({ repoFullName, environmentName, secretName, action }) {
  return {
    repo_full_name: parseRepoFullName(repoFullName).normalized,
    environment_name: environmentName || null,
    secret_name: secretName,
    action
  };
}

async function main() {
  const keepAlive = setInterval(() => {}, 60_000);
  const server = new McpServer(
    {
      name: 'hbtrack-github-admin',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {}
      }
    }
  );

  server.registerTool(
    'github_admin_whoami',
    {
      description:
        'Valida autenticacao administrativa local para GitHub e retorna usuario, repo default e superfícies administrativas suportadas.',
      inputSchema: {
        repo_full_name: z.string().optional()
      },
      outputSchema: {
        login: z.string(),
        repo_full_name: z.string(),
        supported_surfaces: z.array(z.string())
      }
    },
    async ({ repo_full_name }) => {
      const token = getGitHubToken();
      const userResponse = await fetch(`${API_BASE}/user`, {
        headers: {
          Accept: 'application/vnd.github+json',
          Authorization: `Bearer ${token}`,
          'X-GitHub-Api-Version': GITHUB_API_VERSION
        }
      });
      if (!userResponse.ok) {
        throw new Error(`GET /user falhou (${userResponse.status})`);
      }
      const user = await userResponse.json();
      const structuredContent = {
        login: user.login,
        repo_full_name: parseRepoFullName(repo_full_name).normalized,
        supported_surfaces: [
          'rulesets',
          'branch_policy',
          'environments',
          'actions_variables',
          'actions_secrets'
        ]
      };
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_request',
    {
      description:
        'Executa chamada REST administrativa allowlisted para rulesets, branch policy, environments e Actions variables/secrets.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        method: z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']),
        surface: z.string().describe('Ex.: /rulesets, /rules/branches/main, /environments, /actions/variables'),
        body_json: z.string().optional().describe('JSON string para metodos mutadores.')
      },
      outputSchema: {
        repo_full_name: z.string(),
        method: z.string(),
        surface: z.string(),
        status: z.number(),
        payload: z.unknown()
      }
    },
    async ({ repo_full_name, method, surface, body_json }) => {
      const body = body_json ? JSON.parse(body_json) : undefined;
      const structuredContent = await githubRequest({
        repoFullName: repo_full_name,
        method,
        surface,
        body
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_get_branch_policy',
    {
      description:
        'Retorna regras efetivas do branch via rulesets e, quando existir, branch protection classica para o branch solicitado.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        branch: z.string()
      },
      outputSchema: {
        repo_full_name: z.string(),
        branch: z.string(),
        applied_rules: z.unknown(),
        classic_branch_protection: z.unknown().nullable()
      }
    },
    async ({ repo_full_name, branch }) => {
      const appliedRules = await githubRequest({
        repoFullName: repo_full_name,
        method: 'GET',
        surface: `/rules/branches/${branch}`
      });

      let classicBranchProtection = null;
      try {
        const classic = await githubRequest({
          repoFullName: repo_full_name,
          method: 'GET',
          surface: `/branches/${branch}/protection`
        });
        classicBranchProtection = classic.payload;
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        if (!message.includes('(404)')) {
          throw error;
        }
      }

      const structuredContent = {
        repo_full_name: appliedRules.repo_full_name,
        branch,
        applied_rules: appliedRules.payload,
        classic_branch_protection: classicBranchProtection
      };

      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_list_actions_variables',
    {
      description:
        'Lista Actions variables no nível de repositório ou de environment.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        environment_name: z.string().optional()
      },
      outputSchema: {
        repo_full_name: z.string(),
        scope: z.enum(['repository', 'environment']),
        environment_name: z.string().nullable(),
        payload: z.unknown()
      }
    },
    async ({ repo_full_name, environment_name }) => {
      const surface = environment_name
        ? `/environments/${environment_name}/variables`
        : '/actions/variables';
      const result = await githubRequest({
        repoFullName: repo_full_name,
        method: 'GET',
        surface
      });
      const structuredContent = {
        repo_full_name: result.repo_full_name,
        scope: environment_name ? 'environment' : 'repository',
        environment_name: environment_name || null,
        payload: result.payload
      };
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_set_actions_variable',
    {
      description:
        'Cria ou atualiza uma GitHub Actions variable no repositório ou em um environment.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        environment_name: z.string().optional(),
        name: z.string(),
        value: z.string()
      },
      outputSchema: {
        repo_full_name: z.string(),
        scope: z.enum(['repository', 'environment']),
        environment_name: z.string().nullable(),
        name: z.string(),
        action: z.literal('upserted')
      }
    },
    async ({ repo_full_name, environment_name, name, value }) => {
      const repo = parseRepoFullName(repo_full_name).normalized;
      const args = ['variable', 'set', name, '--repo', repo, '--body', value];
      if (environment_name) {
        args.push('--env', environment_name);
      }
      runGhCommand(args);
      const structuredContent = {
        repo_full_name: repo,
        scope: environment_name ? 'environment' : 'repository',
        environment_name: environment_name || null,
        name,
        action: 'upserted'
      };
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_delete_actions_variable',
    {
      description:
        'Remove uma GitHub Actions variable no repositório ou em um environment.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        environment_name: z.string().optional(),
        name: z.string()
      },
      outputSchema: {
        repo_full_name: z.string(),
        scope: z.enum(['repository', 'environment']),
        environment_name: z.string().nullable(),
        name: z.string(),
        action: z.literal('deleted')
      }
    },
    async ({ repo_full_name, environment_name, name }) => {
      const repo = parseRepoFullName(repo_full_name).normalized;
      const args = ['variable', 'delete', name, '--repo', repo];
      if (environment_name) {
        args.push('--env', environment_name);
      }
      runGhCommand(args, 'y\n');
      const structuredContent = {
        repo_full_name: repo,
        scope: environment_name ? 'environment' : 'repository',
        environment_name: environment_name || null,
        name,
        action: 'deleted'
      };
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_list_actions_secrets',
    {
      description:
        'Lista nomes de GitHub Actions secrets no repositório ou em um environment.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        environment_name: z.string().optional()
      },
      outputSchema: {
        repo_full_name: z.string(),
        scope: z.enum(['repository', 'environment']),
        environment_name: z.string().nullable(),
        payload: z.unknown()
      }
    },
    async ({ repo_full_name, environment_name }) => {
      const surface = environment_name
        ? `/environments/${environment_name}/secrets`
        : '/actions/secrets';
      const result = await githubRequest({
        repoFullName: repo_full_name,
        method: 'GET',
        surface
      });
      const structuredContent = {
        repo_full_name: result.repo_full_name,
        scope: environment_name ? 'environment' : 'repository',
        environment_name: environment_name || null,
        payload: result.payload
      };
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_set_actions_secret',
    {
      description:
        'Cria ou atualiza um GitHub Actions secret no repositório ou em um environment usando criptografia local do gh.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        environment_name: z.string().optional(),
        name: z.string(),
        value: z.string()
      },
      outputSchema: {
        repo_full_name: z.string(),
        environment_name: z.string().nullable(),
        secret_name: z.string(),
        action: z.literal('upserted')
      }
    },
    async ({ repo_full_name, environment_name, name, value }) => {
      const repo = parseRepoFullName(repo_full_name).normalized;
      const args = ['secret', 'set', name, '--repo', repo, '--body', value];
      if (environment_name) {
        args.push('--env', environment_name);
      }
      runGhCommand(args);
      const structuredContent = sanitizeSecretResult({
        repoFullName: repo,
        environmentName: environment_name,
        secretName: name,
        action: 'upserted'
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  server.registerTool(
    'github_admin_delete_actions_secret',
    {
      description:
        'Remove um GitHub Actions secret no repositório ou em um environment.',
      inputSchema: {
        repo_full_name: z.string().optional(),
        environment_name: z.string().optional(),
        name: z.string()
      },
      outputSchema: {
        repo_full_name: z.string(),
        environment_name: z.string().nullable(),
        secret_name: z.string(),
        action: z.literal('deleted')
      }
    },
    async ({ repo_full_name, environment_name, name }) => {
      const repo = parseRepoFullName(repo_full_name).normalized;
      const args = ['secret', 'delete', name, '--repo', repo];
      if (environment_name) {
        args.push('--env', environment_name);
      }
      runGhCommand(args, 'y\n');
      const structuredContent = sanitizeSecretResult({
        repoFullName: repo,
        environmentName: environment_name,
        secretName: name,
        action: 'deleted'
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(structuredContent, null, 2) }],
        structuredContent
      };
    }
  );

  const transport = new StdioServerTransport();
  await server.connect(transport);
  process.stdin.resume();
  console.error('hbtrack-github-admin MCP server running on stdio');
  const shutdown = async () => {
    clearInterval(keepAlive);
    try {
      await server.close();
    } catch {
      // ignore shutdown errors
    }
    process.exit(0);
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.stack || error.message : String(error));
  process.exit(1);
});
