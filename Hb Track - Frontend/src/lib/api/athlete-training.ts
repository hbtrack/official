/**
 * API Layer — Athlete Training Preview
 *
 * AR_187 (AR-TRAIN-019): Visão pré-treino do atleta com gate de wellness
 *
 * Invariantes:
 * - INV-TRAIN-068: atleta pode ver treino antes de iniciar
 * - INV-TRAIN-069: mídia acessível ao atleta
 * - INV-TRAIN-071: wellness missing bloqueia conteúdo completo
 */

import { apiClient } from './client';

// ==================== TYPES ====================

export interface TrainingExercisePreview {
  id: string;
  name: string;
  description: string | null;
  media_url: string | null;
}

export interface TrainingPreview {
  session_id: string;
  name: string | null;
  scheduled_date: string | null;
  status: string;
  /** INV-TRAIN-071: true quando wellness do dia não está preenchido */
  wellness_blocked: boolean;
  /** Mensagem informativa quando wellness_blocked=true */
  message?: string;
  /** Lista de exercícios — vazia quando wellness_blocked=true */
  exercises: TrainingExercisePreview[];
}

// ==================== API FUNCTIONS ====================

/**
 * Busca a pré-visualização do treino para o atleta autenticado.
 *
 * - Se wellness_blocked=true: retorna info mínima (nome, horário, flag)
 * - Se wellness_blocked=false: retorna exercícios completos + mídia
 *
 * INV-TRAIN-071: acesso a conteúdo completo exige wellness preenchido.
 */
export async function getTrainingPreview(sessionId: string): Promise<TrainingPreview> {
  return await apiClient.get<TrainingPreview>(
    `/athlete/training-sessions/${sessionId}/preview`
  );
}
