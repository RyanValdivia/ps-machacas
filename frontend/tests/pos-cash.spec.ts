import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

// E2E-POS-06: Cierre de caja con balance
// Abre caja (si hace falta), procesa una venta rápida para tener movimiento,
// y va a cerrar caja. Caso BVA: monto declarado = 0 debe dejar el botón
// "Cerrar Caja" deshabilitado; con monto real (150.00) sí permite cerrar.
// Al cerrar, redirige a apertura de caja de la siguiente sesión.
test.describe.serial('Módulo POS - Cierre de Caja (IEEE §V.B)', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'vendedor1', 'Admin123!');
  });

  test('E2E-POS-06: Cierre de caja con balance', async ({ page }) => {
    await page.goto('/sale-point');
    
    // Ensure caja is open for this test
    const lunaBtn = page.getByRole('button', { name: /Luna/i }).first();
    const abrirBtn = page.getByRole('button', { name: /Abrir caja/i }).first();
    
    try {
      await Promise.race([
        lunaBtn.waitFor({ state: 'visible', timeout: 5000 }),
        abrirBtn.waitFor({ state: 'visible', timeout: 5000 })
      ]);
    } catch (e) {}

    if (await abrirBtn.isVisible()) {
      const montoInicialInput = page.getByRole('spinbutton', { name: /Monto inicial/i }).first();
      if (!await montoInicialInput.isVisible()) {
          // fallback
          await page.locator('input[type="number"]').first().fill('100.00');
      } else {
          await montoInicialInput.fill('100.00');
      }
      await abrirBtn.click();
      await lunaBtn.waitFor({ state: 'visible' });
    }
    
    // Do a quick sale to ensure we have ventas
    await page.getByRole('button', { name: /Luna/i }).click();
    await page.getByPlaceholder(/Ingresa el precio/i).fill('50.00');
    await page.getByRole('button', { name: /^Agregar$/i }).click();
    await page.getByRole('button', { name: /Procesar Venta/i }).click();
    await page.getByRole('button', { name: /Confirmar e Imprimir/i }).click();
    await expect(page.locator('#swal2-title')).toBeVisible({ timeout: 8000 }); // Wait for success swal
    await page.keyboard.press('Escape'); // close swal
    
    // Now close cash
    await page.goto('/sale-point/close-cash');
    
    const heading = page.getByRole('heading', { name: /Cierre de Sesión/i });
    await expect(heading).toBeVisible();

    const btnCerrar = page.getByRole('button', { name: /Cerrar Caja/i });

    // BVA: Monto declarado = 0 (debe estar bloqueado)
    const inputMonto = page.getByPlaceholder(/Ej. 950.00/i).first();
    await inputMonto.fill('0');
    await expect(btnCerrar).toBeDisabled();

    // Fill real amount
    await inputMonto.fill('150.00');
    
    // Ingresar observaciones
    const textarea = page.locator('textarea');
    await textarea.fill('Cierre de prueba E2E');
    
    await btnCerrar.click();

    // Verify it navigates back to /sale-point and caja is closed
    // Verify it navigates back to /sale-point and caja is closed (it will redirect to open-cash)
    await page.waitForURL('**/open-cash*', { timeout: 10000 });
    const headingApertura = page.getByRole('heading', { name: /Abrir Caja Registradora/i });
    await expect(headingApertura).toBeVisible();
    
    await page.screenshot({ path: 'test-results/E2E-POS-06.png' });
  });
});
