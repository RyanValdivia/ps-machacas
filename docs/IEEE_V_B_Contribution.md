# Contribución a sección IEEE §V.B: Ejecución de Pruebas y Criterios de Aceptación

En el marco del plan de pruebas, se han implementado exitosamente las pruebas E2E correspondientes al módulo de Punto de Venta (POS) utilizando la herramienta Playwright. Las pruebas siguen el enfoque destructivo de Myers y aplican Análisis de Valores Límite.

## 1. Implementación de Escenarios
Se implementaron 7 escenarios cubriendo los flujos más críticos del Módulo POS:

- **E2E-POS-01: Apertura de Caja Exitosa**: Se aplicó Análisis de Valores Límite validando el ingreso de monto de apertura (Ej: S/0 como frontera inválida y S/100 como frontera válida). (`pos-sale.spec.ts`)
- **E2E-POS-02: Venta Simple de Montura (Stock Límite)**: Selección de producto con método de pago EFECTIVO, verificando reducción de stock (-1 unidad). (`pos-sale.spec.ts`)
- **E2E-POS-03: Venta con Luna Personalizada**: Validación de carga asíncrona y modificación de precio dinámico desde el modal de lunas. (`pos-sale.spec.ts`)
- **E2E-POS-04: Venta con Pago Parcial (Adelanto)**: Análisis de Valores Límite en pagos, verificando que el sistema acepte adelantos menores al total (Ej: S/100 de S/200) y cambie a estado PARCIAL. (`pos-payments.spec.ts`)
- **E2E-POS-05: Registro de Pago de Saldo Pendiente**: Gestión de deudas y transición de estado (de PARCIAL a PAGADO) tras liquidar el saldo. (`pos-payments.spec.ts`)
- **E2E-POS-06: Cierre de Caja con Balance**: Análisis de Valores Límite en la declaración final, exigiendo justificación si el monto en caja difiere del esperado. (`pos-cash.spec.ts`)
- **E2E-POS-07: Anulación de Venta**: Validación del proceso destructivo de anulación, pidiendo motivo obligatorio y devolviendo el stock automáticamente. (`pos-cancel.spec.ts`)

## 2. Refactorización para Mantenibilidad
Se diseñó un helper de autenticación en `frontend/tests/helpers/auth.ts` (`loginAs()`) para promover la reutilización de código de inicio de sesión en futuros paquetes de pruebas (P5, P7), reduciendo el código repetitivo en la Suite.

## 3. Evidencias y Trazabilidad

A continuación, se presentan las evidencias de ejecución de los escenarios E2E. Todos los casos se evaluaron bajo un criterio estricto de éxito funcional y manejo de excepciones mediante el patrón Arrange-Act-Assert.

### E2E-POS-01: Apertura de Caja Exitosa (Análisis de Valores Límite)

**Descripción:**  
Verifica que el sistema rechace montos de apertura inválidos (frontera inferior S/ 0) y apruebe montos válidos (Ej. S/ 100), asegurando la correcta inicialización de la caja.

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Iniciar sesión como `vendedor1` y acceder al Módulo POS. | Ingreso exitoso, redirección a `/sale-point`. |
| 2 | El sistema detecta caja cerrada y lanza modal de apertura. | Modal de "Apertura de Caja" es visible. |
| 3 | Ingresar monto límite inferior (S/ 0) y enviar. | El sistema rechaza el valor con advertencia visual. |
| 4 | Ingresar monto válido (S/ 100) y enviar. | Se registra el monto, la caja cambia a estado "ABIERTA". |

**Evidencia:**  
<video src="./assets/E2E-POS-01.webm" width="600" controls></video>

**Resultado:** ✅ SATISFACTORIO

---

### E2E-POS-02: Venta Simple de Montura con Stock Límite

**Descripción:**  
Comprueba el flujo de búsqueda de productos con validación estricta, agregación al carrito y posterior procesamiento de la venta de un artículo con stock unitario.

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Buscar montura ingresando el código `M1` en el panel izquierdo. | Se muestra la montura PEGASUS en los resultados. |
| 2 | Seleccionar la montura de los resultados listados. | El artículo se agrega correctamente al carrito lateral. |
| 3 | Presionar "Procesar Venta" y completar modal de Ticket. | El sistema avanza al cierre de venta (Efectivo por defecto). |
| 4 | Confirmar e imprimir ticket. | Alerta "Venta guardada" se dispara y se procesa. |

**Evidencia:**  
<video src="./assets/E2E-POS-02.webm" width="600" controls></video>  
*(Screenshot adjunto: `docs/assets/E2E-POS-02.png`)*

**Resultado:** ✅ SATISFACTORIO

---

### E2E-POS-03: Venta con Luna Personalizada

