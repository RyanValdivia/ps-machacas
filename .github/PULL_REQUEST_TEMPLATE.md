## Checklist — Antes de hacer merge de este PR

### ✅ Tests y CI/CD
- [ ] Los tests corren **localmente** antes de hacer push (`npx playwright test` / `pytest`)
- [ ] El test usa credenciales del archivo `database_seed.sql` o de variables de entorno (`process.env.TEST_USER`), NO contraseñas hardcodeadas
- [ ] No hay contraseñas, tokens ni claves API escritas directamente en el código
- [ ] Si el test levanta el sistema, fue probado con Docker local primero (`docker compose up -d` en `infra/local/`)

### ✅ Playwright (P4, P5, P7)
- [ ] El test sigue el patrón **AAA** (Arrange / Act / Assert)
- [ ] Las credenciales usadas existen en `database_seed.sql` con ese usuario y contraseña exactos
- [ ] Se guardó al menos un screenshot como evidencia en `test-results/`
- [ ] El test pasa en **los 3 navegadores** (Chromium, Firefox, WebKit) localmente

### ✅ Locust (P6)
- [ ] El script `locustfile_*.py` corre en modo headless sin errores
- [ ] El reporte HTML fue generado y guardado en `backend/tests/stress/`
- [ ] La tabla de métricas (P95, error rate, throughput) está completada con datos reales

### ✅ Seguridad (P7)
- [ ] Los tests de `test_security.py` pasan todos con `python -m pytest tests/security/ -v`
- [ ] Ninguna prueba de SQL injection produce HTTP 500

### ✅ General (todos)
- [ ] El PR apunta a la rama correcta (`develop`, no directamente a `qa` ni `main`)
- [ ] El título del commit sigue el formato: `tipo(scope): descripción` (ej: `feat(pos): add E2E tests for cash opening`)
- [ ] Los archivos de evidencia (screenshots, reportes) están incluidos en el commit

---

> **¿Tienes dudas?** Revisa el [Plan Maestro](../Plan_pruebas_maestro.md) o consulta con P1 (@FernandoGarambelM) antes de mergear.
