import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../client';

export function useTrainingSessions(params?: { teamId?: string; seasonId?: string; organizationId?: string }) {
  return useQuery({
    queryKey: ['training-sessions', params],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/training-sessions', {
        params: { query: params as Record<string, string | undefined> },
      });
      if (error) throw error;
      return data!;
    },
  });
}

export function useTrainingSession(id: string) {
  return useQuery({
    queryKey: ['training-sessions', id],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/training-sessions/{id}', {
        params: { path: { id } },
      });
      if (error) throw error;
      return data!;
    },
    enabled: !!id,
  });
}

export function useCreateTrainingSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      teamId?: string;
      seasonId?: string;
      sessionAt: string;
      durationPlannedMinutes?: number;
      sessionType: string;
      mainObjective?: string;
    }) => {
      const { data, error } = await apiClient.POST('/training-sessions', { body });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-sessions'] });
    },
  });
}

export function usePublishTrainingSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data, error } = await apiClient.POST('/training-sessions/{id}/publish', {
        params: { path: { id } },
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['training-sessions', id] });
      queryClient.invalidateQueries({ queryKey: ['training-sessions'] });
    },
  });
}
