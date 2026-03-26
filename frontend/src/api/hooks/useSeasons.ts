import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../client';

export function useSeasons(params?: { organizationId?: string; teamId?: string }) {
  return useQuery({
    queryKey: ['seasons', params],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/seasons', {
        params: { query: params as Record<string, string | undefined> },
      });
      if (error) throw error;
      return data!;
    },
  });
}

export function useSeason(seasonId: string) {
  return useQuery({
    queryKey: ['seasons', seasonId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/seasons/{seasonId}', {
        params: { path: { seasonId } },
      });
      if (error) throw error;
      return data!;
    },
    enabled: !!seasonId,
  });
}

export function useCreateSeason() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: { year: number; startDate?: string; endDate?: string; teamId?: string }) => {
      const { data, error } = await apiClient.POST('/seasons', { body });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seasons'] });
    },
  });
}
