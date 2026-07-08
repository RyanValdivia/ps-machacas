# Plan de Pruebas No Funcionales — Estrés, Carga y Seguridad
## RegistraMe — Sprint 4 (Hito 3)

---

| Campo | Detalle |
|---|---|
| **Proyecto** | RegistraMe — Sistema de Gestión para Ópticas |
| **Curso** | Pruebas de Software — EPIS-UNSA 2026-A |
| **Sprint** | Sprint 4 / Hito 3 |
| **Tipo de Prueba** | Pruebas No Funcionales — Estrés/Carga (Locust) + Seguridad (pytest) |
| **Herramientas** | Locust (Python) · pytest + DRF APIClient |
| **Responsables** | P6 (@AjraHuacsoAnthony) — Estrés/Carga · P7 (@shanccom) — Seguridad |
| **Fecha de creación** | 08 de Julio de 2026 |
| **Versión** | 1.0 |

---

## Índice

1. [Introducción y Alcance](#1-introducción-y-alcance)
2. [Base Teórica — Spillner y la Mochila](#2-base-teórica--spillner-y-la-mochila)
3. [Estrategia de Pruebas de Estrés y Carga (Locust)](#3-estrategia-de-pruebas-de-estrés-y-carga-locust)
4. [Estrategia de Pruebas de Seguridad (pytest)](#4-estrategia-de-pruebas-de-seguridad-pytest)
5. [Catálogo de Casos de Prueba No Funcionales](#5-catálogo-de-casos-de-prueba-no-funcionales)
   - 5.1 [Pruebas de Estrés y Carga](#51-pruebas-de-estrés-y-carga)
   - 5.2 [Pruebas de Seguridad](#52-pruebas-de-seguridad)
6. [Métricas y Criterios de Aceptación](#6-métricas-y-criterios-de-aceptación)
7. [Entorno de Pruebas y Herramientas](#7-entorno-de-pruebas-y-herramientas)
8. [Criterios de Salida](#8-criterios-de-salida)

---

## 1. Introducción y Alcance

El presente documento establece el **Plan Formal de Pruebas No Funcionales** para el proyecto **RegistraMe** en el Sprint 4 (Tercer Hito). Las pruebas no funcionales verifican que el sistema cumple con atributos de calidad más allá de la funcionalidad: **rendimiento bajo carga concurrente**, **resistencia a condiciones de carrera** y **seguridad ante accesos no autorizados e inyecciones**.

### Alcance

**Pruebas de Estrés y Carga (Locust):**
- Comportamiento del módulo POS ante 50 usuarios concurrentes creando ventas
- Integridad de stock ante 10 usuarios comprando simultáneamente el mismo producto (race condition)
- Tiempo de respuesta del endpoint de búsqueda ante 100 usuarios con filtros combinados
- Latencia del sistema de autenticación JWT ante pico de 100 logins simultáneos
- Carga sostenida del dashboard de estadísticas durante 5 minutos

**Pruebas de Seguridad (pytest):**
- Rechazo de peticiones a endpoints protegidos sin token JWT
- Control de acceso basado en roles (vendedor vs. gerente)
- Comportamiento ante tokens JWT expirados o manipulados
- Resistencia a inyecciones SQL en parámetros de búsqueda

### Fuera de alcance

- Pruebas funcionales E2E (ver `PLAN_PRUEBAS_SISTEMA_E2E.md`)
- Pruebas de aceptación con usuario externo (ver `PLAN_PRUEBAS_ACEPTACION_UAT.md`)
- Pruebas de penetración avanzadas (fuera del alcance del curso)

---

## 2. Base Teórica — Spillner y la Mochila

Las pruebas no funcionales del presente plan se fundamentan en el **Principio de la Mochila** de **Andreas Spillner**:

> *"Las pruebas no funcionales pueden verse como una mochila acoplada a las pruebas funcionales. No inventan flujos nuevos; toman los flujos funcionales ya diseñados y miden cómo se comportan bajo condiciones extremas."*

### Aplicación práctica en este plan

P6 **no necesita diseñar flujos nuevos**. Debe tomar los flujos funcionales ya especificados por P4 (realizar una venta, abrir caja) y ejecutarlos con Locust simulando **50 o 100 usuarios virtuales al mismo tiempo**, midiendo:

- ¿Cuántas solicitudes por segundo puede atender el sistema?
- ¿Cuánto tiempo tarda el percentil 95 (P95) de las respuestas?
- ¿Se producen condiciones de carrera (race conditions) en el stock?
- ¿El sistema falla graciosamente o colapsa?

Este acoplamiento garantiza que las pruebas de carga sean **representativas del uso real** del sistema, no pruebas artificiales desconectadas del negocio.

---

## 3. Estrategia de Pruebas de Estrés y Carga (Locust)

### 3.1 Instalación

```bash
pip install locust

# Verificar
locust --version
```

### 3.2 Estructura de archivos

```
backend/tests/stress/
├── __init__.py
├── locustfile_pos.py         → NF-STRESS-01, NF-STRESS-03, NF-STRESS-05
├── locustfile_inventory.py   → NF-STRESS-02 (requiere seed masivo)
└── locustfile_auth.py        → NF-STRESS-04
```

### 3.3 Patrón de usuario virtual Locust

```python
from locust import HttpUser, task, between

class VendedorPOS(HttpUser):
    wait_time = between(1, 3)  # Simula tiempo humano entre acciones

    def on_start(self):
        """Login al nacer. Se ejecuta UNA sola vez por usuario virtual."""
        response = self.client.post("/api/user/token/", json={
            "usuNom": "vendedor1",
            "password": "Admin123!"
        })
        if response.status_code == 200:
            self.headers = {"Authorization": f"Bearer {response.json()['access']}"}
        else:
            self.headers = {}

    @task(3)  # peso 3 = se ejecuta 3x más que tareas con peso 1
    def buscar_productos(self):
        self.client.get("/api/products/?search=PEGASUS", headers=self.headers,
                        name="/api/products/?search=[term]")
```

### 3.4 Ejecución

```bash
# Con interfaz web (recomendado para explorar)
locust -f backend/tests/stress/locustfile_pos.py --host=http://localhost:8000
# Abrir http://localhost:8089 → configurar usuarios y duración → "Start swarming"

# Headless (para CI/reportes automáticos)
locust -f backend/tests/stress/locustfile_pos.py \
  --host=http://localhost:8000 \
  --users 50 --spawn-rate 10 --run-time 2m \
  --headless \
  --html=backend/tests/stress/report_pos.html
```

### 3.5 Seed masivo para NF-STRESS-02

La prueba de 100 búsquedas concurrentes requiere un catálogo de **1000+ productos** para ser representativa. Crear un script `seed_masivo.py` que inserte productos con variedad de marcas, materiales y tallas antes de ejecutar esta prueba.

---

## 4. Estrategia de Pruebas de Seguridad (pytest)

### 4.1 Estructura de archivos

```
backend/tests/security/
├── __init__.py
└── test_security.py   → NF-SEC-01, NF-SEC-02, NF-SEC-03, NF-SEC-04
```

### 4.2 Ejecución

```bash
cd backend
python -m pytest tests/security/test_security.py -v
```

### 4.3 Justificación técnica

Django REST Framework usa **Django ORM** para todas las consultas, lo que proporciona protección nativa contra inyecciones SQL al parametrizar automáticamente las consultas. La prueba NF-SEC-04 verifica que esta protección esté activa y que ningún payload SQL genere error 500 (que indicaría procesamiento SQL directo).

---

## 5. Catálogo de Casos de Prueba No Funcionales

### 5.1 Pruebas de Estrés y Carga

**Responsable:** P6 (@AjraHuacsoAnthony) — NF-STRESS-01, 02, 03, 05 | P7 (@shanccom) — NF-STRESS-04

| ID | Tipo | Endpoint Objetivo | Escenario (Mochila de Spillner) | Usuarios | Duración | Criterio de Éxito |
|---|---|---|---|---|---|---|
| **NF-STRESS-01** | Estrés | `POST /api/sales/ventas/` | Tomar flujo E2E-POS-02 (venta simple) y ejecutarlo con 50 usuarios concurrentes | 50 | 2 min | P95 ≤ 3s · Error rate < 5% · Sin race conditions |
| **NF-STRESS-02** | Carga | `GET /api/products/?search=...` | Tomar flujo E2E-INV-02 (búsqueda con filtros) y ejecutarlo con 100 usuarios concurrentes | 100 | 3 min | P95 ≤ 2s · 0 timeouts |
| **NF-STRESS-03** | Race Condition | `POST /api/sales/ventas/` (mismo producto) | 10 usuarios intentan comprar simultáneamente un producto con stock = 1 | 10 | 30 seg | **Exactamente 1 venta exitosa** · Stock final = 0 · 9 rechazadas con HTTP 400 |
| **NF-STRESS-04** | Pico de carga | `POST /api/user/token/` | Tomar flujo E2E-AUTH-01 (login) y ejecutarlo con 100 usuarios concurrentes en oleada | 100 | 1 min | P95 ≤ 2s · 100% tokens válidos · Error rate < 1% |
| **NF-STRESS-05** | Carga sostenida | `GET /api/sales/ventas/estadisticas_dashboard/` | 20 gerentes consultando dashboard durante 5 minutos continuos | 20 | 5 min | P95 ≤ 5s · Sin memory leaks |

> **Verificación especial NF-STRESS-03 (race condition):**
> Después de ejecutar la prueba, verificar el stock final directamente en la base de datos:
> ```sql
> SELECT stock FROM products_product WHERE id = <id_del_producto>;
> -- Resultado esperado: 0
> ```

### 5.2 Pruebas de Seguridad

**Responsable:** P7 (@shanccom)

| ID | Tipo | Escenario | Método | Criterio de Éxito |
|---|---|---|---|---|
| **NF-SEC-01** | Autenticación | Acceder a `GET /api/products/`, `GET /api/sales/ventas/`, `GET /api/user/list/`, `POST /api/cash/opening/`, `GET /api/user/me/` **sin** header `Authorization` | Request HTTP directo sin Bearer token | HTTP 401 Unauthorized en **todos** los endpoints |
| **NF-SEC-02** | Autorización RBAC | Vendedor (nivel 2) accede a `GET /api/user/list/` y `DELETE /api/user/delete/1/` con token válido de vendedor | Request con token de `vendedor1` a endpoints de Gerente | HTTP 403 Forbidden |
| **NF-SEC-03** | Token expirado | Usar access token expirado o manipulado para acceder a endpoints protegidos | Request con token inválido; verificar que refresh token funciona correctamente | HTTP 401 con token expirado · Refresh token genera nuevo access token |
| **NF-SEC-04** | Inyección SQL | Enviar payloads maliciosos en campo `search`: `'; DROP TABLE users; --` · `' OR '1'='1` · `1; SELECT * FROM users --` · `' UNION SELECT * FROM users --` | `GET /api/products/?search=<payload>` | Respuesta normal (HTTP 200 con lista vacía o filtrada) · **Sin HTTP 500** · Stock y tablas intactas |

---

## 6. Métricas y Criterios de Aceptación

### Tabla de resultados a completar (Locust)

| ID | Escenario | Usuarios | Duración | P50 Latencia | P95 Latencia | P99 Latencia | Error Rate | Throughput | ¿Pasó? |
|---|---|---|---|---|---|---|---|---|---|
| NF-STRESS-01 | Ventas concurrentes | 50 | 2 min | ___ ms | ___ ms | ___ ms | ___ % | ___ req/s | ✅/❌ |
| NF-STRESS-02 | Búsquedas masivas | 100 | 3 min | ___ ms | ___ ms | ___ ms | ___ % | ___ req/s | ✅/❌ |
| NF-STRESS-03 | Race condition stock=1 | 10 | 30 seg | N/A | N/A | N/A | N/A | N/A | ✅/❌ |
| NF-STRESS-04 | Login pico | 100 | 1 min | ___ ms | ___ ms | ___ ms | ___ % | ___ req/s | ✅/❌ |
| NF-STRESS-05 | Dashboard sostenido | 20 | 5 min | ___ ms | ___ ms | ___ ms | ___ % | ___ req/s | ✅/❌ |

### Cómo obtener cada métrica

| Métrica | Fuente |
|---|---|
| P50, P95, P99 latencia | Reporte HTML de Locust |
| Error rate | Reporte HTML de Locust |
| Throughput (req/s) | Reporte HTML de Locust |
| Stock final en BD | Query SQL post-prueba |
| Uso CPU/RAM | `docker stats` durante la prueba |

---

## 7. Entorno de Pruebas y Herramientas

| Elemento | Valor |
|---|---|
| Herramienta de estrés | Locust 2.x (Python) |
| Herramienta de seguridad | pytest + DRF APIClient |
| Backend bajo prueba | Django 5.2.10 + PostgreSQL |
| Modo de ejecución | Local (backend corriendo en `http://localhost:8000`) |
| Reportes Locust | HTML (`backend/tests/stress/report_*.html`) |
| Salida pytest | Consola + guardado manual para evidencia IEEE |

### Prerrequisito: Backend corriendo

```bash
# Opción Docker (recomendada)
cd infra/local && docker compose up -d

# Opción manual
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

---

## 8. Criterios de Salida

### Definition of Done para este plan

- [ ] 5 pruebas de estrés ejecutadas con reportes HTML generados y guardados
- [ ] NF-STRESS-03 verifica stock final = 0 con query SQL documentado
- [ ] 4 pruebas de seguridad ejecutadas, ninguna produce HTTP 500
- [ ] Tabla de métricas §6 completada con valores reales
- [ ] Gráficas de rendimiento de Locust exportadas para el IEEE
- [ ] Resultados documentados en el **Informe de Pruebas No Funcionales** (documento separado)

---

*Documento preparado por: P1 (Fernando Garambel) — Líder / Coordinador*
*Basado en: Spillner, A. (2014). Software Testing Foundations. dpunkt.verlag.*
*Trazabilidad: Plan Maestro de Pruebas §3.3 | ISO/IEC/IEEE 29119-3 | ISO/IEC 25010 (Performance, Security)*
