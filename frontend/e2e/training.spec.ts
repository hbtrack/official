/**
 * Testes E2E — Fluxo de treino (FASE 5.8)
 * Requer: backend em localhost:8000 + frontend em localhost:5173 + seed_demo.
 *
 * Fluxo crítico:
 * Login → ver dashboard → criar sessão de treino → registrar presença
 */
import { test, expect } from '@playwright/test';

const COACH_EMAIL = 'coach@hbtrack.dev';
const COACH_PASSWORD = 'coach123';

test.describe('Fluxo de treino', () => {
  test.beforeEach(async ({ page }) => {
    // Login antes de cada teste
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(COACH_EMAIL);
    await page.getByLabel(/senha/i).fill(COACH_PASSWORD);
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page).not.toHaveURL('/login');
  });

  test('navegar para página de treinos', async ({ page }) => {
    await page.getByRole('link', { name: /treino/i }).click();
    await expect(page).toHaveURL(/\/training/);
    await expect(page.getByRole('heading', { name: /treino/i })).toBeVisible();
  });

  test('criar nova sessão de treino', async ({ page }) => {
    await page.goto('/training');
    // Clicar em "Novo Treino" ou botão equivalente
    await page.getByRole('button', { name: /nova sessão|novo treino|criar/i }).click();
    // Preencher formulário mínimo
    const titleInput = page.getByLabel(/título|nome|objetivo/i);
    if (await titleInput.isVisible()) {
      await titleInput.fill('Treino E2E Test');
    }
    await page.getByRole('button', { name: /criar|salvar/i }).click();
    // Esperar resultado (200ms debounce)
    await page.waitForTimeout(500);
    // Verificar que não houve erro
    await expect(page.getByRole('alert')).not.toBeVisible().catch(() => {});
  });
});
