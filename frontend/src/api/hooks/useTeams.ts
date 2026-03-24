import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../client';

export function useTeams(params?: { organizationId?: string }) {
  return useQuery({
    queryKey: ['teams', params],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/teams', {
        params: { query: params as Record<string, string | undefined> },
      });
      if (error) throw error;
      return data!;
    },
  });
}

export function useTeam(teamId: string) {
  return useQuery({
    queryKey: ['teams', teamId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/teams/{teamId}', {
        params: { path: { teamId } },
      });
      if (error) throw error;
      return data!;
    },
    enabled: !!teamId,
  });
}

export function useCreateTeam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: { name: string; city?: string }) => {
      const { data, error } = await apiClient.POST('/teams', { body });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });
}
