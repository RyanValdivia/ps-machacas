# Plan de Pruebas de Aceptación — UAT (User Acceptance Testing)
## RegistraMe — Sprint 4 (Hito 3)

---

| Campo | Detalle |
|---|---|
| **Proyecto** | RegistraMe — Sistema de Gestión para Ópticas |
| **Curso** | Pruebas de Software — EPIS-UNSA 2026-A |
| **Sprint** | Sprint 4 / Hito 3 |
| **Tipo de Prueba** | Pruebas de Aceptación — UAT (Prueba Beta Formal) |
| **Responsable de coordinación** | P3 (@FabbPP) |
| **Supervisor** | P1 (@FernandoGarambelM) |
| **Fecha de creación** | 08 de Julio de 2026 |
| **Versión** | 1.0 |

---

## Índice

1. [Introducción y Alcance](#1-introducción-y-alcance)
2. [Base Teórica — Pressman y la Prueba Beta](#2-base-teórica--pressman-y-la-prueba-beta)
3. [Procedimiento de la Sesión UAT](#3-procedimiento-de-la-sesión-uat)
4. [Matriz de Validación UAT](#4-matriz-de-validación-uat)
5. [Criterios de Aceptación por Módulo](#5-criterios-de-aceptación-por-módulo)
6. [Entorno y Preparación](#6-entorno-y-preparación)
7. [Registro de Evidencias](#7-registro-de-evidencias)
8. [Criterios de Salida y Firma](#8-criterios-de-salida-y-firma)

---

## 1. Introducción y Alcance

El presente documento establece el **Plan Formal de Pruebas de Aceptación (UAT)** para el proyecto **RegistraMe** en el Sprint 4 (Tercer Hito). Las pruebas de aceptación constituyen la validación definitiva del software, respondiendo a la pregunta fundamental de la calidad:

> *"¿Construimos el producto correcto?"*

A diferencia de las pruebas de sistema (que verifican si el software funciona según los requisitos técnicos), las pruebas de aceptación verifican si el software satisface las **necesidades reales del negocio** desde la perspectiva del usuario final.

### Alcance

La sesión UAT cubre los 12 escenarios de negocio más críticos del sistema RegistraMe, agrupados en los módulos:
- **Autenticación:** Login y control de acceso
- **POS y Caja:** Apertura, ventas, pagos, cierre y anulación
- **Inventario:** Gestión de productos y stock
- **Reportes y Configuración:** Dashboard, usuarios, restricciones de acceso

---

## 2. Base Teórica — Pressman y la Prueba Beta

Las pruebas de aceptación del presente plan se fundamentan en **Roger Pressman (2010)**:

> *"La validación responde a la pregunta: ¿construimos el producto correcto? La prueba beta debe realizarse por los usuarios finales en su propio entorno, no por los desarrolladores."*

### Principios aplicados

| Principio | Aplicación en este plan |
|---|---|
| **Ejecución por el usuario final** | El usuario externo ejecuta los escenarios. El equipo solo observa y registra, sin intervenir |
| **Entorno real del usuario** | La sesión se realiza con el sistema desplegado en VPS o con pantalla compartida desde equipo del usuario |
| **Entregable obligatorio: firma** | El resultado no puede ser "el usuario dijo que estaba bien". Debe existir la **Matriz UAT firmada** digitalmente |
| **Validación del negocio, no del código** | Los criterios de aceptación están redactados en lenguaje de negocio, no técnico |

### Diferencia entre Prueba Alpha y Beta (Pressman)

| | Prueba Alpha | Prueba Beta |
|---|---|---|
| **¿Quién la hace?** | El equipo de desarrollo | El usuario final real |
| **¿Dónde?** | En el entorno del desarrollador | En el entorno del usuario |
| **¿Qué busca?** | Defectos antes de liberar al usuario | Validar que el software cumple las expectativas del negocio |
| **En este proyecto** | Las pruebas E2E y de integración | **Esta sesión UAT** |

---

## 3. Procedimiento de la Sesión UAT

### Paso 1: Coordinación previa (P3 — antes de la sesión)

- [ ] Contactar al usuario externo y confirmar fecha y hora
- [ ] Comunicar al usuario que la sesión dura aproximadamente **45–60 minutos**
- [ ] Confirmar que el usuario tiene: dispositivo con navegador web y conexión a internet
- [ ] Compartir previamente la URL del sistema (VPS) o coordinar pantalla compartida

### Paso 2: Preparación del entorno (P3 — 1 hora antes)

- [ ] Verificar que el sistema está accesible desde la URL del usuario
- [ ] Cargar los datos seed: usuarios de prueba, productos, caja disponible
- [ ] Preparar esta Matriz UAT en formato digital (Google Sheets o similar)
- [ ] Configurar grabación de pantalla (OBS Studio o grabación de Google Meet/Zoom)
- [ ] Tener una copia impresa/digital de los 12 escenarios para guiar al usuario

### Paso 3: Ejecución de la sesión

1. Iniciar la grabación de pantalla
2. Dar la bienvenida al usuario y explicar el propósito (validar que el sistema cumple sus necesidades)
3. Aclarar que el usuario **no puede equivocarse** — si algo no funciona como espera, eso es información valiosa
4. Ir escenario por escenario (UAT-01 a UAT-12) siguiendo el orden de la matriz
5. Por cada escenario:
   - Leer el criterio en voz alta al usuario
   - Dejar que el usuario ejecute los pasos sin ayuda del equipo (observar, no intervenir)
   - Preguntar: *"¿Esto cumple con lo que esperabas para esta situación?"*
   - Anotar la respuesta y observaciones en la columna correspondiente
6. Al finalizar, solicitar confirmación escrita (ver §8)

### Paso 4: Post-sesión

- [ ] Guardar el video de la sesión
- [ ] Completar la columna "Observaciones" con las notas tomadas
- [ ] Redactar la sección IEEE §V.D con los resultados

---

## 4. Matriz de Validación UAT

> **Instrucciones para completar:** La columna "Validado" se marca ✅ si el usuario confirma que el criterio se cumple, ❌ si no se cumple (anotar el defecto en "Observaciones").

| ID | Rol del Usuario | Historia de Usuario | Criterio de Aceptación | Pasos a ejecutar por el usuario | Validado | Observaciones del Usuario |
|---|---|---|---|---|---|---|
| **UAT-01** | Vendedor | Como **vendedor**, quiero iniciar sesión para acceder al sistema | El sistema permite login con credenciales válidas y redirige al Dashboard en menos de 5 segundos | 1. Abrir el sistema 2. Ingresar usuario y contraseña 3. Clic en "Entrar" | ⬜ | |
| **UAT-02** | Cajero | Como **cajero**, quiero abrir caja para comenzar a registrar ventas | Al abrir caja con monto inicial, el sistema habilita el Punto de Venta y muestra confirmación | 1. Ir a Punto de Venta 2. Ingresar monto inicial S/100 3. Clic "Abrir Caja" | ⬜ | |
| **UAT-03** | Vendedor | Como **vendedor**, quiero registrar una venta de monturas | El carrito muestra productos, precio y total; genera comprobante al confirmar el pago | 1. Buscar una montura 2. Agregarla al carrito 3. Seleccionar forma de pago 4. Confirmar | ⬜ | |
| **UAT-04** | Vendedor | Como **vendedor**, quiero registrar una venta con lunas personalizadas | El sistema permite configurar tipo y material de luna con actualización dinámica del precio | 1. Agregar montura al carrito 2. Activar opción de luna personalizada 3. Seleccionar características 4. Verificar precio | ⬜ | |
| **UAT-05** | Vendedor | Como **vendedor**, quiero registrar pagos parciales (adelantos) | El sistema calcula el saldo pendiente y permite completar el pago en otro momento | 1. Crear venta 2. Pagar solo una parte del total 3. Verificar que el estado muestra saldo pendiente | ⬜ | |
| **UAT-06** | Cajero | Como **cajero**, quiero cerrar caja al final del turno | El cierre muestra el balance del turno: ventas registradas, monto esperado y diferencia con lo declarado | 1. Ir a Cierre de Caja 2. Ver el resumen de ventas 3. Ingresar el monto real en caja 4. Confirmar cierre | ⬜ | |
| **UAT-07** | Gerente | Como **gerente**, quiero ver reportes de ventas del día | El dashboard muestra gráficas de ventas por día, por vendedor y por caja con datos actualizados | 1. Ir a Reportes / Dashboard 2. Revisar las gráficas y datos del día | ⬜ | |
| **UAT-08** | Logística | Como **logística**, quiero gestionar el inventario de productos | El sistema permite agregar, buscar y filtrar productos mostrando el stock en tiempo real | 1. Ir a Inventario 2. Crear un nuevo producto 3. Buscarlo por nombre 4. Verificar stock | ⬜ | |
| **UAT-09** | Gerente | Como **gerente**, quiero gestionar los usuarios del sistema | El sistema permite crear, editar y asignar roles a usuarios; cada rol restringe el acceso correctamente | 1. Ir a Configuración → Usuarios 2. Crear un usuario nuevo con rol Vendedor 3. Verificar que aparece en la lista | ⬜ | |
| **UAT-10** | Vendedor | Como **vendedor**, quiero consultar los datos del cliente por DNI | Al ingresar un DNI, el sistema consulta RENIEC y autocompleta los nombres automáticamente | 1. En el formulario de cliente, ingresar un DNI 2. Verificar que los nombres se autocompletan | ⬜ | |
| **UAT-11** | Vendedor | Como **vendedor**, quiero anular una venta registrada por error | La anulación devuelve el stock del producto y marca la venta como ANULADA con un motivo registrado | 1. Ir a la lista de ventas 2. Seleccionar una venta 3. Clic en "Anular" 4. Ingresar motivo 5. Confirmar | ⬜ | |
| **UAT-12** | Gerente | Como **gerente**, quiero que el sistema impida el acceso no autorizado | Un usuario con rol Vendedor no puede acceder a la sección de Reportes ni Configuración | 1. Iniciar sesión como vendedor 2. Intentar navegar a Reportes 3. Intentar navegar a Configuración | ⬜ | |

---

## 5. Criterios de Aceptación por Módulo

| Módulo | Criterio mínimo de aceptación |
|---|---|
| Autenticación | UAT-01 y UAT-12 deben validarse ✅ obligatoriamente |
| POS y Caja | Al menos UAT-02, UAT-03 y UAT-06 deben validarse ✅ |
| Inventario | UAT-08 debe validarse ✅ |
| Pagos y Anulaciones | UAT-05 o UAT-11 deben validarse ✅ (al menos uno) |
| **Resultado global** | Mínimo 10 de 12 criterios ✅ para considerar el UAT aprobado |

---

## 6. Entorno y Preparación

### Datos seed necesarios para la sesión

| Dato | Descripción |
|---|---|
| Usuario gerente | `admin` / `admin123` (disponible en seed) |
| Usuario vendedor | `vendedor1` / `Admin123!` (disponible en seed) |
| Producto de prueba | "PEGASUS" — montura en stock (disponible en seed) |
| Caja disponible | Verificar que exista al menos una caja en el sistema |
| Cliente con DNI | Tener un DNI real disponible para probar UAT-10 |

### URL del sistema

- **Opción A (VPS desplegado):** URL pública del servidor QA — confirmar con P2 (@RyanValdivia)
- **Opción B (pantalla compartida):** Sistema corriendo localmente en máquina de P3 compartida por Google Meet/Zoom

---

## 7. Registro de Evidencias

Las siguientes evidencias deben recopilarse durante la sesión:

| Evidencia | Descripción | Responsable |
|---|---|---|
| Video de la sesión | Grabación completa de Google Meet/Zoom u OBS | P3 |
| Screenshots por escenario | Captura de pantalla del resultado de cada UAT | P3 |
| Observaciones del usuario | Notas textuales de los comentarios del usuario | P3 |
| Confirmación escrita | Mensaje de WhatsApp/correo del usuario confirmando su validación | P3 |

---

## 8. Criterios de Salida y Firma

### Definition of Done para este plan

- [ ] Sesión UAT ejecutada con el usuario externo real
- [ ] Video de la sesión guardado
- [ ] Capturas de pantalla de cada escenario validado
- [ ] Matriz UAT completada con resultados reales (✅ o ❌ por criterio)
- [ ] **Confirmación escrita del usuario** (mensaje o correo) — equivale a firma digital
- [ ] Sección IEEE §V.D redactada con:
  - Descripción del proceso UAT seguido
  - Resultados por criterio (tabla de la Matriz)
  - Observaciones textuales del usuario
  - Screenshots representativos embebidos

### Formato sugerido para la confirmación escrita del usuario

> *"Yo, [Nombre del usuario], confirmo haber participado en la sesión de validación del sistema RegistraMe el día [fecha], y valido que los criterios marcados como aprobados en la Matriz UAT cumplen con mis expectativas de negocio."*

Esta confirmación puede recibirse por mensaje de WhatsApp, correo electrónico o firma en documento digital. **Adjuntarla como evidencia al informe.**

---

*Documento preparado por: P1 (Fernando Garambel) — Líder / Coordinador*
*Basado en: Pressman, R. S. (2010). Software Engineering: A Practitioner's Approach. McGraw-Hill.*
*Trazabilidad: Plan Maestro de Pruebas §3.4 | ISO/IEC/IEEE 29119-3 | IEEE 829*
