/**
 * ForgotPasswordPage — Solicitação de reset de senha
 * Conformidade: AUTH_EXPERIENCE_CONTRACT.md §3
 *
 * Estado obrigatório: "reset solicitado com sucesso" (AUTH_EXPERIENCE_CONTRACT §4)
 */

import { ArrowLeft } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import { useForgotPassword } from '../../../api/hooks/useAuth';

type PageState = 'idle' | 'reset solicitado com sucesso' | 'error';

export function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [pageState, setPageState] = useState<PageState>('idle');
    const [errorMsg, setErrorMsg] = useState('');
    const forgotMutation = useForgotPassword();

    const formValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setErrorMsg('');
        forgotMutation.mutate(email.trim(), {
            onSuccess: () => setPageState('reset solicitado com sucesso'),
            onError: () => {
                setPageState('error');
                setErrorMsg('Não foi possível enviar o email. Tente novamente.');
            },
        });
    }

    if (pageState === 'reset solicitado com sucesso') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
                <div className="w-full max-w-md">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-800 text-center">
                        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-600">
                            ✉️
                        </div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Email enviado</h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                            Se o email <strong>{email}</strong> estiver cadastrado, você receberá um link para redefinir sua senha.
                        </p>
                        <Link
                            to="/login"
                            className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 hover:underline"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            Voltar para o login
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
                        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Recuperar senha</h1>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Informe seu email para receber o link de redefinição.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} noValidate className="space-y-4">
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
                                className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="seu@email.com"
                            />
                        </div>

                        {pageState === 'error' && (
                            <div role="alert" className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                                {errorMsg}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={!formValid || forgotMutation.isPending}
                            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {forgotMutation.isPending ? 'Enviando...' : 'Enviar link de redefinição'}
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
