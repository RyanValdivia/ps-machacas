import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe.serial('Módulo POS - Pagos Parciales (IEEE §V.B)', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'vendedor1', 'Admin123!');
  });

  test('E2E-POS-04: Venta con pago parcial (Adelanto de S/100 para un total de S/200)', async ({ page }) => {
    await page.goto('/sale-point');
    
    // Check if caja is open, open if needed
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
          await page.locator('input[type="number"]').first().fill('100.00');
      } else {
          await montoInicialInput.fill('100.00');
      }
      await abrirBtn.click();
      await lunaBtn.waitFor({ state: 'visible' });
    }

    // Add product to reach S/ 200 (Luna con precio manual)
    await page.getByRole('button', { name: /Luna/i }).click();
    const modalHeading = page.getByText(/Personalizacion de Luna/i);
    await expect(modalHeading).toBeVisible();

    const precioInput = page.getByPlaceholder(/Ingresa el precio/i);
    await precioInput.fill('200.00');
    await page.getByRole('button', { name: /^Agregar$/i }).click();

    // Wait for the cart to update the total to S/ 200.00 before filling adelanto
    // If we don't wait, totalVenta might still be 0 and the input will cap the adelanto at 0
    await expect(page.locator('.text-gray-900.font-bold').filter({ hasText: 'S/ 200.00' }).first()).toBeVisible({ timeout: 5000 });
    
    // Check Adelanto section - Boundary Value Analysis
    // Test says: "Adelanto = S/0 (debe rechazarse o permitir?)"
    // The UI handles adelanto optionally. We will put 100.00
    const adelantoInput = page.getByPlaceholder('0.00').first();
    await adelantoInput.fill('100.00');

    // Process sale
    await page.getByRole('button', { name: /Procesar Venta/i }).click();

    // Confirmar e Imprimir en el modal de Ticket
    await page.getByRole('button', { name: /Confirmar e Imprimir/i }).click();

    // Wait for success alert
    await expect(page.locator('#swal2-title')).toContainText(/Venta guardada/i, { timeout: 10000 });
    await page.keyboard.press('Escape');

    await page.screenshot({ path: 'test-results/E2E-POS-04.png' });
  });

  test('E2E-POS-05: Registro de pago de saldo pendiente', async ({ page }) => {
    await page.goto('/sales');
    await page.waitForLoadState('networkidle'); // Wait for load

    // Expandir filtros avanzados
    await page.getByRole('button', { name: /Filtros/i }).click();

    // Filter by PARCIAL
    const selectEstado = page.locator('select').first();
    await selectEstado.selectOption('PARCIAL');
    await page.waitForLoadState('networkidle');

    // Click "Gestionar" on the first result
    await page.getByTitle('Gestionar venta').first().click();

    // Click "Registrar Pago Parcial" (or Completar Pago)
    await page.getByText(/Registrar Pago Parcial/i).click();

    // Fill the remaining amount (100.00)
    const inputPago = page.getByPlaceholder('0.00');
    await inputPago.fill('100.00');
    
    await page.getByRole('button', { name: 'Confirmar Pago' }).click();

    // Verify success
    await expect(page.locator('#swal2-title')).toContainText(/Pago registrado/i, { timeout: 10000 });
    await page.keyboard.press('Escape');

    await page.screenshot({ path: 'test-results/E2E-POS-05.png' });
  });
});
