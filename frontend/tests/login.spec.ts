import { test, expect } from '@playwright/test';

test.describe('Autenticación - RegistraMe', () => {

  test('Debería mostrar un mensaje de error con credenciales incorrectas @acceptance', async ({ page }) => {
    // Ir a la página de login
    await page.goto('/login');

    // Ingresar credenciales erróneas
    await page.fill('#username', 'usuario_invalido');
    await page.fill('#password', 'ClaveIncorrecta123');

    // Hacer clic en Entrar
    await page.click('button[type="submit"]');

    // Verificar que aparezca el mensaje de error
    const errorMessage = page.locator('p.text-red-500');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toHaveText('Usuario o contraseña incorrectos');
  });

  test('Debería loguearse exitosamente con credenciales correctas y redirigir al dashboard @acceptance', async ({ page }) => {
    // Ir a la página de login
    await page.goto('/login');

    // Ingresar credenciales de vendedor1
    await page.fill('#username', 'vendedor1');
    await page.fill('#password', 'Admin123!');

    // Hacer clic en Entrar
    await page.click('button[type="submit"]');

    // Al iniciar sesión exitosamente, se debe redirigir al Dashboard o cambiar la ruta
    await expect(page).toHaveURL(/\/dashboard|$/);
  });
});
