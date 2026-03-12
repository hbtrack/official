/**
 * PageLayout
 *
 * Shell da página administrativa. Define background canônico e altura mínima.
 *
 * Regras de uso (TRAINING_UI_CONTRACT.md §6):
 * - Toda SCREEN deve começar em PageLayout.
 * - Sem padding próprio — padding é responsabilidade do layout filho.
 * - Sem lógica de domínio, sem fetch, sem state.
 * - style={{}} é permitido neste arquivo porque consome exclusivamente tokens.
 *   CSS inline está proibido apenas quando usaria valores arbitrários ou literais.
 *
 * Nota: usa 100dvh (dynamic viewport height) em vez de 100vh para evitar
 * o bug de viewport em browsers móveis (Safari iOS e equivalentes).
 */

import { tokens } from "@/design/tokens";

type PageLayoutProps = {
  testId: string;
  children: React.ReactNode;
};

export function PageLayout({ testId, children }: PageLayoutProps) {
  return (
    <div
      data-test-id={testId}
      style={{
        minHeight: "100dvh",
        backgroundColor: tokens.colors.bg.app,
        fontFamily: tokens.typography.fontFamily.sans,
      }}
    >
      {children}
    </div>
  );
}
