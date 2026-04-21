import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../stores/authStore';
import apiClient from '../client';

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const { data, error } = await apiClient.POST('/auth/login', {
        body: { email, password },
      });
      if (error) throw error;
      return data!;
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
    mutationFn: async () => {
      await apiClient.POST('/auth/logout', {});
    },
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
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/auth/me');
      if (error) throw error;
      return data;
    },
    enabled: isAuthenticated,
    retry: false,
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (email: string) => {
      const { error } = await apiClient.POST('/auth/forgot-password', { body: { email } });
      if (error) throw error;
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async ({
      token,
      resetRequestId,
      newPassword,
    }: {
      token: string;
      resetRequestId: string;
      newPassword: string;
    }) => {
      const { error } = await apiClient.POST('/auth/new-password', {
        body: { token, resetRequestId, newPassword },
      });
      if (error) throw error;
      await apiClient.POST('/auth/confirm-reset', { body: { resetRequestId } }).catch(() => null);
    },
  });
}
