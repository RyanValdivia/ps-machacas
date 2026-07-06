# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard.spec.ts >> Navegación y Dashboard - RegistraMe >> Debería cargar los componentes principales del dashboard @system
- Location: tests/dashboard.spec.ts:16:3

# Error details

```
Error: expect(page).not.toHaveURL(expected) failed

Expected pattern: not /\/login/
Received string: "http://localhost:5173/login"
Timeout: 5000ms

Call log:
  - Expect "not toHaveURL" with timeout 5000ms
    13 × unexpected value "http://localhost:5173/login"

```

```yaml
- heading "Iniciar Sesión" [level=1]
- text: Usuario
- textbox "Usuario":
  - /placeholder: Ingrese su usuario
  - text: vendedor1
- text: Contraseña
- textbox "Contraseña":
  - /placeholder: Ingrese su contraseña
  - text: Admin123!
- button "Entrar"
- paragraph: Usuario o contraseña incorrectos
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Navegación y Dashboard - RegistraMe', () => {
  4  | 
  5  |   test.beforeEach(async ({ page }) => {
  6  |     // Iniciar sesión antes de cada prueba de navegación
  7  |     await page.goto('/login');
  8  |     await page.fill('#username', 'vendedor1');
  9  |     await page.fill('#password', 'Admin123!');
  10 |     await page.click('button[type="submit"]');
  11 |     
  12 |     // Esperar a que cargue la interfaz principal
> 13 |     await expect(page).not.toHaveURL(/\/login/);
     |                            ^ Error: expect(page).not.toHaveURL(expected) failed
  14 |   });
  15 | 
  16 |   test('Debería cargar los componentes principales del dashboard @system', async ({ page }) => {
  17 |     // Verificar que el título o contenedor del dashboard sea visible
  18 |     const dashboardTitle = page.locator('h1, h2, .title');
  19 |     await expect(dashboardTitle.first()).toBeVisible();
  20 |   });
  21 | 
  22 |   test('Debería permitir navegar a las diferentes vistas usando el Sidebar @system', async ({ page }) => {
  23 |     // Buscar y hacer clic en el menú Inventario
  24 |     const inventarioLink = page.locator('nav a:has-text("Inventario"), nav a:has-text("Productos"), a[href*="inventory"]');
  25 |     if (await inventarioLink.count() > 0) {
  26 |       await inventarioLink.first().click();
  27 |       await expect(page).toHaveURL(/.*inventory|.*products|.*/);
  28 |     }
  29 | 
  30 |     // Buscar y hacer clic en el menú Clientes
  31 |     const clientesLink = page.locator('nav a:has-text("Clientes"), a[href*="clients"]');
  32 |     if (await clientesLink.count() > 0) {
  33 |       await clientesLink.first().click();
  34 |       await expect(page).toHaveURL(/.*clients|.*/);
  35 |     }
  36 |   });
  37 | });
  38 | 
```