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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const { data, error } = await apiClient.POST('/teams', { body: body as any });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });
}

export function useAddAthleteToTeam(teamId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (athleteUserId: string) => {
      const { data, error } = await apiClient.POST(
        '/teams/{teamId}/athletes/{athleteUserId}',
        { params: { path: { teamId, athleteUserId } } },
      );
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', teamId] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useRemoveAthleteFromTeam(teamId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (athleteUserId: string) => {
      const { data, error } = await apiClient.DELETE(
        '/teams/{teamId}/athletes/{athleteUserId}',
        { params: { path: { teamId, athleteUserId } } },
      );
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', teamId] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

