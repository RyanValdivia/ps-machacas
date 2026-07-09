# Plan de Pruebas — Unitarias y Funcionales (Sprint 2)

---

## Índice

1. [Introducción](#1-introducción)
   - 1.1. [Alcance](#11-alcance)
   - 1.2. [Referencias](#12-referencias)
   - 1.3. [Glosario](#13-glosario)
2. [Contexto de las Pruebas](#2-contexto-de-las-pruebas)
   - 2.1. [Módulos / Componentes bajo prueba](#21-módulos--componentes-bajo-prueba)
   - 2.2. [Elementos de Prueba — Unitarias](#22-elementos-de-prueba--unitarias)
   - 2.3. [Alcance de las Pruebas](#23-alcance-de-las-pruebas)
   - 2.4. [Suposiciones y Restricciones](#24-suposiciones-y-restricciones)
   - 2.5. [Partes Interesadas](#25-partes-interesadas)
3. [Estrategia de Pruebas Unitarias](#3-estrategia-de-pruebas-unitarias)
   - 3.1. [Enfoque de prueba](#31-enfoque-de-prueba)
   - 3.2. [Técnicas de diseño](#32-técnicas-de-diseño)
   - 3.3. [Cobertura de código objetivo](#33-cobertura-de-código-objetivo)
   - 3.4. [Manejo de dependencias](#34-manejo-de-dependencias)
   - 3.5. [Criterios de entrada y salida](#35-criterios-de-entrada-y-salida)
   - 3.6. [Métricas](#36-métricas)
   - 3.7. [Criterios de suspensión y reanudación](#37-criterios-de-suspensión-y-reanudación)
4. [Entorno de Pruebas](#4-entorno-de-pruebas)
   - 4.1. [Ambiente de ejecución](#41-ambiente-de-ejecución)
   - 4.2. [Frameworks y herramientas](#42-frameworks-y-herramientas)
   - 4.3. [Integración con CI/CD](#43-integración-con-cicd)
5. [Registro de Riesgos](#5-registro-de-riesgos)
   - 5.1. [Riesgos identificados](#51-riesgos-identificados)
   - 5.2. [Plan de mitigación](#52-plan-de-mitigación)
6. [Entregables](#6-entregables)
   - 6.1. [Casos de prueba unitaria](#61-casos-de-prueba-unitaria)
   - 6.2. [Reportes de ejecución y cobertura](#62-reportes-de-ejecución-y-cobertura)
   - 6.3. [Registro de defectos](#63-registro-de-defectos)
7. [Actividades y Cronograma — Sprint 2](#7-actividades-y-cronograma--sprint-2)
   - 7.1. [Estructura de actividades](#71-estructura-de-actividades)
   - 7.2. [Estimados de esfuerzo](#72-estimados-de-esfuerzo)
   - 7.3. [Cronograma](#73-cronograma)
8. [Personal](#8-personal)
   - 8.1. [Roles y responsabilidades](#81-roles-y-responsabilidades)
   - 8.2. [Necesidades de entrenamiento](#82-necesidades-de-entrenamiento)
9. [Pruebas Funcionales — Sprint 2](#9-pruebas-funcionales--sprint-2)
   - 9.1. [Diseño de Pruebas Funcionales (Black-Box)](#91-diseño-de-pruebas-funcionales-black-box)
   - 9.2. [Ejecución QA — Punto de Venta (TSK-18)](#92-ejecución-qa--punto-de-venta-tsk-18)
   - 9.3. [Ejecución QA — Dashboard (TSK-19)](#93-ejecución-qa--dashboard-tsk-19)
   - 9.4. [Ejecución QA — Clientes (TSK-20)](#94-ejecución-qa--clientes-tsk-20)
   - 9.5. [Ejecución QA — Reportes y Usuarios (TSK-21)](#95-ejecución-qa--reportes-y-usuarios-tsk-21)
   - 9.6. [Resultados y Reporte (TSK-17)](#96-resultados-y-reporte-tsk-17)
10. [Planificación de Pruebas de Integración](#10-planificación-de-pruebas-de-integración)
    - 10.1. [Alcance de Integración](#101-alcance-de-integración)
    - 10.2. [Estrategia de Integración](#102-estrategia-de-integración)
    - 10.3. [Hitos de Integración (TSK-25, TSK-26)](#103-hitos-de-integración-tsk-25-tsk-26)

---

## 1. Introducción

Este documento constituye el Plan de Pruebas para el sistema **RegistraMe**, una aplicación de gestión óptica. El plan integra dos niveles de aseguramiento de calidad correspondientes al Sprint 2 del proyecto:

- **Pruebas Unitarias Automatizadas**: cobertura del backend Django REST Framework (10 módulos, ~384 tests).
- **Pruebas Funcionales (Black-Box)**: ejecución manual de QA sobre los módulos críticos de la aplicación (Punto de Venta, Dashboard, Clientes, Reportes y Usuarios).
- **Planificación de Pruebas de Integración**: definición de estrategia y hitos para la integración del backend con el frontend Tauri y servicios externos.

El documento fue elaborado por el equipo de desarrollo como parte del aseguramiento de calidad del proyecto.

### 1.1. Alcance

**Pruebas Unitarias** — cubre los siguientes módulos del backend:

- **users**: modelo de usuario personalizado, roles, permisos, autenticación (JWT) y gestión de usuarios.
- **clients**: clientes, optometristas, recetas (`recipes`) y filtros personalizados.
- **products**: productos (monturas, accesorios), lunas (materiales, tipos, características, configuraciones) y acciones de stock.
- **sales**: ventas, detalles de venta, comprobantes, dashboard de estadísticas e impresión térmica.
- **categories**: categorías de productos con validaciones y conversiones automáticas.
- **cash**: cajas, aperturas de caja, cierre de caja y ventas por sesión.
- **suppliers**: proveedores con validaciones de RUC, teléfono y email.
- **sequences**: generación de correlativos únicos para comprobantes.
- **opticalCenter**: configuración general de la óptica (singleton) y manejo de logo/imágenes.
- **external_services**: proxy de consulta DNI (RENIEC) y RUC (SUNAT) con manejo de errores HTTP y timeout.

**Pruebas Funcionales (Sprint 2)** — cubre la ejecución manual de black-box testing sobre:

- **Punto de Venta (POS)**: flujo completo de creación de venta, registro de pago, anulación, comprobante.
- **Dashboard**: visualización de estadísticas, filtros por período, indicadores clave.
- **Clientes**: CRUD de clientes, optometristas y recetas desde la interfaz de usuario.
- **Reportes y Usuarios**: generación de reportes, administración de usuarios y roles.

**Queda fuera del alcance actual**: pruebas de integración con APIs externas reales, pruebas de carga, pruebas de seguridad (penetración, OWASP), pruebas end-to-end (E2E) automatizadas, pruebas de interfaz de usuario (frontend Tauri) y pruebas de migraciones de base de datos.

### 1.2. Referencias

| #   | Documento | Versión | Enlace |
| --- | --------- | ------- | ------ |
| 1   | Documento de Arquitectura Técnica | 1.0 | `docs/architecture.md` |
| 2   | Modelo de Datos | 1.0 | `docs/data_model.md` |
| 3   | Estándares de Codificación Django | 1.0 | `docs/coding_standards.md` |
| 4   | README del proyecto | 1.0 | `README.md` |
| 5   | Sprint 2 Testing Schedule | 1.0 | `docs/sprint2_testing_schedule.md` |
| 6   | Plan de Integración | 1.0 | `docs/integration_plan.md` |

### 1.3. Glosario

| Término | Definición |
| ------- | ---------- |
| UT (Unit Test) | Prueba unitaria automatizada que verifica una unidad aislada de código (método, función o clase). |
| Mock | Objeto simulado que imita el comportamiento de una dependencia real para aislar la unidad bajo prueba. |
| Fixture | Función de pytest que prepara datos o estado antes de ejecutar pruebas. |
| Cobertura de código | Métrica que indica el porcentaje de líneas/ramas del código ejecutadas durante las pruebas. |
| TDD (Test-Driven Development) | Metodología donde se escribe la prueba antes del código de producción. |
| Django TestCase | Clase base de Django para pruebas con soporte de base de datos transaccional. |
| pytest | Framework de pruebas para Python usado como ejecutor principal (unitarias). |
| DRF (Django REST Framework) | Framework sobre Django para construir APIs REST. |
| ViewSet | Clase de DRF que agrupa acciones CRUD de un recurso REST. |
| Singleton | Patrón que asegura una única instancia de un modelo (ej: OpticalCenter con pk=1). |
| Black-Box Testing | Técnica de prueba basada en especificaciones, sin conocimiento de la implementación interna. |
| POS (Point of Sale) | Módulo de Punto de Venta para la creación y gestión de ventas. |
| QA (Quality Assurance) | Proceso sistemático de verificación de calidad del software. |
| Pruebas de Integración | Pruebas que verifican la interacción correcta entre dos o más componentes del sistema. |

---

## 2. Contexto de las Pruebas

Las pruebas unitarias cubren todo el backend de RegistraMe, compuesto por 10 módulos Django con un total aproximado de **384 pruebas** distribuidas en **14 archivos de prueba**. Las pruebas funcionales (Sprint 2) cubren 4 módulos críticos de la aplicación mediante ejecución manual de QA.

### 2.1. Módulos / Componentes bajo prueba

**Pruebas Unitarias:**

| Módulo / Componente | Descripción breve | Responsable |
| ------------------- | ----------------- | ----------- |
| users | Gestión de usuarios, roles, autenticación JWT y permisos | Desarrollo |
| clients | CRUD de clientes, optometristas, recetas y filtros | Desarrollo |
| products | CRUD de productos, lunas, acciones de stock y búsqueda | Desarrollo |
| sales | Ventas, detalles, comprobantes, dashboard e impresión térmica | Desarrollo |
| categories | CRUD de categorías de productos con validaciones | Desarrollo |
| cash | Cajas, aperturas, cierres y ventas por sesión | Desarrollo |
| suppliers | CRUD de proveedores con validaciones de RUC/teléfono | Desarrollo |
| sequences | Generación de correlativos únicos para comprobantes | Desarrollo |
| opticalCenter | Configuración singleton de la óptica y manejo de logo | Desarrollo |
| external_services | Proxy de consulta DNI (RENIEC) y RUC (SUNAT) | Desarrollo |

**Pruebas Funcionales (Sprint 2):**

| Módulo / Componente | Descripción breve | Responsable |
| ------------------- | ----------------- | ----------- |
| Punto de Venta (POS) | Creación de venta, registro de pago, anulación, comprobante | QA |
| Dashboard | Estadísticas de ventas, filtros por período, indicadores | QA |
| Clientes | CRUD de clientes, optometristas, recetas | QA |
| Reportes y Usuarios | Reportes de ventas, administración de usuarios y roles | QA |

### 2.2. Elementos de Prueba — Unitarias

| Módulo | Clase / Archivo | Método / Función | Prioridad |
| ------ | --------------- | ---------------- | --------- |
| users | `TestRoleModel` | 5 tests: creación, estado default, nivel default, choices, suspendido | Alta |
| users | `TestUserModel` | 8 tests: creación (con/sin username, email), superuser, str, estado, roles M2M, normalized email | Alta |
| users | `TestUserSerializer` | 5 tests: serializar, crear, update, password, staff roles | Alta |
| users | `TestCurrentUserSerializer` | 1 test: serializer del usuario actual | Alta |
| users | `TestPermissions` | 7 tests: nivel1 denied/granted, nivel2-4, unauthenticated, sin roles | Alta |
| users | `TestLoginLogoutFunctions` | 3 tests: login success/invalid, logout | Alta |
| users | `TestNewUserView` | 4 tests: create first user, authenticated, denied, invalid, duplicate | Alta |
| users | `TestListUsersView` | 3 tests: list as gerente, non-gerente denied, unauthenticated denied | Alta |
| users | `TestGetUserView` | 2 tests: get by id, not found | Alta |
| users | `TestUpdateUserView` | 3 tests: update, not found, update with roles | Alta |
| users | `TestChangePasswordView` | 3 tests: change password, missing new, user not found | Alta |
| users | `TestDeleteUserView` | 2 tests: delete, not found | Alta |
| users | `TestCurrentUserView` | 2 tests: get current, unauthenticated | Alta |
| users | `TestListCashierUsersView` | 2 tests: list cashiers as gerente, non-manager denied | Alta |
| users | `TestListSellerUsersView` | 1 test: list sellers | Media |
| users | `TestTokenSerializer` | 5 tests: obtain success, invalid, missing, refresh, custom claims | Alta |
| users | `TestUserViewSet` | 1 test: list via viewset | Media |
| users | `TestRoleSerializer` | 2 tests: serializer, fields present | Media |
| clients | `test_models.py` | 3 tests: client upper/str, optometrist str, recipe str | Alta |
| clients | `test_serializers.py` | 2 tests: client serializer, recipe minimal input | Alta |
| clients | `test_views.py` | 24 tests: CRUD clientes, optometristas, recetas, búsqueda, paginación | Alta |
| clients | `test_filters.py` | 7 tests: filtros cliTipoDoc, edad min/max, valores inválidos/vacíos | Media |
| products | `TestProductModel` | 25 tests: creación montura/accesorio, str, validaciones, códigos, descripciones, márgenes | Alta |
| products | `TestLunaModels` | 6 tests: material, tipo, característica, configuración, unique_together, precio negativo | Alta |
| products | `TestProductSerializers` | 7 tests: list, detail, create serializers, luna serializers | Alta |
| products | `TestProductViewSet` | 9 tests: list auth/unauthenticated, search, retrieve, create, update, delete | Alta |
| products | `TestProductActions` | 5 tests: monturas, accesorios, stock bajo, estadísticas, ajustar stock | Alta |
| products | `TestLunaViewSets` | 6 tests: list/create luna material, tipo, característica, configuración | Media |
| products | `TestProductPermissions` | 2 tests: logistica access, gerente access | Alta |
| products | Standalone functions | 6 tests: update stock invalid, buscar config missing/not found, calcular precio | Media |
| sales | `TestVentaModel` | 27 tests: creación, str, totales, estados, anular, pagos, pedidos, asignación caja | Alta |
| sales | `TestVentaDetalleModel` | 7 tests: creación, str, copiar datos, totales, devolver stock, luna descripción | Alta |
| sales | `TestComprobanteModel` | 6 tests: creación, str, completo, correlativo, copia datos, genera detalles | Alta |
| sales | `TestEstadisticasDashboard` | 15 tests: periodos (dia/semana/mes/personalizado), resumen, stats, pendientes, top productos | Alta |
| sales | `TestVentaViewSet` | 20 tests: list, retrieve, search, filter, pendientes, del día, crear, anular, pagar, comprobante | Alta |
| sales | `TestVentaDetalleViewSet` | 4 tests: list, retrieve, anular, ya anulado | Alta |
| sales | `TestVentaSerializers` | 22 tests: list/detail/create serializer, pago, comprobante, estadísticas, búsqueda | Alta |
| sales | `TestImpresoraTermica` (test_printer.py) | 23 tests: init, encode, generar_ticket (mínimo, completo, descuento, adelanto, logo, multilinea), imprimir, enviar | Media |
| categories | `TestProductCategoryModel` | 13 tests: creación, str, uppercase, title, strip, unique, default, full_clean, vacíos | Alta |
| categories | `TestProductCategorySerializer` | 6 tests: all fields, valid, invalid sin code/nom, requiereInventario, empty | Alta |
| categories | `TestProductCategoryViewSet` | 11 tests: list auth/unauthenticated, create, uppercase, retrieve, update, partial, destroy, duplicate | Alta |
| categories | `TestProductCategoryUrls` | 2 tests: list url, detail url | Media |
| cash | `TestCashModel` | 8 tests: create, str, min_length, unique, default estado, apertura_activa, apertura_actual, sin_descripcion | Alta |
| cash | `TestCashOpeningModel` | 18 tests: create, str, estado, monto negativo, fecha, duplicado, cerrar, anular, total_ventas | Alta |
| cash | `TestCashSerializers` | 6 tests: cash serializer all/valid/invalid, opening serializer all/valid/invalid | Alta |
| cash | `TestCashViewSet` | 8 tests: list auth/unauthenticated, create, retrieve, update, partial, destroy, sin_rol | Alta |
| cash | `TestCashOpeningViewSet` | 15 tests: list, create, retrieve, patch, destroy, cerrar, abrir_actual, session_sales, aperturas_por_caja | Alta |
| cash | `TestCashUrls` | 8 tests: todas las URLs (list, detail, opening, close, open, session-sales, aperturas-por-caja) | Media |
| suppliers | `TestSupplierModel` | 15 tests: create, str, ruc validaciones (short/long/numeric), telefono, email, razon_social, dpto, active, duplicate, all_departments | Alta |
| suppliers | `TestSupplierSerializer` | 13 tests: valid, ruc validators, telefono validators, email, razon_social, ciu, empty-to-none, create, update | Alta |
| suppliers | `TestSupplierListSerializer` | 1 test: list serializer fields | Media |
| suppliers | `TestSupplierViewSet` | 13 tests: list auth/unauthenticated, search, retrieve, create, update, delete, delete with products | Alta |
| suppliers | `TestSupplierPermissions` | 3 tests: logistica, gerente, vendedor | Alta |
| sequences | Standalone functions | 11 tests: create, str, unique_type, get_next_value (new/existing/concurrent), reset, default_values, ordering, updated_at | Media |
| opticalCenter | Standalone functions | 14 tests: auto_create, retrieve, create_or_update, exception handling, update with logo, partial_update, destroy, ensure_media_dirs (branches, permission error, critical error), model delete prevention, model str | Alta |
| external_services | Standalone functions | 12 tests: consultar_dni (success, invalid, not found, rate_limit, 503, timeout, connection, generic error), consultar_ruc (success, missing, invalid, error responses) | Media |

### 2.3. Alcance de las Pruebas

## **Dentro del alcance — Pruebas Unitarias:**
- Pruebas de modelos Django: creación, validación, métodos `__str__`, `save`, propiedades calculadas, constraints de base de datos.
- Pruebas de serializers DRF: validación de entrada, serialización de salida, campos personalizados, `create`/`update`.
- Pruebas de ViewSets DRF: autenticación, permisos, CRUD, filtros, búsqueda, acciones personalizadas.
- Pruebas de funciones utilitarias: impresión térmica (ESC/POS), generación de secuencias, proxy de consultas externas (con mocks).
- Pruebas de filtros personalizados (`django-filter`): filtros por rango, ChoiceFilter, NumberFilter.
- Pruebas de URLs: resolución de nombres de ruta.
- Aislamiento de dependencias externas mediante mocks (requests, subprocess, file system).

## **Dentro del alcance — Pruebas Funcionales (Sprint 2):**
- Ejecución manual de black-box testing sobre los módulos funcionales de la aplicación.
- Verificación de flujos completos de usuario (crear venta, registrar pago, generar comprobante).
- Validación de datos de entrada y salida en formularios e interfaces.
- Verificación de reglas de negocio desde la perspectiva del usuario final.

## **Fuera del alcance:**
- Pruebas de integración con APIs externas reales (RENIEC, SUNAT).
- Pruebas de impresión en una impresora térmica real.
- Pruebas de carga, estrés o rendimiento.
- Pruebas de seguridad (penetración, OWASP).
- Pruebas de interfaz de usuario automatizadas (frontend Tauri).
- Pruebas end-to-end (E2E) automatizadas.
- Pruebas de migraciones de base de datos.

### 2.4. Suposiciones y Restricciones

## **Suposiciones:**
- El código fuente está escrito y accesible en el repositorio Git.
- El equipo de desarrollo conoce Django, DRF y pytest.
- La base de datos de pruebas unitarias se ejecuta en SQLite `:memory:` a través de `settings_test.py`.
- No se requiere conexión a internet para ejecutar las pruebas unitarias (las APIs externas están mockeadas).
- El modelo de usuario personalizado (`users.User`) reemplaza a `auth.User`.
- Para las pruebas funcionales, la aplicación se despliega en un entorno de staging con datos de prueba.
- Las pruebas funcionales son ejecutadas manualmente por el equipo de QA.

## **Restricciones:**
- Tiempo limitado: las pruebas unitarias se implementan a posteriori del código de producción.
- La cobertura de ciertos módulos (printer, external_services) es parcial porque dependen de hardware o APIs externas.
- El password de la base de datos PostgreSQL de producción/desarrollo es desconocido; por ello se modificó `pg_hba.conf` a `trust` para autenticación local.
- pytest-django se instaló tardíamente en el ciclo de desarrollo.
- Las pruebas funcionales manuales no son repetibles de forma automatizada.
- No hay entorno de integración continua (CI/CD) configurado al inicio del Sprint 2.

### 2.5. Partes Interesadas

| Nombre | Rol | Interés / Responsabilidad |
| ------ | --- | ------------------------- |
| Equipo de Desarrollo | Desarrollador | Implementar y ejecutar pruebas unitarias |
| Líder Técnico | Líder Técnico | Revisar estrategia, aprobar resultados, mantener calidad de código |
| QA / Tester | Analista QA | Diseñar casos de prueba funcional, ejecutar pruebas manuales, analizar cobertura, reportar defectos |
| Product Owner | PO | Validar que la funcionalidad crítica esté cubierta por pruebas |

---

## 3. Estrategia de Pruebas Unitarias

### 3.1. Enfoque de prueba

Se adopta un enfoque de **pruebas a posteriori** (pruebas unitarias escritas después del código de producción) combinado con **cobertura de ramas** para maximizar la detección de defectos en la lógica de negocio existente. Las pruebas son de **caja blanca** (conocimiento de la implementación interna) para los modelos y serializers, y de **caja negra** (basadas en la API REST) para los ViewSets.

Se utiliza **pytest** como framework de ejecución con el plugin `pytest-django` para integración con Django. Las dependencias externas (APIs HTTP, subprocess, sistema de archivos) se aíslan mediante **mocks** de `unittest.mock`.

### 3.2. Técnicas de diseño

- [x] Partición de equivalencia
- [x] Análisis de valores límite
- [x] Cobertura de ramas (branch coverage)
- [ ] Cobertura de condiciones
- [ ] Tablas de decisión
- [x] Otra: Pruebas de estados (máquina de estados para ventas y aperturas de caja)

**Ejemplos de aplicación:**
- **Partición de equivalencia**: validaciones de RUC (11 dígitos numéricos), DNI (8 dígitos), teléfono (7-15 dígitos), email (formato).
- **Valores límite**: `min_length` en nombre de caja (3 caracteres), `monto_inicial` en apertura de caja (> 0).
- **Cobertura de ramas**: `_generar_ticket` en printer.py (logo sí/no, OpticalCenter sí/no, adelanto parcial/completo, producto con/sin descuento).
- **Estados**: estados de venta (PENDIENTE, PARCIAL, PAGADO, ANULADO, ENTREGADO, LISTO), apertura de caja (ABIERTO, CERRADO, ANULADO).

### 3.3. Cobertura de código objetivo

| Tipo de cobertura | Objetivo mínimo |
| ----------------- | --------------- |
| Cobertura de líneas | 70 % |
| Cobertura de ramas | 60 % |
| Cobertura de condiciones | 50 % |

### 3.4. Manejo de dependencias

| Dependencia | Tipo de doble usado | Justificación |
| ----------- | ------------------- | ------------- |
| Base de datos (SQLite) | Base de datos transaccional en memoria | pytest-django crea y destruye la BD entre pruebas |
| API RENIEC/SUNAT (requests.get) | Mock (`unittest.mock.patch`) | Evitar llamadas HTTP reales y dependencia de internet |
| Impresora térmica (subprocess.run) | Mock (`unittest.mock.patch`) | No hay impresora física disponible en el entorno de prueba |
| Sistema de archivos (os.makedirs, open) | Mock y tempfile | Aislar operaciones de escritura en disco |
| Almacenamiento de archivos (FileSystemStorage) | Mock | Evitar escritura real de archivos de logo |
| Modelo de usuario (auth.User) | Modelo personalizado (`users.User`) | `AUTH_USER_MODEL = 'users.User'` está configurado en settings |

### 3.5. Criterios de entrada y salida

## **Criterios de entrada (para iniciar pruebas):**
- El código fuente está disponible en el repositorio.
- Las dependencias Python están instaladas (`requirements.txt` o `pyproject.toml`).
- Django puede importar los settings de prueba (`registrame.settings_test`).
- La base de datos de prueba (SQLite `:memory:`) se puede crear sin errores.
- No hay errores de sintaxis en los archivos de prueba.

## **Criterios de salida (para finalizar pruebas):**
- Todas las pruebas planificadas están implementadas en archivos `tests.py` o `test_*.py`.
- La suite completa se ejecuta sin errores de importación.
- Al menos el 70 % de las pruebas pasan exitosamente.
- No hay pruebas omitidas (skipped) por errores de configuración.
- El reporte de cobertura se genera en formato HTML y texto.

### 3.6. Métricas

| Métrica | Descripción | Objetivo |
| ------- | ----------- | -------- |
| % de cobertura de código | Porcentaje de líneas de código ejecutadas por las pruebas | ≥ 70 % |
| # de pruebas unitarias ejecutadas | Número total de pruebas en la suite | ~384 |
| # de pruebas pasadas / fallidas | Estado de cada prueba individual | 100 % pasadas |
| Densidad de defectos | Defectos encontrados por cada 100 líneas de código | < 2 |
| Tiempo promedio de ejecución | Tiempo total de la suite completa | < 30 segundos |
| # de casos funcionales ejecutados | Cantidad de escenarios black-box verificados por QA | 20+ por módulo |
| # de defectos funcionales encontrados | Bugs identificados durante la ejecución de QA | Reportados en GitHub Issues |

### 3.7. Criterios de suspensión y reanudación

## **Criterios de suspensión:**
- Error crítico de configuración de Django (settings no encontrados, base de datos no accesible).
- Dependencia faltante (pytest-django, requests, Pillow) que impide la ejecución.
- Fallo masivo (>50 %) de pruebas por cambio estructural en el código base.
- Ambiente de pruebas (Python, paquetes) no disponible.
- Entorno de staging caído o no disponible para pruebas funcionales.

## **Criterios de reanudación:**
- Se corrigió la configuración de Django o la base de datos.
- Se instalaron las dependencias faltantes.
- Se actualizaron las pruebas para reflejar los cambios estructurales.
- El ambiente de pruebas está operativo nuevamente.
- El entorno de staging fue restaurado o reemplazado.

---

## 4. Entorno de Pruebas

### 4.1. Ambiente de ejecución

| Elemento | Detalle |
| -------- | ------- |
| Sistema operativo | Windows 11 / Windows 10 |
| Lenguaje / versión | Python 3.11.0 |
| Runtime / SDK | CPython |
| Gestor de dependencias | pip / pyproject.toml |
| Base de datos (unitarias) | SQLite en memoria (`registrame.settings_test`) |
| Base de datos (funcionales) | PostgreSQL (staging) |
| Frontend | Tauri + Svelte (entorno de staging) |

### 4.2. Frameworks y herramientas

| Herramienta | Propósito | Versión |
| ----------- | --------- | ------- |
| pytest | Framework de pruebas unitarias | 8.4.2 |
| pytest-django | Integración de Django con pytest | 4.12.0 |
| Django | Framework web | 5.2.11 |
| Django REST Framework | Framework de APIs REST | 3.15.2 |
| coverage.py | Medición de cobertura de código | 7.x |
| unittest.mock | Creación de mocks y stubs | Biblioteca estándar Python |
| Pillow (PIL) | Procesamiento de imágenes para pruebas de logo | 10.x |
| requests | Cliente HTTP (mockeado en pruebas) | 2.x |

### 4.3. Integración con CI/CD

Actualmente no hay integración automática con un pipeline de CI/CD. Las pruebas se ejecutan de forma local mediante:

```bash
cd backend
$env:DJANGO_SETTINGS_MODULE='registrame.settings_test'
python -m pytest
```

Para medir cobertura:

```bash
coverage run --source='.' manage.py test
coverage report -m
```

Se recomienda configurar GitHub Actions o similar para ejecutar las pruebas automáticamente en cada pull request a la rama `develop`. Las pruebas funcionales manuales se documentan en hojas de cálculo y se consolidan en el informe de resultados (TSK-17).

---

## 5. Registro de Riesgos

### 5.1. Riesgos identificados

| ID  | Riesgo | Probabilidad | Impacto | Nivel |
| --- | ------ | :----------: | :-----: | :---: |
| R01 | Dependencia de APIs externas (RENIEC/SUNAT) caídas o que cambien su interfaz | Alta | Medio | Alto |
| R02 | Cambios en el modelo de datos que invaliden las pruebas existentes | Media | Alto | Alto |
| R03 | Falta de cobertura en ramas condicionales complejas (printer.py) | Media | Medio | Medio |
| R04 | Dependencia de hardware de impresora térmica no disponible en CI/CD | Alta | Bajo | Medio |
| R05 | Pruebas funcionales manuales no cubren todos los escenarios de borde | Media | Alto | Alto |
| R06 | Retraso en la configuración del entorno de staging para ejecución de QA | Media | Alto | Alto |
| R07 | Desalineación entre criterios de aceptación del PO y casos de prueba funcional | Baja | Medio | Medio |

### 5.2. Plan de mitigación

| ID  | Acción de mitigación | Responsable | Fecha límite |
| --- | -------------------- | ----------- | :----------: |
| R01 | Mantener mocks actualizados; segregar pruebas de integración en suite separada | Desarrollo | Por definir |
| R02 | Revisar y actualizar pruebas tras cada migración de modelo | Desarrollo | Continuo |
| R03 | Agregar pruebas de caja blanca para ramas no cubiertas en printer.py | Desarrollo | Próximo sprint |
| R04 | Asegurar que las pruebas de printer.py usen mocks y no requieran hardware real | Desarrollo | Completado |
| R05 | Priorizar escenarios críticos (happy path + errores comunes) en la ejecución manual | QA | 06/06/2026 |
| R06 | Preparar entorno de staging con al menos una semana de anticipación | DevOps / Desarrollo | 01/06/2026 |
| R07 | Revisión conjunta (PO + QA) de los casos de prueba antes de la ejecución | QA / PO | 05/06/2026 |

---

## 6. Entregables

### 6.1. Casos de prueba unitaria

Los casos de prueba están documentados directamente en el código fuente dentro de los archivos de prueba de cada módulo. Cada test sigue la convención de nomenclatura `test_<nombre descriptivo>` y su propósito se describe en comentarios `# TEST: <descripción>` al inicio del método.

Los archivos de prueba son:

| Archivo | Tests | Formato |
| ------- | :---: | ------- |
| `backend/users/tests.py` | 61 | Clases pytest |
| `backend/clients/tests/test_models.py` | 3 | Funciones pytest |
| `backend/clients/tests/test_serializers.py` | 2 | Funciones pytest |
| `backend/clients/tests/test_views.py` | 24 | Funciones pytest |
| `backend/clients/tests/test_filters.py` | 7 | Funciones pytest |
| `backend/products/tests.py` | 46 | Clases pytest |
| `backend/sales/tests.py` | 67 | Clases pytest |
| `backend/sales/test_printer.py` | 23 | Clases pytest |
| `backend/categories/tests.py` | 28 | Clases pytest |
| `backend/cash/tests.py` | 48 | Clases pytest |
| `backend/suppliers/tests.py` | 38 | Clases pytest |
| `backend/sequences/tests.py` | 11 | Funciones pytest |
| `backend/opticalCenter/tests.py` | 14 | Funciones pytest |
| `backend/external_services/tests.py` | 12 | Funciones pytest |

### 6.2. Reportes de ejecución y cobertura

Los reportes se generan mediante:

- **Reporte de texto**: `coverage report -m` (consola)
- **Reporte HTML**: `coverage html` (directorio `htmlcov/`)
- **Reporte XML**: `coverage xml` (para integración con CI/CD)

Los reportes de pruebas funcionales se consolidan en el **Informe de Resultados (TSK-17)** que incluye:

- Resumen de casos ejecutados por módulo (POS, Dashboard, Clientes, Reportes/Usuarios).
- Defectos encontrados, clasificados por severidad.
- Evidencia de ejecución (capturas de pantalla, logs).
- Estado general por módulo (APROBADO / APROBADO CON OBSERVACIONES / REPROBADO).

Los reportes actuales se almacenan localmente y no se publican en un servidor externo.

### 6.3. Registro de defectos

No se utiliza un sistema formal de seguimiento de defectos para las pruebas unitarias. Los defectos encontrados durante las pruebas se corrigen directamente y se registran como commits en el repositorio Git.

Para las pruebas funcionales (Sprint 2), los defectos se registran en **GitHub Issues** con el siguiente flujo de estados:

1. **Nuevo** — defecto reportado por QA.
2. **En progreso** — asignado a Desarrollo para corrección.
3. **Resuelto** — corrección implementada y desplegada en staging.
4. **Verificado** — QA confirma la corrección.
5. **Cerrado** — defecto solucionado y aceptado.

---

## 7. Actividades y Cronograma — Sprint 2

### 7.1. Estructura de actividades

**Fase 1 — Planificación de Pruebas Unitarias (TSK-01, TSK-02, TSK-03, TSK-05, TSK-06):**

| #   | Actividad | Descripción | Responsable |
| --- | --------- | ----------- | ----------- |
| 1 | Análisis de componentes a probar | Identificar módulos, clases y métodos críticos del backend | Desarrollo |
| 2 | Diseño de casos de prueba unitaria | Definir escenarios, datos de entrada y resultados esperados | Desarrollo / QA |
| 3 | Implementación de pruebas unitarias | Escribir código de pruebas en archivos `tests.py` | Desarrollo |
| 4 | Ejecución de pruebas unitarias | Ejecutar suite completa y verificar resultados | Desarrollo |
| 5 | Análisis de resultados y cobertura | Revisar reporte de cobertura, identificar brechas | QA |
| 6 | Corrección de defectos y re-testing | Corregir errores encontrados y re-ejecutar | Desarrollo |
| 7 | Generación de reporte de cobertura | Consolidar métricas de cobertura y documentar | Desarrollo / QA |

**Fase 2 — Pruebas Funcionales (TSK-15, TSK-18, TSK-19, TSK-20, TSK-21, TSK-17):**

| #   | Actividad | Descripción | Responsable |
| --- | --------- | ----------- | ----------- |
| 8 | Diseño de pruebas funcionales | Definir casos black-box para POS, Dashboard, Clientes, Reportes | QA |
| 9 | Ejecución QA — Punto de Venta | Verificar flujo completo de ventas y pagos | QA |
| 10 | Ejecución QA — Dashboard | Validar estadísticas, filtros e indicadores | QA |
| 11 | Ejecución QA — Clientes | Verificar CRUD de clientes, optometristas y recetas | QA |
| 12 | Ejecución QA — Reportes y Usuarios | Validar reportes de ventas y gestión de usuarios | QA |
| 13 | Informe de resultados Sprint 2 | Consolidar hallazgos, defectos y estado por módulo | QA |

**Fase 3 — Planificación de Integración (TSK-25, TSK-26):**

| #   | Actividad | Descripción | Responsable |
| --- | --------- | ----------- | ----------- |
| 14 | Definición de estrategia de integración | Establecer enfoque, hitos y dependencias entre componentes | Desarrollo / QA |
| 15 | Plan de pruebas de integración | Documentar casos de integración backend-frontend y servicios externos | Desarrollo / QA |

### 7.2. Estimados de esfuerzo

| Actividad | Estimado (horas) | Responsable |
| --------- | :--------------: | ----------- |
| Análisis de componentes | 4 | Desarrollo |
| Diseño de casos de prueba unitaria | 6 | Desarrollo / QA |
| Implementación de pruebas unitarias | 24 | Desarrollo |
| Ejecución de pruebas unitarias | 2 | Desarrollo |
| Análisis de resultados y cobertura | 3 | QA |
| Corrección de defectos y re-testing (unitarias) | 6 | Desarrollo |
| Generación de reporte de cobertura | 2 | Desarrollo / QA |
| Diseño de pruebas funcionales (TSK-15) | 8 | QA |
| Ejecución QA — Punto de Venta (TSK-18) | 6 | QA |
| Ejecución QA — Dashboard (TSK-19) | 4 | QA |
| Ejecución QA — Clientes (TSK-20) | 6 | QA |
| Ejecución QA — Reportes y Usuarios (TSK-21) | 6 | QA |
| Informe de resultados Sprint 2 (TSK-17) | 4 | QA |
| Definición de estrategia de integración (TSK-25) | 4 | Desarrollo / QA |
| Plan de pruebas de integración (TSK-26) | 6 | Desarrollo / QA |
| **Total** | **91** | |

### 7.3. Cronograma

| Actividad | Fecha inicio | Fecha fin | Estado |
| --------- | :----------: | :-------: | :----: |
| **Fase 1 — Planificación de Pruebas Unitarias** | | | |
| TSK-01: Análisis de componentes | 02/06/2026 | 02/06/2026 | ✅ Completado |
| TSK-02: Diseño de casos de prueba unitaria | 02/06/2026 | 02/06/2026 | ✅ Completado |
| TSK-03: Configuración de entorno de pruebas | 03/06/2026 | 03/06/2026 | ✅ Completado |
| TSK-05: Implementación de pruebas (cobertura) | 03/06/2026 | 03/06/2026 | ✅ Completado |
| TSK-06: Organización del plan de pruebas | 04/06/2026 | 04/06/2026 | ✅ Completado |
| Implementación de pruebas unitarias (adicionales) | 05/06/2026 | 11/06/2026 | 🔄 En progreso |
| Ejecución de pruebas unitarias | 11/06/2026 | 11/06/2026 | ⬜ Pendiente |
| Análisis de resultados y cobertura | 12/06/2026 | 12/06/2026 | ⬜ Pendiente |
| Corrección de defectos y re-testing | 12/06/2026 | 13/06/2026 | ⬜ Pendiente |
| Generación de reporte de cobertura | 13/06/2026 | 13/06/2026 | ⬜ Pendiente |
| **Fase 2 — Pruebas Funcionales** | | | |
| TSK-15: Diseño de pruebas funcionales | 05/06/2026 | 05/06/2026 | ✅ Completado |
| TSK-18: Ejecución QA — Punto de Venta | 06/06/2026 | 06/06/2026 | ⬜ Pendiente |
| TSK-19: Ejecución QA — Dashboard | 07/06/2026 | 07/06/2026 | ⬜ Pendiente |
| TSK-20: Ejecución QA — Clientes | 08/06/2026 | 08/06/2026 | ⬜ Pendiente |
| TSK-21: Ejecución QA — Reportes y Usuarios | 09/06/2026 | 09/06/2026 | ⬜ Pendiente |
| TSK-17: Informe de resultados Sprint 2 | 10/06/2026 | 10/06/2026 | ⬜ Pendiente |
| **Fase 3 — Planificación de Integración** | | | |
| TSK-25: Definición de estrategia de integración | 11/06/2026 | 11/06/2026 | ⬜ Pendiente |
| TSK-26: Plan de pruebas de integración | 11/06/2026 | 11/06/2026 | ⬜ Pendiente |

---

## 8. Personal

### 8.1. Roles y responsabilidades

| Rol | Nombre | Responsabilidades |
| --- | ------ | ---------------- |
| Líder Técnico | Por definir | Revisar estrategia, aprobar resultados, supervisar calidad del código |
| Desarrollador | Equipo de Desarrollo | Implementar y ejecutar pruebas unitarias, corregir defectos |
| QA / Tester | Por definir | Diseñar casos de prueba funcional, ejecutar pruebas manuales, analizar cobertura, reportar defectos, elaborar informe de resultados |
| Product Owner | Por definir | Validar criterios de aceptación, priorizar funcionalidades a probar |
| DevOps | Por definir | Configurar integración en CI/CD, gestionar entornos de staging |

### 8.2. Necesidades de entrenamiento

| Persona / Rol | Tema de entrenamiento | Modalidad | Fecha estimada |
| ------------- | --------------------- | --------- | :------------: |
| Equipo de Desarrollo | pytest-django y mocking avanzado | Autodidacta / Documentación | Completado |
| Equipo de Desarrollo | Cobertura de ramas con coverage.py | Autodidacta / Documentación | Completado |
| QA / Tester | Black-box testing: técnicas de partición de equivalencia y valores límite | Presencial / Taller | 04/06/2026 |
| QA / Tester | Registro de defectos en GitHub Issues | Autodidacta / Guía rápida | 04/06/2026 |

---

## 9. Pruebas Funcionales — Sprint 2

### 9.1. Diseño de Pruebas Funcionales (Black-Box)

Las pruebas funcionales se diseñan utilizando la técnica de **black-box testing** (caja negra), donde los casos de prueba se derivan de las especificaciones funcionales y los criterios de aceptación definidos por el Product Owner, sin considerar la implementación interna.

**Técnicas aplicadas:**
- **Partición de equivalencia**: agrupar datos de entrada en clases válidas e inválidas.
- **Análisis de valores límite**: probar valores en los bordes de los rangos permitidos.
- **Tablas de decisión**: para reglas de negocio con múltiples condiciones (ej: estados de venta × forma de pago).
- **Transición de estados**: para flujos que cambian el estado de una entidad (ej: venta PENDIENTE → PAGADO → ANULADO).

**Estructura de cada caso funcional:**

| Campo | Descripción |
| ----- | ----------- |
| ID | Identificador único del caso (ej: POS-001) |
| Módulo | POS / Dashboard / Clientes / Reportes y Usuarios |
| Título | Nombre descriptivo del escenario |
| Precondiciones | Estado inicial necesario para ejecutar el caso |
| Datos de entrada | Valores específicos a ingresar |
| Pasos | Secuencia numerada de acciones del usuario |
| Resultado esperado | Comportamiento esperado del sistema |
| Resultado obtenido | Comportamiento real observado (se completa durante ejecución) |
| Estado | APROBADO / FALLIDO / BLOQUEADO |

### 9.2. Ejecución QA — Punto de Venta (TSK-18)

**Fecha:** 06/06/2026
**Responsable:** QA
**Objetivo:** Verificar el flujo completo de creación, pago, anulación y generación de comprobante de una venta desde el POS.

**Escenarios a ejecutar:**

| ID | Escenario | Prioridad |
| -- | --------- | --------- |
| POS-001 | Crear venta con cliente existente (seleccionado desde lista) | Alta |
| POS-002 | Crear venta con cliente nuevo (registro rápido desde el POS) | Alta |
| POS-003 | Crear venta como cliente genérico ("Sin nombre") | Alta |
| POS-004 | Agregar productos al detalle de venta (monturas, accesorios) | Alta |
| POS-005 | Agregar luna personalizada al detalle de venta | Alta |
| POS-006 | Aplicar descuento a producto individual | Media |
| POS-007 | Registrar pago total (CANCELADO) | Alta |
| POS-008 | Registrar pago parcial (PENDIENTE DE CANCELAR) | Alta |
| POS-009 | Anular venta con motivo obligatorio | Alta |
| POS-010 | Anular venta ya anulada (debe rechazar) | Media |
| POS-011 | Generar comprobante (boleta/factura) después del pago | Alta |
| POS-012 | Verificar que el stock se descuente al crear venta | Alta |
| POS-013 | Verificar que el stock se restaure al anular venta | Alta |
| POS-014 | Imprimir ticket térmico (verificar datos en el ticket) | Media |
| POS-015 | Validar campos obligatorios en formulario de venta | Alta |

**Criterios de aceptación:**
- El POS permite crear una venta en menos de 5 pasos.
- El pago se registra correctamente y actualiza el estado de la venta.
- La anulación requiere motivo y revierte el stock.
- El comprobante refleja los datos correctos de la venta.
- Los errores de validación se muestran claramente al usuario.

### 9.3. Ejecución QA — Dashboard (TSK-19)

**Fecha:** 07/06/2026
**Responsable:** QA
**Objetivo:** Validar que el Dashboard de estadísticas muestre datos correctos y responda adecuadamente a los filtros.

**Escenarios a ejecutar:**

| ID | Escenario | Prioridad |
| -- | --------- | --------- |
| DSH-001 | Visualizar dashboard sin aplicar filtros (período por defecto) | Alta |
| DSH-002 | Filtrar estadísticas por día | Alta |
| DSH-003 | Filtrar estadísticas por semana | Alta |
| DSH-004 | Filtrar estadísticas por mes | Alta |
| DSH-005 | Filtrar estadísticas por rango personalizado de fechas | Alta |
| DSH-006 | Verificar indicador de ventas totales del período | Alta |
| DSH-007 | Verificar indicador de ventas pendientes | Alta |
| DSH-008 | Verificar top productos más vendidos | Alta |
| DSH-009 | Verificar estadísticas de ventas por vendedor | Media |
| DSH-010 | Verificar estadísticas de ventas por caja | Media |
| DSH-011 | Verificar gráfico de ventas por día | Media |
| DSH-012 | Verificar que los datos sean consistentes con los registros de venta | Alta |
| DSH-013 | Dashboard sin datos (base vacía) debe mostrar mensaje informativo | Media |

**Criterios de aceptación:**
- Los indicadores del dashboard coinciden con los datos de venta registrados.
- Los filtros por período actualizan correctamente todos los indicadores.
- Los gráficos se renderizan sin errores.
- La respuesta del dashboard es menor a 3 segundos.

### 9.4. Ejecución QA — Clientes (TSK-20)

**Fecha:** 08/06/2026
**Responsable:** QA
**Objetivo:** Verificar el CRUD de clientes, optometristas y recetas, así como las búsquedas y filtros.

**Escenarios a ejecutar:**

| ID | Escenario | Prioridad |
| -- | --------- | --------- |
| CLI-001 | Crear cliente con todos los campos obligatorios | Alta |
| CLI-002 | Crear cliente sin documento de identidad (debe rechazar) | Alta |
| CLI-003 | Crear cliente con documento duplicado (debe rechazar) | Alta |
| CLI-004 | Actualizar datos de cliente existente | Alta |
| CLI-005 | Actualizar cliente con datos inválidos (debe rechazar) | Alta |
| CLI-006 | Eliminar cliente sin recetas asociadas | Alta |
| CLI-007 | Buscar cliente por número de documento | Alta |
| CLI-008 | Buscar cliente por nombre | Alta |
| CLI-009 | Listar clientes con paginación | Media |
| CLI-010 | Crear optometrista con todos los campos | Alta |
| CLI-011 | Actualizar optometrista | Alta |
| CLI-012 | Eliminar optometrista sin recetas asociadas | Media |
| CLI-013 | Crear receta médica asociada a un cliente y optometrista | Alta |
| CLI-014 | Crear receta con datos inválidos (debe rechazar) | Alta |
| CLI-015 | Listar recetas filtradas por cliente | Alta |
| CLI-016 | Eliminar receta | Media |
| CLI-017 | Buscar cliente por documento con tipo de documento específico | Media |
| CLI-018 | Validar formato de email, teléfono y documento en cliente | Alta |

**Criterios de aceptación:**
- El CRUD de clientes funciona correctamente en todos los flujos.
- Las búsquedas devuelven resultados precisos y rápidos.
- Las validaciones de formato rechazan datos inválidos.
- No se permite eliminar un optometrista con recetas asociadas.
- La paginación funciona correctamente con listas grandes.

### 9.5. Ejecución QA — Reportes y Usuarios (TSK-21)

**Fecha:** 09/06/2026
**Responsable:** QA
**Objetivo:** Validar la generación de reportes de ventas y la administración de usuarios y roles.

**Escenarios a ejecutar (Reportes):**

| ID | Escenario | Prioridad |
| -- | --------- | --------- |
| REP-001 | Generar reporte de ventas por período | Alta |
| REP-002 | Generar reporte de ventas por vendedor | Alta |
| REP-003 | Generar reporte de ventas por caja | Media |
| REP-004 | Exportar reporte a formato PDF/CSV (si aplica) | Media |
| REP-005 | Reporte sin datos debe mostrar mensaje informativo | Baja |

**Escenarios a ejecutar (Usuarios):**

| ID | Escenario | Prioridad |
| -- | --------- | --------- |
| USR-001 | Crear usuario con rol y contraseña | Alta |
| USR-002 | Crear usuario con username duplicado (debe rechazar) | Alta |
| USR-003 | Crear usuario sin email (debe rechazar) | Alta |
| USR-004 | Iniciar sesión con credenciales correctas | Alta |
| USR-005 | Iniciar sesión con credenciales incorrectas (debe rechazar) | Alta |
| USR-006 | Cerrar sesión | Alta |
| USR-007 | Actualizar datos de usuario existente | Alta |
| USR-008 | Cambiar contraseña de usuario | Alta |
| USR-009 | Cambiar contraseña sin contraseña nueva (debe rechazar) | Alta |
| USR-010 | Eliminar usuario | Alta |
| USR-011 | Listar todos los usuarios con sus roles | Alta |
| USR-012 | Listar solo cajeros | Media |
| USR-013 | Listar solo vendedores | Media |
| USR-014 | Acceder a funcionalidades sin autenticación (debe redirigir/rechazar) | Alta |
| USR-015 | Usuario sin rol intenta acceder a función restringida (debe rechazar) | Alta |

**Criterios de aceptación:**
- Los reportes reflejan datos correctos y consistentes.
- La administración de usuarios permite crear, actualizar, eliminar y listar.
- La autenticación JWT funciona correctamente (login, logout, refresh).
- Los permisos por rol se aplican correctamente.
- Las contraseñas se almacenan de forma segura (hash).

### 9.6. Resultados y Reporte (TSK-17)

**Fecha:** 10/06/2026
**Responsable:** QA
**Objetivo:** Consolidar los resultados de todas las ejecuciones de QA del Sprint 2 en un informe final.

**Entregables del informe:**
- Resumen ejecutivo de la calidad del sistema.
- Matriz de casos ejecutados por módulo con estado (APROBADO / FALLIDO / BLOQUEADO).
- Lista de defectos encontrados con severidad (CRÍTICO, ALTO, MEDIO, BAJO).
- Evidencia de ejecución (capturas de pantalla, logs).
- Recomendaciones para el Sprint 3.
- Métricas de calidad:
  - Porcentaje de casos aprobados.
  - Densidad de defectos por módulo.
  - Tiempo promedio de ejecución por caso.

**Formato del informe:** Documento PDF + presentación al equipo.

---

## 10. Planificación de Pruebas de Integración

### 10.1. Alcance de Integración

Las pruebas de integración verifican la comunicación correcta entre los siguientes componentes del sistema RegistraMe:

| Componente A | Componente B | Protocolo / Medio | Prioridad |
| ------------ | ------------ | ----------------- | --------- |
| Backend (Django REST API) | Frontend (Tauri + Svelte) | HTTP REST (JSON) | Alta |
| Backend | Base de datos PostgreSQL | Django ORM | Alta |
| Backend | Servicio RENIEC (consulta DNI) | HTTPS / REST | Media |
| Backend | Servicio SUNAT (consulta RUC) | HTTPS / REST | Media |
| Backend | Impresora térmica | Subprocess (ESC/POS) | Baja |
| Autenticación JWT | Frontend | HTTP Headers (Bearer token) | Alta |
| Módulo POS | Módulo Cash (cajas) | API interna REST | Alta |
| Módulo Sales | Módulo Products (stock) | API interna REST | Alta |

### 10.2. Estrategia de Integración

Se adopta un enfoque de **integración ascendente (bottom-up)**, comenzando por los componentes de menor nivel (base de datos, modelos) y progresando hacia los de mayor nivel (interfaz de usuario).

**Fases de integración:**

| Fase | Componentes | Descripción |
| ---- | ----------- | ----------- |
| 1 | Modelos + Base de datos | Verificar migraciones, constraints, relaciones y consultas ORM |
| 2 | APIs REST internas | Probar comunicación entre módulos (Sales→Products para stock, Sales→Cash para registro de caja) |
| 3 | Autenticación (Backend→Frontend) | Verificar flujo JWT: login, token refresh, protección de rutas |
| 4 | Backend→Servicios externos | Probar consulta DNI/RUC con API real (en entorno controlado) |
| 5 | Backend→Impresora | Probar generación de ticket e impresión (con impresora de prueba) |
| 6 | Full stack (Backend + Frontend) | Pruebas end-to-end de flujos completos de usuario |

**Herramientas propuestas:**
- **Postman / Insomnia**: para pruebas manuales de integración de APIs.
- **pytest + requests**: para pruebas automatizadas de integración de APIs.
- **Django test client**: para pruebas de integración entre módulos del backend.
- **GitHub Actions**: para ejecutar pruebas de integración en CI/CD (futuro).

### 10.3. Hitos de Integración (TSK-25, TSK-26)

| Hito | Descripción | Fecha estimada | Responsable |
| ---- | ----------- | :------------: | ----------- |
| H01 | Estrategia de integración definida y documentada (TSK-25) | 11/06/2026 | Desarrollo / QA |
| H02 | Plan de pruebas de integración completo (TSK-26) | 11/06/2026 | Desarrollo / QA |
| H03 | Integración de modelos con base de datos verificada | 15/06/2026 | Desarrollo |
| H04 | Integración entre módulos REST internos verificada | 18/06/2026 | Desarrollo |
| H05 | Integración de autenticación JWT verificada | 20/06/2026 | Desarrollo / QA |
| H06 | Integración con servicios externos (DNI/RUC) verificada | 22/06/2026 | Desarrollo |
| H07 | Prueba de integración full stack completada | 27/06/2026 | QA |
| H08 | Informe de integración y recomendaciones | 30/06/2026 | QA |

**Criterios de aceptación para integración:**
- Todos los endpoints REST documentados responden con los códigos HTTP esperados.
- La autenticación JWT funciona en todas las rutas protegidas.
- El flujo de datos entre módulos (POS → Cash → Products) es consistente y transaccional.
- Los servicios externos se integran con manejo de errores (timeout, caída del servicio).
- El frontend Tauri puede consumir todos los endpoints del backend sin errores CORS.

---