**Descripción:**  
Valida la integridad de componentes asíncronos y la configuración de atributos anidados (Material y Tipo de Luna) junto a un valor numérico libre de ingreso (Precio Manual).

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Presionar botón principal "LUNA" en el panel de opciones. | Se abre el modal "Personalización de Luna". |
| 2 | El sistema autoselecciona atributos de fábrica (NK / Monofocal). | Los botones de selección reflejan el estado activo. |
| 3 | Ingresar manualmente el "Precio de Venta" (Ej. 150.00). | Se habilita y acepta el precio customizado para la luna. |
| 4 | Agregar luna al carrito, procesar venta y confirmar ticket. | Venta completada, alerta "Venta guardada" lanzada. |

**Evidencia:**  
<video src="./assets/E2E-POS-03.webm" width="600" controls></video>  
*(Screenshot adjunto: `docs/assets/E2E-POS-03.png`)*

**Resultado:** ✅ SATISFACTORIO

---

### E2E-POS-04: Venta con Pago Parcial (Adelanto)

**Descripción:**  
Verifica el flujo de ventas permitiendo que un cliente realice un pago parcial (adelanto) menor al total de la venta (Ej: Adelanto de S/100 sobre un total de S/200), generando un ticket con estado PARCIAL.

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Crear venta en POS por un total de S/200 (Luna personalizada). | El total de la boleta refleja S/200. |
| 2 | Ingresar monto de S/100 en el campo opcional "Adelanto". | El saldo pendiente se calcula en S/100. |
| 3 | Procesar venta con el método de pago por defecto. | La venta es guardada en el sistema. |
| 4 | Confirmar e imprimir ticket. | Alerta "Venta guardada" se dispara y se procesa correctamente. |

**Evidencia:**  
<video src="./assets/E2E-POS-04.webm" width="600" controls></video>  
*(Screenshot adjunto: `docs/assets/E2E-POS-04.png`)*

**Resultado:** ✅ SATISFACTORIO

---

### E2E-POS-05: Registro de Pago de Saldo Pendiente

**Descripción:**  
Comprueba la gestión de deudas buscando una venta en estado PARCIAL y registrando el pago del saldo restante para actualizar su estado a PAGADO.

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Navegar a `/sales` y filtrar por estado `PARCIAL`. | Se lista la venta creada en el escenario E2E-POS-04. |
| 2 | Clic en el botón "Gestionar Venta" (⚙️). | Se abre el modal de gestión de la venta. |
| 3 | Seleccionar "Registrar Pago Parcial" e ingresar S/100.00. | Se habilita la confirmación del pago. |
| 4 | Clic en "Confirmar Pago". | Alerta de "Pago registrado" exitosamente, saldo en 0. |

**Evidencia:**  
<video src="./assets/E2E-POS-05.webm" width="600" controls></video>  
*(Screenshot adjunto: `docs/assets/E2E-POS-05.png`)*

**Resultado:** ✅ SATISFACTORIO

---

### E2E-POS-06: Cierre de Caja con Balance

**Descripción:**  
Aplica Análisis de Valores Límite ingresando un monto declarado (Ej: S/0 como frontera y S/150 como valor normal), y verificando que el sistema bloquee ventas posteriores o solicite un motivo por la diferencia de cuadre.

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Ingresar a la ruta de "Cierre de Caja". | Se carga el resumen con las ventas totales de la sesión. |
| 2 | Ingresar S/ 0 como monto contado en caja. | El botón de "Cerrar Caja" se mantiene bloqueado. |
| 3 | Ingresar el monto real (Ej: S/ 150.00). | Se habilita el botón y se muestra la diferencia (faltante/sobrante). |
| 4 | Confirmar el cierre (llenando motivo si es requerido). | Caja cerrada, redirección a POS, se exige nueva apertura. |

**Evidencia:**  
<video src="./assets/E2E-POS-06.webm" width="600" controls></video>  
*(Screenshot adjunto: `docs/assets/E2E-POS-06.png`)*

**Resultado:** ✅ SATISFACTORIO

---

### E2E-POS-07: Anulación de Venta

**Descripción:**  
Verifica el correcto funcionamiento del botón de anulación de pedidos/ventas, asegurando que se solicite un motivo y el sistema actúe según los criterios de frontera (Ej: bloquear anulación si ya fue entregado).

**Pasos de Ejecución:**
| Paso | Acción / Entrada | Resultado Esperado |
|------|------------------|--------------------|
| 1 | Navegar al panel de Ventas y seleccionar la última venta. | Modal de gestión abierto correctamente. |
| 2 | Clic en "Anular Venta" para desplegar el formulario. | Se advierte que la acción devolverá stock. |
| 3 | Ingresar motivo de anulación y confirmar doblemente. | Alerta modal pide confirmación final. |
| 4 | Confirmar anulación de venta. | Alerta "Venta anulada", estado cambia y stock retorna. |

**Evidencia:**  
<video src="./assets/E2E-POS-07.webm" width="600" controls></video>  
*(Screenshot adjunto: `docs/assets/E2E-POS-07.png`)*

**Resultado:** ✅ SATISFACTORIO
