# Documento de Requerimientos de Software

**Proyecto:** REGISTRA-ME
**Fecha:** 03/06/26

---

## Tabla de contenido

- [Documento de Requerimientos de Software](#documento-de-requerimientos-de-software)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Información del Proyecto](#información-del-proyecto)
  - [1. Propósito](#1-propósito)
  - [2. Alcance del producto / Software](#2-alcance-del-producto--software)
  - [3. Arquitectura](#3-arquitectura)
  - [4. Funcionalidades del producto](#4-funcionalidades-del-producto)
  - [5. Clases y características de usuarios](#5-clases-y-características-de-usuarios)
  - [6. Entorno operativo](#6-entorno-operativo)
  - [7. Requerimientos funcionales](#7-requerimientos-funcionales)
    - [7.1. Gestión de Clientes (CL-0000-0005, CL-0000-0007, CL-0000-0009)](#71-gestión-de-clientes-cl-0000-0005-cl-0000-0007-cl-0000-0009)
    - [7.2. Gestión de Punto de Venta - Caja](#72-gestión-de-punto-de-venta---caja)
    - [7.3. Gestión de Ventas (VE-0000-0001, VE-0000-0002)](#73-gestión-de-ventas-ve-0000-0001-ve-0000-0002)
    - [7.4. Gestión de Logística e Inventario (LO-0000-0001, LO-0000-0002)](#74-gestión-de-logística-e-inventario-lo-0000-0001-lo-0000-0002)
    - [7.5. Generación de reportes y Estadísticas (SU-0000-0001, SU-0000-0002, SU-0000-0004, SU-0000-0005)](#75-generación-de-reportes-y-estadísticas-su-0000-0001-su-0000-0002-su-0000-0004-su-0000-0005)
    - [7.6. Control de usuarios, permisos y seguridad en general](#76-control-de-usuarios-permisos-y-seguridad-en-general)
    - [7.7. Dashboard](#77-dashboard)
  - [8. Reglas de negocio](#8-reglas-de-negocio)
    - [8.1. Reglas Generales del Sistema](#81-reglas-generales-del-sistema)
    - [8.2. Reglas por Módulo](#82-reglas-por-módulo)
      - [8.2.1. Gestión de Cajas](#821-gestión-de-cajas)
      - [8.2.2. Gestión de Ventas](#822-gestión-de-ventas)
      - [8.2.3. Gestión de Óptica / Recetas](#823-gestión-de-óptica--recetas)
      - [8.2.4. Reportes y Estadísticas](#824-reportes-y-estadísticas)
      - [8.2.5. Gestión de Logística e Inventario](#825-gestión-de-logística-e-inventario)
  - [9. Requerimientos de interfaces externas](#9-requerimientos-de-interfaces-externas)
    - [9.1. Interfaces de usuario](#91-interfaces-de-usuario)
    - [9.2. Interfaces de hardware](#92-interfaces-de-hardware)
    - [9.3. Interfaces de software](#93-interfaces-de-software)
    - [9.4. Interfaces de comunicación](#94-interfaces-de-comunicación)
  - [10. Requerimientos no funcionales](#10-requerimientos-no-funcionales)

---

## Información del Proyecto

| Empresa / Organización | Centro Óptico Visión Ideal |
| :--- | :--- |
| **Proyecto** | Registra-me V. Óptica |
| **Fecha de preparación** | 28/02/2026 |
| **Cliente** | Cristina Palo Peña |
| **Patrocinador principal** | Centro Óptico Visión Ideal |
| **Gerente / Líder de Proyecto** | Sergio Danilo Hancco Mullisaca |
| **Gerente / Líder de Análisis de negocio y requerimientos** | Fabiana Francinet Pacheco Palo |

---

## 1. Propósito

La versión 1 del proyecto “REGISTRA-ME” tiene como propósito automatizar los principales procesos de gestión en una óptica orientado a un local, principalmente la emisión de orden de ventas, la gestión de inventario, control de ventas, gestión de clientes y recetas.

En esta versión no se considerarán procesos relacionados con sueldos u otros sistemas complementarios. Tampoco se incluye el servicio de migración de datos históricos de recetas médicas, la página web de la óptica u otras funcionalidades externas. El sistema se plantea como una plataforma de escritorio local de gestión.

## 2. Alcance del producto / Software

Esta versión del proyecto, tiene como propósito optimizar los principales procesos dentro de una óptica, con el objetivo de digitalizar procesos comúnmente hechos manualmente y brindar una base de organización a partir de la cuál una óptica pueda crecer y gestionar su negocio.

Esta es una plataforma virtual diseñada para digitalizar y optimizar la gestión de procesos en una óptica cuyo propósito, abarcando desde la emisión automática de orden de ventas, hasta el control exhaustivo de inventarios, la gestión de ventas por empleado, la generación de estadísticas detalladas y la implementación de estrategias de fidelización de clientes.

Este sistema brinda beneficios significativos al área dentro del modelo de negocio:

- Permite realizar de forma inmediata la emisión de órdenes de venta validadas.
- Optimiza el flujo de ventas, al reducir el tiempo de atención al cliente. Lo que le permite brindar una mejor atención al cliente.
- Permite tener un mejor seguimiento de las ventas y por ende de los clientes, al brindar reportes que se pueden utilizar para gestionar promociones, descuentos y unificación de ingresos y egresos para el control de los trabajadores.
- Permite tener un mejor control y transparencia dentro de las operaciones del negocio, lo que permite identificar puntos de mejora, tomar decisiones estratégicas y permite un mejor análisis del negocio.

Objetivos y metas. Es recomendable establecer la relación de los objetivos del software con los objetivos corporativos y estrategias de negocio.

Se puede hacer referencia a otros documentos, por ejemplo una definición de alcance u acta de constitución del proyecto.

El sistema tiene como objetivos principales:

- Emitir orden de ventas en tiempo real.
- Administrar el inventario de productos y servicios con un control de stock preciso.
- Generar un dashboard personalizado para la gestión rápida de elementos constantes o recordatorios de agenda de acuerdo al rol de la cuenta.
- Implementar un sistema de gestión de ventas con la interfaz caja que represente todos las operaciones realizadas dentro de una óptica, gestión de ventas por trabajadores, ingresos y egresos y caja.
- Brindar estadísticas confiables sobre ventas por periodo, vendedores y sucursales.

Estos objetivos están alineados con los objetivos corporativos de modernización de procesos, mejora de la fidelización de clientes y optimización del tiempo utilizado en el cumplimiento tributario, apoyando directamente la toma de decisiones de la gerencia mediante reportes de inventario, ventas y rentabilidad. Este alcance se define en mayor detalle en el Product Backlog y en el EDT.

## 3. Arquitectura

*(Sección pendiente de definición en el documento original)*

## 4. Funcionalidades del producto

El sistema REGISTRA-ME contará con las siguientes funcionalidades/módulos principales:

1. Gestión de clientes (Recetas, compras)
2. Gestión de Punto de Venta-cajas
3. Gestión de Ventas y preferencias del cliente
4. Gestión de logística, inventario y proveedores
5. Generación de reportes y estadísticas
6. Control de usuarios, permisos y seguridad en general
7. Dashboard

## 5. Clases y características de usuarios

1. **Gerente**
   - Uso muy frecuente.
   - Acceso total a todas las funcionalidades.
   - Funcionalidades principales:
     - Ver reportes del sistema.
     - Control de todas las áreas del sistema.
2. **Usuario de logística**
   - Uso frecuente, acceso al módulo de inventario.
   - Encargado del registro de productos y control de stock.
   - Funcionalidades principales:
     - Gestión de logística, inventario y proveedores.
     - Generación de reportes de inventario.
3. **Optómetra**
   - Uso medio, acceso a la sección de recetas.
   - Registra recetas y asocia la información clínica al historial del cliente.
   - Funcionalidades principales:
     - Gestión de óptica y recetas clínicas.
     - Generación de recetas e historial de pacientes.
4. **Cajero**
   - Uso muy frecuente, acceso a la sección de ventas e inventario.
   - Apertura de caja, registra y asigna a vendedores las ventas de productos y servicios, emite órdenes de venta, da información del inventario.
   - Funcionalidades principales:
     - Emisión de orden de ventas.
     - Consulta de productos y servicios.
5. **Vendedor**
   - No tiene acceso al sistema, se crea su usuario para registro de la venta formal.
   - Su participación se limita al registro de ventas realizadas por el cajero bajo su nombre.
   - Obtiene información teniendo de intermediario a otro usuario o a través de un reporte general.
6. **Cliente**
   - Está dentro de la base de datos del sistema más no tiene acceso al sistema.
   - Sus requerimientos se gestionan de manera indirecta a través de los módulos internos.

## 6. Entorno operativo

El entorno operativo contempla los siguientes aspectos:

1. **Plataforma de hardware**
   - Memoria RAM 5 GB.
   - Almacenamiento SSD de al menos 250 GB.
   - Equipos periféricos como impresoras térmicas para emisión de orden de venta.
2. **Sistemas operativos compatibles**
   - El sistema puede trabajar dentro de Windows.
3. **Software y componentes**
   - Dentro del sistema se trabajará con las tecnologías detalladas a continuación:
     - **Backend:** Django
     - **Frontend:** React
     - **Base de datos:** PostgreSQL

## 7. Requerimientos funcionales

### 7.1. Gestión de Clientes (CL-0000-0005, CL-0000-0007, CL-0000-0009)

**Descripción:** Permitir la recuperación de información de compras realizadas, historial de recetas e información de contacto y validación (Dni, Nro, etc).
**Prioridad:** Alta

**Acciones iniciadoras y comportamiento esperado:**
- El sistema crea un cliente en una compra nueva y relaciona dicha compra con el cliente.
- El sistema permite recuperar clientes ya existentes y consultar su historial de compras y recetas.
- El sistema tiene la opción de enviar mensajes al whatsapp del cliente cuando su compra este lista para recojo. (Link de whatsapp)

**Requerimientos funcionales:**
- **REQ-01 (CL5):** El sistema debe permitir registrar, actualizar clientes manualmente con datos obligatorios: tipo de documento, número de documento, nombre completo, celular y fecha de nacimiento.
- **REQ-02 (CL7):** El sistema debe crear automáticamente un cliente al realizar una compra nueva, vinculando la compra al objeto cliente con validación de DNI para evitar duplicados y consistencia de ingreso. De otro modo recuperar en una compra el cliente asociado para agregarlo a sus compras.
- **REQ-03 (CL9):** El sistema debe permitir recuperar el historial de compras mostrando detalles como fecha, productos, estado del pedido, total y medios de pagos.
- **REQ-04 (CL9):** El sistema debe permitir registrar y recuperar el historial de recetas asociadas a cada cliente incluyendo todos los detalles y observaciones extras siguiendo el formato de una receta de medición de la vista.

### 7.2. Gestión de Punto de Venta - Caja

**Descripción:** Gestionar el movimiento de dinero de caja mediante el registro de ventas de manera asociada al vendedor, ingresos y egresos. Registrar los distintos medios de pago para automatizar el cierre de caja.
**Prioridad:** Alta

**Acciones iniciadoras y comportamiento esperado:**
- El cajero genera una orden de venta para el cliente al finalizar la compra.
- El cajero registra una venta y esta queda asociada al vendedor correspondiente para los reportes correspondientes.
- El sistema envía automáticamente la información de la venta.
- El sistema contabiliza automáticamente los diferentes medios de pago al cuadrar y cierre de caja.

**Requerimientos funcionales:**
- **REQ-05 (CA1):** El sistema debe permitir la apertura de una caja registrando el monto inicial de efectivo, junto con la fecha y hora exacta de apertura. Esta información debe quedar almacenada en el historial de movimientos para auditoría.
- **REQ-06 (CA5):** El sistema debe poder recuperar los productos del inventario por el código y la aplicación de descuentos al momento de la venta.
- **REQ-07 (CA5):** El sistema debe registrar ventas asociadas a la caja vinculando a un cliente identificado por nombre y documento (suficiente para la creación automática del cliente), el vendedor asociado (puede ser el mismo cajero).
- **REQ-08 (CA5):** El sistema debe enviar la información de la venta confirmada a la impresora térmica configurada, generando un comprobante con datos del cliente, productos, totales y forma de pago.
- **REQ-09 (CA5):** El sistema debe permitir registrar ingresos y egresos de dinero no vinculados a ventas, como pagos a proveedores, gastos menores o abonos. Cada movimiento debe incluir fecha, monto, concepto y responsable.
- **REQ-10 (CA5):** El sistema debe permitir realizar el cálculo automático al cierre de caja mostrando el conteo de dinero física y entrada por Yape y mostrar diferencias (sobrante o faltante) para control y auditoría.
- **REQ-11 (CA5):** El sistema debe permitir al realizar el cierre de caja satisfactoriamente almacenar los ingresos y egresos clasificados por medio de pago para poder ser recuperados en un reporte consolidado de la jornada.

### 7.3. Gestión de Ventas (VE-0000-0001, VE-0000-0002)

**Descripción:** Permitir la recuperación de ventas en total priorizando las que aún han sido concluidas como falta de recojo, pendiente de cancelar en pago o aun no listas.
**Prioridad:** Alta

**Acciones iniciadoras y comportamiento esperado:**
- Los roles cajeros, gerente vendedor consultan las ventas para gestionar sus estados.

**Requerimientos funcionales:**
- **REQ-12:** El sistema debe permitir consultar todas las ventas registradas, mostrando un resumen detallado de cada venta: cliente, productos, cantidad, precios unitarios, subtotal, descuentos, total, saldo pendiente y estado.
- **REQ-13:** El sistema debe permitir cambiar el estado de un pedido (ej. “Listo”, “Entregado”, “Pendiente”) mediante acciones explícitas en la interfaz, registrando fecha y usuario responsable.
- **REQ-14:** El sistema debe permitir registrar pagos completos o parciales asociados a una venta, actualizando automáticamente el saldo pendiente y reflejando el estado de pago.

### 7.4. Gestión de Logística e Inventario (LO-0000-0001, LO-0000-0002)

**Descripción:** Permitir el registro de productos y su costo de inversión, así como la gestión de compras e integración con proveedores para actualizar el inventario.
**Prioridad:** Alta

**Acciones iniciadoras y comportamiento esperado:**
- El miembro de logística registra nuevos productos en el inventario.
- El sistema guarda el costo de inversión asociado a cada producto.

**Requerimientos funcionales:**
- **REQ-15 (LO1):** El sistema debe permitir registrar nuevos productos en el inventario, incluyendo categoría, enlace a proveedor existente, características, costo de inversión, precio de venta y stock inicial, stock mínimo.
- **REQ-16 (LO2):** El sistema debe guardar y mostrar el stock actual de cada producto, permitiendo aplicar filtros para conocer cuántos productos activos existen y cuáles están por debajo del stock mínimo.
- **REQ-17 (LO2):** La plataforma debe facilitar el acceso a formularios personalizados según la categoría del producto; específicamente, debe incluir campos adicionales para el registro de monturas y opciones simplificadas para el caso de los accesorios.

### 7.5. Generación de reportes y Estadísticas (SU-0000-0001, SU-0000-0002, SU-0000-0004, SU-0000-0005)

**Descripción:** Generar reportes de ventas por vendedor, estadísticas generales, reportes de stock y estadísticas de productos vendidos.
**Prioridad:** Media

**Acciones iniciadoras y comportamiento esperado:**
- El gerente solicita un reporte de ventas por periodo.
- El sistema genera reportes con información consolidada.
- El sistema alerta sobre productos con stock bajo.
- El gerente consulta estadísticas de productos vendidos.

**Requerimientos funcionales:**
- **REQ-18 (SU1):** El sistema debe permitir generar reportes de ventas filtrados por periodo (día, mes, año) y agrupados por vendedor, mostrando ingresos totales, número de transacciones y ticket promedio.
- **REQ-19:** El sistema debe mostrar métricas como ingresos totales, costos, ganancias y distribución de ventas por caja.
- **REQ-20:** El sistema debe mostrar estadísticas de productos vendidos en un periodo determinado, incluyendo cantidades, categorías más demandadas, productos con mayor rotación, ventas por vendedor.
- **REQ-21:** El sistema debe consultar toda la información de reportes filtrada por día, mes, año y día especifica con las gráficas correspondientes incluyendo estadísticas de ventas por vendedor y distribución por caja, permitiendo identificar desempeño y carga de trabajo.

### 7.6. Control de usuarios, permisos y seguridad en general

**Descripción:** Administración integral de la estructura organizacional, que abarca la gestión de datos corporativos, proveedores y perfiles de usuario. Este componente centraliza el control de accesos, credenciales, cuentas y la operatividad de las cajas financieras. Asimismo, establece las bases de datos fundamentales de proveedores y cajas, necesarias para garantizar la correcta ejecución de los módulos de logística y puntos de venta.
**Prioridad:** Alta

**Requerimientos funcionales:**
- **REQ-22:** El sistema debe permitir registrar y actualizar información de la empresa (nombre, logo, ruc, dirección, datos de contacto, nro. de contacto).
- **REQ-23 (SU1):** El sistema debe permitir crear, editar, desactivar y eliminar cuentas de usuario, asignando roles y permisos específicos.
- **REQ-24 (SU1):** El sistema debe permitir configurar y administrar cajas registradoras, incluyendo nombre, descripción, estado y permisos de acceso (cajero asignado).
- **REQ-25 (SU1):** El sistema puede incluir la creación y administración de proveedores dentro de este módulo.

### 7.7. Dashboard

**Descripción:** Proporcionar una vista rápida y consolidada de la información clave del sistema (ventas, pedidos, ganancias, movimientos de caja), con acceso restringido según el rol del usuario.
**Prioridad:** Alta

**Requerimientos funcionales:**
- **REQ-26:** El sistema debe mostrar en el dashboard una vista rápida de pedidos pendientes (ej. falta de recojo, pendiente de pago, no listos), permitiendo al usuario acceder rápidamente a su detalle.
- **REQ-27:** El sistema debe mostrar en el dashboard el resumen de movimientos de caja abierta (aperturas, ingresos, egresos, saldo actual).
- **REQ-28:** El sistema debe controlar la información visible en el dashboard según el rol del usuario: ganancias solo visibles para el Gerente, movimientos de caja visibles para Cajero y Gerente, pedidos pendientes visibles para todos los roles autorizados.

## 8. Reglas de negocio

### 8.1. Reglas Generales del Sistema

- **RN-001: Control de Acceso por Roles**
  El sistema opera bajo control de acceso basado en roles (RBAC):
  - **Administrador:** Acceso total al sistema.
  - **Supervisor:** Reportes, gestión de usuarios y configuración.
  - **Cajero/Vendedor:** Punto de venta y registro de ventas.
  - **Logística:** Inventario, compras y proveedores.
  - **Optómetra:** Gestión de recetas y clientes.

- **RN-002: Trazabilidad de Operaciones**
  Toda operación crítica debe registrar: usuario, fecha/hora, tipo de operación, datos modificados y dispositivo. Incluye: ventas, apertura/cierre de caja, modificación de precios, ajustes de inventario, y anulación de comprobantes.

### 8.2. Reglas por Módulo

#### 8.2.1. Gestión de Cajas
- **RN-CA-001: Asociación de Ventas**
  - Toda venta debe estar asociada a un vendedor/cajero autenticado.
  - No se permiten ventas anónimas.
- **RN-CA-002: Estado de Caja Obligatorio**
  - Solo se registran ventas con caja abierta y activa.
  - Una caja abierta por usuario simultáneamente.
  - Flujo obligatorio: Iniciar sesión → Apertura de caja → Ventas → Cierre de caja → Cerrar sesión.
- **RN-CA-004: Registro de Métodos de Pago**
  - Métodos soportados: Efectivo, Tarjeta Crédito/Débito, Transferencia, Yape.
  - Se permite pago mixto (múltiples métodos).
  - La suma de todos los métodos debe igualar el total de la venta.
  - Para efectivo: registrar monto recibido y vuelto.
- **RN-CA-005: Cierre de Caja Automático**
  Sistema calcula automáticamente totales esperados y compara con arqueo físico declarado:
  - **Cuadre perfecto:** Total contado = Total esperado.
  - **Sobrante/Faltante:** Requiere justificación por escrito.
  - Diferencias >S/ 10.00 requieren aprobación de Supervisor.

#### 8.2.2. Gestión de Ventas
- **RN-VE-001: Validación de Stock**
  - No se completa venta sin stock suficiente.
  - Validación en tiempo real al agregar al carrito.
- **RN-VE-002: Búsqueda de Productos**
  - Filtros disponibles: código, nombre, categoría, rango de precio, stock disponible, proveedor. Búsqueda rápida (<1 segundo).
- **RN-VE-003: Historial de Ventas**
  - **Cajero:** Solo sus ventas.
  - **Supervisor:** Ventas de su sucursal.
  - **Administrador:** Todas las ventas.
- **RN-VE-004: Aplicación de Descuentos**
  - **Cajero:** Hasta 10% sin autorización.
  - **Supervisor:** Hasta 30%.
  - **Administrador:** Sin límite.
  - Descuentos mayores requieren autorización en tiempo real.

#### 8.2.3. Gestión de Óptica / Recetas
- **RN-OP-001: Recetas Asociadas a Cliente**
  - Toda receta debe estar asociada a un cliente registrado. El cliente puede tener múltiples recetas (historial clínico).
- **RN-OP-002: Datos Esenciales de Receta**
  - Campos obligatorios: fecha, cliente, graduación OD/OI (esfera, cilindro, eje), distancia pupilar, tipo de lente.
- **RN-OP-003: Historial Clínico**
  - Sistema mantiene historial cronológico completo. Solo Optómetra/Supervisor/Administrador pueden ver datos clínicos detallados.
- **RN-OP-004: Vinculación Receta-Venta**
  - Al vender producto óptico, debe asociarse a receta existente del cliente para trazabilidad.

#### 8.2.4. Reportes y Estadísticas
- **RN-RE-001: Alcance de Reportes por Rol**
  - **Cajero:** Solo ventas propias.
  - **Supervisor:** Ventas e inventario de su sucursal.
  - **Administrador:** Reportes globales de todas las sucursales.
- **RN-RE-002: Reportes de Ventas**
  - Periodos: hoy, ayer, semana, mes, rango personalizado. Agrupación: por vendedor, método de pago, sucursal, categoría, turno.
- **RN-RE-003: Alertas de Stock Bajo**
  - Sistema genera alertas automáticas cuando stock ≤ stock mínimo configurado. Notificaciones a Logística/Supervisor/Administrador.
- **RN-RE-004: Estadísticas de Productos**
  - Métricas: productos más/menos vendidos, margen de utilidad, rotación de inventario. Comparativas entre sucursales y periodos.

#### 8.2.5. Gestión de Logística e Inventario
- **RN-LO-001: Costo de Inversión Obligatorio**
  - Todo producto debe tener costo de inversión registrado. Sistema calcula costo promedio ponderado al registrar compras.
- **RN-LO-002: Compras y Actualización de Inventario**
  - Al registrar compra: actualiza stock automáticamente, actualiza costo promedio, genera cuenta por pagar (si es a crédito).
- **RN-LO-003: Gestión de Proveedores**
  - Proveedores deben estar registrados antes de compras. RUC obligatorio y único.
- **RN-LO-004: Ajustes de Inventario**
  - Ajustes manuales requieren justificación. Ajustes >10% del stock o >S/ 500 requieren autorización de Administrador.
- **RN-LO-005: Stock Negativo**
  - Por defecto no se permite stock negativo. Administrador puede habilitar excepción temporal para productos específicos.

## 9. Requerimientos de interfaces externas

### 9.1. Interfaces de usuario

1. **Interfaz de Punto de Venta (POS)**
   Interfaz principal para operaciones de venta en tiempo real, diseñada para ser intuitiva y rápida.
   **Características principales:**
   - Búsqueda de productos por código, nombre o categoría.
   - Calculadora integrada de vuelto.
   - Selección de método de pago (efectivo, tarjeta, transferencia, mixto).
   - Visualización clara del total con IGV desglosado.
   
   **Estándares GUI:**
   - Fuente principal: Se utiliza una fuente sans-serif, para asegurar legibilidad y claridad.
   - Botones de acción: Como Pagar, Cancelar, Aplicar descuento, deben ser grandes y visibles, con un diseño claro que diferencie sus funciones.
   - Esquema de colores: Alto contraste para facilitar la lectura rápida.

2. **Interfaz de Gestión Administrativa**
   Panel de control para los administradores del sistema, permitiéndoles configurar y administrar todas las operaciones internas del sistema de ventas y órdenes de venta.
   **Características principales:**
   - Dashboard con métricas clave (ventas del día, mes, año, comprobantes pendientes, clientes frecuentes, etc).
   - Menú lateral con módulos organizados.
   - Tablas de datos con ordenamiento, filtrado y exportación.
   - Notificaciones push para alertas del sistema, como cuando se realizó una venta, creaciones, errores, etc.
   
   **Estándares GUI:**
   - Diseño responsive adaptable.
   - Iconografía consistente basada en estándares Material Design o similar.
   - Estados visuales claros (hover, active, disabled, error, success).

3. **Interfaz de Reportes y Consultas**
   Módulo que comprende la visualización de los datos, y generación de reportes.
   **Características principales:**
   - Filtros dinámicos por fecha, categoría, producto, cliente.
   - Gráficos interactivos (barras, líneas, tortas) para un mejor análisis visual y rápido.
   - Comparativas periódicas donde se pueda comparar los resultados de diferentes períodos (día vs día, mes vs mes) para evaluar el desempeño del negocio.
   
   **Estándares GUI:**
   - Paleta de colores diferenciada para gráficos estadísticos.
   - Mensajes emergentes que proporcionen información adicional o explicaciones breves en los gráficos.
   - Botones de acción que destaquen las opciones de exportación, deben ser visibles, con un diseño claro que diferencie sus funciones.

4. **Guías de Estilo y Organización de Pantalla:**
   **Estándares Generales:**
   - Cabecera fija: Logo del negocio (izquierda), nombre de usuario y opciones de sesión (derecha).
   - Barra de navegación: Menú principal con iconos + nombre de la sección.
   - Área de trabajo: Contenido principal con padding consistente.
   - Pie de página: Información de versión, soporte técnico y hora del sistema.
   
   **Estándar de los botones:**
   - Botón Primario: Acción principal (Guardar, Confirmar, Emitir).
   - Botón Secundario: Acciones alternativas (Cancelar, Volver).
   - Botón de Peligro: Acciones destructivas (Eliminar, Anular). Color: Rojo (#D32F2F).
   
   **Funciones Globales en Todas las Pantallas:**
   - Barra de búsqueda global: En la parte superior de la pantalla, generalmente visible en todas las páginas. Esto permitirá al usuario buscar rápidamente productos, clientes, ventas, reportes u otros elementos relevantes sin necesidad de navegar entre pantallas.
   - Centro de notificaciones: En la parte superior de la pantalla. Tiene como función mostrar alertas o notificaciones sobre acciones importantes. Icono de campana con badge de contador.
   - Ayuda contextual: Icono de interrogación con tooltips y enlaces a documentación.
   - Selector de sucursal/caja: Visible cuando aplique multi-tienda.

### 9.2. Interfaces de hardware

**Tipos de Dispositivos Soportados**
El sistema está diseñado para ser compatible con los siguientes dispositivos de hardware:

1. **Computadoras y Laptops**
   **Requisitos Mínimos:**
   - Procesador: Intel Core i3 o AMD Ryzen 3 (8va generación o superior).
   - RAM: 4GB mínimo (8GB recomendado).
   - Almacenamiento: 128GB SSD, con 20GB de espacio libre.
   - Pantalla: Resolución mínima 1366x768px (1920x1080px recomendado).
   - Conectividad: Ethernet (recomendado) o Wi-Fi 802.11n o superior.
   - Sistema Operativo: Windows 10 (versión 21H2 o superior) o Windows 11.

2. **Impresoras**
   Impresoras Térmicas para Comprobantes, opcional:
   - Uso: Impresión de orden de ventas.

### 9.3. Interfaces de software

**Sistema Operativo**
- Windows: Compatible con Windows 10 y Windows 11.

**Base de Datos**
- Se utiliza ORM (Object-Relational Mapping) para el acceso eficiente a datos. Las conexiones a la base de datos son seguras mediante cadenas de conexión encriptadas. Además, se utiliza un pool de conexiones para soportar hasta 100 conexiones concurrentes.

**Servicios Web Externos:**
- Consulta de DNI: Para verificación de la identidad del cliente, el sistema puede integrar con la API con base de datos externa y comprobación interna.

**Componentes Internos del Sistema**
- Módulo de Autenticación y Autorización: Utiliza JWT (JSON Web Tokens) para gestionar la autenticación y autorización de usuarios. Los roles incluyen Administrador, Cajero, Supervisor, Almacenero, y Reportes, con permisos granulares por módulo y operación (CRUD).
- API Backend: La aplicación se comunica con el backend mediante una API RESTful o API GraphQL.
- Frontend Web: El frontend usa tecnologías modernas como React 18+ con TypeScript.

### 9.4. Interfaces de comunicación

**Protocolos de Red**
- HTTP/HTTPS: Protocolo para la comunicación entre el frontend y el backend, con HTTPS como estándar de seguridad.
- WebSockets: Es un protocolo para actualizaciones en tiempo real entre cliente y servidor, útil para notificaciones y sincronización.
- FTP/SFTP (opcional): Usado para la transferencia segura de archivos (como respaldos o logs) entre sistemas.

**Seguridad en Comunicaciones**
- Cifrado TLS/SSL: Asegura las comunicaciones entre el cliente y servidor mediante encriptación, usando TLS 1.2 o superior.
- Autenticación de APIs: Uso de JWT o OAuth 2.0 para asegurar y autenticar las interacciones con las APIs externas.

## 10. Requerimientos no funcionales

**1. Rendimiento y Escalabilidad**
- RNF-01: El sistema debe responder a las operaciones de registro, consulta y venta con un timer máximo de 3 segundos.

**2. Seguridad y Privacidad**
- RNF-02: El sistema debe garantizar la unicidad de los usuarios mediante credenciales (usuarios y contraseñas).
- RNF-03: La comunicación entre cliente y servidor debe realizarse mediante protocolo HTTPS.

**3. Confiabilidad y Disponibilidad**
- RNF-04: El sistema debe tener una disponibilidad mínima del 99% mensual.
- RNF-05: El sistema debe garantizar la integridad de la información y guardado sin necesidad de internet.

**4. Usabilidad y Accesibilidad**
- RNF-06: El sistema debe ofrecer una interfaz intuitiva y fácil de usar para usuarios no técnicos.
- RNF-07: La interfaz debe estar disponible en español y con terminología clara para el personal de la óptica.
- RNF-08: El sistema debe ser accesible desde Windows 10 o superior.

**5. Mantenibilidad y Portabilidad**
- RNF-09: El sistema debe estar desarrollado con arquitectura modular y con reusabilidad para facilitar la actualización de componentes en React.
- RNF-10: El código debe seguir estándares de programación y estar documentado.