// src/design/tokens.ts
// SSOT de design tokens do HB Track / TRAINING
// Proibido hardcode de cores, spacing, radius, shadow e z-index fora deste arquivo.

export const spacing = {
  none: "0",
  xs: "0.25rem",   // 4px
  sm: "0.5rem",    // 8px
  md: "0.75rem",   // 12px
  lg: "1rem",      // 16px
  xl: "1.5rem",    // 24px
  "2xl": "2rem",   // 32px
  "3xl": "3rem",   // 48px
} as const;

export const radius = {
  none: "0",
  sm: "0.375rem",  // 6px
  md: "0.5rem",    // 8px
  lg: "0.75rem",   // 12px
  xl: "1rem",      // 16px
  full: "9999px",
} as const;

export const borderWidth = {
  none: "0",
  sm: "1px",
  md: "2px",
} as const;

export const shadow = {
  none: "none",
  sm: "0 1px 2px rgba(0,0,0,0.06)",
  md: "0 4px 12px rgba(0,0,0,0.08)",
  lg: "0 10px 24px rgba(0,0,0,0.10)",
} as const;

export const zIndex = {
  base: 0,
  dropdown: 10,
  sticky: 20,
  overlay: 30,
  modal: 40,
  toast: 50,
} as const;

export const typography = {
  fontFamily: {
    sans: "Inter, ui-sans-serif, system-ui, sans-serif",
    mono: "ui-monospace, SFMono-Regular, Menlo, monospace",
  },
  fontSize: {
    xs: "0.75rem",   // 12px
    sm: "0.875rem",  // 14px
    md: "1rem",      // 16px
    lg: "1.125rem",  // 18px
    xl: "1.25rem",   // 20px
    "2xl": "1.5rem", // 24px
  },
  lineHeight: {
    tight: "1.2",
    normal: "1.5",
    relaxed: "1.7",
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const;

// As cores devem apontar para CSS variables.
// Proibido hex direto aqui se você quiser suportar theming/light-dark mode com segurança.
export const colors = {
  bg: {
    app: "var(--color-bg-app)",
    surface: "var(--color-bg-surface)",
    muted: "var(--color-bg-muted)",
    elevated: "var(--color-bg-elevated)",
  },
  text: {
    primary: "var(--color-text-primary)",
    secondary: "var(--color-text-secondary)",
    muted: "var(--color-text-muted)",
    inverse: "var(--color-text-inverse)",
    danger: "var(--color-text-danger)",
    success: "var(--color-text-success)",
    warning: "var(--color-text-warning)",
  },
  border: {
    default: "var(--color-border-default)",
    subtle: "var(--color-border-subtle)",
    strong: "var(--color-border-strong)",
    danger: "var(--color-border-danger)",
    success: "var(--color-border-success)",
    warning: "var(--color-border-warning)",
  },
  action: {
    primary: "var(--color-action-primary)",
    primaryHover: "var(--color-action-primary-hover)",
    secondary: "var(--color-action-secondary)",
    secondaryHover: "var(--color-action-secondary-hover)",
    danger: "var(--color-action-danger)",
    dangerHover: "var(--color-action-danger-hover)",
  },
  state: {
    infoBg: "var(--color-state-info-bg)",
    successBg: "var(--color-state-success-bg)",
    warningBg: "var(--color-state-warning-bg)",
    dangerBg: "var(--color-state-danger-bg)",
  },
} as const;

// pageMaxWidth: decisão canônica 2026-03-09 para páginas administrativas.
// Este valor é global — todos os módulos que consumirem tokens.layout.pageMaxWidth herdam "1600px".
export const layout = {
  pageMaxWidth: "1600px",
  contentMaxWidth: "960px",
  sidebarWidth: "320px",
  headerHeight: "64px",
  tableRowHeight: "44px",
} as const;

export const motion = {
  duration: {
    fast: "120ms",
    normal: "180ms",
    slow: "260ms",
  },
  easing: {
    standard: "cubic-bezier(0.2, 0, 0, 1)",
    enter: "cubic-bezier(0, 0, 0, 1)",
    exit: "cubic-bezier(0.4, 0, 1, 1)",
  },
} as const;

// Tokens específicos de densidade e controle de formulários do TRAINING
export const form = {
  controlHeight: {
    sm: "32px",
    md: "40px",
    lg: "48px",
  },
  labelGap: spacing.xs,
  fieldGap: spacing.sm,
  sectionGap: spacing.lg,
} as const;

// Tokens úteis para listas, cards e telas administrativas do TRAINING
export const trainingUi = {
  cardPadding: spacing.lg,
  cardGap: spacing.md,
  sectionGap: spacing.xl,
  pageGap: spacing.xl,
  listItemGap: spacing.sm,
  stickyActionBarOffset: spacing.lg,
} as const;

export const tokens = {
  spacing,
  radius,
  borderWidth,
  shadow,
  zIndex,
  typography,
  colors,
  layout,
  motion,
  form,
  trainingUi,
} as const;

export type SpacingToken = keyof typeof spacing;
export type RadiusToken = keyof typeof radius;
export type ShadowToken = keyof typeof shadow;
export type ZIndexToken = keyof typeof zIndex;
export type FontSizeToken = keyof typeof typography.fontSize;
export type FontWeightToken = keyof typeof typography.fontWeight;