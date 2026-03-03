'use client';

/**
 * Página: Fila de Pendências de Sessão de Treino
 *
 * AR_186 (AR-TRAIN-018) — Rota: /training/pending-queue
 * Acesso: treinador / admin (proteção via middleware RBAC)
 *
 * Invariantes:
 * - INV-TRAIN-066: atleta pode enviar justificativa, NÃO pode resolver
 * - INV-TRAIN-067: treinador tem autoridade final de resolução
 */

import React, { useEffect, useState } from 'react';
import { listPendingItems, type PendingItem } from '@/lib/api/pending';
import { PendingQueueTable } from '@/components/training/PendingQueueTable';

export default function PendingQueuePage() {
  const [items, setItems] = useState<PendingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionFilter, setSessionFilter] = useState('');

  const loadItems = async (sessionId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await listPendingItems(sessionId || undefined);
      setItems(data);
    } catch (err) {
      setError('Erro ao carregar pendências. Verifique a conexão.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionFilter) {
      loadItems(sessionFilter);
    }
  }, [sessionFilter]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Fila de Pendências</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Itens pendentes de resolução pelo treinador (INV-TRAIN-067). Atletas podem adicionar
        justificativas, mas apenas o treinador fecha cada item.
      </p>

      {/* Filtro por sessão */}
      <div className="mb-4 flex gap-2 items-center">
        <label htmlFor="session-filter" className="text-sm font-medium">
          ID da Sessão:
        </label>
        <input
          id="session-filter"
          type="text"
          className="border rounded px-2 py-1 text-sm w-72"
          placeholder="UUID da sessão de treino"
          value={sessionFilter}
          onChange={(e) => setSessionFilter(e.target.value)}
        />
        <button
          className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded"
          onClick={() => loadItems(sessionFilter || undefined)}
        >
          Filtrar
        </button>
      </div>

      {!sessionFilter && (
        <p className="text-muted-foreground text-sm mb-4">
          Informe o ID de uma sessão para listar os pending items.
        </p>
      )}

      {loading && <p className="text-sm text-muted-foreground">Carregando...</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}

      {!loading && !error && sessionFilter && (
        <PendingQueueTable items={items} onResolved={() => loadItems(sessionFilter)} />
      )}
    </div>
  );
}
