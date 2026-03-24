import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './shared/components/ProtectedRoute';
import { AppLayout } from './shared/layouts/AppLayout';
import { LoginPage } from './features/auth/pages/LoginPage';
import { DashboardPage } from './features/dashboard/pages/DashboardPage';
import { UsersPage } from './features/users/pages/UsersPage';
import { UserDetailPage } from './features/users/pages/UserDetailPage';
import { TeamsPage } from './features/teams/pages/TeamsPage';
import { TeamDetailPage } from './features/teams/pages/TeamDetailPage';
import { SeasonsPage } from './features/seasons/pages/SeasonsPage';
import { SeasonDetailPage } from './features/seasons/pages/SeasonDetailPage';
import { TrainingPage } from './features/training/pages/TrainingPage';
import { TrainingDetailPage } from './features/training/pages/TrainingDetailPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/users/:userId" element={<UserDetailPage />} />
            <Route path="/teams" element={<TeamsPage />} />
            <Route path="/teams/:teamId" element={<TeamDetailPage />} />
            <Route path="/seasons" element={<SeasonsPage />} />
            <Route path="/seasons/:seasonId" element={<SeasonDetailPage />} />
            <Route path="/training" element={<TrainingPage />} />
            <Route path="/training/:id" element={<TrainingDetailPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
