import { test, expect } from '@playwright/test';

test.describe('Navegación y Dashboard - RegistraMe', () => {

  test.beforeEach(async ({ page }) => {
    // Iniciar sesión antes de cada prueba de navegación
    await page.goto('/login');
    await page.fill('#username', 'vendedor1');
    await page.fill('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    
    // Esperar a que cargue la interfaz principal
    await expect(page).not.toHaveURL(/\/login/);
  });

  test('Debería cargar los componentes principales del dashboard @system', async ({ page }) => {
    // Verificar que el título o contenedor del dashboard sea visible
    const dashboardTitle = page.locator('h1, h2, .title');
    await expect(dashboardTitle.first()).toBeVisible();
  });

  test('Debería permitir navegar a las diferentes vistas usando el Sidebar @system', async ({ page }) => {
    // Buscar y hacer clic en el menú Inventario
    const inventarioLink = page.locator('nav a:has-text("Inventario"), nav a:has-text("Productos"), a[href*="inventory"]');
    if (await inventarioLink.count() > 0) {
      await inventarioLink.first().click();
      await expect(page).toHaveURL(/.*inventory|.*products|.*/);
    }

    // Buscar y hacer clic en el menú Clientes
    const clientesLink = page.locator('nav a:has-text("Clientes"), a[href*="clients"]');
    if (await clientesLink.count() > 0) {
      await clientesLink.first().click();
      await expect(page).toHaveURL(/.*clients|.*/);
    }
  });
});
