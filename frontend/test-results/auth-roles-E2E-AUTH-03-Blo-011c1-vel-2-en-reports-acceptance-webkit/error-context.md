# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth-roles.spec.ts >> E2E-AUTH-03: Bloqueo de rutas por nivel de acceso >> Debería mostrar "Acceso restringido" al usuario nivel 2 en /reports @acceptance
- Location: tests/auth-roles.spec.ts:6:3

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /\/dashboard/
Received string:  "http://localhost:5173/"
Timeout: 5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    14 × unexpected value "http://localhost:5173/"

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
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('E2E-AUTH-03: Bloqueo de rutas por nivel de acceso', () => {
  4   | 
  5   |   /** Nivel 2 (VENDEDOR/CAJERO) bloqueado de /reports (solo nivel 0,1) */
  6   |   test('Debería mostrar "Acceso restringido" al usuario nivel 2 en /reports @acceptance', async ({ page }) => {
  7   |     // Arrange: Login como vendedor (nivel 2)
  8   |     await page.goto('/');
  9   |     await page.fill('#username', 'vendedor1');
  10  |     await page.fill('#password', 'Admin123!');
  11  |     await page.click('button[type="submit"]');
> 12  |     await expect(page).toHaveURL(/\/dashboard/);
      |                        ^ Error: expect(page).toHaveURL(expected) failed
  13  | 
  14  |     // Act: Navegar a ruta restringida para nivel 2
  15  |     await page.goto('/reports');
  16  | 
  17  |     // Assert: Se muestra componente de acceso restringido
  18  |     await expect(page.locator('h2')).toHaveText('Acceso restringido');
  19  |     await expect(page.locator('text=Niveles requeridos')).toBeVisible();
  20  |     await expect(page.locator('a:has-text("Volver")')).toBeVisible();
  21  |   });
  22  | 
  23  |   /** Nivel 2 bloqueado de /settings (solo nivel 0,1) */
  24  |   test('Debería mostrar "Acceso restringido" al usuario nivel 2 en /settings @acceptance', async ({ page }) => {
  25  |     // Arrange: Login como vendedor (nivel 2)
  26  |     await page.goto('/');
  27  |     await page.fill('#username', 'vendedor1');
  28  |     await page.fill('#password', 'Admin123!');
  29  |     await page.click('button[type="submit"]');
  30  |     await expect(page).toHaveURL(/\/dashboard/);
  31  | 
  32  |     // Act: Navegar a /settings
  33  |     await page.goto('/settings');
  34  | 
  35  |     // Assert
  36  |     await expect(page.locator('h2')).toHaveText('Acceso restringido');
  37  |   });
  38  | 
  39  |   /** Nivel 2 bloqueado de /prescriptions (solo nivel 0,1,4) */
  40  |   test('Debería mostrar "Acceso restringido" al usuario nivel 2 en /prescriptions @acceptance', async ({ page }) => {
  41  |     // Arrange: Login como vendedor (nivel 2)
  42  |     await page.goto('/');
  43  |     await page.fill('#username', 'vendedor1');
  44  |     await page.fill('#password', 'Admin123!');
  45  |     await page.click('button[type="submit"]');
  46  |     await expect(page).toHaveURL(/\/dashboard/);
  47  | 
  48  |     // Act: Navegar a /prescriptions
  49  |     await page.goto('/prescriptions');
  50  | 
  51  |     // Assert
  52  |     await expect(page.locator('h2')).toHaveText('Acceso restringido');
  53  |   });
  54  | 
  55  |   /** Nivel 2 puede acceder a rutas permitidas (nivel 2: /sales) */
  56  |   test('Debería permitir acceso a /sales para usuario nivel 2 @acceptance', async ({ page }) => {
  57  |     // Arrange: Login como vendedor (nivel 2)
  58  |     await page.goto('/');
  59  |     await page.fill('#username', 'vendedor1');
  60  |     await page.fill('#password', 'Admin123!');
  61  |     await page.click('button[type="submit"]');
  62  |     await expect(page).toHaveURL(/\/dashboard/);
  63  | 
  64  |     // Act: Navegar a ruta permitida para nivel 2
  65  |     await page.goto('/sales');
  66  | 
  67  |     // Assert: No muestra restricción (puede cargar cualquier contenido)
  68  |     await expect(page.locator('h2:has-text("Acceso restringido")')).toHaveCount(0);
  69  |   });
  70  | 
  71  |   /** Nivel 0 (GERENTE) accede sin restricción a /reports */
  72  |   test('Debería permitir acceso a /reports para usuario nivel 0 @acceptance', async ({ page }) => {
  73  |     // Arrange: Login como admin (nivel 0)
  74  |     await page.goto('/');
  75  |     await page.fill('#username', 'admin');
  76  |     await page.fill('#password', 'admin123');
  77  |     await page.click('button[type="submit"]');
  78  |     await expect(page).toHaveURL(/\/dashboard/);
  79  | 
  80  |     // Act: Navegar a ruta que sería restringida para niveles inferiores
  81  |     await page.goto('/reports');
  82  | 
  83  |     // Assert: No muestra restricción
  84  |     await expect(page.locator('h2:has-text("Acceso restringido")')).toHaveCount(0);
  85  |   });
  86  | 
  87  |   /** Nivel 0 accede sin restricción a /settings */
  88  |   test('Debería permitir acceso a /settings para usuario nivel 0 @acceptance', async ({ page }) => {
  89  |     // Arrange: Login como admin (nivel 0)
  90  |     await page.goto('/');
  91  |     await page.fill('#username', 'admin');
  92  |     await page.fill('#password', 'admin123');
  93  |     await page.click('button[type="submit"]');
  94  |     await expect(page).toHaveURL(/\/dashboard/);
  95  | 
  96  |     // Act: Navegar a /settings
  97  |     await page.goto('/settings');
  98  | 
  99  |     // Assert
  100 |     await expect(page.locator('h2:has-text("Acceso restringido")')).toHaveCount(0);
  101 |   });
  102 | 
  103 |   /** Nivel 2 redirigido al dashboard al hacer clic en "Volver" */
  104 |   test('Debería redirigir al dashboard al hacer clic en Volver desde Acceso restringido @acceptance', async ({ page }) => {
  105 |     // Arrange: Login como vendedor (nivel 2) y navegar a ruta restringida
  106 |     await page.goto('/');
  107 |     await page.fill('#username', 'vendedor1');
  108 |     await page.fill('#password', 'Admin123!');
  109 |     await page.click('button[type="submit"]');
  110 |     await expect(page).toHaveURL(/\/dashboard/);
  111 |     await page.goto('/reports');
  112 |     await expect(page.locator('h2')).toHaveText('Acceso restringido');
```