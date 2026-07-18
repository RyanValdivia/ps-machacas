-- NF-REC-01: verificación de integridad transaccional tras caída/reinicio de PostgreSQL.
-- Ejecutar después de reiniciar el contenedor de base de datos y de que el backend
-- vuelva a responder (ver .github/workflows/deploy-qa.yml, job "recoverability").

-- 1. Ventas registradas en la ventana de la prueba (evidencia, no debe haber estados
--    intermedios/corruptos: solo PENDIENTE, PAGADO, PARCIAL o ANULADO son válidos).
SELECT "ventCod", "ventEstado", "ventEstadoRecoj", "ventTotal", "ventFecha"
FROM venta
WHERE "ventFecha" > NOW() - INTERVAL '10 minutes'
ORDER BY "ventFecha" DESC;

-- 2. Ventas con estado fuera del dominio esperado por el modelo (indicaría una
--    escritura parcial que el SGBD no debió permitir). Resultado esperado: 0 filas.
SELECT "ventCod", "ventEstado", "ventEstadoRecoj"
FROM venta
WHERE "ventFecha" > NOW() - INTERVAL '10 minutes'
  AND ("ventEstado" NOT IN ('PENDIENTE', 'PAGADO', 'PARCIAL', 'ANULADO')
       OR "ventEstadoRecoj" NOT IN ('PENDIENTE', 'LISTO', 'ENTREGADO', 'ANULADO'));

-- 3. Consistencia de stock: ningún producto debe quedar en negativo.
--    Resultado esperado: 0 filas.
SELECT "prodCod", "prodStock"
FROM product
WHERE "prodStock" < 0;
