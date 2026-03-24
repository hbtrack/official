import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useUser } from '../../../api/hooks/useUsers';

const ROLE_LABELS: Record<string, string> = {
  ATHLETE: 'Atleta', COACH: 'Treinador', COORDINATOR: 'Coordenador', ADMIN: 'Admin', MEMBER: 'Membro',
};

export function UserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const { data: user, isLoading, error } = useUser(userId ?? '');

  if (isLoading) return (
    <div className="flex justify-center py-12">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
    </div>
  );

  if (error || !user) return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
      Membro não encontrado.
    </div>
  );

  return (
    <div className="space-y-6 max-w-2xl">
      <Link to="/users" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
        <ArrowLeft className="h-4 w-4" /> Voltar para Membros
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-5 mb-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold text-2xl">
            {user.displayName?.[0]?.toUpperCase() ?? '?'}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{user.displayName}</h1>
            <span className="mt-1 inline-block rounded-full bg-indigo-100 text-indigo-800 px-2 py-0.5 text-xs font-medium">
              {ROLE_LABELS[user.roleLabel] ?? user.roleLabel}
            </span>
          </div>
        </div>

        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2 text-sm">
          {user.firstName && (
            <div>
              <dt className="font-medium text-gray-500">Nome</dt>
              <dd className="mt-1 text-gray-900">{user.firstName} {user.lastName}</dd>
            </div>
          )}
          {user.positionLabel && (
            <div>
              <dt className="font-medium text-gray-500">Posição</dt>
              <dd className="mt-1 text-gray-900">{user.positionLabel}</dd>
            </div>
          )}
          {user.statusLabel && (
            <div>
              <dt className="font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-gray-900">{user.statusLabel}</dd>
            </div>
          )}
          <div>
            <dt className="font-medium text-gray-500">Criado em</dt>
            <dd className="mt-1 text-gray-900">{new Date(user.createdAt).toLocaleDateString('pt-BR')}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
