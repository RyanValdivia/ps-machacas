<div style="text-align: center; background: linear-gradient(135deg, #F0FDF4 0%, #E0F2FE 100%); padding: 40px 20px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #E2E8F0;">
  <img src="logo_mach_aca.png" alt="Logo La Machaca" width="160" style="border-radius: 50%; border: 4px solid #FFFFFF; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);" />
  <h1 style="color: #0F172A; font-size: 2.5rem; margin: 15px 0 5px 0; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">Proyecto Healthchecks</h1>
  <p style="color: #0284C7; font-size: 1.2rem; margin: 0 0 20px 0; font-weight: 500; letter-spacing: 0.5px;">QA Engineering Team: La Machaca</p>
  
  <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;">
    <img src="https://img.shields.io/badge/Language-Python_3.12+-0284C7?style=flat-square" />
    <img src="https://img.shields.io/badge/Framework-Django_6.0-0369A1?style=flat-square" />
    <img src="https://img.shields.io/badge/Licencia-BSD--3-0F766E?style=flat-square" />
    <img src="https://img.shields.io/badge/Target_Coverage-85%25-166534?style=flat-square" />
  </div>
</div>

<div style="background-color: #FFFFFF; border-left: 5px solid #0284C7; padding: 25px; border-radius: 4px 12px 12px 4px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03); margin-bottom: 35px; border-top: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; border-bottom: 1px solid #F1F5F9;">
  <h3 style="color: #1E293B; margin-top: 0; font-size: 1.3rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; font-weight: 600;">Información Institucional</h3>
  <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
    <tr>
      <td style="padding: 6px 0; color: #64748B; width: 25%; font-weight: 500;">Universidad:</td>
      <td style="padding: 6px 0; color: #334155;">Universidad Nacional de San Agustín (UNSA)</td>
    </tr>
    <tr>
      <td style="padding: 6px 0; color: #64748B; font-weight: 500;">Escuela:</td>
      <td style="padding: 6px 0; color: #334155;">Profesional de Ingeniería de Sistemas</td>
    </tr>
    <tr>
      <td style="padding: 6px 0; color: #64748B; font-weight: 500;">Curso:</td>
      <td style="padding: 6px 0; color: #334155;">Pruebas de Software</td>
    </tr>
    <tr>
      <td style="padding: 6px 0; color: #64748B; font-weight: 500;">Docente:</td>
      <td style="padding: 6px 0; color: #334155;">Mg. Robert E. Arisaca</td>
    </tr>
    <tr>
      <td style="padding: 6px 0; color: #64748B; font-weight: 500;">Sustentación:</td>
      <td style="padding: 6px 0; color: #334155;">Primer Hito — Sprint 1 (28/29 de Mayo de 2026)</td>
    </tr>
  </table>
  
  <p style="color: #1E293B; font-weight: 600; margin: 20px 0 10px 0; font-size: 1.05rem;">Integrantes del Equipo:</p>
  <ul style="color: #334155; margin: 0; padding-left: 20px; line-height: 1.6;">
    <li>Ajra Huacso, Jeans Anthony</li>
    <li>Garambel Marin, Fernando Miguel</li>
    <li>Hancco Mullisaca, Sergio Danilo</li>
    <li>Huacani Jara, Denise Andrea</li>
    <li>Luque Condori, Luis Guillermo</li>
    <li>Pacheco Palo, Fabiana Francinet</li>
    <li>Valdivia Segovia, Ryan Fabian</li>
  </ul>
</div>

## 1. Introducción

