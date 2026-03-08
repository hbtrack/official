/**
 * Hook: useCycles
 * 
 * Gerencia estado de Training Cycles (Macrociclos e Mesociclos)
 * Base: TRAINNIG.MD + trainings.ts API
 * Data: 2026-01-04
 */

'use client';

import { cyclesApi } from '@/api/generated/api-instance';
import {
  CycleFilters,
  TrainingCycle,
  TrainingCycleWithMicrocycles
} from '@/lib/api/trainings';
import { useCallback, useEffect, useState } from 'react';

// ============================================================================
// TYPES
// ============================================================================

interface UseCyclesState {
  cycles: TrainingCycle[];
  isLoading: boolean;
  error: string | null;
}

interface UseCyclesReturn extends UseCyclesState {
  fetchCycles: (filters: CycleFilters) => Promise<void>;
  refetch: () => Promise<void>;
  createCycle: (data: any) => Promise<TrainingCycle | null>;
  updateCycle: (id: string, data: any) => Promise<TrainingCycle | null>;
  deleteCycle: (id: string, reason: string) => Promise<boolean>;
  currentFilters: CycleFilters | null;
}

interface UseCycleDetailState {
  cycle: TrainingCycleWithMicrocycles | null;
  isLoading: boolean;
  error: string | null;
}

interface UseCycleDetailReturn extends UseCycleDetailState {
  fetchCycle: () => Promise<void>;
  refetch: () => Promise<void>;
  updateCycle: (data: any) => Promise<TrainingCycleWithMicrocycles | null>;
  deleteCycle: (reason: string) => Promise<boolean>;
}

// ============================================================================
// HOOK: useCycles (Lista)
// ============================================================================

/**
 * Hook para listar ciclos de treinamento
 * 
 * @example
 * const { cycles, isLoading, fetchCycles } = useCycles();
 * useEffect(() => {
 *   fetchCycles({ team_id: 'uuid', type: 'macro' });
 * }, []);
 */
