<div style="text-align: center; background: linear-gradient(135deg, #F0FDF4 0%, #E0F2FE 100%); padding: 40px 20px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #E2E8F0;">
  <img src="logo_machaca.png" alt="Logo La Machaca" width="160" style="border-radius: 50%; border: 4px solid #FFFFFF; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);" />
  <h1 style="color: #0F172A; font-size: 2.5rem; margin: 15px 0 5px 0; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">Proyecto RegistraMe</h1>
  <p style="color: #0284C7; font-size: 1.2rem; margin: 0 0 20px 0; font-weight: 500; letter-spacing: 0.5px;">QA Engineering Team: La Machaca</p>
  
  <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;">
    <img src="https://img.shields.io/badge/Language-Python_3.12+-0284C7?style=flat-square" />
    <img src="https://img.shields.io/badge/Framework-Django_REST-0369A1?style=flat-square" />
    <img src="https://img.shields.io/badge/Frontend-React_%2B_Tauri-0F766E?style=flat-square" />
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

El presente plan de trabajo describe la organización, metodología, roles y lineamientos técnicos contemplados por el **Equipo La Machaca** para la ejecución de pruebas de software, aseguramiento de la calidad y automatización aplicados al sistema de gestión de óptica **RegistraMe**, desarrollado íntegramente por el propio equipo.

El propósito fundamental de este proyecto es establecer una estrategia de QA orientada a prácticas ágiles, garantizando la trazabilidad desde los requerimientos iniciales hasta la automatización de la evidencia. El flujo completo se apoya en el ecosistema avanzado de GitHub: *GitHub Projects* para la gestión ágil, *GitHub Issues* para el backlog de historias de usuario, *GitHub Actions* para la ejecución continua de pipelines de testing, y *GitHub Pages* para la centralización de la documentación y presentación formal del producto.

---

## 2. Definición del Proyecto

### 2.1. Descripción del Producto de Software Seleccionado

**RegistraMe** es un sistema de escritorio para la **gestión integral de ópticas y tiendas de lentes**, desarrollado con una arquitectura moderna cliente-servidor. La aplicación permite administrar el ciclo completo de una óptica: desde el inventario de monturas y lunas hasta el punto de venta con comprobantes, gestión de clientes, control de caja y reportes por sucursal.

El sistema está orientado a negocios del sector óptico que requieren control de inventario especializado (monturas por material, talla y marca; lunas personalizadas por tipo y características como Blue Block o fotocromático), así como trazabilidad completa de ventas con estados de pago y de entrega de pedidos.

#### Características Principales del Sistema

* **Dashboard Gerencial en Tiempo Real:** Panel centralizado con métricas de ventas, ganancias, egresos y productos activos, con vistas por día, semana, mes y año. Soporte multisurcusal.
* **Punto de Venta Ágil:** Interfaz de venta rápida con búsqueda de productos, selección de cliente, múltiples métodos de pago (Efectivo, Yape, Visa, Transferencia, Plin, Mixto), gestión de adelantos y generación automática de comprobantes.
* **Gestión de Inventario Especializado:** Control de monturas (por marca, material, talla, color, forma y género) y lunas personalizadas (por material, tipo y características adicionales), con generación automática de códigos y descripciones.
* **Control de Caja y Sucursales:** Apertura y cierre de caja por sesión, con asignación automática al vendedor activo y soporte para múltiples sucursales.
* **Administración y Roles:** Gestión de usuarios con roles diferenciados (Gerente, Vendedor, Cajero, Supervisor, Optómetra, Logística), configuración de sucursales, proveedores y laboratorios.

