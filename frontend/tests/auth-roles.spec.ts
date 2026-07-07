import { test, expect } from '@playwright/test';

async function loginAs(page: any, username: string, password: string) {
  await page.goto('/');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/);
}

const DENIED = page => page.locator('h2:has-text("Acceso restringido")');

test.describe('E2E-AUTH: Roles y permisos - RegistraMe', () => {

  /** E2E-AUTH-03A: Bloqueo de rutas por nivel de acceso */
  test('Debería bloquear rutas no autorizadas para usuario nivel 2 @acceptance', async ({ page }) => {
    // Arrange: Login como vendedor1 (nivel 2)
    await loginAs(page, 'vendedor1', 'Admin123!');

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
    await loginAs(page, 'gerente1', 'Admin123!');

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
    await loginAs(page, 'logistica1', 'Admin123!');

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
    await loginAs(page, 'optometra1', 'Admin123!');

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
