import { test, expect, type Page } from '@playwright/test';
import { execSync } from 'child_process';
import { resetProductStock } from './helpers/auth';

// Helper robusto para login
async function loginAs(page: Page, username: string, password: string) {
  // Capturar logs de la consola del navegador para depuración
  page.on('console', msg => {
    console.log(`[BROWSER CONSOLE] ${msg.type()}: ${msg.text()}`);
  });

  await page.goto('/');

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

// Asegurar que la caja registradora está abierta para poder vender
async function ensureCashSessionOpen(page: Page) {
  await page.goto('/sale-point');
  
  const openCashHeader = page.locator('h2:has-text("Abrir Caja Registradora")');
  const posHeader = page.locator('h1:has-text("Punto de Venta")');
  
  // Esperar a que una de las pantallas se haga visible
  const result = await Promise.any([
    openCashHeader.waitFor({ state: 'visible', timeout: 10000 }).then(() => 'open'),
    posHeader.waitFor({ state: 'visible', timeout: 10000 }).then(() => 'pos')
  ]).catch(() => 'timeout');

  if (result === 'open') {
    // Llenar el monto inicial y abrir la caja
    await page.locator('#openingAmount').fill('100');
    await page.locator('button').filter({ hasText: 'Abrir caja' }).first().click();
    
    // Esperar a volver a la vista principal
    await expect(posHeader).toBeVisible({ timeout: 10000 });
  } else if (result === 'timeout') {
    throw new Error('No cargó la pantalla de Punto de Venta ni la de Abrir Caja a tiempo.');
  }
}

test.describe('E2E-INV-03: Validación de stock insuficiente (Alta prioridad 🔴)', () => {
  test.describe.configure({ mode: 'serial' });

  test.beforeEach(async ({ request }) => {
    // Reset vía API REST: funciona en CI (no depende de Docker) y es idempotente
    // sin importar qué proyecto de browser (chromium/firefox/webkit) corra primero,
    // ya que los 3 comparten la misma BD dentro de un mismo job.
    await resetProductStock(request, 'M1', 1);
    await resetProductStock(request, 'M2', 1);

    try {
      // BVA Myers: Forzar que el producto PEGASUS (código M1) tenga exactamente Stock = 1
      // También preparamos la caja registradora para el usuario 'admin' y cerramos cualquier sesión abierta que genere conflictos
      const pythonScript = `
from products.models import Product
from cash.models import Cash, CashOpening
from users.models import User
from sales.models import Venta

# Asegurar stock = 1 para M1 y M2
for code in ('M1', 'M2'):
    p = Product.objects.filter(prodCode=code).first()
    if p:
        p.prodStock = 1
        p.prodEstado = 'Active'
        p.save()

# Borrar todas las ventas para evitar ProtectedError al limpiar aperturas de caja
Venta.objects.all().delete()

# Asegurar caja asignada a vendedor1 y sin aperturas conflictivas
vendedor_user = User.objects.filter(usuNom='vendedor1').first()
if vendedor_user:
    CashOpening.objects.filter(usuCod=vendedor_user, cajaAperEstado='ABIERTA').delete()
    caja, _ = Cash.objects.get_or_create(cajNom='Caja Principal', defaults={'usuCod': vendedor_user, 'cajEstado': 'ACTIVO'})
    caja.usuCod = vendedor_user
    caja.cajEstado = 'ACTIVO'
    caja.save()
    CashOpening.objects.filter(cajCod=caja, cajaAperEstado='ABIERTA').delete()

print('DB Prepared Successfully')
`;
      const output = execSync('docker exec -i registrame-backend python manage.py shell', {
        input: pythonScript,
      });
      console.log('Docker preparation output:', output.toString());
    } catch (e: any) {
      console.warn('Advertencia: No se pudo preparar la BD de prueba en Docker. Error:', e.message);
      if (e.stdout) console.warn('Stdout:', e.stdout.toString());
      if (e.stderr) console.warn('Stderr:', e.stderr.toString());
    }
  });

  test('Caso 1: Permitir agregar exactamente 1 unidad al carrito y procesar la venta @acceptance', async ({ page }) => {
    await loginAs(page, 'vendedor1', 'Admin123!');
    await ensureCashSessionOpen(page);

    // Buscar el producto M2 (PEGASUS con stock = 1)
    // NOTA: se usa M2 (no M1) para no consumir el stock que necesitan
    // los Casos 2 y 3 de este archivo y E2E-POS-02 en pos-sale.spec.ts.
    const searchInput = page.locator('input[placeholder="Buscar por código..."]');
    await searchInput.fill('M2');

    // Esperar a que aparezca la coincidencia exacta
    const resultItem = page.locator('.cursor-pointer').filter({ hasText: 'PEGASUS' }).first();
    await expect(resultItem).toBeVisible({ timeout: 5000 });
    
    // Hacer clic para agregar al carrito
    await resultItem.click();

    // Verificar que se agregue al carrito con cantidad = 1
    const cartItem = page.locator('.group.flex.items-center:has-text("PEGASUS")').first();
    await expect(cartItem).toBeVisible({ timeout: 5000 });
    
    const quantitySpan = cartItem.locator('span.w-8, span.w-10');
    await expect(quantitySpan).toHaveText('1');

    // Seleccionar vendedor para completar la venta
    const vendorSelect = page.locator('select').first();
    await vendorSelect.selectOption({ index: 1 });

    // Procesar la venta
    await page.click('button:has-text("Procesar Venta")');

    // Confirmar en la vista previa del ticket
    const ticketModal = page.locator('h2:has-text("Vista Previa del Ticket")');
    await expect(ticketModal).toBeVisible({ timeout: 5000 });
    await page.click('button:has-text("Confirmar e Imprimir")');

    // Verificar diálogo de éxito (SweetAlert2)
    const successAlert = page.locator('.swal2-popup').filter({ hasText: /registrada|guardada/i });
    await expect(successAlert).toBeVisible({ timeout: 10000 });
    
    // Evidencia de venta exitosa
    await page.screenshot({ path: 'screenshots/inv-03-caso1-venta-exitosa.png', fullPage: true });

    // Cerrar el popup de éxito
    await page.click('button:has-text("Aceptar")');
  });

  test('Caso 2: Bloquear intento de agregar 2 unidades (Stock + 1) mostrando advertencia de stock insuficiente @acceptance', async ({ page }) => {
    await loginAs(page, 'vendedor1', 'Admin123!');
    await ensureCashSessionOpen(page);

    // Buscar el producto M1
    const searchInput = page.locator('input[placeholder="Buscar por código..."]');
    await searchInput.fill('M1');
    
    const resultItem = page.locator('.cursor-pointer').filter({ hasText: 'PEGASUS' }).first();
    await expect(resultItem).toBeVisible({ timeout: 5000 });
    await resultItem.click();

    // Verificar agregado con cantidad 1
    const cartItem = page.locator('.group.flex.items-center:has-text("PEGASUS")').first();
    await expect(cartItem).toBeVisible({ timeout: 5000 });
    await expect(cartItem.locator('span.w-8, span.w-10')).toHaveText('1');

    // Intentar agregar otra unidad buscando el mismo producto e intentando agregarlo
    await searchInput.fill('M1');
    await expect(resultItem).toBeVisible({ timeout: 5000 });
    await resultItem.click();

    // Debe mostrar error/advertencia en pantalla (SweetAlert Toast)
    // El texto configurado es "Stock máximo alcanzado (1 unidades)"
    const toast = page.locator('.swal2-toast, .swal2-popup, [role="status"]').filter({ hasText: /Stock/i });
    await expect(toast.first()).toBeVisible({ timeout: 5000 });
    
    // Evidencia de bloqueo y mensaje de stock insuficiente
    await page.screenshot({ path: 'screenshots/inv-03-caso2-stock-insuficiente.png', fullPage: true });

    // Verificar que la cantidad en el carrito NO se incrementó a 2 y sigue en 1
    await expect(cartItem.locator('span.w-8, span.w-10')).toHaveText('1');
  });

  test('Caso 3: Impedir agregar 0 unidades (Validar bloqueo de decremento por debajo de 1 en la interfaz) @acceptance', async ({ page }) => {
    await loginAs(page, 'vendedor1', 'Admin123!');
    await ensureCashSessionOpen(page);

    // Buscar el producto M1
    const searchInput = page.locator('input[placeholder="Buscar por código..."]');
    await searchInput.fill('M1');
    
    const resultItem = page.locator('.cursor-pointer').filter({ hasText: 'PEGASUS' }).first();
    await expect(resultItem).toBeVisible({ timeout: 5000 });
    await resultItem.click();

    // Verificar agregado
    const cartItem = page.locator('.group.flex.items-center:has-text("PEGASUS")').first();
    await expect(cartItem).toBeVisible({ timeout: 5000 });
    await expect(cartItem.locator('span.w-8, span.w-10')).toHaveText('1');

    // Verificar que el botón de decremento (Minus) está deshabilitado
    // Buscamos específicamente el botón que contiene la clase o ícono lucide-minus
    const minusButton = cartItem.locator('button').filter({ has: page.locator('.lucide-minus, svg.lucide-minus') }).first();
    await expect(minusButton).toBeDisabled();

    // Evidencia del bloqueo de decremento a 0
    await page.screenshot({ path: 'screenshots/inv-03-caso3-decremento-bloqueado.png', fullPage: true });
  });
});
