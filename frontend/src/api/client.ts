import type { Middleware } from 'openapi-fetch';
import createClient from 'openapi-fetch';
import type { paths } from './schema';

export type HbTrackApiClient = ReturnType<typeof createClient<paths>>;
export type TokenProvider = () => string | null | undefined;

const defaultBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function browserTokenProvider() {
  if (typeof localStorage === 'undefined') {
    return null;
  }
  return localStorage.getItem('access_token');
}

function buildAuthMiddleware(tokenProvider: TokenProvider): Middleware {
  return {
    onRequest({ request }) {
      const token = tokenProvider();
      if (token) {
        request.headers.set('Authorization', `Bearer ${token}`);
      }
      return request;
    },
  };
}

export function createHbTrackApiClient(options: {
  baseUrl?: string;
  tokenProvider?: TokenProvider;
} = {}): HbTrackApiClient {
  const client = createClient<paths>({ baseUrl: options.baseUrl || defaultBaseUrl });
  const tokenProvider = options.tokenProvider || browserTokenProvider;
  client.use(buildAuthMiddleware(tokenProvider));
  return client;
}

export const apiClient = createHbTrackApiClient();

export default apiClient;
