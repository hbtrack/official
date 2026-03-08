/**
 * ExerciseACLModal — AR_184
 *
 * Modal para gerenciar ACL (Access Control List) de exercícios restricted.
 * Apenas o criador do exercício pode ver e modificar a ACL.
 *
 * Endpoints utilizados:
 * - GET /exercises/{id}/acl — listar usuários com acesso
 * - POST /exercises/{id}/acl — adicionar usuário
 * - DELETE /exercises/{id}/acl/{user_id} — remover usuário
 */

'use client';

import { exercisesApi } from '@/api/generated/api-instance';
import type { ExerciseACLEntry } from '@/lib/api/exercises';
import { useEffect, useState } from 'react';

interface ExerciseACLModalProps {
  exerciseId: string;
  exerciseName: string;
  isOpen: boolean;
  onClose: () => void;
}

export function ExerciseACLModal({
  exerciseId,
  exerciseName,
  isOpen,
  onClose,
}: ExerciseACLModalProps) {
  const [aclEntries, setAclEntries] = useState<ExerciseACLEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newUserId, setNewUserId] = useState('');
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchACL();
    }
  }, [isOpen, exerciseId]);

  async function fetchACL() {
    setLoading(true);
    setError(null);
    try {
      const resp = await exercisesApi.listExerciseAclApiV1ExercisesExerciseIdAclGet(exerciseId);
      setAclEntries(resp.data as unknown as ExerciseACLEntry[]);
    } catch {
      setError('Erro ao carregar lista de acesso.');
    } finally {
      setLoading(false);
    }
  }

  async function handleAddUser() {
    if (!newUserId.trim()) return;
    setAdding(true);
    setError(null);
    try {
      const resp = await exercisesApi.grantExerciseAclApiV1ExercisesExerciseIdAclPost(exerciseId, { user_id: newUserId.trim() } as any);
      setAclEntries((prev) => [...prev, resp.data as unknown as ExerciseACLEntry]);
      setNewUserId('');
    } catch {
      setError('Erro ao adicionar usuário. Verifique o ID e tente novamente.');
    } finally {
      setAdding(false);
    }
  }

  async function handleRemoveUser(userId: string) {
    setError(null);
    try {
      await exercisesApi.revokeExerciseAclApiV1ExercisesExerciseIdAclUserIdDelete(exerciseId, userId);
      setAclEntries((prev) => prev.filter((e) => e.user_id !== userId));
    } catch {
      setError('Erro ao remover usuário.');
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Gerenciar Acesso
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-[280px]">
              {exerciseName}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100
              dark:hover:text-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Fechar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4 space-y-4">
          {error && (
            <div className="p-3 rounded-md bg-red-50 text-red-700 text-sm dark:bg-red-900/20 dark:text-red-400">
              {error}
            </div>
          )}

          {/* Add user */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Adicionar usuário (ID)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newUserId}
                onChange={(e) => setNewUserId(e.target.value)}
                placeholder="UUID do usuário"
                className="flex-1 px-3 py-2 text-sm rounded-md border border-gray-300 dark:border-gray-600
                  bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                  focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={handleAddUser}
                disabled={adding || !newUserId.trim()}
                className="px-4 py-2 text-sm font-medium rounded-md
                  bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50
                  transition-colors"
              >
                {adding ? 'Adicionando...' : 'Adicionar'}
              </button>
            </div>
          </div>

          {/* ACL list */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Usuários com acesso ({aclEntries.length})
            </h3>
            {loading ? (
              <p className="text-sm text-gray-500 py-4 text-center">Carregando...</p>
            ) : aclEntries.length === 0 ? (
              <p className="text-sm text-gray-400 py-4 text-center">
                Nenhum usuário com acesso (além do criador).
              </p>
            ) : (
              <ul className="space-y-2 max-h-48 overflow-y-auto">
                {aclEntries.map((entry) => (
                  <li
                    key={entry.id}
                    className="flex items-center justify-between p-2 rounded-md
                      bg-gray-50 dark:bg-gray-700/50"
                  >
                    <span className="text-xs text-gray-700 dark:text-gray-300 font-mono truncate max-w-[260px]">
                      {entry.user_id}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleRemoveUser(entry.user_id)}
                      className="ml-2 p-1 rounded text-red-400 hover:text-red-600 hover:bg-red-50
                        dark:hover:bg-red-900/20 transition-colors flex-shrink-0"
                      aria-label="Remover acesso"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium rounded-md
              bg-gray-100 text-gray-700 hover:bg-gray-200
              dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600
              transition-colors"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
