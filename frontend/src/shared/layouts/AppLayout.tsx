/**
 * AppLayout — Shell autenticada do HB Track
 * Conformidade: UX_SHELL_CONTRACT.md + NAVIGATION_VISIBILITY_CONTRACT.md + UX_BRAND_CONTRACT.md
 *
 * Taxonomia estrutural (NAVIGATION_VISIBILITY_CONTRACT §2):
 *   Início | Organização | Planejamento Técnico | Jogo e Competição | Performance e Saúde | Administração
 *
 * Estado inicial do primeiro batch (NAVIGATION_VISIBILITY_CONTRACT §3):
 *   Ativos: Dashboard, Teams, Seasons, Training, Users, Conta e Acesso
 *   Desabilitados: Competitions, Matches, Scout, Video, Wellness, Medical,
 *                  Exercises, Analytics, Reports, AI Ingestion, Audit
 *
 * Top bar capabilities (NAVIGATION_VISIBILITY_CONTRACT §3):
 *   Notificações | Command palette | Breadcrumbs | User menu
 */

import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Shield,
  Calendar,
  Dumbbell,
  Trophy,
  Swords,
  Crosshair,
  Video,
  Activity,
  Stethoscope,
  BarChart2,
  FileText,
  Brain,
  UserCog,
  ClipboardList,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Search,
  Bell,
  ChevronDown,
  UserCircle,
} from 'lucide-react';
import { useState, useEffect, useCallback, Fragment } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useLogout } from '../../api/hooks/useAuth';

