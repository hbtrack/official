import { createClient } from 'openapi-fetch';
import type { paths } from './schema';

const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = createClient<paths>({
  baseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors = {
  beforeRequest: async (request) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};

export default apiClient;
