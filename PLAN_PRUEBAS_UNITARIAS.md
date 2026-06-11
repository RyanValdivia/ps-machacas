# Plan de Pruebas Unitarias

---

## Índice

1. [Introducción](#1-introducción)
   - 1.1. [Alcance](#11-alcance)
   - 1.2. [Referencias](#12-referencias)
   - 1.3. [Glosario](#13-glosario)
2. [Contexto de las Pruebas Unitarias](#2-contexto-de-las-pruebas-unitarias)
   - 2.1. [Módulos / Componentes bajo prueba](#21-módulos--componentes-bajo-prueba)
   - 2.2. [Elementos de Prueba](#22-elementos-de-prueba)
   - 2.3. [Alcance de las Pruebas Unitarias](#23-alcance-de-las-pruebas-unitarias)
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
7. [Actividades y Cronograma](#7-actividades-y-cronograma)
   - 7.1. [Estructura de actividades](#71-estructura-de-actividades)
   - 7.2. [Estimados de esfuerzo](#72-estimados-de-esfuerzo)
   - 7.3. [Cronograma](#73-cronograma)
8. [Personal](#8-personal)
   - 8.1. [Roles y responsabilidades](#81-roles-y-responsabilidades)
   - 8.2. [Necesidades de entrenamiento](#82-necesidades-de-entrenamiento)

---

## 1. Introducción

> 📝 _Breve presentación del documento. Explica el propósito del plan, el proyecto al que pertenece y quién lo elaboró. Eliminar esta nota al completar._

### 1.1. Alcance

> 📝 _Define qué cubre este plan: qué proyecto, qué módulos, qué tipo de pruebas (unitarias) y qué queda fuera del alcance. Ser específico evita malentendidos. Eliminar esta nota al completar._

### 1.2. Referencias

> 📝 _Lista los documentos relacionados: requerimientos, historias de usuario, arquitectura técnica, estándares de codificación, etc. Incluir versión y enlace si aplica. Eliminar esta nota al completar._

| #   | Documento | Versión | Enlace |
| --- | --------- | ------- | ------ |
| 1   |           |         |        |

### 1.3. Glosario

> 📝 _Define términos técnicos usados en el documento: UT (Unit Test), mock, stub, cobertura de código, TDD, etc. Útil para que todos los miembros del equipo partan del mismo vocabulario. Eliminar esta nota al completar._

| Término | Definición |
| ------- | ---------- |
|         |            |

---

## 2. Contexto de las Pruebas Unitarias

> 📝 _Sección que ubica al lector en el contexto del proyecto: qué se va a probar, quiénes están involucrados y bajo qué condiciones se desarrollarán las pruebas. Eliminar esta nota al completar._

### 2.1. Módulos / Componentes bajo prueba

> 📝 _Lista los módulos, clases o servicios del sistema que serán cubiertos por las pruebas unitarias. Ayuda a delimitar el trabajo y asignar responsabilidades. Eliminar esta nota al completar._

| Módulo / Componente | Descripción breve | Responsable |
| ------------------- | ----------------- | ----------- |
|                     |                   |             |

### 2.2. Elementos de Prueba

> 📝 _Detalla las unidades específicas a probar: clases, métodos, funciones o procedimientos. Es el nivel más granular del alcance. Eliminar esta nota al completar._

| Módulo | Clase / Archivo | Método / Función | Prioridad |
| ------ | --------------- | ---------------- | --------- |
|        |                 |                  |           |

### 2.3. Alcance de las Pruebas Unitarias

> 📝 _Especifica explícitamente qué SI está dentro del alcance y qué NO. Por ejemplo: se prueban métodos de lógica de negocio, pero NO se prueban integraciones con base de datos ni APIs externas. Eliminar esta nota al completar._

## **Dentro del alcance:**

## **Fuera del alcance:**

### 2.4. Suposiciones y Restricciones

> 📝 _Lista los supuestos bajo los que se diseñó el plan (ej: el código ya está escrito, el equipo conoce el framework) y las restricciones existentes (ej: tiempo limitado, deuda técnica, falta de documentación). Eliminar esta nota al completar._

## **Suposiciones:**

## **Restricciones:**

### 2.5. Partes Interesadas

> 📝 _Identifica a todas las personas que tienen interés en los resultados de las pruebas unitarias: líder técnico, QA, desarrolladores, product owner, etc. Eliminar esta nota al completar._

| Nombre | Rol | Interés / Responsabilidad |
| ------ | --- | ------------------------- |
|        |     |                           |

---

## 3. Estrategia de Pruebas Unitarias

> 📝 _Corazón del plan. Describe cómo se van a realizar las pruebas: qué técnicas se usarán, qué nivel de cobertura se busca y cuáles son los criterios de calidad. Eliminar esta nota al completar._

### 3.1. Enfoque de prueba

> 📝 _Describe el modelo de trabajo adoptado: ¿se usará TDD (escribir prueba antes del código)? ¿BDD? ¿Pruebas a posteriori? ¿Caja blanca o caja negra? Justificar brevemente la elección. Eliminar esta nota al completar._

### 3.2. Técnicas de diseño

> 📝 _Indica qué técnicas se usarán para diseñar los casos de prueba, por ejemplo: partición de equivalencia, análisis de valores límite, cobertura de condiciones/ramas, tablas de decisión. Eliminar esta nota al completar._

- [ ] Partición de equivalencia
- [ ] Análisis de valores límite
- [ ] Cobertura de ramas (branch coverage)
- [ ] Cobertura de condiciones
- [ ] Tablas de decisión
- [ ] Otra: \_\_\_

### 3.3. Cobertura de código objetivo

> 📝 _Define el porcentaje mínimo de cobertura aceptable para considerar que las pruebas son suficientes. Se recomienda establecer umbrales por tipo: líneas, ramas y condiciones. Eliminar esta nota al completar._

| Tipo de cobertura        | Objetivo mínimo |
| ------------------------ | --------------- |
| Cobertura de líneas      | %               |
| Cobertura de ramas       | %               |
| Cobertura de condiciones | %               |

### 3.4. Manejo de dependencias

> 📝 _Explica cómo se aislarán las unidades bajo prueba de sus dependencias externas (BD, APIs, servicios). Indica qué tipo de dobles de prueba se usarán: mocks, stubs, spies, fakes o dummies. Eliminar esta nota al completar._

| Dependencia | Tipo de doble usado | Justificación |
| ----------- | ------------------- | ------------- |
|             |                     |               |

### 3.5. Criterios de entrada y salida

> 📝 _Define cuándo se puede empezar a ejecutar pruebas (criterios de entrada) y cuándo se considera que las pruebas unitarias están terminadas (criterios de salida). Eliminar esta nota al completar._

## **Criterios de entrada (para iniciar pruebas):**

## **Criterios de salida (para finalizar pruebas):**

### 3.6. Métricas

> 📝 _Define los indicadores que se medirán para evaluar la calidad y el avance de las pruebas unitarias. Sirven para tomar decisiones basadas en datos. Eliminar esta nota al completar._

| Métrica                         | Descripción                  | Objetivo |
| ------------------------------- | ---------------------------- | -------- |
| % de cobertura de código        |                              | ≥ %      |
| # de pruebas ejecutadas         |                              |          |
| # de pruebas pasadas / fallidas |                              |          |
| Densidad de defectos            | Defectos por cada 100 líneas |          |
| Tiempo promedio de ejecución    |                              |          |

### 3.7. Criterios de suspensión y reanudación

> 📝 _Establece bajo qué condiciones se deben pausar las pruebas (ej: bloqueo crítico, ambiente caído) y qué debe ocurrir para reanudarlas. Evita que el equipo continúe ejecutando pruebas en condiciones inválidas. Eliminar esta nota al completar._

## **Criterios de suspensión:**

## **Criterios de reanudación:**

---

## 4. Entorno de Pruebas

> 📝 _Describe el ambiente técnico necesario para ejecutar las pruebas unitarias. Garantiza que todos los miembros del equipo trabajen bajo las mismas condiciones. Eliminar esta nota al completar._

### 4.1. Ambiente de ejecución

> 📝 _Especifica el entorno técnico requerido: sistema operativo, lenguaje de programación y su versión, runtime, gestor de dependencias, etc. Eliminar esta nota al completar._

| Elemento               | Detalle |
| ---------------------- | ------- |
| Sistema operativo      |         |
| Lenguaje / versión     |         |
| Runtime / SDK          |         |
| Gestor de dependencias |         |

### 4.2. Frameworks y herramientas

> 📝 _Lista los frameworks de prueba y herramientas de soporte que se utilizarán (ej: JUnit, Jest, pytest, Mockito, coverage.py, etc.). Incluir versión recomendada. Eliminar esta nota al completar._

| Herramienta | Propósito | Versión |
| ----------- | --------- | ------- |
|             |           |         |

### 4.3. Integración con CI/CD

> 📝 _Indica si las pruebas unitarias se ejecutarán de forma automática dentro de un pipeline de CI/CD. Describe en qué etapa del pipeline se ejecutan y qué sucede si fallan (bloqueo de merge, notificación, etc.). Eliminar esta nota al completar._

---

## 5. Registro de Riesgos

> 📝 _Identifica los riesgos que podrían afectar la ejecución o calidad de las pruebas unitarias, junto con su probabilidad, impacto y plan de acción. Cuanto antes se identifiquen, más fácil es mitigarlos. Eliminar esta nota al completar._

### 5.1. Riesgos identificados

| ID  | Riesgo |    Probabilidad     |       Impacto       | Nivel |
| --- | ------ | :-----------------: | :-----------------: | :---: |
| R01 |        | Alto / Medio / Bajo | Alto / Medio / Bajo |       |
| R02 |        |                     |                     |       |

### 5.2. Plan de mitigación

| ID  | Acción de mitigación | Responsable | Fecha límite |
| --- | -------------------- | ----------- | :----------: |
| R01 |                      |             |              |
| R02 |                      |             |              |

---

## 6. Entregables

> 📝 _Lista todos los artefactos que se producirán como resultado del proceso de pruebas unitarias. Define quién es responsable de cada uno y cuándo deben estar listos. Eliminar esta nota al completar._

### 6.1. Casos de prueba unitaria

> 📝 _Documento o suite de pruebas que describe cada caso: ID, descripción, precondiciones, datos de entrada, resultado esperado y resultado obtenido. Puede vivir en el propio repositorio de código. Eliminar esta nota al completar._

### 6.2. Reportes de ejecución y cobertura

> 📝 _Informes generados automáticamente por el framework de pruebas y la herramienta de cobertura. Indica el formato (HTML, XML, JSON) y dónde se publicarán (CI/CD, repositorio, wiki). Eliminar esta nota al completar._

### 6.3. Registro de defectos

> 📝 _Bitácora de los bugs encontrados durante las pruebas unitarias. Indica la herramienta de seguimiento (Jira, GitHub Issues, etc.) y el flujo de estados de un defecto. Eliminar esta nota al completar._

---

## 7. Actividades y Cronograma

> 📝 _Planificación temporal del trabajo de pruebas unitarias: qué se hace, cuánto tiempo toma y en qué orden. Sirve para coordinar con el resto del equipo de desarrollo. Eliminar esta nota al completar._

### 7.1. Estructura de actividades

> 📝 _Desglosa las tareas del proceso de pruebas unitarias en actividades concretas y asignables. Eliminar esta nota al completar._

| #   | Actividad                           | Descripción | Responsable |
| --- | ----------------------------------- | ----------- | ----------- |
| 1   | Análisis de componentes a probar    |             |             |
| 2   | Diseño de casos de prueba           |             |             |
| 3   | Implementación de pruebas           |             |             |
| 4   | Ejecución de pruebas                |             |             |
| 5   | Análisis de resultados y cobertura  |             |             |
| 6   | Corrección de defectos y re-testing |             |             |
| 7   | Generación de reporte final         |             |             |

### 7.2. Estimados de esfuerzo

> 📝 _Estimación en horas o días de cada actividad. Permite planificar la capacidad del equipo y detectar cuellos de botella. Eliminar esta nota al completar._

| Actividad | Estimado (horas) | Responsable |
| --------- | :--------------: | ----------- |
|           |                  |             |

### 7.3. Cronograma

> 📝 _Fechas concretas de inicio y fin para cada actividad. Puede representarse como tabla o como diagrama de Gantt. Eliminar esta nota al completar._

| Actividad | Fecha inicio | Fecha fin |    Estado    |
| --------- | :----------: | :-------: | :----------: |
|           |              |           | ⬜ Pendiente |

---

## 8. Personal

> 📝 _Define quiénes participan en las pruebas unitarias, qué rol cumple cada uno y si requieren capacitación para ejecutar el plan. Eliminar esta nota al completar._

### 8.1. Roles y responsabilidades

> 📝 _Describe las responsabilidades de cada perfil involucrado: quién diseña las pruebas, quién las ejecuta, quién revisa la cobertura, quién aprueba los resultados. Eliminar esta nota al completar._

| Rol           | Nombre | Responsabilidades                        |
| ------------- | ------ | ---------------------------------------- |
| Líder Técnico |        | Revisar estrategia, aprobar resultados   |
| Desarrollador |        | Implementar y ejecutar pruebas unitarias |
| QA / Tester   |        | Diseñar casos, analizar cobertura        |
| DevOps        |        | Configurar integración en CI/CD          |

### 8.2. Necesidades de entrenamiento

> 📝 _Identifica si algún miembro del equipo necesita capacitación en el framework de pruebas, en TDD, en el uso de mocks, etc. Incluir cómo y cuándo se daría esa capacitación. Eliminar esta nota al completar._

| Persona / Rol | Tema de entrenamiento | Modalidad | Fecha estimada |
| ------------- | --------------------- | --------- | :------------: |
|               |                       |           |                |

---

_Documento generado como plantilla base — completar cada sección y eliminar las notas en itálica antes de publicar._
