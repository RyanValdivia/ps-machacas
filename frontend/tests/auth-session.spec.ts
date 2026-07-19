import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('E2E-AUTH: Persistencia de sesión - RegistraMe', () => {

  /** E2E-AUTH-04: Persistencia de sesión */
  test('Debería mantener la sesión al recargar la página @acceptance', async ({ page }) => {
    // Arrange: Login exitoso como admin
    await loginAs(page, process.env.TEST_USER ?? 'admin', process.env.TEST_PASSWORD ?? 'admin123');

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
