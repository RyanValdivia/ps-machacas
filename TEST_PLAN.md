# Plan de Pruebas - ps-machacas

## 1. Objetos de Prueba (Test Objects)
Los siguientes componentes del repositorio forman el alcance de pruebas:
1. **hc/accounts**: autenticacion, perfiles, equipos, roles, credenciales y flujos de cuenta.
2. **hc/api**: modelos (Check, Ping, Channel, Notification), endpoints REST, logica de estados y reglas de negocio.
3. **hc/front**: vistas, formularios, validaciones y flujos UI web.
4. **hc/integrations**: integraciones externas (email, slack, telegram, signal, etc.) y sus transportes.
5. **hc/lib**: utilidades internas (fechas, firmas, HTML, emails, statsd, S3).
6. **hc/logs**: registro de eventos y auditoria.
7. **hc/settings.py / hc/urls.py**: configuracion critica y rutas.
8. **templates/** y **static/**: render basico de plantillas y recursos.

## 2. Objetivos de Testing y Calidad
**Objetivos:**
- Validar la correccion funcional de los flujos criticos (auth, checks, notificaciones).
- Detectar regresiones en modelos y endpoints principales.
- Verificar compatibilidad multi-BD (SQLite, Postgres, MySQL/MariaDB).
- Asegurar calidad de codigo con analisis estatico.

**Calidades priorizadas:**
- Confiabilidad, mantenibilidad, compatibilidad, seguridad basica y estabilidad ante regresiones.

## 3. Estrategia y Tecnicas de Prueba
**Enfoque:**
- **Caja blanca**: cobertura de logica en modelos, utilidades y reglas de negocio.
- **Caja negra**: validacion de entradas/salidas en vistas y endpoints.
- **Integracion**: flujos end-to-end (crear check -> ping -> notificar).
- **Analisis estatico**: mypy en modo estricto sobre `hc/`.
- **Cobertura**: coverage sobre `hc/` excluyendo `migrations` y `tests`.

**Herramientas actuales del repo:**
- Django test runner (CustomRunner en `hc.api.tests`).
- Workflows CI: `.github/workflows/tests.yml`, `mypy.yml`, `coverage.yml`.

## 4. Criterios de Salida y Cobertura (Exit Criteria)
El testing se considera suficiente cuando:
1. CI verde en **tests**, **mypy** y **coverage**.
2. Cobertura minima >= **80%** sobre `hc/` (excluye `migrations` y `tests`).
3. Defectos criticos abiertos = **0**.
4. No hay fallos nuevos en flujos criticos.

## 5. Entorno e Infraestructura de Pruebas
**Tecnologia:**
- Python 3.12+
- Django 6.0.5
- Dependencias: `requirements.txt` y `requirements-dev.txt`

**BD soportadas:**
- SQLite (default)
- Postgres / MySQL / MariaDB via `DB` y `DB_*`

**Ejecucion local basica:**
```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
python manage.py test
```

**CI (GitHub Actions):**
- `tests.yml`: matriz de BD + versiones de Python.
- `mypy.yml`: tipado estricto.
- `coverage.yml`: coverage + coveralls.

**Nota de plataforma:**
- En Windows, ciertas pruebas de `hc.integrations.signal` dependen de `AF_UNIX`. Para resultados consistentes, preferir Linux/CI.

## 6. Cronograma de Pruebas (10 semanas desde 28/05/2026)
| Semana | Fechas | Actividades principales | Entregables |
| --- | --- | --- | --- |
| 1 | 28/05/2026 - 03/06/2026 | Analisis del repo, riesgos y alcance. | Inventario de pruebas y riesgos. |
| 2 | 04/06/2026 - 10/06/2026 | Diseno de estrategia detallada y criterios de salida. | Estrategia y criterios aprobados. |
| 3 | 11/06/2026 - 17/06/2026 | Diseno de casos para `accounts`, `api`, `lib`. | Casos base priorizados. |
| 4 | 18/06/2026 - 24/06/2026 | Diseno de casos para `front` e `integrations`. | Casos por integraciones y UI. |
| 5 | 25/06/2026 - 01/07/2026 | Implementacion/ajuste de tests unitarios. | Suite unitaria actualizada. |
| 6 | 02/07/2026 - 08/07/2026 | Implementacion/ajuste de tests de integracion. | Suite de integracion estable. |
| 7 | 09/07/2026 - 15/07/2026 | Ejecucion multi-BD, analisis de fallos. | Reporte de fallos y fixes. |
| 8 | 16/07/2026 - 22/07/2026 | Cobertura y analisis estatico (mypy). | Reporte de cobertura/mypy. |
| 9 | 23/07/2026 - 29/07/2026 | Regresion completa en CI y hardening. | CI verde, backlog limpio. |
| 10 | 30/07/2026 - 05/08/2026 | Cierre: reporte final y lecciones aprendidas. | Informe final de testing. |

## Entregables
1. Plan de pruebas actualizado (este documento).
2. Reportes de ejecucion (CI + local).
3. Matriz de defectos y acciones correctivas.
4. Informe final de cierre.
