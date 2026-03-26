import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Calendar, Clock } from 'lucide-react';
import { useTrainingSessions, useCreateTrainingSession } from '../../../api/hooks/useTraining';

const STATUS_LABELS: Record<string, { label: string; cls: string }> = {
  SCHEDULED: { label: 'Agendado', cls: 'bg-blue-100 text-blue-700' },
  PUBLISHED: { label: 'Publicado', cls: 'bg-green-100 text-green-700' },
  IN_PROGRESS: { label: 'Em andamento', cls: 'bg-yellow-100 text-yellow-700' },
  COMPLETED: { label: 'Concluído', cls: 'bg-gray-100 text-gray-700' },
  CANCELLED: { label: 'Cancelado', cls: 'bg-red-100 text-red-700' },
};

const SESSION_TYPES = ['TACTICAL', 'PHYSICAL', 'TECHNICAL', 'SCRIMMAGE', 'RECOVERY', 'MIXED'];

export function TrainingPage() {
  const { data, isLoading, error } = useTrainingSessions();
  const createSession = useCreateTrainingSession();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    sessionAt: '',
    sessionType: 'TACTICAL',
    durationPlannedMinutes: '',
    mainObjective: '',
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    createSession.mutate(
      {
        body: {
          sessionAt: form.sessionAt,
          sessionType: form.sessionType,
          durationPlannedMinutes: form.durationPlannedMinutes ? parseInt(form.durationPlannedMinutes) : undefined,
          mainObjective: form.mainObjective || undefined,
        },
      },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({ sessionAt: '', sessionType: 'TACTICAL', durationPlannedMinutes: '', mainObjective: '' });
        },
      }
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Treinos</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" /> Novo Treino
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Novo Treino</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data e hora *</label>
              <input
                type="datetime-local"
                required
                value={form.sessionAt}
                onChange={(e) => setForm({ ...form, sessionAt: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo *</label>
              <select
                required
                value={form.sessionType}
                onChange={(e) => setForm({ ...form, sessionType: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {SESSION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duração (min)</label>
              <input
                type="number"
                min={1}
                value={form.durationPlannedMinutes}
                onChange={(e) => setForm({ ...form, durationPlannedMinutes: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo principal</label>
              <input
                type="text"
                value={form.mainObjective}
                onChange={(e) => setForm({ ...form, mainObjective: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
          {createSession.error && <p className="text-sm text-red-600">Erro ao criar treino.</p>}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createSession.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors"
            >
              {createSession.isPending ? 'Salvando...' : 'Salvar'}
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
          </div>
        </form>
      )}

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
        </div>
      )}

      {error && <p className="text-sm text-red-600">Erro ao carregar treinos.</p>}

      {data && (
        <div className="space-y-3">
          {data.items.length === 0 && <p className="text-sm text-gray-400 py-8 text-center">Nenhum treino cadastrado.</p>}
          {data.items.map((s) => {
            const badge = STATUS_LABELS[s.status] ?? { label: s.status, cls: 'bg-gray-100 text-gray-700' };
            return (
              <Link
                key={s.id}
                to={`/training/${s.id}`}
                className="flex items-center justify-between bg-white rounded-xl border border-gray-200 px-6 py-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <div className="flex flex-col items-center justify-center w-12 h-12 rounded-lg bg-indigo-50 text-indigo-700">
                    <Calendar className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{s.sessionType}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(s.sessionAt).toLocaleString('pt-BR')}
                    </p>
                    {s.mainObjective && <p className="text-xs text-gray-400 mt-0.5 truncate max-w-xs">{s.mainObjective}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {s.durationPlannedMinutes && (
                    <span className="flex items-center gap-1 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />{s.durationPlannedMinutes}min
                    </span>
                  )}
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge.cls}`}>{badge.label}</span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