#### Galería de Componentes del Producto

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">A. Dashboard Gerencial Principal</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Panel de control en tiempo real con KPIs de ventas, ganancias, egresos y productos activos. Incluye ranking de clientes más frecuentes y gráfico de ventas totales por período.</p>
  <div style="text-align: center;">
    <img src="Dashboard_Principal.png" alt="Dashboard Principal de RegistraMe" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">B. Punto de Venta</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Interfaz de venta rápida con búsqueda de productos, registro de datos del cliente, selección de tipo de comprobante (Boleta/Factura), múltiples métodos de pago (Efectivo, Yape, Visa, Transferencia, Plin, Mixto), gestión de adelantos y procesamiento de la venta con generación automática de nota de venta.</p>
  <div style="text-align: center;">
    <img src="Punto_Venta.png" alt="Punto de Venta de RegistraMe" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">C. Inventario Central</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Módulo de gestión de productos globales disponibles para todas las sucursales. Muestra código, descripción, stock central, categoría, material, público objetivo, precio de venta, margen de ganancia y estado. Permite agregar nuevos productos con generación automática de código y descripción.</p>
  <div style="text-align: center;">
    <img src="Inventario.png" alt="Inventario Central de RegistraMe" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">D. Clientes y Prescripciones</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Módulo de gestión de clientes y sus recetas oftalmológicas. Permite registrar clientes con DNI, nombre completo, teléfono, edad y fecha de nacimiento, con búsqueda y filtros integrados.</p>
  <div style="text-align: center;">
    <img src="Clientes.png" alt="Clientes y Prescripciones de RegistraMe" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">E. Reportes Analíticos</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Panel de análisis de ventas, rentabilidad y desempeño. Muestra ingresos totales, ganancias, costos y ticket promedio, con vistas por día, mes y año. Incluye métricas de desempeño por vendedor, distribución por caja, ventas por vendedor y ventas por caja.</p>
  <div style="text-align: center;">
    <img src="Reportes.png" alt="Reportes Analíticos de RegistraMe" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
  <p style="font-weight: 600; color: #1E293B; margin-top: 0; margin-bottom: 10px;">F. Configuración y Administración de Acceso</p>
  <p style="font-size: 0.9rem; color: #64748B; margin-top: 0; margin-bottom: 12px;">Panel de administración con gestión de usuarios y permisos por rol, configuración de sucursales, cajas registradoras y proveedores. Permite agregar usuarios con roles como Gerente, Supervisor, Cajero, Vendedor y Optómetra.</p>
  <div style="text-align: center;">
    <img src="Ajustes.png" alt="Configuración de RegistraMe" style="max-width: 100%; border-radius: 6px; border: 1px solid #E2E8F0;" />
  </div>
</div>

### 2.2. Stack Tecnológico

<table style="width: 100%; border-collapse: collapse; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 30px;">
  <thead>
    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 30%;">Capa</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 70%;">Tecnologías</th>
    </tr>
  </thead>
  <tbody style="color: #334155; line-height: 1.5;">
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Backend</td>
      <td style="padding: 12px;">Python 3.12+, Django REST Framework, SQLite / PostgreSQL</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Frontend</td>
      <td style="padding: 12px;">React 19, TypeScript, Vite, TailwindCSS</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Empaquetado Desktop</td>
      <td style="padding: 12px;">Tauri (app nativa multiplataforma)</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">CI/CD y QA</td>
      <td style="padding: 12px;">GitHub Actions, pytest, coverage.py, mypy</td>
    </tr>
  </tbody>
</table>

### 2.3. Módulos del Sistema

El backend de **RegistraMe** está organizado en aplicaciones Django independientes, cada una con responsabilidad única dentro del dominio de la óptica:

<table style="width: 100%; border-collapse: collapse; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 30px;">
  <thead>
    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 25%;">Módulo</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 75%;">Responsabilidad</th>
    </tr>
  </thead>
  <tbody style="color: #334155; line-height: 1.5;">
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>users</code></td>
      <td style="padding: 12px;">Autenticación JWT, gestión de usuarios y asignación de roles (Gerente, Vendedor, Cajero, Supervisor, Optómetra, Logística).</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>products</code></td>
      <td style="padding: 12px;">Gestión de monturas y accesorios con validaciones por categoría (material, talla, marca), generación automática de códigos y descripciones, y configuración de lunas personalizadas (material, tipo, características adicionales como Blue Block o fotocromático).</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>sales</code></td>
      <td style="padding: 12px;">Flujo completo de ventas: creación de venta, detalle de productos y lunas, registro de pagos (adelantos y saldo), gestión de estados de pago (Pendiente, Parcial, Pagado, Anulado) y de entrega (Pendiente, Listo, Entregado), y generación de comprobantes (Nota de Venta).</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>cash</code></td>
      <td style="padding: 12px;">Apertura y cierre de sesiones de caja por sucursal, con asignación automática de ventas a la caja activa y registro de montos iniciales y de cierre.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>clients</code></td>
      <td style="padding: 12px;">Registro de clientes con datos personales (DNI, nombre completo, teléfono, fecha de nacimiento) y gestión de recetas oftalmológicas.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>categories</code></td>
      <td style="padding: 12px;">Catálogo de categorías de productos (Montura — <code>MO</code>, Accesorio — <code>AC</code>, Lunas), usado para aplicar validaciones específicas por tipo de producto.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>suppliers</code></td>
      <td style="padding: 12px;">Gestión de proveedores de monturas y laboratorios fabricantes de lunas personalizadas, asociados a los detalles de venta.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>opticalCenter</code></td>
      <td style="padding: 12px;">Configuración de la empresa óptica: nombre, logo, sucursales, dirección y datos de contacto institucional.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>external_services</code></td>
      <td style="padding: 12px;">Proxy para integraciones con servicios externos (p. ej., consulta de DNI/RUC a APIs de SUNAT o RENIEC).</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;"><code>sequences</code></td>
      <td style="padding: 12px;">Gestión de secuencias numéricas y correlativos para la generación automática de códigos de producto y números de comprobante.</td>
    </tr>
  </tbody>
