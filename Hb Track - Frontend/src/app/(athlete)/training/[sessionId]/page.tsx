'use client';

/**
 * Página: Pré-visualização do Treino (Atleta)
 *
 * AR_187 (AR-TRAIN-019) — Rota: /(athlete)/training/[sessionId]
 *
 * Invariantes:
 * - INV-TRAIN-068: atleta pode ver treino antes de iniciar
 * - INV-TRAIN-071: banner de wellness se wellness_blocked=true
 * - INV-TRAIN-069: mídia dos exercícios exibida quando acesso liberado
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getTrainingPreview, type TrainingPreview } from '@/lib/api/athlete-training';

export default function AthleteTrainingPreviewPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params?.sessionId ?? '';

  const [preview, setPreview] = useState<TrainingPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getTrainingPreview(sessionId);
        setPreview(data);
      } catch (err) {
        setError('Não foi possível carregar o treino. Tente novamente.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [sessionId]);

  if (loading) {
    return <div className="p-6 text-sm text-muted-foreground">Carregando treino…</div>;
  }

  if (error) {
    return <div className="p-6 text-sm text-destructive">{error}</div>;
  }

  if (!preview) {
    return <div className="p-6 text-sm text-muted-foreground">Treino não encontrado.</div>;
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-1">{preview.name ?? 'Treino'}</h1>
      {preview.scheduled_date && (
        <p className="text-sm text-muted-foreground mb-4">
          {new Date(preview.scheduled_date).toLocaleDateString('pt-BR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      )}

      {/* INV-TRAIN-071: Banner de wellness bloqueado */}
      {preview.wellness_blocked && (
        <div
          role="alert"
          className="mb-6 rounded-lg border border-yellow-300 bg-yellow-50 p-4 flex items-start gap-3"
        >
          <span className="text-yellow-600 text-xl" aria-hidden="true">
            ⚠️
          </span>
          <div>
            <p className="font-semibold text-yellow-800">Wellness do dia não preenchido</p>
            <p className="text-sm text-yellow-700 mt-1">
              {preview.message ??
                'Preencha o wellness do dia para acessar o conteúdo completo do treino.'}
            </p>
          </div>
        </div>
      )}

      {/* INV-TRAIN-069: Exercícios (só exibidos se wellness liberado) */}
      {!preview.wellness_blocked && preview.exercises.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-3">Exercícios do Treino</h2>
          <ul className="space-y-4">
            {preview.exercises.map((ex) => (
              <li key={ex.id} className="border rounded-lg p-4">
                <p className="font-medium">{ex.name}</p>
                {ex.description && (
                  <p className="text-sm text-muted-foreground mt-1">{ex.description}</p>
                )}
                {ex.media_url && (
                  <a
                    href={ex.media_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary underline mt-2 inline-block"
                  >
                    Ver mídia do exercício
                  </a>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {!preview.wellness_blocked && preview.exercises.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Nenhum exercício cadastrado para este treino.
        </p>
      )}
    </div>
  );
}
