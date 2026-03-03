'use client';

/**
 * SCREEN-TRAIN-025: Modal de revisão de rascunho gerado pela IA para o treinador.
 *
 * AR_192 — AR-TRAIN-021
 *
 * INV-080: Toda proposta da IA chega como draft — treinador DEVE aprovar.
 * INV-081: Justificativa exibida de forma proeminente; sem ela = 'Ideia Genérica'.
 */

import React from 'react';

// Tipos (CONTRACT-TRAIN-101..104)
export interface TrainingSessionDraft {
  title: string;
  status: 'draft';                     // INV-080: SEMPRE 'draft'
  source: 'ai_coach_suggestion';       // INV-080: SEMPRE este valor
  requires_coach_approval: true;       // INV-080: SEMPRE true
  justification: string;               // INV-081: obrigatório para 'recomendacao'
  label: 'recomendacao' | 'ideia_generica';  // INV-081
  context_summary?: string;
}

export interface MicrocycleDraft {
  title: string;
  week_focus: string;
  status: 'draft';
  source: 'ai_coach_suggestion';
  requires_coach_approval: true;
  justification: string;
  label: 'recomendacao' | 'ideia_generica';
}

export type AIDraft = TrainingSessionDraft | MicrocycleDraft;

interface AICoachDraftModalProps {
  draft: AIDraft;
  onApprove: (draft: AIDraft) => void;
  onReject: (draft: AIDraft) => void;
  onEdit: (draft: AIDraft) => void;
  onClose: () => void;
}

/**
 * Modal de revisão de draft gerado pela IA Coach.
 *
 * Exibe a justificativa da IA de forma proeminente (INV-081).
 * Badge "Aprovação Necessária" sempre visível (INV-080).
 */
export function AICoachDraftModal({
  draft,
  onApprove,
  onReject,
  onEdit,
  onClose,
}: AICoachDraftModalProps) {
  const isIdeia = draft.label === 'ideia_generica';

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="draft-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 id="draft-modal-title" className="text-lg font-bold text-gray-900">
            Revisão de Rascunho IA
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
            aria-label="Fechar modal"
          >
            ×
          </button>
        </div>

        {/* Badge "Aprovação Necessária" (INV-080) */}
        <div className="flex items-center gap-2">
          <span className="inline-block rounded-full bg-yellow-100 px-3 py-1 text-xs font-semibold text-yellow-800 border border-yellow-300">
            ⚠ Aprovação Necessária
          </span>
          {/* Badge label INV-081 */}
          <span
            className={`inline-block rounded-full px-3 py-1 text-xs font-semibold border ${
              isIdeia
                ? 'bg-gray-100 text-gray-600 border-gray-300'
                : 'bg-green-100 text-green-700 border-green-300'
            }`}
          >
            {isIdeia ? 'Ideia Genérica' : 'Recomendação'}
          </span>
        </div>

        {/* Título do draft */}
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Título</p>
          <p className="font-semibold text-gray-800">{draft.title}</p>
        </div>

        {/* Foco da semana (se microciclo) */}
        {'week_focus' in draft && (
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Foco da Semana</p>
            <p className="text-gray-700">{draft.week_focus}</p>
          </div>
        )}

        {/* Justificativa da IA — proeminente (INV-081) */}
        <div
          className={`rounded-lg p-3 ${
            isIdeia
              ? 'bg-gray-50 border border-gray-200'
              : 'bg-blue-50 border border-blue-200'
          }`}
        >
          <p className="text-xs font-semibold uppercase tracking-wide mb-1 text-gray-500">
            Justificativa da IA {isIdeia && '(ausente — ideia genérica)'}
          </p>
          {draft.justification ? (
            <p className="text-sm text-gray-700">{draft.justification}</p>
          ) : (
            <p className="text-sm text-gray-400 italic">
              Nenhuma justificativa fornecida. Esta sugestão é classificada como
              &ldquo;Ideia Genérica&rdquo; — não é uma recomendação baseada em dados.
            </p>
          )}
        </div>

        {/* Aviso INV-080 */}
        <p className="text-xs text-gray-400">
          Esta proposta foi gerada pela IA Coach e nunca é publicada automaticamente.
          Você decide se aprova, edita ou rejeita.
        </p>

        {/* Ações */}
        <div className="flex gap-3 pt-2">
          <button
            onClick={() => onApprove(draft)}
            className="flex-1 rounded-lg bg-green-600 py-2 text-sm font-semibold text-white hover:bg-green-700"
          >
            Aprovar
          </button>
          <button
            onClick={() => onEdit(draft)}
            className="flex-1 rounded-lg border border-blue-600 py-2 text-sm font-semibold text-blue-600 hover:bg-blue-50"
          >
            Editar
          </button>
          <button
            onClick={() => onReject(draft)}
            className="flex-1 rounded-lg border border-red-300 py-2 text-sm font-semibold text-red-600 hover:bg-red-50"
          >
            Rejeitar
          </button>
        </div>
      </div>
    </div>
  );
}

export default AICoachDraftModal;
