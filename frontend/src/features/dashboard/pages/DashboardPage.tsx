import { Calendar, Dumbbell, Shield, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../../../stores/authStore';

const CARDS = [
  { label: 'Usuários', icon: Users, href: '/users', color: 'bg-blue-50 text-blue-700 border-blue-100' },
  { label: 'Times', icon: Shield, href: '/teams', color: 'bg-indigo-50 text-indigo-700 border-indigo-100' },
  { label: 'Temporadas', icon: Calendar, href: '/seasons', color: 'bg-green-50 text-green-700 border-green-100' },
  { label: 'Treinos', icon: Dumbbell, href: '/training', color: 'bg-orange-50 text-orange-700 border-orange-100' },
];

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Olá{user?.username ? `, ${user.username}` : ''}!
        </h1>
        <p className="text-sm text-gray-500 mt-1">Bem-vindo ao HB Track — Gestão Esportiva de Handebol.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {CARDS.map(({ label, icon: Icon, href, color }) => (
          <Link
            key={href}
            to={href}
            className={`rounded-xl border p-6 flex flex-col items-center gap-3 hover:shadow-md transition-shadow ${color}`}
          >
            <Icon className="h-8 w-8" />
            <span className="font-semibold text-sm">{label}</span>
          </Link>
        ))}
      </div>
    </div >
  );
}
