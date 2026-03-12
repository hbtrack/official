// src/design/primitives/Button.tsx
import { tokens } from "@/design/tokens";

type ButtonProps = {
  testId: string;
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
};

export function Button({ testId, children, disabled, onClick }: ButtonProps) {
  return (
    <button
      data-test-id={testId}
      onClick={onClick}
      disabled={disabled}
      style={{
        minHeight: tokens.form.controlHeight.md,
        paddingInline: tokens.spacing.lg,
        borderRadius: tokens.radius.md,
        borderWidth: tokens.borderWidth.sm,
        borderStyle: "solid",
        borderColor: tokens.colors.border.default,
        background: tokens.colors.action.primary,
        color: tokens.colors.text.inverse,
        boxShadow: tokens.shadow.sm,
        fontFamily: tokens.typography.fontFamily.sans,
        fontSize: tokens.typography.fontSize.sm,
        fontWeight: tokens.typography.fontWeight.semibold,
      }}
    >
      {children}
    </button>
  );
}