import { test, expect, type Page } from '@playwright/test';
import { execSync } from 'child_process';

/**
 * Helper temporal: login como un usuario específico usando la pantalla de login.
 * Reemplazar por el helper de auth definitivo cuando esté disponible.
 */

async function loginAs(page: Page, username: string, password: string) {
  await page.goto('/');
  
  // 1. Asegurar el foco e introducir texto simulando las pulsaciones reales del teclado
  await page.locator('#username').focus();
  await page.locator('#username').pressSequentially(username, { delay: 50 });
  
  await page.locator('#password').focus();
  await page.locator('#password').pressSequentially(password, { delay: 50 });
  
  // 2. Hacer clic en el botón de submit
  await page.click('button[type="submit"]');
  
  // 3. En lugar de esperar el cambio de URL, esperamos a que aparezca un elemento 
  // que demuestre que ya entramos a la aplicación (ej: el menú lateral, navbar o el botón de salir)
  // Cambia 'nav' o 'text=Cerrar Sesión' por un elemento real que tengas dentro del sistema
  await page.waitForSelector('nav, button:has-text("Cerrar"), [href*="logout"]', { timeout: 10000 });
}

test.describe('E2E-INV: Catálogo e Inventario', () => {

  test.beforeAll(async () => {
    try {
      // Limpieza de datos de prueba previos para asegurar idempotencia
      execSync(
        'docker exec registrame-backend python manage.py shell -c ' +
        '"from products.models import Product; from suppliers.models import Supplier; ' +
        'Product.objects.filter(prodMarca=\'BVA-TEST\').delete(); ' +
        'Supplier.objects.filter(provRazSocial=\'Óptica Los Andes SAC\').delete()"',
        { stdio: 'ignore' }
      );
    } catch (e) {
      console.warn('Advertencia: No se pudo realizar la limpieza de base de datos en Docker.', e);
    }
  });

  // ────────────────────────────────────────────────────────
  // E2E-INV-01: Registro de montura nueva
  // ────────────────────────────────────────────────────────
  test.describe('E2E-INV-01: Registro de montura nueva', () => {

    test('Debería crear una montura nueva y mostrar la descripción correcta @acceptance', async ({ page }) => {
      // CORREGIDO: Credenciales reales de la tabla para logística
      await loginAs(page, 'logistica1', 'Admin123!');
      await page.goto('/inventory');

      // Esperar a que la tabla cargue
      await expect(page.locator('h2:has-text("Inventario de Productos")')).toBeVisible();
      await page.waitForSelector('h2:has-text("Inventario de Productos")', { timeout: 10000 });

      // Act: Abrir modal "Nuevo Producto"
      await page.click('button:has-text("Nuevo Producto")');
      await expect(page.getByRole('dialog', { name: /Nuevo Producto/i })).toBeVisible({ timeout: 5000 });

      // Seleccionar categoría "Monturas"
      await page.locator('label:has-text("Categoría") + select').selectOption({ label: 'Monturas' });
      await page.locator('label:has-text("Proveedor") + select').selectOption({ label: 'Proveedor Genérico' });

      // Llenar campos de montura
      await page.fill('input[placeholder="Ej: Ray-Ban"]', 'RAYBAN');
      await page.locator('label:has-text("Material") + select').selectOption({ label: 'Acetato' });
      await page.fill('input[placeholder="Ej: 54-18-140"]', '52-18-140');
      await page.fill('input[placeholder="Ej: Negro"]', 'NEGRO');

      // Llenar precios y stock
      await page.locator('label:has-text("Costo") + input[type="number"]').fill('80');
      await page.locator('label:has-text("Precio Venta") + input[type="number"]').fill('150');
      await page.locator('label:has-text("Stock Actual") + input[type="number"]').fill('5');

      // Guardar
      await page.click('button[type="submit"]:has-text("Crear Producto")');

      // Assert: El modal se cierra
      await expect(page.getByRole('dialog', { name: /Nuevo Producto/i })).not.toBeVisible({ timeout: 10000 });
      await page.waitForTimeout(1000); 

      // Verificar que la descripción aparece en la tabla
      const productRow = page.locator(`text=RAYBAN | 52-18-140 NEGRO`).first();
      await expect(productRow).toBeVisible({ timeout: 10000 });

      await page.screenshot({ path: 'screenshots/inv-01-montura-registrada.png', fullPage: true });
    });

    test('Debería crear una montura con stock límite (Stock = 0) @acceptance', async ({ page }) => {
      // CORREGIDO: Credenciales reales de la tabla para logística
      await loginAs(page, 'logistica1', 'Admin123!');
      await page.goto('/inventory');
      await expect(page.locator('h2:has-text("Inventario de Productos")')).toBeVisible();

      // Act: Abrir modal
      await page.click('button:has-text("Nuevo Producto")');
      await expect(page.getByRole('dialog', { name: /Nuevo Producto/i })).toBeVisible({ timeout: 5000 });

      // Llenar formulario con stock = 0 (BVA)
      await page.locator('label:has-text("Categoría") + select').selectOption({ label: 'Monturas' });
      await page.locator('label:has-text("Proveedor") + select').selectOption({ label: 'Proveedor Genérico' });
      await page.fill('input[placeholder="Ej: Ray-Ban"]', 'BVA-TEST');
      await page.locator('label:has-text("Material") + select').selectOption({ label: 'Metal' });
      await page.fill('input[placeholder="Ej: 54-18-140"]', '50-18-130');
      await page.fill('input[placeholder="Ej: Negro"]', 'GRIS');
      await page.locator('label:has-text("Costo") + input[type="number"]').fill('50');
      await page.locator('label:has-text("Precio Venta") + input[type="number"]').fill('120');
      await page.locator('label:has-text("Stock Actual") + input[type="number"]').fill('0');

      // Guardar
      await page.click('button[type="submit"]:has-text("Crear Producto")');

      // Assert
      await expect(page.getByRole('dialog', { name: /Nuevo Producto/i })).not.toBeVisible({ timeout: 10000 });
      await page.waitForTimeout(1000);

      const productRow = page.locator(`text=BVA-TEST`).first();
      await expect(productRow).toBeVisible({ timeout: 10000 });

      await page.screenshot({ path: 'screenshots/inv-01-bva-stock-cero.png', fullPage: true });
    });
  });

  // ────────────────────────────────────────────────────────
  // E2E-INV-04: Gestión de proveedores
  // ────────────────────────────────────────────────────────
  test.describe('E2E-INV-04: Gestión de proveedores', () => {

    test('Debería crear un nuevo proveedor y mostrarlo en la lista @acceptance', async ({ page }) => {
      // Credenciales correctas de gerente1
      await loginAs(page, 'gerente1', 'Admin123!');
      await page.goto('/settings/supliers');

      await expect(page.locator('text=Gestión Central de Proveedores')).toBeVisible({ timeout: 10000 });

      await page.click('button:has-text("Agregar Proveedor")');
      await expect(page.getByRole('dialog', { name: /Agregar Proveedor/i })).toBeVisible({ timeout: 5000 });

      await page.fill('#provRazSocial', 'Óptica Los Andes SAC');
      await page.fill('#provRuc', '20123456789');
      await page.fill('#provDirec', 'Av. Ejército 456, Miraflores');

      await page.click('button[type="submit"]:has-text("Agregar")');

      await expect(page.locator('.swal2-popup:has-text("¡Proveedor Creado!")')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('.swal2-popup:has-text("¡Proveedor Creado!")')).not.toBeVisible({ timeout: 5000 });

      const supplierRow = page.locator('text=Óptica Los Andes SAC').first();
      await expect(supplierRow).toBeVisible({ timeout: 10000 });

      await page.screenshot({ path: 'screenshots/inv-04-proveedor-creado.png', fullPage: true });
    });

    test('Debería mostrar error de validación al ingresar RUC con formato inválido (BVA) @acceptance', async ({ page }) => {
      // Credenciales correctas de gerente1
      await loginAs(page, 'gerente1', 'Admin123!');
      await page.goto('/settings/supliers');
      await expect(page.locator('text=Gestión Central de Proveedores')).toBeVisible({ timeout: 10000 });

      await page.click('button:has-text("Agregar Proveedor")');
      await expect(page.getByRole('dialog', { name: /Agregar Proveedor/i })).toBeVisible({ timeout: 5000 });

      await page.fill('#provRazSocial', 'Proveedor Test BVA');
      await page.fill('#provRuc', '123'); 

      await page.click('button[type="submit"]:has-text("Agregar")');

      const errorText = page.locator('text=El RUC debe tener 11 dígitos').first();
      await expect(errorText).toBeVisible({ timeout: 5000 });

      await expect(page.getByRole('dialog', { name: /Agregar Proveedor/i })).toBeVisible();

      await page.screenshot({ path: 'screenshots/inv-04-bva-ruc-invalido.png', fullPage: true });
    });
  });
});