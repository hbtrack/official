/**
 * FormLayout
 *
 * Container para telas de formulário e edição. Largura reduzida (contentMaxWidth)
 * e padding de seção canônico.
 *
 * Regras de uso (TRAINING_UI_CONTRACT.md §6):
 * - Usado dentro de PageLayout para telas narrow (formulários, wizards).
 * - max-width lido de tokens.layout.contentMaxWidth (960px).
 * - Padding lido de tokens.trainingUi.cardPadding.
 * - style={{}} é permitido neste arquivo porque consome exclusivamente tokens.
 *   CSS inline está proibido apenas quando usaria valores arbitrários ou literais.
 */

import { tokens } from "@/design/tokens";

type FormLayoutProps = {
  testId: string;
  children: React.ReactNode;
};

export function FormLayout({ testId, children }: FormLayoutProps) {
  return (
    <main
      data-test-id={testId}
      style={{
        maxWidth: tokens.layout.contentMaxWidth,
        marginInline: "auto",
        padding: tokens.trainingUi.cardPadding,
      }}
    >
      {children}
    </main>
  );
}
