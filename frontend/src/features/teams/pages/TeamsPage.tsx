import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Shield } from 'lucide-react';
import { useTeams, useCreateTeam } from '../../../api/hooks/useTeams';

export function TeamsPage() {
  const { data, isLoading, error } = useTeams();
  const createTeam = useCreateTeam();

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [city, setCity] = useState('');
  const [formError, setFormError] = useState('');

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) { setFormError('Nome é obrigatório.'); return; }
    setFormError('');
    createTeam.mutate(
      { name: name.trim(), city: city.trim() || undefined },
      {
        onSuccess: () => { setShowForm(false); setName(''); setCity(''); },
        onError: () => setFormError('Erro ao criar time. Tente novamente.'),
      }
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Times</h1>
          <p className="text-sm text-gray-500 mt-1">Elencos registrados no sistema</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Novo Time
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="rounded-xl bg-white border border-gray-200 p-5 space-y-4 max-w-md">
          <h3 className="font-semibold text-gray-900">Criar novo time</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ex: Handebol Clube A"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cidade</label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Ex: São Paulo"
            />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={createTeam.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {createTeam.isPending ? 'Criando...' : 'Criar'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
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

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Erro ao carregar times.
        </div>
      )}

      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.length === 0 && (
            <p className="col-span-full text-center py-12 text-gray-400">Nenhum time cadastrado.</p>
          )}
          {data.items.map((team) => (
            <Link
              key={team.teamId}
              to={`/teams/${team.teamId}`}
              className="flex items-center gap-4 rounded-xl bg-white border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-sm transition-all"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-indigo-700">
                <Shield className="h-6 w-6" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">{team.name}</p>
                {team.city && <p className="text-sm text-gray-500">{team.city}</p>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