</table>

### 2.4. Justificación de la Elección

La elección de **RegistraMe** se fundamenta en su idoneidad para el trabajo de QA del curso:

* **Dominio real y representativo:** Sistema orientado al sector empresarial de ópticas, con lógica de negocio compleja y validaciones críticas en modelos.
* **Arquitectura modular:** Backend Django separado en 10 apps independientes que facilita la cobertura por capas y el aislamiento de pruebas.
* **Código propio:** Al ser un proyecto desarrollado por el equipo, se tiene acceso total al código fuente, lo que permite diseñar pruebas tanto de caja blanca como de caja negra con mayor profundidad.
* **Reglas de negocio verificables:** Validaciones en modelos (stock, precios, lunas personalizadas, estados de venta) y flujos completos que pueden probarse con precisión mediante pruebas unitarias y de integración.

---

## 3. Objetivos del Proyecto

* **Objetivo General:** Diseñar, implementar y automatizar una estrategia de aseguramiento de calidad ágil para RegistraMe, incorporando pipelines de integración continua, trazabilidad absoluta de defectos y una cobertura final demostrable del **85%**.
* **Objetivos Específicos:**
  * Configurar un entorno de desarrollo local (DEV) homogéneo y reproducible para todos los miembros del equipo.
  * Definir formalmente el flujo de ramas de Git para la transición de código segura entre los entornos de `DEV` y `QA`.
  * Modelar las historias de usuario y criterios de aceptación mediante plantillas estructuradas en GitHub Issues.
  * Diseñar e implementar flujos automáticos en GitHub Actions para ejecutar pruebas de software ante cada Pull Request hacia la rama de calidad.
  * Incrementar y auditar la cobertura de código (Coverage) hasta asegurar un mínimo del 85% de efectividad en los módulos core del backend.
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
* **GitHub Wiki:** Documentación técnica interna, manuales de instalación (DEV) y Plan de Pruebas detallado.

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

* **Alcance Funcional:** Las pruebas y el aseguramiento de calidad se concentrarán de forma estricta en los siguientes módulos del backend de RegistraMe:
  * Módulo `products`: validaciones de modelos de monturas y accesorios, generación automática de códigos y descripciones, lógica de lunas personalizadas.
  * Módulo `sales`: flujo completo de venta (creación, pago, anulación), cálculo de totales, estados de pago y de pedido, generación de comprobantes.
  * Módulo `clients`: gestión de clientes con validaciones de documento de identidad.
  * Módulo `users`: autenticación, roles y control de acceso.
  * Módulo `cash`: apertura y cierre de caja, asignación de sesión a ventas.
* **Fuera de Alcance:**
  * Pruebas de la interfaz de usuario del frontend (React/Tauri).
  * Auditorías completas de seguridad perimetral o pruebas de penetración avanzada.
  * Pruebas de carga masiva o rendimiento a gran escala.

---

## 7. Cronograma de Sprints y Entregables

<table style="width: 100%; border-collapse: collapse; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 30px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;">
  <thead>
    <tr style="background-color: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 15%;">Sprint</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 15%;">Fechas</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 45%;">Actividades Principales de QA</th>
      <th style="padding: 12px; text-align: left; color: #1E293B; font-weight: 600; width: 25%;">Entregables Clave</th>
    </tr>
  </thead>
  <tbody style="color: #334155; line-height: 1.5; font-size: 0.95rem;">
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600; color: #64748B;">Sprint 1<br><small style="color: #16A34A; font-weight: 600;">Completado</small></td>
      <td style="padding: 12px; color: #64748B;">14/05 - 28/05</td>
      <td style="padding: 12px; color: #64748B;">Búsqueda y selección del nuevo proyecto de software comercial. Análisis inicial de viabilidad, preparación del repositorio base y despliegue del ecosistema de entornos mediante la configuración de GitHub Pages y GitHub Actions.</td>
      <td style="padding: 12px; color: #64748B;">Repositorio base configurado, GitHub Pages activo y Plan de Trabajo estructurado.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600; color: #0284C7;">Sprint 2<br><small style="color: #0284C7; font-weight: 600;">En curso</small></td>
      <td style="padding: 12px;">28/05 - 10/06</td>
      <td style="padding: 12px;">Fase de Análisis y Diseño (Semanas 1 y 2 del Plan de Pruebas). Elaboración del inventario de módulos críticos enfocados en productos, clientes y usuarios. Identificación de riesgos técnicos, definición de criterios de calidad y modelado detallado de casos de prueba con sus respectivos datos de prueba (fixtures) y matriz de trazabilidad.</td>
      <td style="padding: 12px;">Backlog de historias de usuario en GitHub Issues, matriz de casos de prueba estructurada y datos/fixtures de prueba definidos.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0; background-color: #F8FAFC;">
      <td style="padding: 12px; font-weight: 600;">Sprint 3<br><small style="color: #64748B;">Planificado</small></td>
      <td style="padding: 12px;">11/06 - 24/06</td>
      <td style="padding: 12px;">Fase de Implementación de Código de Pruebas (Semanas 3 y 4 del Plan de Pruebas). Programación y ajuste de la suite de pruebas unitarias y de integración sobre el backend (modelos, servicios y API REST) con énfasis en los flujos lógicos de ventas y caja. Desarrollo y acoplamiento en paralelo de las pruebas de componentes, servicios y rutas en el frontend.</td>
      <td style="padding: 12px;">Suite de pruebas automatizadas de backend y frontend implementada en el entorno local de desarrollo.</td>
    </tr>
    <tr style="border-bottom: 1px solid #E2E8F0;">
      <td style="padding: 12px; font-weight: 600;">Sprint 4<br><small style="color: #64748B;">Planificado</small></td>
      <td style="padding: 12px;">25/06 - 08/07</td>
      <td style="padding: 12px;">Fase de Ejecución y Finalización (Semanas 5 y 6 del Plan de Pruebas). Automatización de la ejecución de la suite en el pipeline de Integración Continua (GitHub Actions). Ejecución de la suite completa de regresión, pruebas negativas y validación estricta de permisos de usuario. Consolidación de métricas finales, auditoría de cobertura de código (Target Cobertura &ge; 85%) y documentación de lecciones aprendidas.</td>
      <td style="padding: 12px;">Pipeline de CI/CD verificado, reporte final de métricas de cobertura de código e informe de cierre de pruebas publicado.</td>
    </tr>
  </tbody>
