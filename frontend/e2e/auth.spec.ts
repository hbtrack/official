/**
 * Testes E2E — Autenticação e rotas protegidas (FASE 5.8)
 * Requer: backend em localhost:8000 + frontend em localhost:5173.
 *
 * Fluxos críticos:
 * 1. Login válido → dashboard
 * 2. Logout → redireciona para /login quando acessa rota protegida
 */
import { test, expect } from '@playwright/test';

const COACH_EMAIL = 'coach@hbtrack.dev';
const COACH_PASSWORD = 'coach123';

test.describe('Autenticação', () => {
  test('login válido redireciona para dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(COACH_EMAIL);
    await page.getByLabel(/senha/i).fill(COACH_PASSWORD);
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page).toHaveURL(/\/(dashboard|training|teams)?$/);
    await expect(page.getByRole('navigation')).toBeVisible();
  });

  test('logout expira sessão e rota protegida redireciona para /login', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(COACH_EMAIL);
    await page.getByLabel(/senha/i).fill(COACH_PASSWORD);
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page).not.toHaveURL('/login');

    // Logout via botão no header/sidebar
    await page.getByRole('button', { name: /logout|sair/i }).click();
    await expect(page).toHaveURL('/login');

    // Tentar acessar rota protegida após logout
    await page.goto('/teams');
    await expect(page).toHaveURL('/login');
  });

  test('acesso direto a rota protegida sem login redireciona para /login', async ({ page }) => {
    // Garantir que não há token no localStorage
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    await page.goto('/teams');
    await expect(page).toHaveURL('/login');
  });
});
