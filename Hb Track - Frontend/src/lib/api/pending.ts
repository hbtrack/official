/**
 * API Layer — Training Pending Items
 *
 * AR_186 (AR-TRAIN-018): UI fila de pendências de sessão de treino
 *
 * Invariantes:
 * - INV-TRAIN-066: atleta pode enviar justificativa mas NÃO pode resolver/fechar item
 * - INV-TRAIN-067: treinador tem autoridade final de resolução
 *
 * Endpoints (base /api/v1):
 *   GET  /attendance/sessions/{sessionId}/pending-items            → listPendingItems
 *   POST /attendance/pending-items/{itemId}/resolve                → resolvePendingItem  (TREINADOR)
 *   POST /attendance/pending-items/{itemId}/athlete-justification  → addAthleteJustification (ATLETA)
 */

import { apiClient } from './client';

// ==================== TYPES ====================

export type PendingItemStatus = 'open' | 'resolved' | 'cancelled';
export type PendingItemType = 'equipment' | 'material' | 'admin' | 'other';

export interface PendingItem {
  id: string;
  training_session_id: string;
  athlete_id: string;
  item_type: PendingItemType;
  description: string | null;
  status: PendingItemStatus;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  resolved_by_user_id: string | null;
}

/** Payload para resolução pelo treinador (INV-TRAIN-067) */
export interface ResolveItemInput {
  new_presence_status: string;
  justification: string;
}

/** Payload para justificativa do atleta (INV-TRAIN-066 — sem poder de resolução) */
export interface AthleteJustificationInput {
  message: string;
}

// ==================== API FUNCTIONS ====================

/**
 * Lista pending items de uma sessão.
 * Filtro por sessão opcional — sem sessionId lista todos (paginado no futuro).
 * RBAC no backend: treinador vê todos; atleta vê apenas os próprios (INV-TRAIN-066).
 */
export async function listPendingItems(sessionId?: string): Promise<PendingItem[]> {
  if (sessionId) {
    return await apiClient.get<PendingItem[]>(
      `/attendance/sessions/${sessionId}/pending-items`
    );
  }
  // Sem sessionId: retorna lista vazia (endpoint requer session_id)
  return [];
}

/**
 * Treinador resolve um pending item: altera presence_status + adiciona justificativa.
 * INV-TRAIN-067: apenas treinador pode resolver.
 */
export async function resolvePendingItem(
  itemId: string,
  data: ResolveItemInput
): Promise<PendingItem> {
  return await apiClient.post<PendingItem>(
    `/attendance/pending-items/${itemId}/resolve`,
    data
  );
}

/**
 * Atleta adiciona justificativa a um pending item.
 * INV-TRAIN-066: atleta pode justificar mas NÃO pode resolver/fechar.
 */
export async function addAthleteJustification(
  itemId: string,
  data: AthleteJustificationInput
): Promise<{ ok: boolean }> {
  return await apiClient.post<{ ok: boolean }>(
    `/attendance/pending-items/${itemId}/athlete-justification`,
    data
  );
}
