/**
 * LoginPage — Tela de login do HB Track
 * Conformidade: AUTH_EXPERIENCE_CONTRACT.md §2
 *
 * Assets oficiais: generated/images/auth-logo.svg | generated/images/auth-logo-dark.svg
 * Tagline oficial: "Dados que decidem jogos"
 * Requisitos: toggle senha, Esqueceu a senha?, loading state, erro controlado, redirect pós-login
 */

import { Eye, EyeOff } from 'lucide-react';
import { FormEvent, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLogin } from '../../../api/hooks/useAuth';
import { useAuthStore } from '../../../stores/authStore';

export function LoginPage() {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const loginMutation = useLogin();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  // toggle mostrar/ocultar senha (AUTH_EXPERIENCE_CONTRACT §2)
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Usuário autenticado não deve permanecer na tela de login (AUTH_EXPERIENCE_CONTRACT §5)
  useEffect(() => {
    if (isAuthenticated) navigate('/', { replace: true });
  }, [isAuthenticated, navigate]);

  const formValid = email.trim().length > 0 && password.length >= 8;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErrorMsg('');
    loginMutation.mutate(
      { email: email.trim(), password },
      {
        onSuccess: () => navigate('/', { replace: true }),
        onError: () => setErrorMsg('Credenciais inválidas. Verifique seu email e senha.'),
      }
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-800">
          {/* ── Branding oficial (AUTH_EXPERIENCE_CONTRACT §2) ──────────── */}
          <div className="text-center mb-8">
            <picture>
              <source
                srcSet="/generated/images/auth-logo-dark.svg"
                media="(prefers-color-scheme: dark)"
              />
              <img
                src="/generated/images/auth-logo.svg"
                alt="HB Track"
                className="mx-auto h-12 w-auto mb-4"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            </picture>
            {/* Tagline oficial (AUTH_EXPERIENCE_CONTRACT §2) */}
            <p className="text-sm text-gray-500 dark:text-gray-400">Dados que decidem jogos</p>
          </div>

          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="seu@email.com"
              />
            </div>

            {/* Senha com toggle (AUTH_EXPERIENCE_CONTRACT §2) */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Senha
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 pr-10 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Link Esqueceu a senha (AUTH_EXPERIENCE_CONTRACT §2) */}
            <div className="flex justify-end">
              <Link
                to="/forgot-password"
                className="text-xs text-blue-600 hover:text-blue-700 hover:underline"
              >
                Esqueceu a senha?
              </Link>
            </div>

            {/* Estado de erro de credenciais (AUTH_EXPERIENCE_CONTRACT §4) */}
            {errorMsg && (
              <div
                role="alert"
                className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 px-3 py-2 text-sm text-red-700 dark:text-red-400"
              >
                {errorMsg}
              </div>
            )}

            {/* Botão principal — habilitado só com formulário válido (AUTH_EXPERIENCE_CONTRACT §2) */}
            <button
              type="submit"
              disabled={!formValid || loginMutation.isPending}
              className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {/* loading state (AUTH_EXPERIENCE_CONTRACT §4) */}
              {loginMutation.isPending ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
