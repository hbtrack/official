import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Clock, Target } from 'lucide-react';
import { useTrainingSession, usePublishTrainingSession } from '../../../api/hooks/useTraining';

const STATUS_LABELS: Record<string, { label: string; cls: string }> = {
  SCHEDULED: { label: 'Agendado', cls: 'bg-blue-100 text-blue-700' },
  PUBLISHED: { label: 'Publicado', cls: 'bg-green-100 text-green-700' },
  IN_PROGRESS: { label: 'Em andamento', cls: 'bg-yellow-100 text-yellow-700' },
  COMPLETED: { label: 'Concluído', cls: 'bg-gray-100 text-gray-700' },
  CANCELLED: { label: 'Cancelado', cls: 'bg-red-100 text-red-700' },
};

export function TrainingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: session, isLoading, error } = useTrainingSession(id ?? '');
  const publish = usePublishTrainingSession();

  if (isLoading) return (
    <div className="flex justify-center py-12">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
    </div>
  );

  if (error || !session) return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
      Treino não encontrado.
    </div>
  );

  const badge = STATUS_LABELS[session.status] ?? { label: session.status, cls: 'bg-gray-100 text-gray-700' };

  return (
    <div className="space-y-6 max-w-3xl">
      <Link to="/training" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
        <ArrowLeft className="h-4 w-4" /> Voltar para Treinos
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{session.sessionType}</h1>
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
              <Calendar className="h-4 w-4" />
              <span>{new Date(session.sessionAt).toLocaleString('pt-BR')}</span>
            </div>
          </div>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${badge.cls}`}>{badge.label}</span>
        </div>

        {session.durationPlannedMinutes && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>Duração planejada: {session.durationPlannedMinutes} minutos</span>
          </div>
        )}

        {session.mainObjective && (
          <div className="flex items-start gap-2 text-sm text-gray-600">
            <Target className="h-4 w-4 mt-0.5 shrink-0" />
            <span>{session.mainObjective}</span>
          </div>
        )}
      </div>

      {session.status === 'SCHEDULED' && (
        <div className="flex gap-3">
          <button
            onClick={() => publish.mutate({ path: { id: session.id } })}
            disabled={publish.isPending}
            className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-60 transition-colors"
          >
            {publish.isPending ? 'Publicando...' : 'Publicar Treino'}
          </button>
        </div>
      )}
    </div>
  );
}
