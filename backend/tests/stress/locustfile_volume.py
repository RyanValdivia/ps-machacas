"""
locustfile_volume.py — NF-VOL-01: Prueba de Volumen (Volume Test).

Objetivo:
  Evaluar el rendimiento del endpoint de búsqueda de productos cuando el
  catalogo tiene un gran volumen de datos (100,000 registros contra ~1000).

Escenario:
  - 50 usuarios concurrentes
  - Duracion: 3 minutos
  - Cada usuario ejecuta busquedas variadas que estresan diferentes partes
    del query planner (búsqueda por texto, filtros exactos, combinaciones,
    paginacion profunda, ordenamientos)

Metricas:
  - Tiempo promedio de respuesta
  - Latencia P95
  - Comparacion contra catalogo normal (~1000 productos)

Criterios de aceptacion:
  - Respuesta < 3 segundos
  - Sin degradacion significativa respecto al catalogo normal

Mejoras de estres real:
  - Busquedas pesadas: terminos genericos que matchean MILES de filas
  - Busquedas sin search (todas las categorias): ?material=A, etc.
  - Paginacion profunda: page=50, page=100 con page_size=100
  - Combinaciones de filtros: search + material + genero + precio_min/precio_max
  - Ordenamientos por diferentes campos: precio, stock, marca, fecha
  - Sin search (solo filtros): estresa indices de columna

Preparacion (catalogo de 100k):
  python tests/stress/seed_masivo.py --count 100000

Ejecucion (volumen):
  locust -f tests/stress/locustfile_volume.py
         --users 50 --spawn-rate 10 --run-time 3m
         --html tests/stress/report_volume.html --headless
         --host http://localhost:8000

Ejecucion (linea base — catalogo normal):
  locust -f tests/stress/locustfile_volume.py
         --users 50 --spawn-rate 10 --run-time 3m
         --html tests/stress/report_volume_baseline.html --headless
         --host http://localhost:8000
         --tag baseline

Comparacion:
  Comparar report_volume.html (100k) vs report_volume_baseline.html (~1000)
  La diferencia en P95 no debe superar el 50% del valor base.

Variables de entorno:
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

# NF-VOL-01: prueba de volumen (no de concurrencia extrema).
# Patrón de carga: 50 usuarios (--users 50) moderados durante 3 minutos,
# pero corriendo contra un catálogo pre-cargado con un GRAN volumen de
# datos (100,000 productos vía seed_masivo.py --count 100000, comparado
# contra una línea base de ~1000). El foco no es cuánta carga aguanta el
# server, sino cómo se degrada la BD/query planner cuando la tabla es
# enorme: búsqueda por texto, filtros exactos, filtros combinados,
# paginación profunda (page=50/100, notoriamente lenta con OFFSET en
# PostgreSQL) y ordenamientos, cada uno en su propia tarea con distinto
# peso (ver comentarios de cada @task más abajo).
# Éxito esperado: P95 <= 3000ms contra el catálogo de 100k, y que la
# diferencia frente al reporte baseline (~1000 productos) no supere el
# 50% del valor base (ver hook on_quitting). Una degradación mayor indica
# que faltan índices o que alguna consulta no escala con el volumen.

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

_test_users_raw = os.getenv("TEST_USERS_JSON")
if not _test_users_raw:
    raise OSError(
        "TEST_USERS_JSON no esta definida. "
        "Ejemplo: export TEST_USERS_JSON='[{\"usuNom\":\"admin\",\"usuContra\":\"admin123\"}]'"
    )
TEST_USERS = json.loads(_test_users_raw)
_user_pool = itertools.cycle(TEST_USERS)
_pool_lock = threading.Lock()


def _next_credentials():
    with _pool_lock:
        return next(_user_pool)


# ---------------------------------------------------------------------------
# Datos de busqueda para estresar el catalogo
# ---------------------------------------------------------------------------

# Terminos de marca (resultados acotados, usan indice parcial)
TERMINOS_MARCA = [
    "PEGASUS", "VIPSUAL", "CARLOS ROSSI", "TENDENCIA", "OZZY",
    "FEILLIS", "LUXOTTICA", "OAKLEY", "RAY-BAN", "CARRERA",
]

# Terminos GENERICOS que matchean MILES de registros (estresan el search)
TERMINOS_PESADOS = [
    "SEED",     # Todos los productos seed comienzan con SEED-*
    "a",        # Letra comun, matchea praticamente todo
    "e",
    "NEGRO",    # Color comun
    "MAR",      # Parcial de MARCA/MARRON
    "PLAT",     # Parcial de PLATEADO
    "ACETATO",  # Descripcion que puede aparecer en muchas
    "METAL",    # Material comun en descripciones
    "MOD",      # Parcial de "Modelo" (presente en descripciones)
]

# Valores para filtros exactos
MATERIALES = ["A", "M", "TR", "C", "N"]
GENEROS = ["Hombre", "Mujer", "Unisex"]

# Ordenamientos que estresan diferentes indices
ORDENAMIENTOS = [
    "prodPrecioVenta", "-prodPrecioVenta",
    "prodStock", "-prodStock",
    "prodMarca", "-prodMarca",
    "created_at", "-created_at",
]


class VolumeTestUser(HttpUser):
    """
    NF-VOL-01: Usuario que realiza busquedas pesadas sobre el catalogo
    de gran volumen, disenadas para estresar diferentes partes del motor
    de busqueda (indices, seq scans, joins, ordenamientos).
    """

    wait_time = between(1, 3)

    def on_start(self):
        creds = _next_credentials()
        self.token = None

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login-volume]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                resp.success()
            else:
                resp.failure(f"Login fallo: HTTP {resp.status_code}")
                raise StopUser()

        self._auth_headers = {"Authorization": f"Bearer {self.token}"}

    @tag("volume", "NF-VOL-01", "baseline")
    @task(3)
    def buscar_por_marca(self):
        """Busqueda por marca conocida (resultados acotados ~100-500 rows)."""
        if not self.token:
            return

        termino = random.choice(TERMINOS_MARCA)

        with self.client.get(
            f"/api/products/?search={termino}",
            headers=self._auth_headers,
            name="GET /api/products/?search=MARCA [NF-VOL-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("volume", "NF-VOL-01")
    @task(4)
    def buscar_pesado(self):
        """
        Busqueda con termino GENERICO que matchea MILES de registros.
        Este es el escenario que realmente estresa el indice GIN de busqueda
        y la capacidad de la BD para manejar grandes sets de resultados.
        """
        if not self.token:
            return

        termino = random.choice(TERMINOS_PESADOS)

        with self.client.get(
            f"/api/products/?search={termino}",
            headers=self._auth_headers,
            name="GET /api/products/?search=GENERICO [NF-VOL-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("volume", "NF-VOL-01")
    @task(2)
    def buscar_con_filtros_combinados(self):
        """
        Combina search + filtro de material + genero + rango de precio.
        Esto estresa los filtros compuestos y la capacidad de la BD para
        combinar condiciones WHERE.
        """
        if not self.token:
            return

        termino = random.choice(TERMINOS_MARCA + TERMINOS_PESADOS)
        material = random.choice(MATERIALES)
        genero = random.choice(GENEROS)
        precio_min = random.choice([0, 10, 25, 50, 100])
        precio_max = precio_min + random.choice([50, 100, 200])

        params = [
            f"search={termino}",
            f"material={material}",
            f"genero={genero}",
            f"precio_min={precio_min}",
            f"precio_max={precio_max}",
        ]
        url = "/api/products/?" + "&".join(params)

        with self.client.get(
            url,
            headers=self._auth_headers,
            name="GET /api/products/?filtros-combinados [NF-VOL-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("volume", "NF-VOL-01")
    @task(2)
    def buscar_sin_search_solo_filtro(self):
        """
        Busqueda SOLO con filtros exactos (sin search).
        Esto estresa indices de columna (material, genero, precio) y
        el planificador de consultas para filtros combinados.
        """
        if not self.token:
            return

        # A veces solo material, a veces material + genero, a veces + precio
        modo = random.choice(["material", "material_genero", "completo"])
        params = []

        material = random.choice(MATERIALES)
        params.append(f"material={material}")

        if modo in ("material_genero", "completo"):
            params.append(f"genero={random.choice(GENEROS)}")

        if modo == "completo":
            params.append(f"precio_min={random.randint(0, 50)}")
            params.append(f"precio_max={random.randint(70, 350)}")

        url = "/api/products/?" + "&".join(params)

        with self.client.get(
            url,
            headers=self._auth_headers,
            name="GET /api/products/?solo-filtros [NF-VOL-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("volume", "NF-VOL-01")
    @task(1)
    def paginacion_profunda(self):
        """
        Paginacion en paginas avanzadas (page=50, page=100).
        Esto estresa el rendimiento de OFFSET en la BD, que es NOTORIAMENTE
        lento en PostgreSQL cuanto mas profunda es la paginacion.
        """
        if not self.token:
            return

        page = random.choice([10, 20, 50, 100, 200])
        page_size = random.choice([20, 50, 100])

        with self.client.get(
            f"/api/products/?page={page}&page_size={page_size}",
            headers=self._auth_headers,
            name="GET /api/products/?page=PROFUNDA [NF-VOL-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 404:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("volume", "NF-VOL-01")
    @task(1)
    def buscar_con_ordenamiento(self):
        """
        Busqueda con ordenamiento por diferentes campos.
        Estresa la capacidad de la BD para ordenar grandes sets de resultados.
        """
        if not self.token:
            return

        ordering = random.choice(ORDENAMIENTOS)

        with self.client.get(
            f"/api/products/?search=SEED&ordering={ordering}",
            headers=self._auth_headers,
            name="GET /api/products/?ordering [NF-VOL-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self.on_start()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")


def _stats_endpoint(stats, name):
    """Obtiene estadisticas de un endpoint por su name tag."""
    for key, entry in stats.entries.items():
        if name in key[1]:
            return entry
    return None


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Resumen detallado de metricas al finalizar la prueba de volumen."""
    stats = environment.stats
    total = stats.total

    print("\n" + "=" * 60)
    print("NF-VOL-01 — Prueba de Volumen")
    print("=" * 60)

    if total.num_requests > 0:
        p95 = total.get_response_time_percentile(0.95)
        p50 = total.get_response_time_percentile(0.5)
        p99 = total.get_response_time_percentile(0.99)

        print(f"  Requests totales:        {total.num_requests:,}")
        print(f"  Failures:                {total.num_failures:,}")
        print(f"  Error Rate:              {(total.num_failures / total.num_requests) * 100:.2f}%")
        print(f"  RPS promedio:            {total.total_rps:.2f}")
        print()
        print(f"  Latencia P50 (mediana):  {p50:.0f} ms")
        print(f"  Latencia P95:            {p95:.0f} ms")
        print(f"  Latencia P99:            {p99:.0f} ms")
        print(f"  Min respuesta:           {total.min_response_time:.0f} ms")
        print(f"  Max respuesta:           {total.max_response_time:.0f} ms")
        print()

        criterio = "OK" if p95 <= 3000 else "FALL"
        print(f"  Criterio P95 <= 3000ms:  {criterio} ({p95:.0f} ms)")
        print()

        print("  Desglose por tipo de busqueda:")
        print(f"  {'Tipo':35s} {'Req':>8s} {'P95(ms)':>9s} {'Avg(ms)':>9s}")
        print("  " + "-" * 61)
        for endpoint_name in [
            "[NF-VOL-01]",
            "[NF-VOL-01-marca]",
            "[NF-VOL-01-generico]",
            "[NF-VOL-01-filtros]",
            "[NF-VOL-01-solo-filtros]",
            "[NF-VOL-01-paginacion]",
            "[NF-VOL-01-ordering]",
        ]:
            entry = _stats_endpoint(stats, endpoint_name)
            if entry and entry.num_requests > 0:
                ep95 = entry.get_response_time_percentile(0.95)
                print(f"  {endpoint_name:35s} {entry.num_requests:>8d} {ep95:>8.0f}ms {entry.avg_response_time:>8.0f}ms")
    else:
        print("  No se registraron requests.")

    print("=" * 60)
