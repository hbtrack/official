// @vitest-environment node

import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { PactV3 } from '@pact-foundation/pact';
import { createHbTrackApiClient } from '../client';
import {
  getCurrentSessionRequest,
  loginRequest,
  logoutRequest,
} from '../requests/auth';

const problemUnauthorized = {
  type: 'about:blank',
  title: 'Unauthorized',
  status: 401,
};

describe('hbtrack-app consumer pact', () => {
  it('captures deterministic auth interactions consumed by the frontend', async () => {
    const provider = new PactV3({
      consumer: 'hbtrack-app',
      provider: 'hbtrack-api',
      dir: path.resolve(process.cwd(), 'pacts'),
      logLevel: 'warn',
    });

    provider
      .uponReceiving('an invalid login attempt from the frontend')
      .withRequest({
        method: 'POST',
        path: '/api/auth/login',
        body: {
          email: 'coach@hbtrack.app',
          password: 'wrong-password',
        },
      })
      .willRespondWith({
        status: 401,
        headers: { 'Content-Type': 'application/problem+json' },
        body: {
          ...problemUnauthorized,
          detail: 'Credenciais inválidas.',
        },
      });

    provider
      .uponReceiving('a current-session lookup with an invalid bearer token')
      .withRequest({
        method: 'GET',
        path: '/api/auth/me',
        headers: {
          Authorization: 'Bearer invalid.jwt.token',
        },
      })
      .willRespondWith({
        status: 401,
        headers: { 'Content-Type': 'application/problem+json' },
        body: {
          ...problemUnauthorized,
          detail: 'Token ausente ou inválido.',
        },
      });

    provider
      .uponReceiving('a logout request with an invalid bearer token')
      .withRequest({
        method: 'POST',
        path: '/api/auth/logout',
        headers: {
          Authorization: 'Bearer invalid.jwt.token',
        },
      })
      .willRespondWith({
        status: 401,
        headers: { 'Content-Type': 'application/problem+json' },
        body: {
          ...problemUnauthorized,
          detail: 'Token ausente ou inválido.',
        },
      });

    await provider.executeTest(async (mockServer) => {
      const anonymousClient = createHbTrackApiClient({
        baseUrl: `${mockServer.url}/api`,
        tokenProvider: () => null,
      });
      const authenticatedClient = createHbTrackApiClient({
        baseUrl: `${mockServer.url}/api`,
        tokenProvider: () => 'invalid.jwt.token',
      });

      await expect(
        loginRequest(anonymousClient, {
          email: 'coach@hbtrack.app',
          password: 'wrong-password',
        }),
      ).rejects.toMatchObject({
        title: 'Unauthorized',
        status: 401,
        detail: 'Credenciais inválidas.',
      });

      await expect(getCurrentSessionRequest(authenticatedClient)).rejects.toMatchObject({
        title: 'Unauthorized',
        status: 401,
        detail: 'Token ausente ou inválido.',
      });

      await expect(logoutRequest(authenticatedClient)).rejects.toMatchObject({
        title: 'Unauthorized',
        status: 401,
        detail: 'Token ausente ou inválido.',
      });
    });
  });
});
