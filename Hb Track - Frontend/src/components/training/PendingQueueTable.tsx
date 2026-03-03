'use client';

/**
 * Componente: PendingQueueTable
 *
 * AR_186 (AR-TRAIN-018) — Tabela de pending items da sessão de treino
 *
 * Invariantes:
 * - INV-TRAIN-066: atleta justifica, treinador resolve
 * - INV-TRAIN-067: treinador é autoridade final de resolução
 */

import React, { useState } from 'react';
import { resolvePendingItem, type PendingItem, type ResolveItemInput } from '@/lib/api/pending';

interface PendingQueueTableProps {
  items: PendingItem[];
  onResolved?: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  open: 'Aberto',
  resolved: 'Resolvido',
  cancelled: 'Cancelado',
};

const STATUS_COLOR: Record<string, string> = {
  open: 'text-yellow-600',
  resolved: 'text-green-600',
  cancelled: 'text-gray-400',
};

export function PendingQueueTable({ items, onResolved }: PendingQueueTableProps) {
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, ResolveItemInput>>({});
  const [error, setError] = useState<string | null>(null);

  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">Nenhum item pendente nesta sessão.</p>;
  }

  const handleResolve = async (itemId: string) => {
    const data = form[itemId];
    if (!data?.new_presence_status || !data?.justification) {
      setError(`Preencha status e justificativa para o item ${itemId}`);
      return;
    }
    setError(null);
    setResolvingId(itemId);
    try {
      await resolvePendingItem(itemId, data);
      onResolved?.();
    } catch (err) {
      setError('Erro ao resolver item. Tente novamente.');
      console.error(err);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div>
      {error && <p className="text-sm text-destructive mb-2">{error}</p>}
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-muted text-left">
              <th className="px-3 py-2">ID</th>
              <th className="px-3 py-2">Sessão</th>
              <th className="px-3 py-2">Atleta</th>
              <th className="px-3 py-2">Tipo</th>
              <th className="px-3 py-2">Descrição</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Criado em</th>
              <th className="px-3 py-2">Ação (INV-TRAIN-067)</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b hover:bg-muted/30">
                <td className="px-3 py-2 font-mono text-xs">{item.id.slice(0, 8)}…</td>
                <td className="px-3 py-2 font-mono text-xs">{item.training_session_id.slice(0, 8)}…</td>
                <td className="px-3 py-2 font-mono text-xs">{item.athlete_id.slice(0, 8)}…</td>
                <td className="px-3 py-2">{item.item_type}</td>
                <td className="px-3 py-2 max-w-xs truncate">{item.description ?? '—'}</td>
                <td className={`px-3 py-2 font-medium ${STATUS_COLOR[item.status] ?? ''}`}>
                  {STATUS_LABEL[item.status] ?? item.status}
                </td>
                <td className="px-3 py-2 text-xs">
                  {new Date(item.created_at).toLocaleString('pt-BR')}
                </td>
                <td className="px-3 py-2">
                  {item.status === 'open' ? (
                    <div className="flex flex-col gap-1 min-w-[220px]">
                      <select
                        className="border rounded px-1 py-0.5 text-xs"
                        value={form[item.id]?.new_presence_status ?? ''}
                        onChange={(e) =>
                          setForm((prev) => ({
                            ...prev,
                            [item.id]: {
                              ...prev[item.id],
                              new_presence_status: e.target.value,
                              justification: prev[item.id]?.justification ?? '',
                            },
                          }))
                        }
                      >
                        <option value="">Selecionar status...</option>
                        <option value="present">Presente</option>
                        <option value="absent">Ausente</option>
                        <option value="justified">Justificado</option>
                      </select>
                      <input
                        type="text"
                        className="border rounded px-1 py-0.5 text-xs"
                        placeholder="Justificativa do treinador…"
                        value={form[item.id]?.justification ?? ''}
                        onChange={(e) =>
                          setForm((prev) => ({
                            ...prev,
                            [item.id]: {
                              ...prev[item.id],
                              new_presence_status: prev[item.id]?.new_presence_status ?? '',
                              justification: e.target.value,
                            },
                          }))
                        }
                      />
                      <button
                        className="px-2 py-0.5 text-xs bg-primary text-primary-foreground rounded disabled:opacity-50"
                        disabled={resolvingId === item.id}
                        onClick={() => handleResolve(item.id)}
                      >
                        {resolvingId === item.id ? 'Salvando…' : 'Resolver'}
                      </button>
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">
                      {item.resolved_at
                        ? `Resolvido em ${new Date(item.resolved_at).toLocaleString('pt-BR')}`
                        : '—'}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
