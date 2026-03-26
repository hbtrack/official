import { ArrowLeft, UserMinus, UserPlus } from 'lucide-react';
import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAddAthleteToTeam, useRemoveAthleteFromTeam, useTeam } from '../../../api/hooks/useTeams';
import { useUsers } from '../../../api/hooks/useUsers';

export function TeamDetailPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const { data: team, isLoading, error } = useTeam(teamId ?? '');
  const { data: members, refetch: refetchMembers } = useUsers({ teamId: teamId ?? '' });
  const { data: allUsers } = useUsers();
  const addAthlete = useAddAthleteToTeam(teamId ?? '');
  const removeAthlete = useRemoveAthleteFromTeam(teamId ?? '');
  const [addingId, setAddingId] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);

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

  const memberIds = new Set((members?.items ?? []).map((m) => m.id));
  const nonMembers = (allUsers?.items ?? []).filter((u) => !memberIds.has(u.id));

  async function handleAdd(athleteUserId: string) {
    setAddingId(athleteUserId);
    try {
      await addAthlete.mutateAsync(athleteUserId);
      await refetchMembers();
    } finally {
      setAddingId(null);
    }
  }

  async function handleRemove(athleteUserId: string) {
    setRemovingId(athleteUserId);
    try {
      await removeAthlete.mutateAsync(athleteUserId);
      await refetchMembers();
    } finally {
      setRemovingId(null);
    }
  }

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
              <div key={m.id} className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50">
                <Link to={`/users/${m.id}`} className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-sm font-semibold">
                    {m.displayName?.[0]?.toUpperCase() ?? '?'}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{m.displayName}</p>
                    <p className="text-xs text-gray-500">{m.roleLabel}</p>
                  </div>
                </Link>
                <button
                  onClick={() => handleRemove(m.id)}
                  disabled={removingId === m.id}
                  className="inline-flex items-center gap-1 text-xs text-red-600 hover:text-red-800 disabled:opacity-40"
                  title="Remover do time"
                >
                  <UserMinus className="h-4 w-4" />
                  {removingId === m.id ? 'Removendo…' : 'Remover'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {nonMembers.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Adicionar membro</h2>
          <div className="space-y-2">
            {nonMembers.map((u) => (
              <div key={u.id} className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-600 text-sm font-semibold">
                    {u.displayName?.[0]?.toUpperCase() ?? '?'}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{u.displayName}</p>
                    <p className="text-xs text-gray-500">{u.roleLabel}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleAdd(u.id)}
                  disabled={addingId === u.id}
                  className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 disabled:opacity-40"
                >
                  <UserPlus className="h-4 w-4" />
                  {addingId === u.id ? 'Adicionando…' : 'Adicionar'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

