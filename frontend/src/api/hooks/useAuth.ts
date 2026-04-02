import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../client';
import {
  getCurrentSessionRequest,
  loginRequest,
  logoutRequest,
} from '../requests/auth';
import { useAuthStore } from '../../stores/authStore';

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      return loginRequest(apiClient, { email, password });
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.accessToken);
      localStorage.setItem('refresh_token', data.refreshToken);
      const session = data.session as { principalUserId?: string };
      setAuth(
        {
          id: session.principalUserId ?? '',
          username: '',
          email: '',
          organization_id: '',
          roles: [],
        },
        data.accessToken
      );
      queryClient.invalidateQueries({ queryKey: ['me'] });
    },
  });
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => logoutRequest(apiClient),
    onSettled: () => {
      logout();
      queryClient.clear();
    },
  });
}

export function useCurrentSession() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => getCurrentSessionRequest(apiClient),
    enabled: isAuthenticated,
    retry: false,
  });
}
