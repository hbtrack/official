/**
 * App.tsx — Roteamento principal do HB Track
 * Conformidade: NAVIGATION_VISIBILITY_CONTRACT.md + AUTH_EXPERIENCE_CONTRACT.md
 *
 * Grupos de navegação (NAVIGATION_VISIBILITY_CONTRACT §2):
 *   Início | Organização | Planejamento Técnico | Jogo e Competição | Performance e Saúde | Administração
 *
 * Módulos ativos do primeiro batch (NAVIGATION_VISIBILITY_CONTRACT §3):
 *   Dashboard | Teams | Seasons | Training | Users | Conta e Acesso
 *
 * Módulos visíveis porém desabilitados (NAVIGATION_VISIBILITY_CONTRACT §3):
 *   Competitions | Matches | Scout | Video | Wellness | Medical |
 *   Exercises | Analytics | Reports | AI Ingestion | Audit
 *
 * Top bar capabilities (NAVIGATION_VISIBILITY_CONTRACT §3):
 *   Notificações | Command palette | Breadcrumbs | User menu
 *
 * Fluxo de auth (AUTH_EXPERIENCE_CONTRACT.md §3):
 *   /login | /forgot-password | /reset-password | /confirm-reset
 */

import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { ConfirmResetPage } from './features/auth/pages/ConfirmResetPage';
import { ForgotPasswordPage } from './features/auth/pages/ForgotPasswordPage';
import { LoginPage } from './features/auth/pages/LoginPage';
import { ResetPasswordPage } from './features/auth/pages/ResetPasswordPage';
import { DashboardPage } from './features/dashboard/pages/DashboardPage';
import { SeasonDetailPage } from './features/seasons/pages/SeasonDetailPage';
import { SeasonsPage } from './features/seasons/pages/SeasonsPage';
import { TeamDetailPage } from './features/teams/pages/TeamDetailPage';
import { TeamsPage } from './features/teams/pages/TeamsPage';
import { TrainingDetailPage } from './features/training/pages/TrainingDetailPage';
import { TrainingPage } from './features/training/pages/TrainingPage';
import { UserDetailPage } from './features/users/pages/UserDetailPage';
import { UsersPage } from './features/users/pages/UsersPage';
import { ProtectedRoute } from './shared/components/ProtectedRoute';
import { AppLayout } from './shared/layouts/AppLayout';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ── Auth routes (AUTH_EXPERIENCE_CONTRACT §3) ──────────────── */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/confirm-reset" element={<ConfirmResetPage />} />

        {/* ── Rotas protegidas ────────────────────────────────────────── */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            {/* Início */}
            <Route path="/" element={<DashboardPage />} />

            {/* Organização */}
            <Route path="/users" element={<UsersPage />} />
            <Route path="/users/:userId" element={<UserDetailPage />} />
            <Route path="/teams" element={<TeamsPage />} />
            <Route path="/teams/:teamId" element={<TeamDetailPage />} />
            <Route path="/seasons" element={<SeasonsPage />} />
            <Route path="/seasons/:seasonId" element={<SeasonDetailPage />} />

            {/* Planejamento Técnico */}
            <Route path="/training" element={<TrainingPage />} />
            <Route path="/training/:id" element={<TrainingDetailPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

