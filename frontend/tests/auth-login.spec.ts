import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

// E2E-AUTH-01/02: Login
// Caso feliz (credenciales válidas → dashboard) y caso negativo
// (credenciales inválidas → mensaje de error en rojo, sin redirigir).
// Punto clave: resaltar que el error se renderiza en la propia vista de login,
// no navega ni expone info de si el usuario existe o no.
test.describe('E2E-AUTH: Autenticación - RegistraMe', () => {

  /** E2E-AUTH-01: Login exitoso */
  test('Debería loguearse exitosamente y redirigir al Dashboard @acceptance', async ({ page }) => {
    // Arrange: Login con credenciales válidas
    await loginAs(page, process.env.TEST_USER ?? 'admin', process.env.TEST_PASSWORD ?? 'admin123');

    // Assert: URL cambia a /dashboard y se muestra "Bienvenido"
    await expect(page).toHaveURL(/\/dashboard/);
    const welcomeMessage = page.locator('p:has-text("Bienvenido")');
    await expect(welcomeMessage).toBeVisible();
  });

  /** E2E-AUTH-02: Login con credenciales inválidas */
  test('Debería mostrar mensaje de error con credenciales incorrectas @acceptance', async ({ page }) => {
    // Arrange:  Navegar al login.
    await page.goto('/');

    // Act: Ingresar credenciales inválidas y enviar.
    await page.fill('#username', 'usuario_invalido');
    await page.fill('#password', 'ClaveIncorrecta123');
    await page.click('button[type="submit"]');

    // Assert:  Aparece mensaje de error en rojo.
    const errorMessage = page.locator('p.text-red-500');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toHaveText('Usuario o contraseña incorrectos');
  });
});
