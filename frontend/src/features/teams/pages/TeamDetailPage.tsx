import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useTeam } from '../../../api/hooks/useTeams';
import { useUsers } from '../../../api/hooks/useUsers';

export function TeamDetailPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const { data: team, isLoading, error } = useTeam(teamId ?? '');
  const { data: members } = useUsers({ teamId: teamId ?? '' });

  if (isLoading) return (
    <div className="flex justify-center py-12">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
    </div>
  );

  if (error || !team) return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
      Time não encontrado.
    </div>
  );

  return (
    <div className="space-y-6 max-w-3xl">
      <Link to="/teams" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
        <ArrowLeft className="h-4 w-4" /> Voltar para Times
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900">{team.name}</h1>
        {team.city && <p className="text-sm text-gray-500 mt-1">{team.city}</p>}
      </div>

      {members && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Membros do time ({members.items.length})</h2>
          <div className="space-y-3">
            {members.items.length === 0 && (
              <p className="text-sm text-gray-400">Nenhum membro vinculado a este time.</p>
            )}
            {members.items.map((m) => (
              <Link
                key={m.id}
                to={`/users/${m.id}`}
                className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-gray-50 transition-colors"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-sm font-semibold">
                  {m.displayName?.[0]?.toUpperCase() ?? '?'}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{m.displayName}</p>
                  <p className="text-xs text-gray-500">{m.roleLabel}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
