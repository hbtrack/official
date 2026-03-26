import { ArrowLeft, Check, Pencil, X } from 'lucide-react';
import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { usePatchUser, useUser } from '../../../api/hooks/useUsers';

const ROLE_LABELS: Record<string, string> = {
  ATHLETE: 'Atleta', COACH: 'Treinador', COORDINATOR: 'Coordenador', ADMIN: 'Admin', MEMBER: 'Membro',
};

const POSITION_OPTIONS = [
  'Goleiro', 'Ponta Esquerda', 'Ponta Direita', 'Armador', 'Pivô', 'Extremo',
];

export function UserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const { data: user, isLoading, error } = useUser(userId ?? '');
  const patchUser = usePatchUser(userId ?? '');
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ firstName: '', lastName: '', positionLabel: '' });

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

  function startEdit() {
    setForm({
      firstName: user?.firstName ?? '',
      lastName: user?.lastName ?? '',
      positionLabel: user?.positionLabel ?? '',
    });
    setEditing(true);
  }

  function cancelEdit() {
    setEditing(false);
  }

  async function saveEdit(e: React.FormEvent) {
    e.preventDefault();
    await patchUser.mutateAsync({
      firstName: form.firstName || undefined,
      lastName: form.lastName || undefined,
      positionLabel: form.positionLabel || undefined,
    });
    setEditing(false);
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <Link to="/users" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
        <ArrowLeft className="h-4 w-4" /> Voltar para Membros
      </Link>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-5">
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
          {!editing && (
            <button
              onClick={startEdit}
              className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Pencil className="h-3.5 w-3.5" /> Editar
            </button>
          )}
        </div>

        {editing ? (
          <form onSubmit={saveEdit} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                <input
                  type="text"
                  value={form.firstName}
                  onChange={(e) => setForm((f) => ({ ...f, firstName: e.target.value }))}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sobrenome</label>
                <input
                  type="text"
                  value={form.lastName}
                  onChange={(e) => setForm((f) => ({ ...f, lastName: e.target.value }))}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Posição</label>
                <select
                  value={form.positionLabel}
                  onChange={(e) => setForm((f) => ({ ...f, positionLabel: e.target.value }))}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Sem posição</option>
                  {POSITION_OPTIONS.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex gap-2 justify-end pt-2">
              <button
                type="button"
                onClick={cancelEdit}
                className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
              >
                <X className="h-3.5 w-3.5" /> Cancelar
              </button>
              <button
                type="submit"
                disabled={patchUser.isPending}
                className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                <Check className="h-3.5 w-3.5" />
                {patchUser.isPending ? 'Salvando…' : 'Salvar'}
              </button>
            </div>
            {patchUser.isError && (
              <p className="text-sm text-red-600">Erro ao salvar. Tente novamente.</p>
            )}
          </form>
        ) : (
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
        )}
      </div>
    </div>
  );
}