export function useCycles(): UseCyclesReturn {
  const [state, setState] = useState<UseCyclesState>({
    cycles: [],
    isLoading: false,
    error: null,
  });

  const [currentFilters, setCurrentFilters] = useState<CycleFilters | null>(null);

  const fetchCycles = useCallback(async (filters: CycleFilters) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    setCurrentFilters(filters);

    try {
      const data = await cyclesApi.listTrainingCyclesApiV1TrainingCyclesGet(filters.team_id ?? null, filters.type ?? null, filters.status ?? null, filters.include_deleted).then(r => r.data as unknown as TrainingCycle[]);
      setState({
        cycles: data,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar ciclos';
      setState({
        cycles: [],
        isLoading: false,
        error: errorMessage,
      });
      console.error('Error fetching cycles:', err);
    }
  }, []);

  const refetch = useCallback(async () => {
    if (currentFilters) {
      await fetchCycles(currentFilters);
    }
  }, [currentFilters, fetchCycles]);

  const createCycle = useCallback(async (data: any): Promise<TrainingCycle | null> => {
    try {
      const newCycle = await cyclesApi.createTrainingCycleApiV1TrainingCyclesPost(data as any).then(r => r.data as unknown as TrainingCycle);
      // Atualiza lista localmente
      setState(prev => ({
        ...prev,
        cycles: [newCycle, ...prev.cycles],
      }));
      return newCycle;
    } catch (err) {
      console.error('Error creating cycle:', err);
      return null;
    }
  }, []);

  const updateCycle = useCallback(async (id: string, data: any): Promise<TrainingCycle | null> => {
    try {
      const updatedCycle = await cyclesApi.updateTrainingCycleApiV1TrainingCyclesCycleIdPatch(id, data as any).then(r => r.data as unknown as TrainingCycle);
      // Atualiza lista localmente
      setState(prev => ({
        ...prev,
        cycles: prev.cycles.map(c => c.id === id ? updatedCycle : c),
      }));
      return updatedCycle;
    } catch (err) {
      console.error('Error updating cycle:', err);
      return null;
    }
  }, []);

  const deleteCycle = useCallback(async (id: string, reason: string): Promise<boolean> => {
    try {
      await cyclesApi.deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete(id, reason).then(r => r.data);
      // Remove da lista localmente
      setState(prev => ({
        ...prev,
        cycles: prev.cycles.filter(c => c.id !== id),
      }));
      return true;
    } catch (err) {
      console.error('Error deleting cycle:', err);
      return false;
    }
  }, []);

  return {
    cycles: state.cycles,
    isLoading: state.isLoading,
    error: state.error,
    fetchCycles,
    refetch,
    createCycle,
    updateCycle,
    deleteCycle,
    currentFilters,
  };
}

// ============================================================================
// HOOK: useCycleDetail (Detalhe)
// ============================================================================

/**
 * Hook para detalhes de um ciclo específico
 * 
 * @param cycleId - ID do ciclo
 * @param autoFetch - Se deve buscar automaticamente (default: true)
 * 
 * @example
 * const { cycle, isLoading, updateCycle } = useCycleDetail('uuid');
 */
export function useCycleDetail(
  cycleId: string,
  autoFetch: boolean = true
): UseCycleDetailReturn {
  const [state, setState] = useState<UseCycleDetailState>({
    cycle: null,
    isLoading: autoFetch,
    error: null,
  });

  const fetchCycle = useCallback(async () => {
    if (!cycleId) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await cyclesApi.getTrainingCycleApiV1TrainingCyclesCycleIdGet(cycleId).then(r => r.data as unknown as TrainingCycleWithMicrocycles);
      setState({
        cycle: data,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar ciclo';
      setState({
        cycle: null,
        isLoading: false,
        error: errorMessage,
      });
      console.error('Error fetching cycle:', err);
    }
  }, [cycleId]);

  const refetch = useCallback(async () => {
    await fetchCycle();
  }, [fetchCycle]);

  const updateCycle = useCallback(async (data: any): Promise<TrainingCycleWithMicrocycles | null> => {
    try {
      const updated = await cyclesApi.updateTrainingCycleApiV1TrainingCyclesCycleIdPatch(cycleId, data as any).then(r => r.data as unknown as TrainingCycleWithMicrocycles);
      // Atualiza estado local com dados atualizados
      setState(prev => ({
        ...prev,
        cycle: prev.cycle ? { ...prev.cycle, ...updated } : null,
      }));
      return updated as TrainingCycleWithMicrocycles;
    } catch (err) {
      console.error('Error updating cycle:', err);
      return null;
    }
  }, [cycleId]);

  const deleteCycle = useCallback(async (reason: string): Promise<boolean> => {
    try {
      await cyclesApi.deleteTrainingCycleApiV1TrainingCyclesCycleIdDelete(cycleId, reason).then(r => r.data);
      setState(prev => ({ ...prev, cycle: null }));
      return true;
    } catch (err) {
      console.error('Error deleting cycle:', err);
      return false;
    }
  }, [cycleId]);

  // Auto-fetch ao montar (se habilitado)
  useEffect(() => {
    if (autoFetch && cycleId) {
      const fetch = () => fetchCycle();
      fetch();
    }
  }, [autoFetch, cycleId, fetchCycle]);

  return {
    cycle: state.cycle,
    isLoading: state.isLoading,
    error: state.error,
    fetchCycle,
    refetch,
    updateCycle,
    deleteCycle,
  };
}

// ============================================================================
// HOOK: useActiveCycles (Ciclos Ativos)
// ============================================================================

/**
 * Hook para buscar ciclos ativos de uma equipe
 * 
 * @param teamId - ID da equipe
 * 
 * @example
 * const { activeCycles, isLoading } = useActiveCycles('team-uuid');
 */
export function useActiveCycles(teamId: string | undefined) {
  const [activeCycles, setActiveCycles] = useState<TrainingCycle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActiveCycles = useCallback(async () => {
    if (!teamId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await cyclesApi.getActiveCyclesApiV1TrainingCyclesTeamsTeamIdActiveGet(teamId).then(r => r.data as unknown as TrainingCycle[]);
      setActiveCycles(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar ciclos ativos';
      setError(errorMessage);
      console.error('Error fetching active cycles:', err);
    } finally {
      setIsLoading(false);
    }
  }, [teamId]);

  useEffect(() => {
    fetchActiveCycles();
  }, [fetchActiveCycles]);

  return {
    activeCycles,
    isLoading,
    error,
    refetch: fetchActiveCycles,
  };
}
