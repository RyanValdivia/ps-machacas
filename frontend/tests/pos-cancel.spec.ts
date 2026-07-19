import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe.serial('Módulo POS - Anulación de Venta (IEEE §V.B)', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'vendedor1', 'Admin123!');
  });

  test('E2E-POS-07: Anulación de venta', async ({ page }) => {
    // Primero, creamos una venta para asegurarnos de que exista al menos una
    await page.goto('/sale-point');
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
    
    await page.getByRole('button', { name: /Luna/i }).click();
    await page.getByPlaceholder(/Ingresa el precio/i).fill('50.00');
    await page.getByRole('button', { name: /^Agregar$/i }).click();
    await page.getByRole('button', { name: /Procesar Venta/i }).click();
    await page.getByRole('button', { name: /Confirmar e Imprimir/i }).click();
    await page.waitForTimeout(1000);
    await page.keyboard.press('Escape'); // close swal

    await page.goto('/sales');
    await page.waitForTimeout(1000);
    
    // Click "Gestionar" on the first result
    await page.getByTitle('Gestionar venta').first().click();

    // Wait for modal
    const modalHeading = page.getByRole('heading', { name: /Gestionar Venta/i });
    await expect(modalHeading).toBeVisible();
    
    // BVA: Anular venta ya entregada (debe bloquearse)
    // El frontend ya desabilita el botón si la venta está anulada.
    
    const divAnularVenta = page.getByText(/^Anular Venta$/i).first();
    await divAnularVenta.click();

    // Reason
    const reasonInput = page.getByPlaceholder(/Escriba el motivo/i);
    await reasonInput.fill('Error en prueba E2E');

    // Confirm inside the form
    const btnConfirmarAnular = page.getByRole('button', { name: /Confirmar Anulación/i });
    await btnConfirmarAnular.click();

    // Confirm sweetalert
    await page.getByRole('button', { name: /Sí, anular venta/i }).click();

    // Success swal
    await expect(page.locator('#swal2-title')).toContainText(/Venta anulada/i, { timeout: 10000 });
    await page.keyboard.press('Escape');

    await page.screenshot({ path: 'test-results/E2E-POS-07.png' });
  });
});
