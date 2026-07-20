"""
locustfile_inventory.py — Prueba NF-STRESS-02: Búsquedas Masivas de Inventario.

Escenario:
  - 100 usuarios concurrentes
  - Duración: 3 minutos
  - Cada usuario ejecuta GET /api/products/ variando búsquedas y filtros aleatoriamente

Criterios de aceptación:
  - P95 ≤ 2 segundos
  - 0 timeouts

Preparación:
  Antes de ejecutar esta prueba, generar al menos 1000 productos con:
    python tests/stress/seed_masivo.py --count 1000

Ejecución (headless — reporte HTML):
  locust -f tests/stress/locustfile_inventory.py \\
         --users 100 --spawn-rate 10 --run-time 3m \\
         --html tests/stress/report_stress_02.html --headless \\
         --host http://localhost:8000

Ejecución (interfaz web — capturas para wiki):
  locust -f tests/stress/locustfile_inventory.py --host http://localhost:8000
  # Abrir http://localhost:8089 → 100 users, spawn 10, ~3 min

Atajo Windows:
  cd backend/tests/stress
  .\\run.ps1 -Test 02 -Mode ui
  .\\run.ps1 -Test 02 -Mode headless

Variables de entorno requeridas:
  TEST_USERS_JSON = '[{"usuNom":"admin","usuContra":"admin123"}]'
"""

import os
import sys
import json
import random
import itertools
import threading
from pathlib import Path

from locust import HttpUser, task, between, events, tag
from locust.exception import StopUser

# ---------------------------------------------------------------------------
# Cargar .env si existe
# ---------------------------------------------------------------------------
_env_file = Path(__file__).resolve().parents[2] / ".env"
if not _env_file.exists():
    _env_file = Path(__file__).resolve().parents[2] / ".env.example"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

# ---------------------------------------------------------------------------
# Pool de credenciales
# ---------------------------------------------------------------------------
_test_users_raw = os.getenv("TEST_USERS_JSON")
if not _test_users_raw:
    raise OSError(
        "TEST_USERS_JSON no está definida. "
        "Ejemplo: export TEST_USERS_JSON='[{\"usuNom\":\"admin\",\"usuContra\":\"admin123\"}]'"
    )
TEST_USERS = json.loads(_test_users_raw)
_user_pool = itertools.cycle(TEST_USERS)
_pool_lock = threading.Lock()


def _next_credentials():
    with _pool_lock:
        return next(_user_pool)


# ---------------------------------------------------------------------------
# Datos de variedad para búsquedas representativas
# ---------------------------------------------------------------------------

# Términos de búsqueda variados (nombres de marca, descripciones parciales)
SEARCH_TERMS = [
    "PEGASUS", "VIPSUAL", "CARLOS ROSSI", "TENDENCIA", "OZZY", "FEILLIS",
    "LUXOTTICA", "OAKLEY", "RAY-BAN", "CARRERA", "POLICE", "LACOSTE",
    "GUCCI", "PRADA", "ARMANI", "VERSACE", "BOSS", "CALVIN", "TOMMY",
    "FOSSIL", "GUESS", "COACH", "RALPH", "DIESEL", "MARC",
    # Términos parciales (para simular búsquedas de usuario real)
    "NEG", "PLAT", "DOR", "AZU", "MAR", "AVA", "HEX", "POL",
    # Términos que retornarán muchos resultados
    "SEED", "M3", "C5", "HZ",
    # Términos de materiales y categorías
    "METAL", "ACETATO", "montura", "accesorio",
]

# Materiales del modelo Product.MATERIAL_CHOICES
MATERIALES = ["A", "M", "TR", "C", "N", ""]  # "" = sin filtro

# Géneros del modelo Product
GENEROS = ["Hombre", "Mujer", "Unisex", "Nino", ""]  # "" = sin filtro

# Ordenamientos posibles
ORDENAMIENTOS = [
    "-created_at",
    "prodMarca",
    "-prodPrecioVenta",
    "prodPrecioVenta",
    "prodStock",
    "-prodStock",
    "",  # sin ordenamiento
]


