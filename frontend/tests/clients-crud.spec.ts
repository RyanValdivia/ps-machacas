import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';
import path from 'path';
import fs from 'fs';

test.describe('Ruta Crítica 4: Módulo Clínico - Gestión de Clientes y Recetas', () => {

  const testResultsDir = path.resolve(process.cwd(), '../test-results');

  test.beforeAll(async () => {
    // Asegurar existencia del directorio de resultados de pruebas
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }
  });

  test.beforeEach(async ({ page }) => {
    // Establecer un timeout por defecto de 8 segundos para acciones individuales
    page.setDefaultTimeout(8000);
    
    // Escuchar consola del navegador para depuración
    page.on('console', msg => {
      console.log(`[BROWSER CONSOLE] ${msg.type()}: ${msg.text()}`);
    });
  });

  test('E2E-CLI-01 — Registro de cliente con DNI duplicado @acceptance', async ({ page }) => {
    try {
      // a) Iniciar sesión mediante el helper auth.ts
      await loginAs(page, 'gerente1', 'Admin123!');

      // Esperar a que la interfaz cargue completamente y se estabilice
      await page.waitForSelector('nav, button:has-text("Cerrar Sesión"), [href*="logout"]', { timeout: 15000 });
      await page.waitForSelector('aside:has-text("gerente1")', { timeout: 15000 });

      // b) Navegar a la ruta /prescriptions haciendo clic en la opción del sidebar "Clientes"
      await page.click('a:has-text("Clientes")');

      await expect(page.locator('h2:has-text("Prescripciones")')).toBeVisible({ timeout: 10000 });
      
      // Esperar a que cargue la tabla de clientes y se estabilice el DOM
      await page.waitForSelector('table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      // Generar un DNI único para registrar al primer cliente
      const uniqueDni = Math.floor(10000000 + Math.random() * 90000000).toString();

      // c) Hacer clic en el botón o elemento interactivo "Nuevo Cliente"
      await page.click('button:has-text("Nuevo Cliente")');
      await page.waitForTimeout(500); // Evitar race condition de useEffect del Modal
      await expect(page.locator('h3').first()).toHaveText('Agregar Cliente', { timeout: 5000 });

      // d) Llenar el formulario de cliente
      await page.fill('#cliNumDoc', uniqueDni);
      await page.fill('#cliNomCompleto', 'CLIENTE ORIGINAL TEST');
      await page.fill('#cliTelef', '999999999');
      await page.fill('#cliFechaNac', '1990-01-01');

      // e) Hacer clic en "Guardar" / "Submit"
      await page.click('button:has-text("Guardar")');

      // Esperar a que el modal se cierre
      await expect(page.locator('h3:has-text("Cliente")')).not.toBeVisible({ timeout: 10000 });
      await page.waitForTimeout(1000); // Dar un momento para el reload

      // Intentar registrar el mismo DNI por segunda vez para forzar el duplicado
      await page.click('button:has-text("Nuevo Cliente")');
      await page.waitForTimeout(500); // Evitar race condition de useEffect del Modal
      await expect(page.locator('h3').first()).toHaveText('Agregar Cliente', { timeout: 5000 });

      await page.fill('#cliNumDoc', uniqueDni);
      await page.fill('#cliNomCompleto', 'CLIENTE DUPLICADO TEST');
      await page.fill('#cliTelef', '988888888');
      await page.fill('#cliFechaNac', '1995-05-05');

      // e) Guardar para forzar error de constraint
      await page.click('button:has-text("Guardar")');

      // f) Verificar explícitamente mediante aserciones de Playwright (expect)
      // que la interfaz renderice de forma visible un mensaje de error de validación
      const errorMsgLocator = page.locator('text=/DNI ya registrado|Error al guardar cliente|ya existe/i').first();
      await expect(errorMsgLocator).toBeVisible({ timeout: 10000 });

      // g) Tomar un screenshot de evidencia y guardarlo
      const screenshotPath = path.join(testResultsDir, 'e2e-cli-01-dni-duplicado.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });

    } catch (err) {
      console.log('FAIL E2E-CLI-01 URL:', page.url());
      console.log('FAIL E2E-CLI-01 BODY:', await page.evaluate(() => document.body.innerHTML));
      throw err;
    }
  });

  test('E2E-CLI-02 — Registro de receta óptica @acceptance', async ({ page }) => {
    try {
      // a) Asegurar la existencia de un cliente activo en el sistema
      await loginAs(page, 'gerente1', 'Admin123!');
      
      // Esperar a que la interfaz cargue completamente y se estabilice
      await page.waitForSelector('nav, button:has-text("Cerrar Sesión"), [href*="logout"]', { timeout: 15000 });
      await page.waitForSelector('aside:has-text("gerente1")', { timeout: 15000 });

      // b) Navegar a /prescriptions haciendo clic en el sidebar "Clientes"
      await page.click('a:has-text("Clientes")');

      await expect(page.locator('h2:has-text("Prescripciones")')).toBeVisible({ timeout: 10000 });

      // Esperar a que cargue la tabla de clientes y se estabilice el DOM
      await page.waitForSelector('table', { timeout: 10000 });
      await page.waitForTimeout(1000);

      const clientDni = Math.floor(10000000 + Math.random() * 90000000).toString();
      // Nombre empieza con "A " para que aparezca al inicio de la tabla (ordenada por cliNomCompleto desc/asc)
      const clientName = `A CLIENTE RECETA ${clientDni}`;

      // Registrar nuevo cliente
      await page.click('button:has-text("Nuevo Cliente")');
      await page.waitForTimeout(500); // Evitar race condition de useEffect del Modal
      await expect(page.locator('h3').first()).toHaveText('Agregar Cliente', { timeout: 5000 });
      await page.fill('#cliNumDoc', clientDni);
      await page.fill('#cliNomCompleto', clientName);
      await page.fill('#cliTelef', '999111222');
      await page.fill('#cliFechaNac', '1985-05-15');
      await page.click('button:has-text("Guardar")');
      await expect(page.locator('h3:has-text("Cliente")')).not.toBeVisible({ timeout: 10000 });
      await page.waitForTimeout(1500); // Esperar que la tabla se recargue y estabilice

      // b) Seleccionar el cliente de la lista/tabla (está garantizado en la primera página por empezar con "A")
      const clientRow = page.locator('tr').filter({ hasText: clientDni }).first();
      await expect(clientRow).toBeVisible({ timeout: 5000 });

      // c) Abrir el panel de detalles del cliente seleccionado
      await clientRow.locator('button[title="Ver detalle del cliente"]').click();
      await expect(page.locator('h2:has-text("Detalle del cliente")')).toBeVisible({ timeout: 5000 });
      await page.waitForTimeout(1000);

      // d) Acceder al formulario de registro de una "Nueva Receta"
      const registerBtn = page.locator('button:has-text("Registrar primera receta"), button:has-text("Registrar nueva receta")').first();
      await registerBtn.click();
      await expect(page.locator('h3:has-text("Nueva Receta")')).toBeVisible({ timeout: 5000 });

      // Registrar un optometrista si no hay uno disponible o seleccionarlo
      // En entornos limpios no hay optometristas, así que creamos uno de forma robusta
      await page.click('button[title="Agregar optometrista"]');
      await expect(page.locator('input[placeholder="Nombre"]')).toBeVisible({ timeout: 5000 });
      await page.fill('input[placeholder="Nombre"]', 'Juan');
      await page.fill('input[placeholder="Apellido"]', 'Perez');
      // Asegurar que hacemos click al botón Guardar del popup de optometra
      await page.locator('button').filter({ hasText: /^Guardar$/ }).click();
      await expect(page.locator('input[placeholder="Nombre"]')).not.toBeVisible({ timeout: 5000 });
      await page.waitForTimeout(500);

      // e) Llenar los campos clínicos mandatorios de la receta (Esfera SPH y Cilindro CYL)
      await page.fill('input[name="receEsfeOD"]', '1.50');
      await page.fill('input[name="receCilinOD"]', '-0.75');
      await page.fill('input[name="receEsfeOI"]', '2.00');
      await page.fill('input[name="receCilinOI"]', '-1.25');

      // f) Guardar el formulario
      await page.click('button[type="submit"]:has-text("Guardar Receta")');

      // El modal de receta debe cerrarse
      await expect(page.locator('h3:has-text("Nueva Receta")')).not.toBeVisible({ timeout: 10000 });
      await page.waitForTimeout(1000);

      // g) Verificar mediante aserciones que la nueva receta aparezca asociada correctamente al cliente
      // dentro de su historial clínico visible en la pantalla (panel de detalles)
      const recipeTable = page.locator('table');
      await expect(recipeTable.locator('td:has-text("1.50")').first()).toBeVisible({ timeout: 10000 });
      await expect(recipeTable.locator('td:has-text("-0.75")').first()).toBeVisible({ timeout: 10000 });
      await expect(recipeTable.locator('td:has-text("2.00")').first()).toBeVisible({ timeout: 10000 });
      await expect(recipeTable.locator('td:has-text("-1.25")').first()).toBeVisible({ timeout: 10000 });

      // h) Tomar un screenshot de evidencia y guardarlo
      const screenshotPath = path.join(testResultsDir, 'e2e-cli-02-receta-optica.png');
      await page.screenshot({ path: screenshotPath, fullPage: true });

    } catch (err) {
      console.log('FAIL E2E-CLI-02 URL:', page.url());
      console.log('FAIL E2E-CLI-02 BODY:', await page.evaluate(() => document.body.innerHTML));
      throw err;
    }
  });

});
