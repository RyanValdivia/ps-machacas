<div align="center">
  <img src="docs/logo_machaca.png" alt="Logo La Machaca" width="320" />
  <h1>Proyecto Healthchecks</h1>
  <p><strong>QA Team: La Machaca</strong></p>
</div>

Repositorio del proyecto final del curso **Pruebas de Software** (UNSA), enfocado en aseguramiento de calidad sobre el repositorio oficial de **Healthchecks**.

## Informacion institucional

- **Universidad:** Universidad Nacional de San Agustin (UNSA)
- **Escuela:** Ingenieria de Sistemas
- **Curso:** Pruebas de Software
- **Docente:** Mg. Robert E. Arisaca
- **Ubicacion:** Arequipa, Peru

## Integrantes

- Ajra Huacso, Jeans Anthony
- Garambel Marin, Fernando Miguel
- Hancco Mullisaca, Sergio Danilo
- Huacani Jara, Denise Andrea
- Luque Condori, Luis Guillermo
- Pacheco Palo, Fabiana Francinet
- Valdivia Segovia, Ryan Fabian

## 1. Introduccion

Este proyecto organiza la estrategia de QA del equipo **La Machaca** para validar calidad, estabilidad y trazabilidad sobre Healthchecks. El trabajo se ejecuta con enfoque agil, evidencia automatizada y seguimiento por sprint.

El flujo del proyecto se apoya en GitHub Projects, Issues, Actions, Pages y Wiki para mantener control de backlog, ejecucion de pruebas, cobertura y documentacion tecnica.

## 2. Definicion del proyecto

### 2.1 Proyecto elegido

- **Proyecto base:** Healthchecks
- **Repositorio fuente:** `https://github.com/healthchecks/healthchecks`
- **Stack principal:** Python, Django, Docker, PostgreSQL/MySQL/MariaDB
- **Dominio:** monitoreo de cron jobs y alertas por fallas operativas

### 2.2 Justificacion

Healthchecks cumple con los criterios del curso para trabajo QA:

- arquitectura real y modular,
- buena base para pruebas unitarias e integracion,
- cobertura inicial verificable para plantear mejora objetiva,
- entorno adecuado para automatizacion CI/CD.

## 3. Objetivos

### Objetivo general

Disenar e implementar una estrategia agil de aseguramiento de calidad para Healthchecks, con trazabilidad completa y automatizacion de pruebas.

### Objetivos especificos

- Estandarizar un entorno DEV reproducible para todo el equipo.
- Definir flujo de ramas DEV -> QA -> MAIN.
- Gestionar historias y defectos con GitHub Issues.
- Automatizar validaciones con GitHub Actions.
- Ejecutar pruebas unitarias e integracion.
- Medir y documentar cobertura, defectos y evidencias.
- Publicar documentacion en GitHub Pages/Wiki.

## 4. Metodologia de trabajo

Se aplica **Scrum** con sprints cortos, revision continua y entregables incrementales.

### Herramientas de gestion

- **Git:** versionado y estrategia de ramas.
- **GitHub Projects:** tablero de trabajo.
- **GitHub Issues:** backlog, tareas y bugs.
- **GitHub Actions:** pipelines de testing.
- **GitHub Pages:** documentacion publica.
- **GitHub Wiki:** documentacion tecnica interna.

## 5. Roles y responsabilidades

- **Test Lead:** Valdivia Segovia, Ryan Fabian; Ajra Huacso, Jeans Anthony
- **Test Analyst:** Luque Condori, Luis Guillermo
- **Test Architect:** Garambel Marin, Fernando Miguel; Hancco Mullisaca, Sergio Danilo
- **Test Designer:** Huacani Jara, Denise Andrea; Pacheco Palo, Fabiana Francinet

## 6. Plan del proyecto y alcance

### Alcance funcional

- Autenticacion y gestion de usuarios.
- Procesamiento de pings y validacion de tiempos esperados.
- Integraciones de alertas y notificaciones.
- API para gestion remota de checks.

### Fuera de alcance

- Pentesting avanzado.
- Despliegue productivo comercial.
- Pruebas de carga masiva a gran escala.

## 7. Cronograma de sprints

- **Sprint 0:** seleccion/configuracion del proyecto y entorno.
- **Sprint 1:** analisis funcional y backlog.
- **Sprint 2:** diseno de pruebas unitarias.
- **Sprint 3:** implementacion y ejecucion de unit tests.
- **Sprint 4:** pruebas de integracion.
- **Sprint 5:** CI/CD en GitHub Actions.
- **Sprint 6:** metricas, cobertura y defectos.
- **Sprint 7:** cierre, documentacion y presentacion.

## 8. Estado actual

- `Work in Progress`: plan de pruebas detallado.
- `Work in Progress`: matriz de trazabilidad (historias-casos-defectos).
- `Work in Progress`: consolidacion final de evidencias y cobertura.
