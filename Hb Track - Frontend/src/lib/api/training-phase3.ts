/**
 * API Layer — Training FASE_3 stubs
 *
 * AR_236 (AR-TRAIN-052) — Frontend Hard Sync v1.3.0
 *
 * Stubs tipados para os endpoints da FASE_3 (CONTRACT-TRAIN-096..105).
 * AVISO: estas funções são stubs não-implementados. Não devem ser chamadas
 * em produção sem o Backend real correspondente.
 *
 * CONTRACT-099/100 DIVERGÊNCIA (documentada em Análise de Impacto AR_236):
 * pending.ts usa /attendance/sessions/{id}/pending-items e
 * /attendance/pending-items/{id}/resolve (AR_186). O CONTRACT define
 * /training/pending-items e PATCH /training/pending-items/{id}/resolve.
 * Re-exportando aliases de pending.ts (write_scope não inclui pending.ts).
 */

import { apiClient } from './client';
import {
    listPendingItems as _listPendingItems,
    resolvePendingItem as _resolvePendingItem,
    PendingItem,
    ResolveItemInput,
} from './pending';

// ==================== INTERFACES FASE_3 ====================

/** Prévia de uma sessão de treino para o atleta (CONTRACT-TRAIN-096) */
export interface AthleteSessionPreview {
    session_id: string;
    session_at: string;           // ISO 8601 datetime
    session_type: string;
    main_objective?: string;
    location?: string;
    team_name?: string;
    exercises_count?: number;
    duration_planned_minutes?: number;
    attendance_status?: string;   // 'confirmed' | 'pending' | 'absent'
}

/** Input para fechamento de sessão com presença (CONTRACT-TRAIN-098) */
export interface CloseSessionInput {
    execution_outcome: string;             // e.g. 'completed' | 'cancelled'
    delay_minutes?: number;
    duration_actual_minutes?: number;
    cancellation_reason?: string;
    deviation_justification?: string;
    presence_records: Array<{
        athlete_id: string;
        status: string;               // 'present' | 'absent' | 'justified'
        justification?: string;
    }>;
}

/** Item pendente de sessão (re-exportado de pending.ts) */
export type { PendingItem };

// ==================== STUBS FASE_3 ====================

/**
 * CONTRACT-TRAIN-096
 * Obtém prévia da sessão de treino para o atleta.
 * GET /api/v1/athlete/training-sessions/{session_id}/preview
 */
export async function getAthleteSessionPreview(
    sessionId: string
): Promise<AthleteSessionPreview> {
    return await apiClient.get<AthleteSessionPreview>(
        `/athlete/training-sessions/${sessionId}/preview`
    );
}

/**
 * CONTRACT-TRAIN-097
 * Pré-confirma presença do atleta em uma sessão.
 * POST /api/v1/attendance/sessions/{session_id}/preconfirm
 * AR_242: corrigido — URL errada sem /attendance/ e sem hifen (veja openapi.json)
 */
export async function preConfirmAttendance(
    sessionId: string,
    athleteId?: string
): Promise<{ status: string; is_official: boolean }> {
    const body = athleteId ? { athlete_id: athleteId } : {};
    return await apiClient.post<{ status: string; is_official: boolean }>(
        `/attendance/sessions/${sessionId}/preconfirm`,
        body
    );
}

/**
 * CONTRACT-TRAIN-098
 * Fecha a sessão registrando presença e dados de execução.
 * POST /api/v1/training-sessions/{session_id}/close
 */
export async function closeSessionWithAttendance(
    sessionId: string,
    data: CloseSessionInput
): Promise<{ closed: boolean; pending_items: PendingItem[] }> {
    return await apiClient.post<{ closed: boolean; pending_items: PendingItem[] }>(
        `/training-sessions/${sessionId}/close`,
        data
    );
}

/**
 * CONTRACT-TRAIN-099 — Alias de pending.ts (listPendingItems)
 * GET /attendance/sessions/{sessionId}/pending-items
 * NOTA: pendente.ts usa /attendance/sessions/{id}/pending-items;
 * CONTRACT define /training/pending-items. Divergência documentada (AR_236).
 */
export const getPendingItems = _listPendingItems;

/**
 * CONTRACT-TRAIN-100 — Alias de pending.ts (resolvePendingItem)
 * POST /attendance/pending-items/{itemId}/resolve
 * NOTA: divergência de URL documentada (AR_236).
 */
export const resolveTrainingPendingItem: (
    itemId: string,
    data: ResolveItemInput
) => Promise<PendingItem> = _resolvePendingItem;

/**
 * CONTRACT-TRAIN-101
 * Solicita à IA Coach um rascunho de sessão de treino.
 * POST /api/v1/ai/coach/suggest-session
 * AR_242: corrigido de URL errada (prefixo ai-coach → ai/coach)
 */
export async function aiDraftSession(
    teamId: string,
    context: object
): Promise<{ draft_id: string; suggested_session: object; justification: string }> {
    return await apiClient.post<{
        draft_id: string;
        suggested_session: object;
        justification: string;
    }>('/ai/coach/suggest-session', { team_id: teamId, context });
}

/**
 * CONTRACT-TRAIN-102
 * Aplica o rascunho da IA Coach (com possíveis edições do treinador).
 * PATCH /api/v1/ai/coach/draft/{draft_id}/apply
 * AR_242: corrigido de URL errada c/ prefixo ai-coach → ai/coach/draft
 */
export async function applyAIDraft(
    draftId: string,
    edits?: object
): Promise<{ training_session_id: string; applied: boolean }> {
    const body = edits ? { edits } : {};
    return await apiClient.patch<{ training_session_id: string; applied: boolean }>(
        `/ai/coach/draft/${draftId}/apply`,
        body
    );
}

/**
 * CONTRACT-TRAIN-103
 * Chat da IA Coach com o atleta.
 * POST /api/v1/ai/chat
 * AR_242: corrigido de URL errada (prefixo ai-coach → ai/chat)
 */
export async function aiAthleteChat(
    sessionId: string,
    message: string
): Promise<{ response: string; type: string }> {
    return await apiClient.post<{ response: string; type: string }>(
        '/ai/chat',
        { session_id: sessionId, message }
    );
}

/**
 * CONTRACT-TRAIN-104
 * Solicita justificativa da IA para uma sugestão.
 * POST /api/v1/ai/coach/justify-suggestion
 * AR_242: corrigido de URL errada (prefixo ai-coach → ai/coach)
 */
export async function aiJustifySuggestion(
    suggestionId: string
): Promise<{ justification: string; references: string[] }> {
    return await apiClient.post<{ justification: string; references: string[] }>(
        '/ai/coach/justify-suggestion',
        { suggestion_id: suggestionId }
    );
}

/**
 * CONTRACT-TRAIN-105
 * Verifica se o atleta tem acesso ao conteúdo completo da sessão (wellness gate).
 * GET /api/v1/athlete/wellness-content-gate/{session_id}
 */
export async function checkWellnessContentGate(
    sessionId: string
): Promise<{ has_wellness: boolean; can_see_full_content: boolean; blocked_reason?: string }> {
    return await apiClient.get<{
        has_wellness: boolean;
        can_see_full_content: boolean;
        blocked_reason?: string;
    }>(`/athlete/wellness-content-gate/${sessionId}`);
}
