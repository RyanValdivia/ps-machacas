import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

const ENV = {
  VENDEDOR_USER: process.env.TEST_VENDEDOR_USER ?? 'vendedor1',
  VENDEDOR_PASS: process.env.TEST_VENDEDOR_PASS ?? 'Admin123!',
  GERENTE_USER: process.env.TEST_GERENTE_USER ?? 'gerente1',
  GERENTE_PASS: process.env.TEST_GERENTE_PASS ?? 'Admin123!',
  LOGISTICA_USER: process.env.TEST_LOGISTICA_USER ?? 'logistica1',
  LOGISTICA_PASS: process.env.TEST_LOGISTICA_PASS ?? 'Admin123!',
  OPTOMETRA_USER: process.env.TEST_OPTOMETRA_USER ?? 'optometra1',
  OPTOMETRA_PASS: process.env.TEST_OPTOMETRA_PASS ?? 'Admin123!',
};

const DENIED = page => page.locator('h2:has-text("Acceso restringido")');

test.describe('E2E-AUTH: Roles y permisos - RegistraMe', () => {

  /** E2E-AUTH-03A: Bloqueo de rutas por nivel de acceso */
  test('Debería bloquear rutas no autorizadas para usuario nivel 2 @acceptance', async ({ page }) => {
    // Arrange: Login como vendedor1 (nivel 2)
    await loginAs(page, ENV.VENDEDOR_USER, ENV.VENDEDOR_PASS);

    // Act 1: Navegar directamente a /settings (nivel 0-1)
    await page.goto('/settings');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 2: Navegar a /reports (nivel 0-1)
    await page.goto('/reports');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 3: Navegar a /inventory (nivel 0,1,3)
    await page.goto('/inventory');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 4: Navegar a /sales (nivel 0,1,2)
    await page.goto('/sales');
    // Assert: Acceso permitido (nivel 2 está en [0,1,2])
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/sales/);
  });

  /** E2E-AUTH-03B: Acceso total para gerente1 (nivel 0) */
  test('Debería permitir acceso a todas las rutas para gerente1 @acceptance', async ({ page }) => {
    // Arrange: Login como gerente1 (nivel 0)
    await loginAs(page, ENV.GERENTE_USER, ENV.GERENTE_PASS);

    // Act 1: Navegar a /settings
    await page.goto('/settings');
    // Assert: Acceso permitido (sin mensaje de restricción)
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/settings/);

    // Act 2: Navegar a /reports
    await page.goto('/reports');
    // Assert: Acceso permitido
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/reports/);

    // Act 3: Navegar a /inventory
    await page.goto('/inventory');
    // Assert: Acceso permitido
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/inventory/);

    // Act 4: Navegar a /sales
    await page.goto('/sales');
    // Assert: Acceso permitido
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/sales/);

    // Act 5: Navegar a /prescriptions
    await page.goto('/prescriptions');
    // Assert: Acceso permitido
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/prescriptions/);
  });

  /** E2E-AUTH-03C: Acceso solo a inventory para logistica1 (nivel 3) */
  test('Debería permitir solo inventory para logistica1 @acceptance', async ({ page }) => {
    // Arrange: Login como logistica1 (nivel 3)
    await loginAs(page, ENV.LOGISTICA_USER, ENV.LOGISTICA_PASS);

    // Act 1: Navegar a /inventory (nivel 0,1,3)
    await page.goto('/inventory');
    // Assert: Acceso permitido
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/inventory/);

    // Act 2: Navegar a /settings (nivel 0-1)
    await page.goto('/settings');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 3: Navegar a /reports (nivel 0-1)
    await page.goto('/reports');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 4: Navegar a /sales (nivel 0,1,2)
    await page.goto('/sales');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();
  });

  /** E2E-AUTH-03D: Acceso solo a prescriptions para optometra1 (nivel 4) */
  test('Debería permitir solo prescriptions para optometra1 @acceptance', async ({ page }) => {
    // Arrange: Login como optometra1 (nivel 4)
    await loginAs(page, ENV.OPTOMETRA_USER, ENV.OPTOMETRA_PASS);

    // Act 1: Navegar a /prescriptions (nivel 0,1,4)
    await page.goto('/prescriptions');
    // Assert: Acceso permitido
    await expect(DENIED(page)).not.toBeVisible();
    await expect(page).toHaveURL(/\/prescriptions/);

    // Act 2: Navegar a /settings (nivel 0-1)
    await page.goto('/settings');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 3: Navegar a /reports (nivel 0-1)
    await page.goto('/reports');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();

    // Act 4: Navegar a /inventory (nivel 0,1,3)
    await page.goto('/inventory');
    // Assert: Muestra mensaje de acceso denegado
    await expect(DENIED(page)).toBeVisible();
  });
});
