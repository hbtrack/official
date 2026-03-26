import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { useSeasons, useCreateSeason } from '../../../api/hooks/useSeasons';

function isActive(start?: string, end?: string): boolean {
  const now = Date.now();
  const s = start ? new Date(start).getTime() : null;
  const e = end ? new Date(end).getTime() : null;
  if (s && e) return now >= s && now <= e;
  return false;
}

export function SeasonsPage() {
  const { data, isLoading, error } = useSeasons();
  const createSeason = useCreateSeason();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ year: new Date().getFullYear(), startDate: '', endDate: '' });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    createSeason.mutate(
      { body: { year: form.year, startDate: form.startDate || undefined, endDate: form.endDate || undefined } },
      {
        onSuccess: () => {
          setShowForm(false);
          setForm({ year: new Date().getFullYear(), startDate: '', endDate: '' });
        },
      }
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Temporadas</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" /> Nova Temporada
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Nova Temporada</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ano *</label>
              <input
                type="number"
                required
                min={2000}
                max={2100}
                value={form.year}
                onChange={(e) => setForm({ ...form, year: parseInt(e.target.value) })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Início</label>
              <input
                type="date"
                value={form.startDate}
                onChange={(e) => setForm({ ...form, startDate: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fim</label>
              <input
                type="date"
                value={form.endDate}
                onChange={(e) => setForm({ ...form, endDate: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
          {createSeason.error && (
            <p className="text-sm text-red-600">Erro ao criar temporada.</p>
          )}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createSeason.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors"
            >
              {createSeason.isPending ? 'Salvando...' : 'Salvar'}
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

      {error && <p className="text-sm text-red-600">Erro ao carregar temporadas.</p>}

      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((season) => (
            <Link
              key={season.seasonId}
              to={`/seasons/${season.seasonId}`}
              className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-lg font-bold text-gray-900">{season.year}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {season.startDate ? new Date(season.startDate).toLocaleDateString('pt-BR') : '—'}&nbsp;→&nbsp;
                    {season.endDate ? new Date(season.endDate).toLocaleDateString('pt-BR') : '—'}
                  </p>
                </div>
                {isActive(season.startDate, season.endDate) && (
                  <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">Ativa</span>
                )}
              </div>
            </Link>
          ))}
          {data.items.length === 0 && <p className="text-sm text-gray-400 col-span-3 py-8 text-center">Nenhuma temporada cadastrada.</p>}
        </div>
      )}
    </div>
  );
}
