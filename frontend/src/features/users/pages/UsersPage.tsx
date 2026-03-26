import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useUsers } from '../../../api/hooks/useUsers';
import { useAuthStore } from '../../../stores/authStore';

const ROLE_LABELS: Record<string, string> = {
  ATHLETE: 'Atleta',
  COACH: 'Treinador',
  COORDINATOR: 'Coordenador',
  ADMIN: 'Admin',
  MEMBER: 'Membro',
};

const ROLE_COLORS: Record<string, string> = {
  ATHLETE: 'bg-blue-100 text-blue-800',
  COACH: 'bg-green-100 text-green-800',
  COORDINATOR: 'bg-purple-100 text-purple-800',
  ADMIN: 'bg-red-100 text-red-800',
  MEMBER: 'bg-gray-100 text-gray-800',
};

export function UsersPage() {
  const user = useAuthStore((s) => s.user);
  const [roleFilter, setRoleFilter] = useState('');

  const { data, isLoading, error } = useUsers({
    organizationId: user?.organization_id,
    roleLabel: roleFilter || undefined,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Membros</h1>
          <p className="text-sm text-gray-500 mt-1">Perfis de atletas e comissão técnica</p>
        </div>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-2">
        {['', 'athlete', 'coach', 'coordinator', 'admin'].map((role) => (
          <button
            key={role}
            onClick={() => setRoleFilter(role)}
            className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
              roleFilter === role
                ? 'bg-indigo-600 text-white'
                : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {role === '' ? 'Todos' : ROLE_LABELS[role.toUpperCase()] ?? role}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          Erro ao carregar membros. Verifique sua conexão.
        </div>
      )}

      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.length === 0 && (
            <p className="col-span-full text-center py-12 text-gray-400">Nenhum membro encontrado.</p>
          )}
          {data.items.map((u) => (
            <Link
              key={u.id}
              to={`/users/${u.id}`}
              className="flex items-center gap-4 rounded-xl bg-white border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-sm transition-all"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-semibold text-lg">
                {u.displayName?.[0]?.toUpperCase() ?? '?'}
              </div>
              <div className="min-w-0">
                <p className="font-medium text-gray-900 truncate">{u.displayName}</p>
                <span className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_COLORS[u.roleLabel] ?? 'bg-gray-100 text-gray-800'}`}>
                  {ROLE_LABELS[u.roleLabel] ?? u.roleLabel}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
