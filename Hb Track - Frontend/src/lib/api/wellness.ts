/**
 * API: Wellness Pre/Post
 * 
 * Gerenciamento de wellness reports com:
 * - Permissões duplas (atleta self-only + staff read-all)
 * - Janelas temporais de edição
 * - Validação de deadlines
 * - Histórico e tendências
 */

import { apiClient } from './client';

/**
 * Wellness Pre (Pré-Treino)
 */
export interface WellnessPre {
  id: string;
  training_session_id: string;
  athlete_id: string;
  
  // Métricas
  sleep_hours: number;         // 0..24, 1 decimal
  sleep_quality: number;       // 1..5
  fatigue_pre: number;         // 0..10
  stress_level: number;        // 0..10
  muscle_soreness: number;     // 0..10
  readiness_score?: number;    // 0..10 (opcional)
  menstrual_cycle_phase?: string; // enum opcional
  
  // Metadados
  notes?: string;
  filled_at: string;
  locked_at?: string;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  
  // Relacionamentos
  session?: {
    id: string;
    session_at: string;
    session_type: string;
    duration_planned_minutes?: number;
  };
}

/**
 * Wellness Post (Pós-Treino)
 */
export interface WellnessPost {
  id: string;
  training_session_id: string;
  athlete_id: string;
  
  // Métricas (0-10)
  session_rpe: number; // Rating of Perceived Exertion
  fatigue_after: number;
  mood_after: number;
  muscle_soreness_after: number;
  
  // Calculado automaticamente (trigger)
  internal_load?: number;
  minutes_effective?: number;
  
  // Metadados
  notes?: string;
  filled_at: string;
  locked_at?: string;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  
  // Relacionamentos
  session?: {
    id: string;
    session_at: string;
    session_type: string;
    duration_planned_minutes?: number;
  };
}

/**
 * Wellness Pre Input
 */
export interface WellnessPreInput {
  sleep_hours: number;         // 0..24, 1 decimal (NOT NULL no DB)
  sleep_quality: number;       // 1..5
  fatigue_pre: number;         // 0..10
  stress_level: number;        // 0..10
  muscle_soreness: number;     // 0..10
  readiness_score?: number;    // 0..10 (opcional)
  menstrual_cycle_phase?: string; // enum opcional
  notes?: string;
}

/**
 * Wellness Post Input
 */
export interface WellnessPostInput {
  session_rpe: number;
  fatigue_after: number;
  mood_after: number;
  muscle_soreness_after: number;
  minutes_effective?: number;
  notes?: string;
}

/**
 * Session Wellness Status
 */
export interface SessionWellnessStatus {
  session_id: string;
  total_athletes: number;
  responded_pre: number;
  responded_post: number;
  pending_pre: string[]; // athlete_ids
  pending_post: string[]; // athlete_ids
  response_rate_pre: number; // percentage
  response_rate_post: number; // percentage
}

/**
 * Athlete Wellness Summary
 */
export interface AthleteWellnessSummary {
  athlete_id: string;
  period_days: number;
  
  // Pre averages
  avg_sleep_quality: number;
  avg_fatigue_pre: number;
  avg_stress_level: number;
  avg_muscle_soreness: number;
  avg_mood_score: number;
  avg_readiness_score: number;
  
  // Post averages
  avg_session_rpe: number;
  avg_internal_load: number;
  
  // Response rate
  total_sessions: number;
  responded_pre: number;
  responded_post: number;
  response_rate: number; // percentage
  
  // Critical patterns
  high_fatigue_days: number; // >= 8
  high_stress_days: number; // >= 8
  low_readiness_days: number; // <= 3
}

/**
 * Wellness Preset
 */
export interface WellnessPreset {
  id: string;
  label: string;
  emoji: string;
  description: string;
  values: Partial<WellnessPreInput>;
}

/**
 * Deadline Info
 */
export interface DeadlineInfo {
  deadline: string; // ISO datetime
  remaining_minutes: number;
  is_expired: boolean;
  can_edit: boolean;
}

/**
 * API Functions - Wellness Pre
 */

/**
 * Submete wellness pré-treino
 * Endpoint: POST /wellness-pre/training_sessions/{sessionId}/wellness_pre
 * Permissão: Atleta (self-only)
 */
export async function submitWellnessPre(
  sessionId: string,
  data: WellnessPreInput
): Promise<WellnessPre> {
  return await apiClient.post<WellnessPre>(
    `/wellness-pre/training_sessions/${sessionId}/wellness_pre`,
    { ...data }
  );
}

/**
 * Busca wellness pre existente do atleta
 * Endpoint: GET /wellness-pre/training_sessions/{sessionId}/wellness_pre
 * Backend infere athlete_id do JWT (DEC-TRAIN-001)
 */
