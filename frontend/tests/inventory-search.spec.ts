import { test, expect, type Page } from '@playwright/test';

// Helper robusto para login
async function loginAs(page: Page, username: string, password: string) {
  await page.goto('http://localhost:8080/');
  
  // 1. Asegurar el foco e introducir texto simulando pulsaciones reales
  await page.locator('#username').focus();
  await page.locator('#username').pressSequentially(username, { delay: 50 });
  
  await page.locator('#password').focus();
  await page.locator('#password').pressSequentially(password, { delay: 50 });
  
  // 2. Hacer clic en el botón de submit
  await page.click('button[type="submit"]');
  
  // 3. Esperar que cargue la SPA de React 19
  await page.waitForSelector('nav, button:has-text("Cerrar"), [href*="logout"]', { timeout: 10000 });
}

test.describe('E2E-INV-02: Búsqueda y filtrado de productos', () => {
  
  test('Debería buscar PEGASUS y filtrar por material Metal @acceptance', async ({ page }) => {
    // a) Realizar login con la función robusta que apunta a http://localhost:8080
    await loginAs(page, 'admin', 'admin123');
    
    // b) Ir a /inventory
    await page.goto('http://localhost:8080/inventory');
    
    // Esperar que la vista de inventario esté completamente cargada
    await expect(page.locator('h2:has-text("Inventario de Productos")')).toBeVisible({ timeout: 10000 });
    
    // c) Buscar en el input de búsqueda el término "PEGASUS"
    const searchInput = page.locator('input[placeholder*="Buscar por código"]');
    await searchInput.fill('PEGASUS');
    
    // Esperar debounce de búsqueda (1 segundo)
    await page.waitForTimeout(1500);
    
    // d) Verificar que el producto aparezca visible en la tabla
    const productRow = page.locator('tbody tr').filter({ hasText: 'PEGASUS' }).first();
    await expect(productRow).toBeVisible({ timeout: 10000 });
    
    // e) Filtrar usando el selector de material por "Metal"
    // Primero abrimos "Filtros Avanzados" para mostrar el dropdown de Material
    await page.click('button:has-text("Filtros Avanzados")');
    
    const materialSelect = page.locator('label:has-text("Material") + select');
    await expect(materialSelect).toBeVisible({ timeout: 5000 });
    
    // Seleccionar "Metal" (valor 'M' / label 'Metal')
    await materialSelect.selectOption({ label: 'Metal' });
    await page.waitForTimeout(500); // Esperar que se aplique el filtro
    
    // f) Verificar que la tabla se actualice mostrando monturas metálicas
    // Verificar que PEGASUS sigue visible (es metálica)
    await expect(page.locator('tbody tr').filter({ hasText: 'PEGASUS' }).first()).toBeVisible();
    
    // Para validar que realmente filtra y solo muestra metálicas, limpiamos el término "PEGASUS" de búsqueda
    // y verificamos que no aparezcan monturas de Acetato (como RAYBAN)
    await searchInput.fill('');
    await page.waitForTimeout(1500); // Esperar debounce
    
    // Verificar que un producto de Acetato (como RAYBAN) ya no es visible
    const acetatoRow = page.locator('tbody tr').filter({ hasText: 'RAYBAN' });
    await expect(acetatoRow).not.toBeVisible();
    
    // Verificar que la tabla se actualizó y no está vacía (muestra productos metálicos)
    await expect(page.locator('tbody tr')).not.toHaveCount(0);
    
    // g) Tomar una captura de pantalla de evidencia
    await page.screenshot({ path: 'screenshots/inventory-search-filter.png', fullPage: true });
  });
});
