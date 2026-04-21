/**
 * ResetPasswordPage — Nova senha (via token de reset)
 * Conformidade: AUTH_EXPERIENCE_CONTRACT.md §3
 *
 * Estados obrigatórios: "token inválido/expirado", "senha redefinida com sucesso"
 * (AUTH_EXPERIENCE_CONTRACT §4)
 */

import { ArrowLeft, Eye, EyeOff } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useResetPassword } from '../../../api/hooks/useAuth';

type PageState = 'idle' | 'senha redefinida com sucesso' | 'token invalido' | 'error';

export function ResetPasswordPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get('token') ?? '';

    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [pageState, setPageState] = useState<PageState>('idle');
    const [errorMsg, setErrorMsg] = useState('');
    const resetMutation = useResetPassword();

    const passwordsMatch = newPassword === confirmPassword;
    const isFormValid = newPassword.length >= 8 && passwordsMatch;

    function handleSubmit(e: FormEvent) {
        e.preventDefault();
        if (!isFormValid) return;
        setErrorMsg('');
        resetMutation.mutate(
            { token, newPassword, confirmPassword },
            {
                onSuccess: () => setPageState('senha redefinida com sucesso'),
                onError: (err: unknown) => {
                    const status = (err as { status?: number })?.status;
                    if (status === 401 || status === 404) {
                        setPageState('token invalido');
                        setErrorMsg('Token inválido ou expirado. Solicite um novo link de redefinição.');
                    } else {
                        setPageState('error');
                        setErrorMsg('Não foi possível redefinir a senha. Tente novamente.');
                    }
                },
            }
        );
    }

    if (pageState === 'senha redefinida com sucesso') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
                <div className="w-full max-w-md">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-800 text-center">
                        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-600">
                            ✅
                        </div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Senha redefinida com sucesso</h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                            Sua nova senha foi definida. Você já pode fazer login.
                        </p>
                        <button
                            onClick={() => navigate('/login', { replace: true })}
                            className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                        >
                            Ir para o login
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (pageState === 'token invalido') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
                <div className="w-full max-w-md">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-800 text-center">
                        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600">
                            ⚠️
                        </div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Token inválido ou expirado</h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">{errorMsg}</p>
                        <Link
                            to="/forgot-password"
                            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                        >
                            Solicitar novo link
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
            <div className="w-full max-w-md">
                <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-800">
                    <div className="text-center mb-6">
                        <picture>
                            <source srcSet="/generated/images/auth-logo-dark.svg" media="(prefers-color-scheme: dark)" />
                            <img
                                src="/generated/images/auth-logo.svg"
                                alt="HB Track"
                                className="mx-auto h-10 w-auto mb-3"
                                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                            />
                        </picture>
                        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Nova senha</h1>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Dados que decidem jogos</p>
                    </div>

                    <form onSubmit={handleSubmit} noValidate className="space-y-4">
                        <div>
                            <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Nova senha
                            </label>
                            <div className="relative">
                                <input
                                    id="new-password"
                                    type={showPassword ? 'text' : 'password'}
                                    required
                                    minLength={8}
                                    autoComplete="new-password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 pr-10 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Mínimo 8 caracteres"
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

                        <div>
                            <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Confirmar nova senha
                            </label>
                            <input
                                id="confirm-password"
                                type={showPassword ? 'text' : 'password'}
                                required
                                autoComplete="new-password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Repita a nova senha"
                            />
                        </div>

                        {confirmPassword && !passwordsMatch && (
                            <p className="text-xs text-red-600">As senhas não coincidem.</p>
                        )}

                        {pageState === 'error' && (
                            <div role="alert" className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                                {errorMsg}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={!isFormValid || resetMutation.isPending}
                            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {resetMutation.isPending ? 'Salvando...' : 'Definir nova senha'}
                        </button>
                    </form>

                    <div className="mt-4 text-center">
                        <Link to="/login" className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline">
                            <ArrowLeft className="h-3 w-3" />
                            Voltar para o login
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
