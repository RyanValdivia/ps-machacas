# Plan de Pruebas de Sistema — Pruebas Funcionales E2E
## RegistraMe — Sprint 4 (Hito 3)

---

| Campo | Detalle |
|---|---|
| **Proyecto** | RegistraMe — Sistema de Gestión para Ópticas |
| **Curso** | Pruebas de Software — EPIS-UNSA 2026-A |
| **Sprint** | Sprint 4 / Hito 3 |
| **Tipo de Prueba** | Pruebas de Sistema — End-to-End (E2E) Funcionales |
| **Herramienta** | Playwright (TypeScript) |
| **Responsables** | P4 (@Choflis) — POS y Caja · P5 (@DeniseHuacani) — Inventario · P7 (@shanccom) — Autenticación |
| **Fecha de creación** | 08 de Julio de 2026 |
| **Versión** | 1.0 |

---

## Índice

1. [Introducción y Alcance](#1-introducción-y-alcance)
2. [Base Teórica — Filosofía de Myers](#2-base-teórica--filosofía-de-myers)
3. [Estrategia de Pruebas](#3-estrategia-de-pruebas)
4. [Catálogo de Casos de Prueba E2E](#4-catálogo-de-casos-de-prueba-e2e)
   - 4.1 [Ruta Crítica 1: POS y Gestión de Caja](#41-ruta-crítica-1-pos-y-gestión-de-caja)
   - 4.2 [Ruta Crítica 2: Catálogo e Inventario](#42-ruta-crítica-2-catálogo-e-inventario)
   - 4.3 [Ruta Crítica 3: Autenticación y Control de Acceso](#43-ruta-crítica-3-autenticación-y-control-de-acceso)
5. [Entorno de Pruebas y Herramientas](#5-entorno-de-pruebas-y-herramientas)
6. [Criterios de Salida](#6-criterios-de-salida)

---

## 1. Introducción y Alcance

El presente documento constituye el **Plan Formal de Pruebas de Sistema E2E** para el proyecto **RegistraMe** en el marco del Sprint 4 (Tercer Hito). Las pruebas de sistema verifican el comportamiento de la aplicación completa —Frontend React + Backend Django REST— simulando flujos reales de usuario de inicio a fin sobre navegadores reales.

### Alcance

Las pruebas E2E cubren los tres flujos de negocio críticos del sistema:

- **POS y Gestión de Caja:** Apertura de caja, registro de ventas (simples y con lunas personalizadas), pagos parciales, cierre de caja y anulación de ventas.
- **Catálogo e Inventario:** Registro de productos, búsqueda y filtrado, validación de stock insuficiente y gestión de proveedores.
- **Autenticación y Control de Acceso:** Login exitoso/fallido, bloqueo de rutas por nivel de acceso y persistencia de sesión JWT.

### Fuera de alcance

- Pruebas de rendimiento o estrés (ver `PLAN_PRUEBAS_NO_FUNCIONALES.md`)
- Pruebas de aceptación con usuario externo (ver `PLAN_PRUEBAS_ACEPTACION_UAT.md`)
- Pruebas unitarias e integración (documentadas en hitos anteriores)

---

## 2. Base Teórica — Filosofía de Myers

Las pruebas de sistema del presente plan se fundamentan en la filosofía de **Glenford Myers (2011)**, quien establece:

> *"Una prueba exitosa es aquella que descubre un error no detectado hasta ese momento."*

Este principio implica que el objetivo de las pruebas **no es demostrar que el software funciona**, sino encontrar defectos. En consecuencia, se adoptan las siguientes directivas:

### 2.1 Enfoque Destructivo

Los casos de prueba están diseñados para **intentar romper el sistema**, no para validar el camino feliz. Cada flujo incluye variantes negativas y condiciones límite.

### 2.2 Análisis de Valores Límite (Boundary Value Analysis — BVA)

Myers indica que el BVA tiene *"mayor beneficio y tasa de descubrimiento de errores"* que cualquier otra técnica de diseño de casos de prueba. Se aplica en los siguientes puntos:

| Contexto | Valor Límite a Probar |
|---|---|
| Apertura de caja | Monto inicial = S/0 (¿se permite?) |
| Stock del producto | stock = 1 (límite inferior para venta exitosa) |
| Stock del producto | Solicitar stock+1 unidades (debe rechazar) |
| Monto de adelanto | adelanto = total exacto (debe marcar como PAGADO) |
| Monto de adelanto | adelanto = S/0 (¿se permite pago sin adelanto?) |
| Login | Credenciales en blanco (campo vacío) |
| Formulario proveedor | RUC con dígito verificador inválido |

### 2.3 Partición de Equivalencia

Los usuarios del sistema se agrupan en clases de equivalencia según su nivel de acceso (0=Gerente, 2=Cajero/Vendedor, 3=Logística, 4=Optómetra). Se prueba al menos un representante de cada clase para validar el control de acceso.

---

## 3. Estrategia de Pruebas

### 3.1 Configuración del Entorno

El entorno ya está configurado. Verificar antes de empezar:

```bash
# Verificar configuración de Playwright
cat frontend/playwright.config.ts
# baseURL debe ser: http://localhost:5173

# Instalar dependencias (una sola vez)
cd frontend
npm install
npx playwright install
```

### 3.2 Helper de Autenticación Compartido

Crear `frontend/tests/helpers/auth.ts` **una sola vez** (coordinar con P4 para no duplicar):

```typescript
import { Page } from '@playwright/test';

export async function loginAs(
  page: Page,
  username = 'vendedor1',
  password = 'Admin123!'
) {
  await page.goto('/login');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/dashboard/, { timeout: 10000 });
}
```

### 3.3 Usuarios de Prueba Disponibles

| Usuario | Contraseña | Rol | Nivel |
|---|---|---|---|
| `admin` | `admin123` | GERENTE | 0 |
| `cajero1` | `Admin123!` | CAJERO | 2 |
| `vendedor1` | `Admin123!` | VENDEDOR | 2 |

### 3.4 Patrón de diseño AAA

Cada test debe seguir el patrón **Arrange → Act → Assert**:

```typescript
test('E2E-POS-01: Debería abrir caja exitosamente', async ({ page }) => {
  // ARRANGE: Preparar el estado inicial
  await loginAs(page, 'vendedor1', 'Admin123!');
  await page.goto('/sale-point');

  // ACT: Ejecutar la acción bajo prueba
  await page.fill('input[name="montoInicial"]', '100');
  await page.click('button:has-text("Abrir")');

  // ASSERT: Verificar el resultado esperado
  await expect(page).toHaveURL(/\/sale-point$/);
  await page.screenshot({ path: 'test-results/E2E-POS-01.png' });
});
```

### 3.5 Ejecución

```bash
# Levantar el sistema primero (Docker recomendado)
cd infra/local && docker compose up -d

# Ejecutar todos los tests E2E
cd frontend && npx playwright test

# Ejecutar un archivo específico
npx playwright test tests/pos-sale.spec.ts --headed

# Ver reporte HTML
npx playwright show-report
```

---

## 4. Catálogo de Casos de Prueba E2E

### 4.1 Ruta Crítica 1: POS y Gestión de Caja

**Responsable:** P4 (@Choflis) | **Archivos:** `pos-sale.spec.ts`, `pos-payments.spec.ts`, `pos-cash.spec.ts`, `pos-cancel.spec.ts`

| ID | Nombre | Precondición | Pasos | Resultado Esperado | BVA | Prioridad |
|---|---|---|---|---|---|---|
| **E2E-POS-01** | Apertura de caja exitosa | `vendedor1` logueado, sin caja abierta | 1. Ir a `/sale-point` → redirige a `/sale-point/open-cash` 2. Seleccionar caja 3. Ingresar S/100 4. Clic "Abrir Caja" | Toast de éxito. Redirección a `/sale-point`. Caja = ABIERTA | Probar con S/0 | 🔴 |
| **E2E-POS-02** | Venta simple de montura | Caja abierta | 1. Buscar "PEGASUS" en POS 2. Seleccionar montura 3. Pago EFECTIVO = total 4. Confirmar venta | Estado = PAGADO. Stock -1. Comprobante generado | Probar stock exactamente = 1 | 🔴 |
| **E2E-POS-03** | Venta con luna personalizada | Caja abierta | 1. Agregar montura 2. Activar "Luna personalizada" 3. Seleccionar NK, Monofocal, Blue Block 4. Pago parcial | Estado = PARCIAL. Detalle muestra "LUNA NK - MONOFOCAL (Blue Block)". Stock montura -1. Luna no consume stock | — | 🔴 |
| **E2E-POS-04** | Venta con pago parcial | Caja abierta | 1. Crear venta total S/200 2. Pagar S/100 como adelanto | Estado = PARCIAL. Saldo = S/100. Adelanto = S/100 | Adelanto = S/0 y adelanto = S/200 (total) | 🟡 |
| **E2E-POS-05** | Pago de saldo pendiente | Venta PARCIAL existente | 1. Ir a `/sales` 2. Buscar venta PARCIAL 3. Registrar saldo restante | Estado = PAGADO. Saldo = S/0. Comprobante generado | — | 🟡 |
| **E2E-POS-06** | Cierre de caja con balance | Caja abierta + al menos 1 venta | 1. Ir a `/sale-point/close-cash` 2. Ver resumen 3. Ingresar monto real 4. Confirmar cierre | Caja cerrada. Diferencia calculada. Nuevas ventas bloqueadas | Monto declarado = S/0 | 🔴 |
| **E2E-POS-07** | Anulación de venta | Venta existente no entregada | 1. Ir a `/sales` 2. Seleccionar venta 3. "Anular" + motivo 4. Confirmar | Estado = ANULADO. Stock devuelto. Comprobante anulado | Anular venta ya entregada (debe bloquearse) | 🟡 |

### 4.2 Ruta Crítica 2: Catálogo e Inventario

**Responsable:** P5 (@DeniseHuacani) | **Archivos:** `inventory-crud.spec.ts`, `inventory-search.spec.ts`, `inventory-stock.spec.ts`

| ID | Nombre | Precondición | Pasos | Resultado Esperado | BVA | Prioridad |
|---|---|---|---|---|---|---|
| **E2E-INV-01** | Registro de montura nueva | Usuario nivel 0 o 3 logueado | 1. Ir a `/inventory` 2. "Nuevo Producto" 3. Categoría "Monturas" 4. Llenar: Marca=RAYBAN, Material=Acetato, Talla=52-18-140, Color=NEGRO, Precio=S/150, Stock=5 5. Guardar | Código `A1` generado. Descripción: "RAYBAN \| 52-18-140 NEGRO". Visible en inventario | Stock = 0 al crear | 🔴 |
| **E2E-INV-02** | Búsqueda y filtrado de productos | Productos seed cargados | 1. Ir a `/inventory` 2. Buscar "PEGASUS" 3. Verificar resultados 4. Filtrar por material "Metal" | Lista filtrada muestra solo coincidencias. Conteo correcto | Búsqueda vacía (todos los productos) | 🟡 |
| **E2E-INV-03** | Validación de stock insuficiente | Producto con stock = 1 | 1. En POS, intentar agregar 2 unidades del producto con stock = 1 | Error visible: "Stock insuficiente". Venta NO registrada | stock = 1 (exitoso), stock+1 = 2 (rechazado) | 🔴 |
| **E2E-INV-04** | Gestión de proveedores | Usuario Gerente logueado | 1. Ir a `/settings/supliers` 2. "Nuevo Proveedor" 3. Llenar RUC, razón social, dirección 4. Guardar | Proveedor creado. Disponible para nuevos productos | RUC con formato inválido | 🟢 |

### 4.3 Ruta Crítica 3: Autenticación y Control de Acceso

**Responsable:** P7 (@shanccom) | **Archivos:** `auth-login.spec.ts`, `auth-roles.spec.ts`, `auth-session.spec.ts`

> **Nota:** `E2E-AUTH-01` y `E2E-AUTH-02` ya existen parcialmente en `frontend/tests/login.spec.ts`. Refinar y añadir verificación explícita del token JWT en `localStorage`.

| ID | Nombre | Precondición | Pasos | Resultado Esperado | BVA | Prioridad |
|---|---|---|---|---|---|---|
| **E2E-AUTH-01** | Login exitoso | — | 1. Ir a `/` 2. Ingresar `vendedor1` / `Admin123!` 3. Clic "Entrar" | Redirección a `/dashboard`. Token JWT en `localStorage`. Sidebar visible | Credenciales en blanco | 🔴 |
| **E2E-AUTH-02** | Login fallido | — | 1. Ir a `/` 2. Ingresar `usuario_invalido` / `ClaveIncorrecta123` 3. Clic "Entrar" | Mensaje de error visible. Sin redirección | — | 🔴 |
| **E2E-AUTH-03** | Bloqueo por nivel de acceso | `vendedor1` (nivel 2) logueado | 1. Navegar a `/settings` (nivel 0-1) 2. Navegar a `/reports` (nivel 0-1) 3. Navegar a `/inventory` (nivel 0,1,3) | Redirección o mensaje "Acceso denegado" en cada ruta no autorizada | Acceder con URL directa (bypass del router) | 🔴 |
| **E2E-AUTH-04** | Persistencia de sesión | Usuario logueado | 1. Loguearse 2. Recargar página (F5) 3. Verificar que sigue logueado | Token en `localStorage` se mantiene. Usuario autenticado sin re-login | — | 🟡 |

---

## 5. Entorno de Pruebas y Herramientas

### 5.1 Configuración (ya existente)

| Elemento | Valor |
|---|---|
| Framework | Playwright Test Runner |
| Lenguaje | TypeScript |
| Config | `frontend/playwright.config.ts` |
| Base URL | `http://localhost:5173` |
| Navegadores | Chromium, Firefox, WebKit |
| Reportes | HTML (`playwright-report/`) — subidos como artefactos en CI |
| Screenshots | `only-on-failure` (automático) + manual con `page.screenshot()` |
| Videos | `retain-on-failure` |

### 5.2 Integración CI/CD

El job `e2e` en `.github/workflows/deploy-qa.yml` ejecuta automáticamente todos los tests de Playwright al hacer push o PR a la rama `qa`. Los reportes HTML quedan disponibles como artefactos durante 30 días.

### 5.3 Datos de Prueba (Seed)

Los datos base están en `database_seed.sql` y se cargan automáticamente en el entorno QA. Para el entorno local con Docker: `cd infra/local && docker compose up -d` (aplica el seed automáticamente al iniciar).

---

## 6. Criterios de Salida

### Definition of Done para este plan

El plan de pruebas E2E del Sprint 4 se considera **completado** cuando:

- [ ] Los 15 tests E2E implementados pasan en verde localmente
- [ ] Los 15 tests pasan en verde en el pipeline CI (job `e2e` en GitHub Actions)
- [ ] Screenshots de evidencia guardados para cada test en `test-results/`
- [ ] Reporte HTML de Playwright generado y disponible como artefacto CI
- [ ] Valores límite (BVA) verificados para los casos marcados
- [ ] Resultados documentados en el **Informe de Pruebas de Sistema E2E** (documento separado)

### Criterios de aprobación por caso

| Prioridad | Criterio |
|---|---|
| 🔴 Alta | Must pass. El Hito 3 no se entrega si alguno falla |
| 🟡 Media | Should pass. Si falla se documenta como defecto y se mitiga |
| 🟢 Baja | Nice to have. Se implementa si hay tiempo |

---

*Documento preparado por: P1 (Fernando Garambel) — Líder / Coordinador*
*Basado en: Myers, G. J. (2011). The Art of Software Testing. Wiley.*
*Trazabilidad: Plan Maestro de Pruebas §3 | ISO/IEC/IEEE 29119-3*
