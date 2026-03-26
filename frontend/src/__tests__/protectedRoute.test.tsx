/**
 * Testes de ProtectedRoute — FASE 5.3
 * Valida que logout expira sessão e rota protegida redireciona para /login.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { ProtectedRoute } from '../shared/components/ProtectedRoute';

const FAKE_USER = {
  id: 'u1', username: 'coach', email: 'coach@hbtrack.dev',
  organization_id: 'org1', roles: ['COACH'],
};

function TestApp({ initialPath }: { initialPath: string }) {
  return (
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<div>Página de Login</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ user: null, token: null, isAuthenticated: false });
  });

  it('redireciona para /login quando não autenticado', () => {
    render(<TestApp initialPath="/dashboard" />);
    expect(screen.getByText('Página de Login')).toBeInTheDocument();
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
  });

  it('exibe o conteúdo protegido quando autenticado', () => {
    useAuthStore.setState({ user: FAKE_USER, token: 'tok', isAuthenticated: true });
    render(<TestApp initialPath="/dashboard" />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.queryByText('Página de Login')).not.toBeInTheDocument();
  });

  it('após logout, rota protegida redireciona para /login', () => {
    useAuthStore.setState({ user: FAKE_USER, token: 'tok', isAuthenticated: true });
    // Simular logout
    useAuthStore.getState().logout();
    render(<TestApp initialPath="/dashboard" />);
    expect(screen.getByText('Página de Login')).toBeInTheDocument();
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
  });
});
