import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../client';

// ─── Session list & detail ────────────────────────────────────────────────────

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

// ─── State transitions ────────────────────────────────────────────────────────

function useSessionTransition(endpoint: '/training-sessions/{id}/publish' | '/training-sessions/{id}/start' | '/training-sessions/{id}/complete' | '/training-sessions/{id}/cancel') {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data, error } = await apiClient.POST(endpoint, {
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

export function usePublishTrainingSession() { return useSessionTransition('/training-sessions/{id}/publish'); }
export function useStartTrainingSession() { return useSessionTransition('/training-sessions/{id}/start'); }
export function useCompleteTrainingSession() { return useSessionTransition('/training-sessions/{id}/complete'); }
export function useCancelTrainingSession() { return useSessionTransition('/training-sessions/{id}/cancel'); }

// ─── Blocks ───────────────────────────────────────────────────────────────────

export function useSessionBlocks(sessionId: string) {
  return useQuery({
    queryKey: ['session-blocks', sessionId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/training-sessions/{id}/blocks', {
        params: { path: { id: sessionId } },
      });
      if (error) throw error;
      return data!.data;
    },
    enabled: !!sessionId,
  });
}

export function useAddSessionBlock(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      phase: 'WARMUP' | 'ACTIVATION' | 'TECHNICAL' | 'DECISION_MAKING' | 'TACTICAL' | 'REDUCED_GAME' | 'COOLDOWN';
      orderIndex: number;
      durationMinutes: number;
      blockObjective: string;
      intensity: 'LOW' | 'MEDIUM' | 'HIGH' | 'MAXIMUM';
      notes?: string;
      isOptional: boolean;
    }) => {
      const { data, error } = await apiClient.POST('/training-sessions/{id}/blocks', {
        params: { path: { id: sessionId } },
        body,
      });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session-blocks', sessionId] });
    },
  });
}

export function useDeleteSessionBlock(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (blockId: string) => {
      const { error } = await apiClient.DELETE('/training-sessions/{id}/blocks/{blockId}', {
        params: { path: { id: sessionId, blockId } },
      });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session-blocks', sessionId] });
    },
  });
}

export function useReorderSessionBlocks(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (blockIds: string[]) => {
      const { data, error } = await apiClient.POST('/training-sessions/{id}/blocks/reorder', {
        params: { path: { id: sessionId } },
        body: { blockIds },
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session-blocks', sessionId] });
    },
  });
}

// ─── Attendance ───────────────────────────────────────────────────────────────

export function useSessionAttendance(sessionId: string) {
  return useQuery({
    queryKey: ['session-attendance', sessionId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/training-sessions/{id}/attendance', {
        params: { path: { id: sessionId } },
      });
      if (error) throw error;
      return data!.items;
    },
    enabled: !!sessionId,
  });
}

export function useRecordAttendance(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: {
      athleteId: string;
      status: 'PRESENT' | 'ABSENT' | 'JUSTIFIED' | 'PRECONFIRMED';
    }) => {
      const { data, error } = await apiClient.POST('/training-sessions/{id}/attendance', {
        params: { path: { id: sessionId } },
        body,
      });
      if (error) throw error;
      return data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session-attendance', sessionId] });
    },
  });
}