class InventorySearchUser(HttpUser):
    """
    NF-STRESS-02: Simula 100 usuarios haciendo búsquedas masivas en el inventario.
    
    Patrones de búsqueda:
    - búsqueda por texto (search=...)
    - filtro por material
    - filtro por género
    - combinación de filtros
    - paginación
    """

    wait_time = between(0.3, 1.0)

    def on_start(self):
        """Login y obtención del token JWT."""
        creds = _next_credentials()
        self.token = None

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login-inventory]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                resp.success()
            else:
                resp.failure(f"Login falló: HTTP {resp.status_code}")
                raise StopUser()

        self._auth_headers = {"Authorization": f"Bearer {self.token}"}

    def _build_search_url(self) -> tuple[str, str]:
        """
        Construye una URL de búsqueda aleatoria.
        Retorna (url, nombre_para_locust).
        """
        params = []
        nombre_partes = []

        # Decidir qué tipo de búsqueda hacer
        modo = random.choices(
            ["solo_search", "solo_material", "combinado", "paginado", "sin_filtro"],
            weights=[40, 15, 25, 10, 10],
            k=1,
        )[0]

        if modo in ("solo_search", "combinado"):
            term = random.choice(SEARCH_TERMS)
            params.append(f"search={term}")
            nombre_partes.append(f"search={term[:8]}")

        if modo in ("solo_material", "combinado"):
            material = random.choice([m for m in MATERIALES if m])
            if material:
                params.append(f"material={material}")
                nombre_partes.append(f"material={material}")

        if modo == "paginado":
            page = random.randint(1, 5)
            params.append(f"page={page}")
            nombre_partes.append(f"page={page}")

        # Agregar page_size ocasionalmente
        if random.random() < 0.3:
            page_size = random.choice([10, 20, 50])
            params.append(f"page_size={page_size}")

        # Agregar ordenamiento ocasionalmente
        if random.random() < 0.2:
            ordering = random.choice([o for o in ORDENAMIENTOS if o])
            if ordering:
                params.append(f"ordering={ordering}")

        query_string = "&".join(params)
        url = f"/api/products/{'?' + query_string if query_string else ''}"
        nombre_label = f"GET /api/products/ [{', '.join(nombre_partes) if nombre_partes else 'listado'}]"

        return url, nombre_label

    @tag("inventory", "search", "NF-STRESS-02")
    @task(5)
    def buscar_productos_variado(self):
        """
        Búsqueda aleatoria variando search, material, paginación.
        Es la tarea principal (peso 5).
        """
        if not self.token:
            return

        url, nombre = self._build_search_url()

        with self.client.get(
            url,
            headers=self._auth_headers,
            name="GET /api/products/ [NF-STRESS-02-variado]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    # El endpoint puede retornar paginado {count, results} o lista
                    if isinstance(data, dict):
                        count = data.get("count", len(data.get("results", [])))
                    else:
                        count = len(data)
                    resp.success()
                except Exception as e:
                    resp.failure(f"Error parseando JSON: {e}")
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code} — {resp.text[:100]}")

    @tag("inventory", "search", "NF-STRESS-02")
    @task(3)
    def buscar_por_marca_conocida(self):
        """
        Búsqueda de marca específica (simula búsqueda dirigida del vendedor).
        Peso 3: más frecuente que paginado pero menos que variado.
        """
        if not self.token:
            return

        marca = random.choice(["PEGASUS", "VIPSUAL", "CARLOS ROSSI", "OZZY", "TENDENCIA"])

        with self.client.get(
            f"/api/products/?search={marca}",
            headers=self._auth_headers,
            name="GET /api/products/?search=MARCA [NF-STRESS-02-marca]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("inventory", "NF-STRESS-02")
    @task(1)
    def listar_todos_paginado(self):
        """
        Listado general paginado (simula carga de catálogo completo).
        Peso 1: menos frecuente.
        """
        if not self.token:
            return

        page = random.randint(1, 10)

        with self.client.get(
            f"/api/products/?page={page}&page_size=20",
            headers=self._auth_headers,
            name="GET /api/products/?page=N [NF-STRESS-02-paginado]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 404:
                # Página no existe — aceptable
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")


# ---------------------------------------------------------------------------
# Hooks de eventos para monitoreo adicional
# ---------------------------------------------------------------------------
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "=" * 60)
    print("🚀 NF-STRESS-02 — Búsquedas Masivas de Inventario")
    print("=" * 60)
    print("  Objetivo: P95 ≤ 2s, 0 timeouts")
    print("  Asegúrate de haber generado al menos 1000 productos:")
    print("    python tests/stress/seed_masivo.py --count 1000")
    print("=" * 60 + "\n")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.stats
    total = stats.total

    print("\n" + "=" * 60)
    print("📊 RESUMEN NF-STRESS-02 — Búsquedas Masivas")
    print("=" * 60)

    if total.num_requests > 0:
        p95 = total.get_response_time_percentile(0.95)
        error_rate = (total.num_failures / total.num_requests) * 100

        print(f"  Requests totales:   {total.num_requests:,}")
        print(f"  Failures:           {total.num_failures:,}")
        print(f"  Error Rate:         {error_rate:.2f}%")
        print(f"  Latencia P95:       {p95:.0f} ms")
        print(f"  Avg latencia:       {total.avg_response_time:.0f} ms")
        print(f"  RPS promedio:       {total.total_rps:.2f}")
        print()

        criterio_p95 = "✅ OK" if p95 <= 2000 else "❌ FALLÓ"
        criterio_timeout = "✅ OK" if total.num_failures == 0 else "⚠  REVISAR"
        print(f"  P95 ≤ 2000ms:      {criterio_p95} ({p95:.0f}ms)")
        print(f"  0 timeouts:        {criterio_timeout}")
    else:
        print("  No se registraron requests.")

    print("=" * 60)
