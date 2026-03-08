/**
 * ExerciseVisibilityToggle — AR_184
 *
 * Toggle para alternar visibility_mode entre org_wide e restricted.
 * Chama PATCH /exercises/{id}/visibility.
 * Visível apenas para o criador do exercício.
 */

'use client';

import { exercisesApi } from '@/api/generated/api-instance';
import type { VisibilityMode } from '@/lib/api/exercises';
import { useState } from 'react';

interface ExerciseVisibilityToggleProps {
  exerciseId: string;
  currentVisibility: VisibilityMode;
  onVisibilityChanged?: (newVisibility: VisibilityMode) => void;
}

export function ExerciseVisibilityToggle({
  exerciseId,
  currentVisibility,
  onVisibilityChanged,
}: ExerciseVisibilityToggleProps) {
  const [visibility, setVisibility] = useState<VisibilityMode>(currentVisibility);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleToggle() {
    const newVisibility: VisibilityMode =
      visibility === 'org_wide' ? 'restricted' : 'org_wide';
    setLoading(true);
    setError(null);
    try {
      await exercisesApi.updateExerciseVisibilityApiV1ExercisesExerciseIdVisibilityPatch(exerciseId, { visibility_mode: newVisibility });
      setVisibility(newVisibility);
      onVisibilityChanged?.(newVisibility);
    } catch {
      setError('Erro ao alterar visibilidade.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-1">
      <button
        type="button"
        onClick={handleToggle}
        disabled={loading}
        className={`
          inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md
          transition-colors disabled:opacity-50
          ${visibility === 'org_wide'
            ? 'bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400 dark:hover:bg-green-900/40'
            : 'bg-amber-50 text-amber-700 hover:bg-amber-100 dark:bg-amber-900/20 dark:text-amber-400 dark:hover:bg-amber-900/40'
          }
        `}
        aria-label={`Visibilidade: ${visibility === 'org_wide' ? 'Todos da organização' : 'Restrito'}`}
      >
        <span>{visibility === 'org_wide' ? '🔓' : '🔒'}</span>
        <span>
          {loading
            ? 'Alterando...'
            : visibility === 'org_wide'
            ? 'Visível para Todos'
            : 'Restrito'}
        </span>
      </button>
      {error && (
        <p className="text-xs text-red-500 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}