</table>

### Justificación de la Distribución del Cronograma

La estructuración del cronograma de trabajo responde de manera estratégica a los principios de la ingeniería de pruebas y la gestión ágil de proyectos:

* **Correspondencia de Ciclos (Scrum-Testing Mapping):** La distribución agrupa de manera exacta un plan técnico de pruebas de 6 semanas en 3 Sprints de ejecución activa de 14 días cada uno. El Sprint 1 actuó como la fase de preparación necesaria para asegurar que el repositorio, el stack y las herramientas automáticas estuvieran listas y validadas antes de iniciar el ciclo formal de pruebas de software.
* **Cohesión de Fases por Iteración:** Cada Sprint posee un objetivo temático único para el equipo de QA, evitando la dispersión de esfuerzos. El Sprint 2 une el Análisis y el Diseño para entender el sistema de manera profunda antes de codificar; el Sprint 3 se concentra netamente en la construcción simultánea de pruebas en el backend y frontend; y el Sprint 4 se dedica a la certificación automatizada en el pipeline de Integración Continua.
* **Principio de Detección Temprana de Defectos:** Modelar las historias de usuario, los criterios de aceptación y los fixtures de datos en el Sprint 2, previo a la ejecución masiva de los Sprints siguientes, garantiza que el equipo cuente con una guía clara de trazabilidad. Esto reduce los costos de corrección de errores y asegura que las automatizaciones en GitHub Actions se configuren sobre una base de pruebas previamente validada a nivel local.

---

## 8. Estructura de Entornos y Flujo de Trabajo

### Flujo de Integración Continua (DEV ➔ QA ➔ MAIN)

Para garantizar la estabilidad del software, el equipo implementará un flujo de promoción de código estrictamente controlado por automatizaciones:

1. **Entorno DEV (Ramas de características):** Cada diseñador o arquitecto de pruebas escribe sus scripts localmente en ramas aisladas de tipo `feature/nombre-de-la-tarea`.
2. **Entorno QA (Rama `qa`):** Al solicitar la integración mediante un Pull Request hacia la rama `qa`, *GitHub Actions* se dispara automáticamente ejecutando la suite completa de pruebas. Si el porcentaje de cobertura disminuye por debajo del 85% o una prueba unitaria falla, la integración se bloquea de manera obligatoria para resguardar la calidad.
3. **Entorno Estable (Rama `main`):** Una vez validadas todas las pruebas y métricas en el entorno de calidad, el Test Lead autoriza el paso final (merge) del código hacia la rama principal estable.

---
<div style="background-color: #F0F9FF; border: 1px solid #BEE3F8; padding: 15px; border-radius: 6px; text-align: center; color: #0369A1; font-weight: 500;">
  Información Técnica Adicional: El detalle del Plan de Pruebas, la guía de instalación y la configuración técnica del entorno de desarrollo se encuentran centralizados en nuestra <a href="https://github.com/RyanValdivia/ps-machacas/wiki" style="color: #0284C7; font-weight: bold; text-decoration: underline;">Wiki Oficial del Proyecto</a>.
</div>
---
