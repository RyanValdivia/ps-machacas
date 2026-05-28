<div align="center">
  <img src="logo_machaca.png" alt="Logo La Machaca" width="400"/>
  <h1> Proyecto Healthchecks <br> <small>QA Team: La Machaca</small></h1>

  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Licencia-BSD--3-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Meta_de_Cobertura-85%25-success?style=for-the-badge" />
</div>

<br>

---

## Información Institucional

* **Universidad:** Universidad Nacional de San Agustín (UNSA)
* **Escuela:** Profesional de Ingeniería de Sistemas
* **Curso:** Pruebas de Software
* **Integrantes del Equipo:**
  * Ajra Huacso, Jeans Anthony
  * Garambel Marin, Fernando Miguel
  * Hancco Mullisaca, Sergio Danilo
  * Huacani Jara, Denise Andrea
  * Luque Condori, Luis Guillermo
  * Pacheco Palo, Fabiana Francinet
  * Valvidia Segovia, Ryan Fabian
* **Docente:** Mg. Robert E. Arisaca
* **Ubicación:** Arequipa, Perú
* **Fecha de Entrega:** 21 de mayo de 2026

---

## 1. Introducción

El presente plan de trabajo describe la organización, metodología, roles y lineamientos técnicos contemplados por el **Equipo La Machaca** para la ejecución de pruebas de software, aseguramiento de la calidad y automatización aplicados al repositorio oficial de **Healthchecks** (<https://github.com/healthchecks/healthchecks>).

El propósito fundamental de este proyecto es establecer una estrategia de QA orientada a prácticas ágiles, garantizando la trazabilidad desde los requerimientos iniciales hasta la automatización de la evidencia. El flujo completo se apoya en el ecosistema avanzado de GitHub: *GitHub Projects* para la gestión ágil, *GitHub Issues* para el backlog de historias de usuario, *GitHub Actions* para la ejecución continua de pipelines de testing, y *GitHub Pages* para la centralización de la documentación técnica.

La estrategia prioriza la construcción y réplica esctructurada de pruebas unitarias e integración siguiendo el principio de detección temprana de defectos, asegurando que cada incremento sea auditable y cumpla con los exigentes estándares solicitados.

---

## 2. Definición del Proyecto

### 2.1. Descripción del Proyecto Elegido

El software seleccionado es **Healthchecks**, una plataforma interactiva de monitoreo diseñada para supervisar tareas programadas en segundo plano (cron jobs) e infraestructuras críticas orientada al sector empresarial y de infraestructura TI. Funciona mediante alertas activas: si un proceso automatizado o respaldo de datos no se reporta a tiempo, el sistema notifica de inmediato fallos a través de múltiples canales integrados.

Desarrollado sobre el framework **Django utilizando Python**, el sistema destaca por tener una arquitectura web funcional, limpia y modular. Al prescindir de componentes pesados en el frontend, concentra su lógica en el backend, convirtiéndose en el escenario idóneo para la aplicación rigurosa de pruebas automatizadas en entornos aislados.

### 2.2. Alternativas Evaluadas

Antes de seleccionar el software definitivo, el equipo analizó minuciosamente tres alternativas técnicas:

1. **Django-Ledger (Empresarial):** Sistema de contabilidad financiera de doble entrada. Aunque poseía una robusta lógica de negocio, se descartó debido a que su volumen de código excedía el rango límite permitido y presentaba inestabilidades técnicas críticas para la cobertura ágil.
2. **HealthDB (Salud):** Sistema para la gestión de registros médicos. Fue descartado debido a que la gran mayoría de su base de código estaba desarrollada en componentes de interfaz gráfica (JavaScript/CSS), reduciendo el código Python a un porcentaje mínimo que no cumplía con el núcleo del stack solicitado.
3. **AcademicsToday Django (Educación):** Plataforma para cursos en línea. Se desestimó debido a que su enfoque principal no correspondía estrictamente a los sectores requeridos (Empresarial o Salud) y presentaba una arquitectura desactualizada en sus dependencias de desarrollo.

### 2.3. Justificación de la Elección Final

La elección de **Healthchecks** se fundamenta en su total cumplimiento con los criterios de aceptación del curso:

* **Stack y Licencia:** Construido puramente en Python/Django bajo un esquema de software libre permisivo.
* **Tamaño Controlado:** Su núcleo de código se mantiene estrictamente dentro del rango de 10,000 a 30,000 líneas de código útil, permitiendo un análisis exhaustivo.
* **Idoneidad para QA:** Cuenta con un sólido porcentaje de cobertura base verificable, lo que facilita al equipo estudiar los estándares de pruebas existentes, replicar los entornos y diseñar nuevos escenarios unitarios y de integración de manera óptima.

---

## 3. Objetivos del Proyecto

### Objetivo General

Diseñar, implementar y automatizar una estrategia de aseguramiento de calidad ágil para la plataforma Healthchecks, incorporando pipelines de integración continua, trazabilidad absoluta de defectos y una cobertura final demostrable.

### Objetivos Específicos

* Configurar un entorno de desarrollo local (DEV) homogéneo y reproducible para todos los miembros del equipo.
* Definir formalmente el flujo de ramas de Git para la transición de código segura entre los entornos de `DEV` y `QA`.
* Modelar las historias de usuario y criterios de aceptación mediante plantillas estructuradas en GitHub Issues.
* Diseñar e implementar flujos automáticos en GitHub Actions para ejecutar pruebas de software ante cada Pull Request.
* Incrementar y auditar la cobertura de código (Coverage) hasta asegurar un mínimo del 85% de efectividad.
* Documentar de manera transparente las evidencias, métricas y reportes de defectos mediante GitHub Pages y GitHub Wiki.

---

## 4. Metodología de Trabajo

Se utiliza un enfoque ágil basado en **Scrum**. El trabajo se divide en iteraciones cortas denominadas Sprints, asegurando entregables funcionales y revisiones constantes del backlog.

### Herramientas de Gestión

| Herramienta | Uso Específico en el Proyecto |
| :--- | :--- |
| **Git** | Control de versiones y gestión de ramas fijas (`main`, `qa`, `dev`). |
| **GitHub Projects** | Tablero Kanban (Backlog, Ready, In Progress, In Review, Done). |
| **GitHub Issues** | Gestión de historias de usuario, tareas técnicas y reporte de bugs con etiquetas. |
| **GitHub Actions** | Automatización de la ejecución de `pytest` y generación de reportes de cobertura. |
| **GitHub Pages** | Publicación del Plan de Trabajo institucional y presentación del equipo. |
| **GitHub Wiki** | Documentación técnica interna, manuales de instalación y planes de prueba detallados. |

---

## 5. Roles y Responsabilidades

El equipo se ha organizado distribuyendo las responsabilidades técnicas del ciclo de vida de pruebas de la siguiente manera:

| Rol QA | Responsabilidades Clave | Integrantes Asignados |
| :--- | :--- | :--- |
| **Test Lead** | Planificación estratégica, gestión de riesgos, control de Sprints y aprobación de entregables. | *Valdivia Segovia, Ryan Fabian<br>* Ajra Huacso, Jeans Anthony |
| **Test Analyst** | Análisis de criterios de aceptación, diseño de historias de usuario y documentación de defectos. | Luque Condori, Luis Guillermo |
| **Test Architect** | Diseño del entorno de pruebas, configuración de pipelines CI/CD y estándares de automatización. | *Garambel Marin, Fernando Miguel<br>* Hancco Mullisaca, Sergio Danilo |
| **Test Designer** | Creación detallada de casos de prueba, generación de datos de prueba y scripts de testing. | *Huacani Jara, Denise Andrea<br>* Pacheco Palo, Fabiana Francinet |

---

## 6. Plan del Proyecto y Alcance

### Alcance Funcional

Las pruebas y el aseguramiento de calidad se concentrarán de forma estricta en los siguientes componentes del núcleo de Healthchecks:

* Sistema de autenticación de usuarios y perfiles de administración.
* Motor de procesamiento de peticiones (Pings) y verificación de tiempos de respuesta.
* Módulos de integración de canales de alertas y notificaciones externas.
* API REST técnica para la gestión remota de chequeos de servidores.

### Fuera de Alcance

* Auditorías completas de seguridad perimetral o pruebas de penetración avanzada.
* Despliegue de servidores en entornos de producción comercial real.
* Pruebas de carga masiva o rendimiento a gran escala fuera de entornos simulados.

---

## 7. Cronograma de Sprints y Entregables

Por completar--

## 8. Estructura de Entornos y Flujo de Trabajo

### Flujo de Integración Continua (DEV ➔ QA ➔ MAIN)

Para garantizar la estabilidad del software, el equipo implementará un flujo de promoción de código estrictamente controlado por automatizaciones:

1. **Entorno DEV (Ramas de características):** Cada diseñador o arquitecto de pruebas escribe sus scripts localmente en ramas de tipo `feature/`.
2. **Entorno QA (Rama `qa`):** Al solicitar la integración mediante un Pull Request hacia la rama `qa`, *GitHub Actions* se dispara automáticamente ejecutando la suite completa de pruebas. Si el porcentaje de cobertura disminuye o una prueba falla, la integración se bloquea de manera obligatoria.
3. **Entorno Estable (Rama `main`):** Una vez validadas todas las pruebas y métricas en el entorno de calidad, el Test Lead autoriza el paso final del código hacia la rama principal.
