/**
 * DashboardLayout
 *
 * Container principal para páginas administrativas de listagem e visualização.
 * Define largura máxima e paddings canônicos via tokens — sem utilitários
 * Tailwind parametrizados (px-6, lg:px-8 etc.), que introduziriam valores
 * arbitrários fora do design system.
 *
 * Regras de uso (TRAINING_UI_CONTRACT.md §6):
 * - Usado dentro de PageLayout.
 * - Padding horizontal e vertical lidos exclusivamente de tokens.spacing.
 * - max-width lido de tokens.layout.pageMaxWidth (1600px — canônico global).
 * - style={{}} é permitido neste arquivo porque consome exclusivamente tokens.
 *   CSS inline está proibido apenas quando usaria valores arbitrários ou literais.
 */

import { tokens } from "@/design/tokens";

type DashboardLayoutProps = {
  testId: string;
  children: React.ReactNode;
};

export function DashboardLayout({ testId, children }: DashboardLayoutProps) {
  return (
    <main
      data-test-id={testId}
      style={{
        maxWidth: tokens.layout.pageMaxWidth,
        marginInline: "auto",
        paddingInline: tokens.spacing.xl,
        paddingBlock: tokens.spacing.lg,
      }}
    >
      {children}
    </main>
  );
}