export async function getMyWellnessPre(sessionId: string): Promise<WellnessPre | null> {
  try {
    const response = await apiClient.get<WellnessPre[]>(
      `/wellness-pre/training_sessions/${sessionId}/wellness_pre`
    );
    return response[0] || null;
  } catch (error) {
    return null;
  }
}

/**
 * Busca status de wellness de uma sessão
 * Endpoint: GET /wellness_pre/sessions/{session_id}/status
 * Permissão: Staff (todos do team)
 */
export async function getSessionWellnessStatus(
  sessionId: string
): Promise<SessionWellnessStatus> {
  return await apiClient.get<SessionWellnessStatus>(
    `/wellness_pre/sessions/${sessionId}/status`
  );
}

/**
 * Busca histórico wellness do atleta
 * Endpoint: GET /athletes/me/wellness-summary?days={days}
 */
export async function getMyWellnessSummary(days: number = 28): Promise<AthleteWellnessSummary> {
  return await apiClient.get<AthleteWellnessSummary>(
    `/athletes/me/wellness-summary`,
    {
      params: { days },
    }
  );
}

/**
 * Calcula informações de deadline
 */
export function calculateDeadline(sessionAt: string): DeadlineInfo {
  const sessionDate = new Date(sessionAt);
  const deadline = new Date(sessionDate.getTime() - 2 * 60 * 60 * 1000); // 2h antes
  const now = new Date();
  const remaining_minutes = Math.floor((deadline.getTime() - now.getTime()) / (1000 * 60));
  
  return {
    deadline: deadline.toISOString(),
    remaining_minutes,
    is_expired: remaining_minutes <= 0,
    can_edit: remaining_minutes > 0,
  };
}

/**
 * API Functions - Wellness Post
 */

/**
 * Submete wellness pós-treino
 * Endpoint: POST /wellness-post/training_sessions/{sessionId}/wellness_post
 * Permissão: Atleta (self-only)
 */
export async function submitWellnessPost(
  sessionId: string,
  data: WellnessPostInput
): Promise<WellnessPost> {
  return await apiClient.post<WellnessPost>(
    `/wellness-post/training_sessions/${sessionId}/wellness_post`,
    { ...data }
  );
}

/**
 * Busca wellness post existente do atleta
 * Endpoint: GET /wellness-post/training_sessions/{sessionId}/wellness_post
 * Backend infere athlete_id do JWT (DEC-TRAIN-001)
 */
export async function getMyWellnessPost(sessionId: string): Promise<WellnessPost | null> {
  try {
    const response = await apiClient.get<WellnessPost[]>(
      `/wellness-post/training_sessions/${sessionId}/wellness_post`
    );
    return response[0] || null;
  } catch (error) {
    return null;
  }
}

/**
 * Solicita desbloqueio de wellness (após deadline)
 * Endpoint: POST /wellness_pre/{id}/request-unlock
 */
export async function requestWellnessUnlock(
  wellnessId: string,
  reason: string
): Promise<void> {
  await apiClient.post(`/wellness_pre/${wellnessId}/request-unlock`, { reason });
}

/**
 * Presets pré-configurados
 */
export const WELLNESS_PRE_PRESETS: WellnessPreset[] = [
  {
    id: 'very-rested',
    label: 'Muito Bem Descansado',
    emoji: '💪',
    description: 'Dormiu muito bem, sem fadiga, pronto para treinar',
    values: {
      sleep_hours: 8.0,
      sleep_quality: 5,
      fatigue_pre: 2,
      stress_level: 2,
      muscle_soreness: 1,
      readiness_score: 9,
    },
  },
  {
    id: 'normal',
    label: 'Normal',
    emoji: '😊',
    description: 'Estado normal de treino, sem problemas',
    values: {
      sleep_hours: 7.0,
      sleep_quality: 3,
      fatigue_pre: 5,
      stress_level: 4,
      muscle_soreness: 4,
      readiness_score: 7,
    },
  },
  {
    id: 'tired',
    label: 'Cansado',
    emoji: '😓',
    description: 'Pouco descanso, fadiga moderada',
    values: {
      sleep_hours: 6.0,
      sleep_quality: 2,
      fatigue_pre: 7,
      stress_level: 6,
      muscle_soreness: 6,
      readiness_score: 4,
    },
  },
  {
    id: 'very-tired',
    label: 'Muito Cansado',
    emoji: '😴',
    description: 'Muito fatigado, considere treino leve',
    values: {
      sleep_hours: 5.0,
      sleep_quality: 1,
      fatigue_pre: 9,
      stress_level: 8,
      muscle_soreness: 8,
      readiness_score: 2,
    },
  },
];
