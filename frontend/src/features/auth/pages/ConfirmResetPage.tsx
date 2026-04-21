/**
 * ConfirmResetPage — Confirmação de conclusão do reset
 * Conformidade: AUTH_EXPERIENCE_CONTRACT.md §3
 * Sustenta o estado final de "senha redefinida com sucesso"
 */

import { Link } from 'react-router-dom';

export function ConfirmResetPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
            <div className="w-full max-w-md">
                <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-100 dark:border-gray-800 text-center">
                    <picture>
                        <source srcSet="/generated/images/auth-logo-dark.svg" media="(prefers-color-scheme: dark)" />
                        <img
                            src="/generated/images/auth-logo.svg"
                            alt="HB Track"
                            className="mx-auto h-10 w-auto mb-6"
                            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                        />
                    </picture>
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-600">
                        ✅
                    </div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                        Senha redefinida com sucesso
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                        Sua senha foi alterada. Acesse a plataforma para continuar.
                    </p>
                    <p className="text-xs text-gray-400 italic mb-4">Dados que decidem jogos</p>
                    <Link
                        to="/login"
                        className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                    >
                        Ir para o login
                    </Link>
                </div>
            </div>
        </div>
    );
}
