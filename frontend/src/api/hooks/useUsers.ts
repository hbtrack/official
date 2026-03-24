import { useQuery } from '@tanstack/react-query';
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
