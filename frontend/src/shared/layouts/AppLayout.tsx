import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  Users,
  Shield,
  Calendar,
  Dumbbell,
  LayoutDashboard,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useLogout } from '../../api/hooks/useAuth';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/users',   icon: Users,          label: 'Membros'     },
  { to: '/teams',   icon: Shield,         label: 'Times'       },
  { to: '/seasons', icon: Calendar,       label: 'Temporadas'  },
  { to: '/training',icon: Dumbbell,       label: 'Treinos'     },
];

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const navigate = useNavigate();

  function handleLogout() {
    logout.mutate(undefined, {
      onSettled: () => navigate('/login', { replace: true }),
    });
  }

  const NavLinks = () => (
    <nav className="flex-1 space-y-1 px-2 py-4">
      {navItems.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-indigo-700 text-white'
                : 'text-indigo-100 hover:bg-indigo-700 hover:text-white'
            }`
          }
          onClick={() => setSidebarOpen(false)}
        >
          <Icon className="h-5 w-5 shrink-0" />
          {label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100">
      {/* Sidebar desktop */}
      <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 bg-indigo-800">
        <div className="flex h-16 items-center px-6">
          <Link to="/" className="text-xl font-bold text-white">
            HB Track
          </Link>
        </div>
        <div className="flex flex-1 flex-col overflow-y-auto">
          <NavLinks />
        </div>
        <div className="flex items-center gap-3 border-t border-indigo-700 px-4 py-4">
          <div className="flex-1 min-w-0">
            <p className="truncate text-sm font-medium text-white">{user?.email || 'Usuário'}</p>
          </div>
          <button
            onClick={handleLogout}
            className="rounded p-1 text-indigo-200 hover:text-white"
            title="Sair"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </aside>

      {/* Sidebar mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setSidebarOpen(false)}>
          <div className="fixed inset-0 bg-black/50" />
          <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-indigo-800">
            <div className="flex h-16 items-center justify-between px-6">
              <span className="text-xl font-bold text-white">HB Track</span>
              <button onClick={() => setSidebarOpen(false)} className="text-white">
                <X className="h-5 w-5" />
              </button>
            </div>
            <NavLinks />
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-1 flex-col lg:pl-64 overflow-hidden">
        {/* Top bar */}
        <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-white px-4 lg:px-8 shadow-sm">
          <button
            className="lg:hidden rounded-md p-2 text-gray-500 hover:bg-gray-100"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex-1" />
          <span className="text-sm text-gray-600 hidden sm:block">{user?.email || ''}</span>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
