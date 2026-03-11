/**
 * SCREEN-TRAIN-020 — Cockpit/Detalhe da Sessão
 *
 * Exibe o ledger de uma sessão de treino com três seções canônicas:
 *  - Planned (plano original, imutável após schedule)
 *  - Realized (execução real — presenças e exercícios realizados)
 *  - Adjustments (ajustes pós-sessão, append-only)
 *
 * AR_275: data-test-ids obrigatórios por AR-TRAIN-REC-04.
 * Sem botões para transições automáticas (scheduled→in_progress, in_progress→pending_review).
 */

import Link from 'next/link';

interface SessionDetailPageProps {
  params: { id: string };
}

export default function SessionDetailPage({ params }: SessionDetailPageProps) {
  return (
    <main className="space-y-6 p-6">
      {/* Seção Planned: plano original da sessão */}
      <section
        data-test-id="training-session-planned-section"
        className="rounded-lg border bg-card p-4"
      >
        <h2 className="mb-2 text-lg font-semibold">Planejado</h2>
        <p className="text-sm text-muted-foreground">
          Plano original da sessão (exercícios, focos, metas). Imutável após agendamento.
        </p>
      </section>

      {/* Seção Realized: execução real */}
      <section
        data-test-id="training-session-realized-section"
        className="rounded-lg border bg-card p-4"
      >
        <h2 className="mb-2 text-lg font-semibold">Realizado</h2>
        <p className="text-sm text-muted-foreground">
          Execução real da sessão: presenças e exercícios realizados.
        </p>
      </section>

      {/* Seção Adjustments: ajustes pós-sessão (append-only) */}
      <section
        data-test-id="training-session-adjustments-section"
        className="rounded-lg border bg-card p-4"
      >
        <h2 className="mb-2 text-lg font-semibold">Ajustes</h2>
        <p className="text-sm text-muted-foreground">
          Ajustes pós-sessão (append-only, imutáveis após registro).
        </p>
      </section>

      <div className="flex gap-2">
        <Link
          href={`/training/sessions/${params.id}/edit`}
          className="text-sm text-primary underline-offset-4 hover:underline"
        >
          Editar sessão
        </Link>
      </div>
    </main>
  );
}
