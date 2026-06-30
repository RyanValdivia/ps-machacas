# Informe de Pruebas de Sistema, Aceptación e Integración — RegistraMe (Sprint 3-4)

---

## 1. Resumen Ejecutivo de Calidad

Este informe consolida los resultados de la ejecución de la suite completa de pruebas para el proyecto **RegistraMe**, correspondiente al Sprint 3-4 (Tercer Hito - Entrega al 100%).

Se han implementado y ejecutado exitosamente:
1. **Pruebas de Integración (Backend)**: 10 escenarios cubriendo la persistencia de base de datos ORM, la transaccionalidad de inventario, el control de caja en el Punto de Venta (POS), la adquisición y uso de tokens JWT, niveles de permisos (vendedor vs gerente) y consulta externa (DNI/RUC).
2. **Pruebas de Sistema y Aceptación (E2E con Playwright)**: Suite de pruebas en navegadores reales automatizando los flujos críticos de Login y navegación del Dashboard y Sidebar.
3. **CI/CD Automatizado**: Integración completa en el flujo de pre-despliegue de GitHub Actions para la rama `qa`.

### Métricas de Ejecución
* **Pruebas de Integración**: 10 ejecutadas, 10 aprobadas (100% de éxito).
* **Pruebas de Sistema (Playwright)**: 2 suites ejecutadas, 2 aprobadas (100% de éxito).
* **Defectos Críticos/Altos Abiertos**: 0.

---

## 2. Resultados Detallados de Pruebas de Integración

Las pruebas fueron ejecutadas utilizando la base de datos de pruebas PostgreSQL configurada para el entorno de test (`settings_test.py`).

| ID | Caso de Prueba | Detalle del Caso | Resultado |
| :--- | :--- | :--- | :---: |
| **INT-01** | `test_int_01_venta_descuenta_stock` | Verificar reducción de stock tras venta de producto. | **APROBADO** |
| **INT-02** | `test_int_02_venta_insuficiente_stock` | Verificar rollback ante stock insuficiente. | **APROBADO** |
| **INT-03** | `test_int_03_venta_actualiza_saldo_caja` | Verificar saldo acumulado y registro en caja abierta. | **APROBADO** |
| **INT-04** | `test_int_04_venta_sin_caja_activa_falla` | Validar rechazo de pagos sin sesión de caja abierta. | **APROBADO** |
| **INT-05** | `test_int_05_jwt_autenticacion` | Adquisición y uso de tokens de acceso y refresco JWT. | **APROBADO** |
| **INT-06** | `test_int_06_proxy_dni_requiere_auth` | Denegación de consulta proxy DNI sin cabecera Bearer. | **APROBADO** |
| **INT-07** | `test_int_07_proxy_dni_parametro_invalido` | Respuesta correcta ante parámetros erróneos en proxy DNI. | **APROBADO** |
| **INT-08** | `test_int_08_permisos_por_nivel` | Validar rechazo de acceso a usuarios sin nivel administrativo (vendedor vs gerente). | **APROBADO** |
| **INT-09** | `test_int_09_proxy_ruc_requiere_auth` | Denegación de consulta proxy RUC sin cabecera Bearer. | **APROBADO** |
| **INT-10** | `test_int_10_proxy_ruc_parametro_invalido` | Respuesta correcta ante parámetros erróneos en proxy RUC. | **APROBADO** |

---

## 3. Resultados Detallados de Pruebas de Sistema y Aceptación (E2E)

Las pruebas simuladas con Playwright levantaron la aplicación frontend en `http://localhost:5173` y validaron el comportamiento interactivo sobre el motor Chromium.

| ID | Suite / Prueba | Flujo Evaluado | Resultado |
| :--- | :--- | :--- | :---: |
| **SYS-01** | `login.spec.ts` | Validar inicio de sesión exitoso con credenciales válidas y redirección al Dashboard. | **APROBADO** |
| **SYS-02** | `login.spec.ts` | Validar mensaje de error ante credenciales inválidas. | **APROBADO** |
| **SYS-03** | `dashboard.spec.ts` | Validar navegación a la vista de Inventario y Clientes utilizando el Sidebar principal. | **APROBADO** |

---

## 4. Estado de la Integración Continua (CI/CD)

El pipeline en **[deploy-qa.yml](file:///.github/workflows/deploy-qa.yml)** ha sido reconfigurado para incluir la fase de pruebas automatizadas E2E.

Al hacer `push` o `Pull Request` a la rama `qa`:
1. El backend realiza pruebas unitarias y de integración.
2. Si tienen éxito, el job `e2e` se dispara de forma paralela:
   - Levanta el servicio Postgres temporal.
   - Aplica migraciones y la semilla de base de datos.
   - Inicia el backend Django de prueba en el puerto `8000`.
   - Compila e inicia el frontend React en el puerto `5173`.
   - Ejecuta de forma headless `npx playwright test`.
3. Si la suite de Playwright pasa (retornando exitosamente), se permite la compilación del contenedor Docker y su posterior despliegue automatizado por SSH en el servidor VPS QA.
4. En caso de falla, la ejecución se detiene y se suben las capturas de pantalla/videos resultantes a los artefactos de la ejecución de GitHub Actions para el diagnóstico del desarrollador.

---

## 5. Conclusión y Recomendaciones de Calidad

* **Conclusión**: El entregable del Tercer Hito (Sprint 3-4) cumple con el 100% de los criterios de aceptación y calidad exigidos. El proceso de entrega está blindado contra regresiones funcionales gracias a la combinación de pruebas de integración backend y pruebas de aceptación de caja negra de sistema en la pipeline.
* **Recomendación**: Mantener actualizados los selectores HTML y las credenciales/seeds en los archivos de prueba a medida que se añadan nuevas funcionalidades al Punto de Venta.
