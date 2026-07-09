import { test, expect } from '@playwright/test';

test.describe('E2E-AUTH: Persistencia de sesión - RegistraMe', () => {

  /** E2E-AUTH-04: Persistencia de sesión */
  test('Debería mantener la sesión al recargar la página @acceptance', async ({ page }) => {
    // Arrange: Login exitoso como admin
    await page.goto('/');
    await page.fill('#username', process.env.TEST_USER ?? 'admin');
    await page.fill('#password', process.env.TEST_PASSWORD ?? 'admin123');
    await page.click('button[type="submit"]');

    // Assert: Redirige al dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    const welcomeMessage = page.locator('p:has-text("Bienvenido")');
    await expect(welcomeMessage).toBeVisible();

    // Act: Recargar la página (simula cierre y reapertura del navegador)
    await page.reload();

    // Assert: Sigue en dashboard sin pedir login
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(welcomeMessage).toBeVisible();
  });
});
