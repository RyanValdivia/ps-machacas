# Plan de Pruebas - ps-machacas

## 1. Objetos de Prueba (Test Objects)
**Backend (Django/DRF):**
1. **Apps de dominio**: `categories`, `products`, `suppliers`, `clients`, `users`, `sales`, `cash`, `sequences`, `external_services`, `opticalCenter`.
2. **API REST** (urls en `registrame/urls.py`):  
   `/api/categories`, `/api/products`, `/api/clients`, `/api/user`, `/api/sales`, `/api/suppliers`, `/api/cash`, `/api/proxy`, `/api/opticalcenter`, `/api/lunas/*`.
3. **Autenticacion y seguridad**: JWT (`rest_framework_simplejwt`), permisos y roles asociados a `users`.
4. **Persistencia y reglas de negocio**: modelos, validaciones, transacciones (stock, ventas, cierres/aperturas de caja).
5. **Archivos media** y carga de recursos (configuracion en `settings.py`).

**Frontend (React + Vite):**
1. **Ruteo y shell de la app**: `App.tsx`, `AppRouter.tsx`, `routes/`.
2. **Paginas principales**: `Dashboard`, `Inventory`, `Login`, `Prescriptions`, `Reports`, `Sale-Point`, `Sales`, `Settings`.
3. **Componentes UI reutilizables**: `Forms`, `Modal`, `Table`, `Pagination`, `Sidebar`, `PrinterStatus`.
4. **Servicios de API**: `cashService`, `clientService`, `dashboardService`, `opticalConfigService`, `prescriptionService`, `supplierService`, `reniec/*`.
5. **Auth y estado**: `auth/`, `context/`, `types/`, `utils/`.

**Opcional/Integracion Desktop:**
- `src-tauri/` (si se requiere validar empaquetado y ejecucion en escritorio).

## 2. Objetivos de Testing y Calidad
**Objetivos:**
- Validar la correccion funcional de los flujos criticos: login, gestion de inventario, ventas, apertura/cierre de caja, reportes.
- Garantizar integridad de datos (stock, totales, estados de venta, correlativos).
- Verificar seguridad basica: autenticacion JWT, control de acceso por rol y proteccion de endpoints.
- Asegurar estabilidad de integraciones externas (proxy/RENIEC u otras) y manejo de errores.
- Evitar regresiones en UI y servicios front/back.

**Calidades priorizadas:**
- Confiabilidad, correccion funcional, seguridad basica, consistencia de datos, mantenibilidad y compatibilidad con la BD configurada.

## 3. Estrategia y Tecnicas de Prueba
**Niveles y enfoques:**
- **Caja blanca (backend)**: pruebas unitarias de modelos, serializers, servicios y utilidades con cobertura de ramas en reglas de negocio.
- **Caja negra (API/UI)**: pruebas de endpoints por contrato (entradas/salidas) y validacion de flujos UI desde el punto de vista del usuario.
- **Integracion**: flujos completos (venta -> actualizacion de stock -> registro de pago -> reporte).
- **Regresion**: suite corta para rutas y operaciones criticas en cada release.

**Tecnicas sugeridas:**
- Particion de equivalencia y valores limite para montos, stock, estados y fechas.
- Pruebas negativas (payloads incompletos, permisos insuficientes, tokens expirados).
- Pruebas de concurrencia basicas para caja y ventas (simular operaciones simultaneas).

**Datos de prueba:**
- Uso de migraciones/datos semilla en backend.
- Fixtures especificos para ventas, usuarios y cajas.

## 4. Criterios de Salida y Cobertura (Exit Criteria)
El testing se considera suficiente cuando:
1. **Suite completa** (backend + frontend) pasa sin fallos.
2. **Cobertura backend** >= **80%** en apps criticas (`sales`, `cash`, `products`, `users`).
3. **Cobertura frontend** >= **70%** en componentes y servicios clave (si se implementan pruebas de UI).
4. **Defectos criticos/altos abiertos** = **0**.
5. Todos los endpoints listados en el punto 1 tienen al menos **1 prueba positiva** y **1 negativa**.

## 5. Entorno e Infraestructura de Pruebas
**Backend:**
- Python 3.x, Django 5.2.x, Django REST Framework, SimpleJWT.
- BD: PostgreSQL (default por `settings.py`), parametrizable via `DB_*`.
- Dependencias en `backend/requirements.txt`.
- Runner recomendado: `python manage.py test` o `pytest-django` (si se agrega).

**Frontend:**
- Node 18+ (sugerido), Vite, React 19, TypeScript.
- Lint: ESLint (`npm run lint`).
- Testing sugerido: **Vitest + React Testing Library** para componentes, **MSW** para mocks de API, **Playwright/Cypress** para E2E.

**Herramientas auxiliares:**
- Postman/Insomnia para pruebas exploratorias de API.
- Reportes de cobertura (coverage.py en backend; cobertura de Vitest en frontend).

## 6. Cronograma de Pruebas (6 semanas desde 28/05/2026)
| Semana | Fechas | Fase | Actividades principales | Entregables |
| --- | --- | --- | --- | --- |
| 1 | 28/05/2026 - 03/06/2026 | Analisis | Inventario de modulos, riesgos y criterios de calidad. | Alcance y riesgos aprobados. |
| 2 | 04/06/2026 - 10/06/2026 | Diseno | Casos de prueba por modulo, datos/fixtures, trazabilidad. | Matriz de casos y datos. |
| 3 | 11/06/2026 - 17/06/2026 | Implementacion | Tests unitarios/integracion backend (modelos, servicios, API). | Suite backend inicial. |
| 4 | 18/06/2026 - 24/06/2026 | Implementacion | Tests de frontend (componentes, servicios, rutas). | Suite frontend inicial. |
| 5 | 25/06/2026 - 01/07/2026 | Ejecucion | Regresion completa, pruebas negativas, validacion de permisos. | Reporte de ejecucion. |
| 6 | 02/07/2026 - 08/07/2026 | Finalizacion | Cierre, metricas de cobertura, lecciones aprendidas. | Informe final de testing. |