const navItems = [
  // ── Tipos ──────────────────────────────────────────────────────────────────
  type AllowedRole = 'admin' | 'coordinator' | 'coach' | 'athlete' | 'member';

interface NavItem {
  to: string;
  icon: React.ElementType;
  label: string;
  disabled?: boolean;
  allowedRoles?: AllowedRole[];
  badge?: string;
}

interface NavGroup {
  group: string;
  items: NavItem[];
}

// ── Configuração de navegação (NAVIGATION_VISIBILITY_CONTRACT §2, §3) ───────
// Ativos: Dashboard, Teams, Seasons, Training, Users, Conta e Acesso
// Desabilitados: Competitions, Matches, Scout, Video, Wellness, Medical,
//                Exercises, Analytics, Reports, AI Ingestion, Audit
const NAV_GROUPS: NavGroup[] = [
  {
    group: 'Início',
    items: [
      { to: '/', icon: LayoutDashboard, label: 'Dashboard', allowedRoles: ['admin', 'coordinator', 'coach', 'athlete', 'member'] },
    ],
  },
  {
    group: 'Organização',
    items: [
      { to: '/teams', icon: Shield, label: 'Teams', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/seasons', icon: Calendar, label: 'Seasons', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/users', icon: Users, label: 'Users', allowedRoles: ['admin', 'coordinator'] },
    ],
  },
  {
    group: 'Planejamento Técnico',
    items: [
      { to: '/training', icon: Dumbbell, label: 'Training', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/exercises', icon: Activity, label: 'Exercises', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
    ],
  },
  {
    group: 'Jogo e Competição',
    items: [
      { to: '/competitions', icon: Trophy, label: 'Competitions', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/matches', icon: Swords, label: 'Matches', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/scout', icon: Crosshair, label: 'Scout', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/video', icon: Video, label: 'Video', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
    ],
  },
  {
    group: 'Performance e Saúde',
    items: [
      { to: '/wellness', icon: Activity, label: 'Wellness', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach', 'athlete'] },
      { to: '/medical', icon: Stethoscope, label: 'Medical', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/analytics', icon: BarChart2, label: 'Analytics', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/reports', icon: FileText, label: 'Reports', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator', 'coach'] },
      { to: '/ai-ingestion', icon: Brain, label: 'AI Ingestion', disabled: true, badge: 'em breve', allowedRoles: ['admin', 'coordinator'] },
    ],
  },
  {
    group: 'Administração',
    items: [
      { to: '/conta-acesso', icon: UserCog, label: 'Conta e Acesso', allowedRoles: ['admin', 'coordinator', 'coach', 'athlete', 'member'] },
      { to: '/audit', icon: ClipboardList, label: 'Audit', disabled: true, badge: 'em breve', allowedRoles: ['admin'] },
    ],
  },
];

// ── Top bar capabilities ────────────────────────────────────────────────────
// Notificações | Command palette | Breadcrumbs | User menu
const TOP_BAR_CAPABILITIES = ['Notificações', 'Command palette', 'Breadcrumbs', 'User menu'] as const;

// ── Contexto de equipe/temporada (mock inicial — integrar via API) ──────────
const DEFAULT_TEAM_CONTEXT = { id: '', name: 'Selecionar equipe' };
const DEFAULT_SEASON_CONTEXT = { id: '', name: 'Selecionar temporada' };

// ── Helpers de avatar ────────────────────────────────────────────────────────
function getInitials(name?: string | null, email?: string | null): string {
  if (name) {
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((n) => n[0].toUpperCase())
      .join('');
  }
  if (email) return email[0].toUpperCase();
  return 'HB';
}

// ── Componente de Avatar ─────────────────────────────────────────────────────
function UserAvatar({ avatarUrl, name, email, size = 'md' }: {
  avatarUrl?: string | null;
  name?: string | null;
  email?: string | null;
  size?: 'sm' | 'md';
}) {
  const dim = size === 'sm' ? 'h-7 w-7 text-xs' : 'h-8 w-8 text-sm';
  // Avatar circular (UX_SHELL_CONTRACT §3)
  // Fallback para iniciais quando não houver avatar (avatar fallback)
  if (avatarUrl) {
    return (
      <img
        src={avatarUrl}
        alt="Avatar do usuário"
        className={`${dim} rounded-full object-cover shrink-0`}
      />
    );
  }
  const initials = getInitials(name, email);
  return (
    <span className={`${dim} rounded-full bg-brand-600 flex items-center justify-center font-medium text-white shrink-0`}>
      {initials}
    </span>
  );
}

// ── Componente principal ─────────────────────────────────────────────────────
export function AppLayout() {
  // sidebar desktop colapsável (UX_SHELL_CONTRACT §2)
  const [collapsed, setCollapsed] = useState(false);
  // drawer mobile com overlay (UX_SHELL_CONTRACT §2)
  const [drawerOpen, setDrawerOpen] = useState(false);
  // command palette (UX_SHELL_CONTRACT §3)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  // notificações (UX_SHELL_CONTRACT §3)
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  // user menu (UX_SHELL_CONTRACT §3)
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  // contexto de equipe e temporada (UX_SHELL_CONTRACT §2)
  const [activeTeam, setActiveTeam] = useState(DEFAULT_TEAM_CONTEXT);
  const [activeSeason, setActiveSeason] = useState(DEFAULT_SEASON_CONTEXT);
  // teamSwitcher visível
  const [teamSwitcherOpen, setTeamSwitcherOpen] = useState(false);

  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const navigate = useNavigate();
  const location = useLocation();

  // Fechar drawer ao navegar
  useEffect(() => { setDrawerOpen(false); }, [location.pathname]);

  // Fechar drawer com Escape (UX_SHELL_CONTRACT §2)
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        setDrawerOpen(false);
        setCommandPaletteOpen(false);
        setUserMenuOpen(false);
        setNotificationsOpen(false);
      }
    }
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, []);

  function handleLogout() {
    logout.mutate(undefined, {
      onSettled: () => navigate('/login', { replace: true }),
    });
  }

  // Verificar visibilidade por role (roleVisibility)
  const canAccess = useCallback((allowedRoles?: AllowedRole[]) => {
    if (!allowedRoles || allowedRoles.length === 0) return true;
    const userRoles = (user as { roles?: string[] } | null)?.roles ?? [];
    return allowedRoles.some((r) => userRoles.includes(r));
  }, [user]);

  // Breadcrumbs — construídos a partir do pathname
  const breadcrumbs = location.pathname
    .split('/')
    .filter(Boolean)
    .map((segment, idx, arr) => ({
      label: segment.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      to: '/' + arr.slice(0, idx + 1).join('/'),
    }));

  // Troca de equipe (teamSwitcher)
  function handleTeamChange(team: typeof DEFAULT_TEAM_CONTEXT) {
    setActiveTeam(team);
    setTeamSwitcherOpen(false);
  }

  const sidebarWidthClass = collapsed ? 'w-16' : 'w-64';

  // ── Itens de navegação filtrados por role ─────────────────────────────────
  const NavGroupList = ({ onNavigate }: { onNavigate?: () => void }) => (
    <nav className="flex-1 overflow-y-auto py-4">
      {NAV_GROUPS.map(({ group, items }) => {
        const visibleItems = items.filter((item) => canAccess(item.allowedRoles as AllowedRole[]));
        if (visibleItems.length === 0) return null;
        return (
          <div key={group} className="mb-2">
            {!collapsed && (
              <p className="px-4 pb-1 text-[10px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
                {group}
              </p>
            )}
            {visibleItems.map((item) => (
              <NavItemRow
                key={item.to}
                item={item}
                collapsed={collapsed}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        );
      })}
    </nav>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* ── Sidebar desktop colapsável (UX_SHELL_CONTRACT §2) ────────────── */}
      <aside
        className={`hidden lg:flex flex-col fixed inset-y-0 left-0 z-30 bg-gray-900 transition-all duration-200 ${sidebarWidthClass}`}
        aria-label="Navegação principal"
      >
        {/* Header da sidebar — logos oficiais (UX_SHELL_CONTRACT §2) */}
        <div className="flex h-16 items-center justify-between px-3 border-b border-gray-800">
          {collapsed ? (
            <Link to="/" className="flex items-center justify-center w-full">
              <img
                src="/generated/images/logo-icon.svg"
                alt="HB Track"
                className="h-8 w-8"
                onError={(e) => { (e.target as HTMLImageElement).src = '/generated/images/logo-icon-dark.svg'; }}
              />
            </Link>
          ) : (
            <Link to="/" className="flex items-center gap-2">
              <img
                src="/generated/images/logo.svg"
                alt="HB Track"
                className="h-8"
                onError={(e) => { (e.target as HTMLImageElement).src = '/generated/images/logo-dark.svg'; }}
              />
            </Link>
          )}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="ml-auto rounded p-1 text-gray-400 hover:text-white hover:bg-gray-800"
            aria-label={collapsed ? 'Expandir sidebar' : 'Recolher sidebar'}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Contexto operacional de equipe/temporada */}
        {!collapsed && (
          <div className="px-3 py-2 border-b border-gray-800">
            <button
              onClick={() => setTeamSwitcherOpen((o) => !o)}
              className="w-full flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-gray-300 hover:bg-gray-800"
            >
              <Shield className="h-3.5 w-3.5 shrink-0 text-gray-400" />
              <span className="flex-1 truncate text-left">{activeTeam.name}</span>
              <ChevronDown className="h-3 w-3 text-gray-500" />
            </button>
            {teamSwitcherOpen && (
              <div className="mt-1 rounded-lg bg-gray-800 py-1 text-xs text-gray-300">
                <button
                  className="w-full px-3 py-1.5 text-left hover:bg-gray-700"
                  onClick={() => handleTeamChange({ id: 'demo', name: 'Equipe Demo' })}
                >
                  Equipe Demo
                </button>
              </div>
            )}
            <p className="mt-1 px-2 text-[10px] text-gray-500 truncate">
              {activeSeason.name}
            </p>
          </div>
        )}

        <NavGroupList />

        {/* User area */}
        <div className="border-t border-gray-800 p-3">
          <div className="flex items-center gap-2">
            <UserAvatar
              avatarUrl={(user as { avatarUrl?: string } | null)?.avatarUrl}
              name={(user as { displayName?: string } | null)?.displayName}
              email={user?.email}
              size="sm"
            />
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="truncate text-xs font-medium text-white">{user?.email ?? 'Usuário'}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="rounded p-1 text-gray-400 hover:text-white hover:bg-gray-800"
              title="Sair"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Drawer mobile com overlay (UX_SHELL_CONTRACT §2) ─────────────── */}
      {drawerOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          role="dialog"
          aria-modal="true"
        >
          {/* overlay backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setDrawerOpen(false)}
            aria-label="Fechar menu"
          />
          <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 flex flex-col">
            <div className="flex h-16 items-center justify-between px-4 border-b border-gray-800">
              <Link to="/" onClick={() => setDrawerOpen(false)}>
                <img src="/generated/images/logo.svg" alt="HB Track" className="h-8"
                  onError={(e) => { (e.target as HTMLImageElement).src = '/generated/images/logo-dark.svg'; }} />
              </Link>
              <button onClick={() => setDrawerOpen(false)} className="text-gray-400 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>
            <NavGroupList onNavigate={() => setDrawerOpen(false)} />
            <div className="border-t border-gray-800 p-3">
              <div className="flex items-center gap-2">
                <UserAvatar
                  avatarUrl={(user as { avatarUrl?: string } | null)?.avatarUrl}
                  name={(user as { displayName?: string } | null)?.displayName}
                  email={user?.email}
                  size="sm"
                />
                <div className="flex-1 min-w-0">
                  <p className="truncate text-xs font-medium text-white">{user?.email ?? 'Usuário'}</p>
                </div>
                <button onClick={handleLogout} className="rounded p-1 text-gray-400 hover:text-white" title="Sair">
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>
          </aside>
        </div>
      )}

      {/* ── Área principal ─────────────────────────────────────────────────── */}
      <div className={`flex flex-1 flex-col overflow-hidden transition-all duration-200 ${collapsed ? 'lg:pl-16' : 'lg:pl-64'}`}>
        {/* ── Top bar (UX_SHELL_CONTRACT §3) ─────────────────────────────── */}
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b bg-white px-4 lg:px-6 shadow-sm">
          {/* hamburger mobile */}
          <button
            className="lg:hidden rounded-md p-2 text-gray-500 hover:bg-gray-100"
            onClick={() => setDrawerOpen(true)}
            aria-label="Abrir menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Breadcrumbs (UX_SHELL_CONTRACT §3) */}
          <nav aria-label="breadcrumbs" className="hidden sm:flex items-center gap-1 text-sm text-gray-500 min-w-0 flex-1">
            <Link to="/" className="hover:text-gray-900 shrink-0">Dashboard</Link>
            {breadcrumbs.map((crumb, i) => (
              <Fragment key={crumb.to}>
                <span className="text-gray-300">/</span>
                {i === breadcrumbs.length - 1 ? (
                  <span className="text-gray-900 font-medium truncate">{crumb.label}</span>
                ) : (
                  <Link to={crumb.to} className="hover:text-gray-900 truncate">{crumb.label}</Link>
                )}
              </Fragment>
            ))}
          </nav>

          <div className="flex items-center gap-2 ml-auto">
            {/* Command palette (UX_SHELL_CONTRACT §3) */}
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-sm text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              aria-label="Abrir command palette"
              title="Command palette (⌘K)"
            >
              <Search className="h-4 w-4" />
              <span className="hidden sm:block text-xs">Buscar…</span>
              <kbd className="hidden sm:block ml-1 rounded bg-gray-200 px-1 py-0.5 text-[10px] text-gray-500">⌘K</kbd>
            </button>

            {/* Notificações (UX_SHELL_CONTRACT §3) */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen((o) => !o)}
                className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                aria-label="Notificações"
              >
                <Bell className="h-5 w-5" />
                <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-blue-500" />
              </button>
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-72 rounded-lg border border-gray-200 bg-white shadow-lg py-2 z-50">
                  <p className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-gray-500">Notificações</p>
                  <p className="px-4 py-3 text-sm text-gray-500">Nenhuma notificação no momento.</p>
                </div>
              )}
            </div>

            {/* Avatar + User menu (UX_SHELL_CONTRACT §3) */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen((o) => !o)}
                className="flex items-center gap-2 rounded-lg p-1.5 hover:bg-gray-100"
                aria-label="Menu do usuário"
                aria-expanded={userMenuOpen}
              >
                {/* avatar circular com fallback para iniciais (avatar fallback) */}
                <UserAvatar
                  avatarUrl={(user as { avatarUrl?: string } | null)?.avatarUrl}
                  name={(user as { displayName?: string } | null)?.displayName}
                  email={user?.email}
                />
                <ChevronDown className="h-3.5 w-3.5 text-gray-500 hidden sm:block" />
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-lg border border-gray-200 bg-white shadow-lg py-1 z-50">
                  <div className="px-3 py-2 border-b border-gray-100">
                    <p className="text-xs font-medium text-gray-900 truncate">{user?.email ?? 'Usuário'}</p>
                  </div>
                  <Link
                    to="/conta-acesso"
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <UserCircle className="h-4 w-4" />
                    Conta e Acesso
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="h-4 w-4" />
                    Sair
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Command palette modal */}
        {commandPaletteOpen && (
          <div
            className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/40 backdrop-blur-sm"
            onClick={() => setCommandPaletteOpen(false)}
          >
            <div
              className="w-full max-w-lg rounded-xl bg-white shadow-2xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-label="Command palette"
            >
              <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-100">
                <Search className="h-5 w-5 text-gray-400 shrink-0" />
                <input
                  autoFocus
                  type="text"
                  placeholder="Buscar módulo, ação ou atalho…"
                  className="flex-1 bg-transparent text-sm text-gray-900 outline-none placeholder-gray-400"
                />
                <kbd className="text-xs text-gray-400 bg-gray-100 rounded px-1.5 py-0.5">Esc</kbd>
              </div>
              <div className="p-2 text-xs text-gray-400 text-center py-4">
                Digite para buscar
              </div>
            </div>
          </div>
        )}

        {/* ── Conteúdo da página ──────────────────────────────────────────── */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

// ── NavItemRow ──────────────────────────────────────────────────────────────
function NavItemRow({
  item,
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const { to, icon: Icon, label, disabled, badge } = item;

  if (disabled) {
    return (
      <div
        className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-gray-600 cursor-not-allowed select-none"
        title={badge ? `${label} — ${badge}` : label}
      >
        <Icon className="h-4 w-4 shrink-0 opacity-50" />
        {!collapsed && (
          <>
            <span className="flex-1 truncate opacity-60">{label}</span>
            {badge && (
              <span className="badge rounded-full bg-gray-700 px-1.5 py-0.5 text-[9px] uppercase tracking-wider text-gray-400">
                {badge}
              </span>
            )}
          </>
        )}
      </div>
    );
  }

  return (
    <NavLink
      to={to}
      end={to === '/'}
      onClick={onNavigate}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${isActive
          ? 'bg-blue-700 text-white'
          : 'text-gray-300 hover:bg-gray-800 hover:text-white'
        }`
      }
      title={collapsed ? label : undefined}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed && <span className="flex-1 truncate">{label}</span>}
      {!collapsed && badge && (
        <span className="badge rounded-full bg-blue-900 px-1.5 py-0.5 text-[9px] uppercase tracking-wider text-blue-300">
          {badge}
        </span>
      )}
    </NavLink>
  );
}

