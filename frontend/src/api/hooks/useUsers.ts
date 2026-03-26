import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../client';

export function useUsers(params?: { organizationId?: string; teamId?: string; roleLabel?: string }) {
  return useQuery({
    queryKey: ['users', params],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/users', {
        params: { query: params as Record<string, string | undefined> },
      });
      if (error) throw error;
      return data!;
    },
  });
}

export function useUser(userId: string) {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/users/{userId}', {
        params: { path: { userId } },
      });
      if (error) throw error;
      return data!;
    },
    enabled: !!userId,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      username: string;
      email: string;
      roleLabel: string;
      firstName?: string;
      lastName?: string;
      positionLabel?: string;
    }) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const { data, error } = await apiClient.POST('/users', { body: body as any });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function usePatchUser(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      firstName?: string;
      lastName?: string;
      positionLabel?: string;
      statusLabel?: string;
    }) => {
      const { data, error } = await apiClient.PATCH('/users/{userId}', {
        params: { path: { userId } },
        body,
      });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', userId] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