El presente plan de trabajo describe la organización, metodología, roles y lineamientos técnicos contemplados por el **Equipo La Machaca** para la ejecución de pruebas de software, aseguramiento de la calidad y automatización aplicados al repositorio oficial de **Healthchecks** (<https://github.com/healthchecks/healthchecks>).

El propósito fundamental de este proyecto es establecer una estrategia de QA orientada a prácticas ágiles, garantizando la trazabilidad desde los requerimientos iniciales hasta la automatización de la evidencia. El flujo completo se apoya en el ecosistema avanzado de GitHub: *GitHub Projects* para la gestión ágil, *GitHub Issues* para el backlog de historias de usuario, *GitHub Actions* para la ejecución continua de pipelines de testing, y *GitHub Pages* para la centralización de la documentación de la presentación formal del producto.

---

## 2. Definición del Proyecto

### 2.1. Descripción del Producto de Software Seleccionado

**Healthchecks** es un servicio interactivo y funcional de monitoreo diseñado para supervisar tareas programadas en segundo plano (cron jobs) e infraestructuras críticas orientada al sector empresarial y de TI médica. Funciona mediante un mecanismo de alertas activas: escucha peticiones HTTP y mensajes de correo electrónico ("pings") provenientes de las tareas automatizadas; si un "ping" no llega a tiempo dentro del margen configurado, el sistema detecta un fallo silencioso y despacha notificaciones de emergencia inmediatamente.

#### Características Principales del Sistema

* **Dashboard Médico de Control:** Panel centralizado que actualiza en tiempo real el estado operativo de cada chequeo de infraestructura.
* **Arquitectura API-First:** Posee una API REST robusta para gestionar, crear y supervisar alertas de forma programática.
* **Multicanal de Alertas:** Capacidad nativa para despachar alertas mediante canales como Slack, Discord, Telegram, Microsoft Teams, Webhooks, correos electrónicos y SMS.
* **Seguridad y Gestión:** Soporte para autenticación de dos factores (2FA) mediante WebAuthn, inicio de sesión externo por encabezados HTTP y gestión avanzada de proyectos por equipos.

#### Galería de Componentes del Producto

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">A. Dashboard Principal ("My Checks")</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Panel de control interactivo con actualizaciones en vivo que muestra la estabilidad global de los procesos conectados.</p>
  <div style="text-align: center;">
    <img src="my_checks.png" alt="Dashboard de Healthchecks" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">B. Configuración de Tolerancias (Period & Grace Time)</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Lógica de negocio interactiva para determinar las ventanas de tiempo esperadas y márgenes de gracia antes de disparar alertas.</p>
  <div style="text-align: center;">
    <img src="period_grace.png" alt="Parámetros de Tiempo" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">C. Historial Clínico de Eventos (Log de Chequeos)</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Bitácora detallada de pings entrantes con marcas de tiempo cronológicas, indispensable para auditar las pruebas de integración en el entorno de calidad.</p>
  <div style="text-align: center;">
    <img src="check_details.png" alt="Detalle del Evento" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

### 2.2. Alternativas Evaluadas

Antes de seleccionar el software definitivo, el equipo analizó minuciosamente tres alternativas técnicas bajo los mismos criterios de aceptación de QA:

1. **Django-Ledger (Empresarial):** Sistema de contabilidad financiera de doble entrada. Se descartó debido a que su volumen de código excedía el rango límite permitido por la rúbrica y presentaba inestabilidades técnicas complejas para la cobertura ágil.
2. **HealthDB (Salud):** Gestión de registros médicos. Fue descartado debido a que la gran mayoría de su base de código estaba desarrollada en componentes de interfaz gráfica (JavaScript/CSS), reduciendo el código Python a un porcentaje mínimo que no cumplía con el núcleo del stack solicitado.
3. **AcademicsToday Django (Educación):** Plataforma para cursos en línea. Se desestimó debido a que su enfoque principal no correspondía estrictamente a los sectores prioritarios requeridos (Empresarial o Salud) y presentaba una arquitectura desactualizada.

### 2.3. Justificación de la Elección Final

La elección de **Healthchecks** se fundamenta en su total cumplimiento con los criterios establecidos:

* **Stack y Licencia:** Construido puramente en Python/Django, empleando bases de datos relacionales libres, bajo una licencia compatible con los entornos académicos solicitados.
* **Tamaño Estricto:** Su núcleo de código de backend se mantiene estrictamente dentro del rango de **10,000 a 30,000 líneas de código útil**, permitiendo un análisis profundo y manejable.
* **Idoneidad para QA:** El proyecto ya cuenta con una suite nativa de pruebas estructuradas y una insignia de cobertura verificable. Esto permite al equipo estudiar los estándares de pruebas preexistentes, replicar los flujos y diseñar de manera óptima las nuevas suites unitarias y de integración necesarias para el cumplimiento del 85% solicitado.

---

## 3. Objetivos del Proyecto

* **Objetivo General:** Diseñar, implementar y automatizar una estrategia de aseguramiento de calidad ágil para la plataforma Healthchecks, incorporando pipelines de integración continua, trazabilidad absoluta de defectos y una cobertura final demostrable del **85%**.
* **Objetivos Específicos:**
  * Configurar un entorno de desarrollo local (DEV) homogéneo y reproducible para todos los miembros del equipo.
  * Definir formalmente el flujo de ramas de Git para la transición de código segura entre los entornos de `DEV` y `QA`.
  * Modelar las historias de usuario y criterios de aceptación mediante plantillas estructuradas en GitHub Issues.
  * Diseñar e implementar flujos automáticos en GitHub Actions para ejecutar pruebas de software ante cada Pull Request hacia la rama de calidad.
  * Incrementar y auditar la cobertura de código (Coverage) hasta asegurar un mínimo del 85% de efectividad en los módulos core.
  * Documentar de manera transparente las evidencias, métricas y reportes de defectos mediante GitHub Pages y GitHub Wiki.

---

## 4. Metodología de Trabajo

Se utiliza un enfoque ágil basado en **Scrum**. El trabajo se divide en iteraciones cortas denominadas Sprints, asegurando entregables funcionales y revisiones constantes del backlog de QA.

### Herramientas del Ecosistema de Gestión

* **Git:** Control de versiones y gestión de ramas fijas (`main`, `qa`, `dev`).
* **GitHub Projects:** Tablero Kanban/Scrum para el seguimiento de tareas (Backlog, Ready, In Progress, In Review, Done).
* **GitHub Issues:** Gestión de historias de usuario, tareas técnicas y reporte de bugs con etiquetas estandarizadas.
* **GitHub Actions:** Automatización de la ejecución de `pytest` y generación de reportes de cobertura.
* **GitHub Pages:** Publicación del Plan de Trabajo institucional y presentación oficial del producto seleccionado.
* **GitHub Wiki:** Documentación técnica interna, manuales de instalación (DEV) y Plan de Pruebas Unitarias detallado.

---

## 5. Roles y Responsabilidades

<table style="width: 100%; border-collapse: collapse; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 30px;">
  <thead>
    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 25%;">Rol QA</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 45%;">Responsabilidades Clave</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 30%;">Integrantes Asignados</th>
    </tr>
  </thead>
  <tbody style="color: #334155; line-height: 1.5;">
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Test Lead</td>
      <td style="padding: 12px;">Planificación estratégica, gestión de riesgos, control de Sprints y aprobación de entregables.</td>
      <td style="padding: 12px;">• Valdivia Segovia, Ryan Fabian<br>• Ajra Huacso, Jeans Anthony</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Test Analyst</td>
      <td style="padding: 12px;">Análisis de criterios de aceptación, diseño de historias de usuario y documentación de defectos.</td>
      <td style="padding: 12px;">• Luque Condori, Luis Guillermo</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Test Architect</td>
      <td style="padding: 12px;">Diseño del entorno de pruebas, configuración de pipelines CI/CD y estándares de automatización.</td>
      <td style="padding: 12px;">• Garambel Marin, Fernando Miguel<br>• Hancco Mullisaca, Sergio Danilo</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Test Designer</td>
      <td style="padding: 12px;">Creación detallada de casos de prueba, generación de datos de prueba y scripts de testing.</td>
      <td style="padding: 12px;">• Huacani Jara, Denise Andrea<br>• Pacheco Palo, Fabiana Francinet</td>
    </tr>
  </tbody>
</table>

---

## 6. Plan del Proyecto y Alcance

* **Alcance Funcional:** Las pruebas y el aseguramiento de calidad se concentrarán de forma estricta en los siguientes componentes del núcleo de Healthchecks:
  * Sistema de autenticación de usuarios, perfiles y tokens de administración.
  * Motor de procesamiento de peticiones (Pings) y verificación de tiempos de respuesta en segundo plano.
  * Módulos de integración de canales de alertas y notificaciones externas (Slack, Webhooks, etc.).
  * API REST técnica para la gestión remota de chequeos de servidores.
* **Fuera de Alcance:**
  * Auditorías completas de seguridad perimetral o pruebas de penetración avanzada.
  * Despliegue de servidores en entornos de producción comercial real.
  * Pruebas de carga masiva o rendimiento a gran escala fuera de entornos simulados de testing.

---

## 7. Cronograma de Sprints y Entregables

<table style="width: 100%; border-collapse: collapse; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 30px;">
  <thead>
    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 15%;">Sprint</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 20%;">Fechas</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 35%;">Actividades Principales de QA</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 30%;">Entregables Clave</th>
    </tr>
  </thead>
  <tbody style="color: #334155; line-height: 1.5;">
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600;">Sprint 0</td>
      <td style="padding: 12px; color: #64748B;">28/05 - 03/06</td>
      <td style="padding: 12px;">Análisis inicial del repositorio Healthchecks, identificación de riesgos y configuración de entornos (Pages/Actions).</td>
      <td style="padding: 12px;">Repositorio base, GitHub Pages activo y setup de entorno DEV.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600;">Sprint 1</td>
      <td style="padding: 12px; color: #64748B;">04/06 - 17/06</td>
      <td style="padding: 12px;">Definición de la estrategia detallada de testing y diseño de casos de prueba base para los módulos accounts, api y lib.</td>
      <td style="padding: 12px;">Backlog en GitHub Issues y matriz de casos base priorizados.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600;">Sprint 2</td>
      <td style="padding: 12px; color: #64748B;">18/06 - 01/07</td>
      <td style="padding: 12px;">Diseño de escenarios de prueba para la interfaz (front), integraciones externas y comienzo de la ejecución de pruebas unitarias.</td>
      <td style="padding: 12px;">Casos de prueba de UI e integraciones, suite unitaria actualizada.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600;">Sprint 3</td>
      <td style="padding: 12px; color: #64748B;">02/07 - 15/07</td>
      <td style="padding: 12px;">Implementación y ejecución de pruebas de integración. Pruebas de compatibilidad multi-base de datos (Postgres/MySQL) y análisis de fallos.</td>
      <td style="padding: 12px;">Suite de integración de la API estable y reporte de defectos inicial.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600;">Sprint 4</td>
      <td style="padding: 12px; color: #64748B;">16/07 - 29/07</td>
      <td style="padding: 12px;">Auditoría de cobertura de código (Coverage >= 85%), análisis de tipado estricto con mypy y pruebas de regresión completa en CI.</td>
      <td style="padding: 12px;">Reporte de cobertura final, pipeline verde y hardening del código.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600;">Sprint 5</td>
      <td style="padding: 12px; color: #64748B;">30/07 - 05/08</td>
      <td style="padding: 12px;">Fase de cierre de testing: preparación de métricas finales, lecciones aprendidas y empaquetado de evidencias para la entrega final.</td>
      <td style="padding: 12px;">Informe final de cierre de QA y matriz de defectos cerrada.</td>
    </tr>
  </tbody>
</table>

---

## 8. Estructura de Entornos y Flujo de Trabajo

### Flujo de Integración Continua (DEV ➔ QA ➔ MAIN)

Para garantizar la estabilidad del software, el equipo implementará un flujo de promoción de código estrictamente controlado por automatizaciones:

1. **Entorno DEV (Ramas de características):** Cada diseñador o arquitecto de pruebas escribe sus scripts localmente en ramas aisladas de tipo `feature/nombre-de-la-tarea`.
2. **Entorno QA (Rama `qa`):** Al solicitar la integración mediante un Pull Request hacia la rama `qa`, *GitHub Actions* se dispara automáticamente ejecutando la suite completa de pruebas. Si el porcentaje de cobertura disminuye por debajo del 85% o una prueba unitaria falla, la integración se bloquea de manera obligatoria para resguardar la calidad.
3. **Entorno Estable (Rama `main`):** Una vez validadas todas las pruebas y métricas en el entorno de calidad, el Test Lead autoriza el paso final (merge) del código hacia la rama principal estable.

---
<div style="background-color: #F0F9FF; border: 1px solid #BEE3F8; padding: 15px; border-radius: 6px; text-align: center; color: #0369A1; font-weight: 500;">
  Información Técnica Adicional: El detalle del Plan de Pruebas Unitarias, la guía de comandos de instalación y la configuración técnica de desarrollo local se encuentran centralizados en nuestra <a href="https://github.com/tu-usuario/tu-repositorio/wiki" style="color: #0284C7; font-weight: bold; text-decoration: underline;">Wiki Oficial del Proyecto</a>.
</div>
---
