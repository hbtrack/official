import type { Middleware } from 'openapi-fetch';
import createClient from 'openapi-fetch';
import type { paths } from './schema';

const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = createClient<paths>({ baseUrl });

// Middleware: adiciona JWT Bearer em todas as requisições
const authMiddleware: Middleware = {
  onRequest({ request }) {
    const token = localStorage.getItem('access_token');
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};

apiClient.use(authMiddleware);

export default apiClient;
