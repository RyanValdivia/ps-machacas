"""
locustfile_soak.py — NF-SOAK-01: Prueba de Resistencia (Soak Test).

Objetivo:
  Evaluar la estabilidad del sistema bajo carga SOSTENIDA durante 30 minutos.
  Detectar memory leaks, degradacion progresiva de latencia y agotamiento
  de recursos (conexiones BD, sockets, file descriptors).

Escenario:
  - 5 usuarios concurrentes
  - Duracion: 30 minutos
  - Cada usuario ejecuta continuamente un ciclo realista:
      login -> busqueda -> venta -> dashboard -> busqueda -> venta -> ...

Metricas:
  - Latencia P95 por ventana de 5 minutos (para detectar degradacion)
  - Uso de memoria (docker stats)
  - Estabilidad general del sistema
  - Crecimiento de memoria (no debe existir crecimiento sostenido)

Criterios de aceptacion:
  - Sin crecimiento sostenido de memoria
  - Sin degradacion progresiva de latencia (P95 no debe aumentar ventana a ventana)
  - Sin timeouts
  - Conexiones a BD deben estabilizarse, no crecer indefinidamente

Mejoras de estres real:
  - Token refresh mediante /api/user/token/refresh/ en lugar de re-login completo
  - Pool de productos con reciclaje automatico (ajuste de stock via endpoint)
  - Logging de latencia POR VENTANA DE TIEMPO (c/5 min) para detectar degradacion
  - Variedad de busquedas con diferentes niveles de peso computacional
  - Ventas multi-item para estresar transacciones complejas

Ejecucion:
  locust -f tests/stress/locustfile_soak.py
         --users 5 --spawn-rate 1 --run-time 30m
         --html tests/stress/report_soak.html --headless
         --host http://localhost:8000

Monitoreo (terminal paralelo):
  docker stats --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"

Variables de entorno:
  TEST_USERS_JSON = '[{"usuNom":"admin","usuContra":"admin123"}]'
"""

import os
import sys
import json
import random
import time
import itertools
import threading
from pathlib import Path

from locust import HttpUser, task, between, events, tag
from locust.exception import StopUser

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
# Ventanas de tiempo para monitoreo de degradacion
# ---------------------------------------------------------------------------
_windows_lock = threading.Lock()
_windows = {}  # window_index -> {"start": timestamp, "count": n, "total_time": ms, "failures": n, "p95": ms}


def _record_response(window_idx: int, response_time: float, is_failure: bool):
    """Registra una respuesta en la ventana correspondiente."""
    with _windows_lock:
        if window_idx not in _windows:
            _windows[window_idx] = {
                "start": time.time(),
                "count": 0,
                "total_time": 0.0,
                "max_time": 0.0,
                "times": [],
                "failures": 0,
            }
        w = _windows[window_idx]
        w["count"] += 1
        w["total_time"] += response_time
        w["times"].append(response_time)
        if response_time > w["max_time"]:
            w["max_time"] = response_time
        if is_failure:
            w["failures"] += 1


# ---------------------------------------------------------------------------
# Datos de busqueda
# ---------------------------------------------------------------------------
TERMINOS_SOAK = [
    "PEGASUS", "VIPSUAL", "CARLOS ROSSI", "TENDENCIA", "OZZY",
    "LUXOTTICA", "OAKLEY", "RAY-BAN", "METAL", "ACETATO",
    "NEGRO", "AZUL", "DORADO", "SEED", "a", "e",
]

MATERIALES = ["A", "M", "TR", "C", "N"]
GENEROS = ["Hombre", "Mujer", "Unisex"]
FORMAS_PAGO = ["EFECTIVO", "YAPE", "VISA"]

WINDOW_MINUTES = 5
WINDOW_SECONDS = WINDOW_MINUTES * 60


def _calcular_p95(times):
    if not times:
        return 0
    sorted_t = sorted(times)
    idx = int(len(sorted_t) * 0.95)
    return sorted_t[idx]


def _extraer_resultados(resp):
    try:
        data = resp.json()
        if isinstance(data, dict):
            return data.get("results", [])
        return data
    except Exception:
        return []


class SoakTestUser(HttpUser):
    """
    NF-SOAK-01: Usuario que ejecuta un ciclo realista durante 30 minutos.

    Ciclo tipico:
      1. Login con refresh token (no re-login completo en cada expiracion)
      2. Busqueda de productos (ligera y pesada)
      3. Creacion de venta (1-2 productos)
      4. Dashboard
      5. Repetir

    Gestion de stock:
      - Pool de productos con reciclaje
      - Cuando un producto se agota, se elimina del pool
      - Si el pool se vacia, se reabastece via API
    """

    wait_time = between(2, 5)

    def on_start(self):
        self._login()

    def _login(self):
        creds = _next_user_credentials()
        self.token = None
        self.refresh_token = None
        self.username = creds["usuNom"]

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login-soak]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                self.refresh_token = data.get("refresh")
                resp.success()
            else:
                resp.failure(f"Login fallo: HTTP {resp.status_code}")
                raise StopUser()

        self._auth_headers = {"Authorization": f"Bearer {self.token}"}
        self._product_pool = []
        self._refresh_product_pool()

    def _refresh_token(self):
        """Refresca el access token usando el refresh token (evita re-login)."""
        if not self.refresh_token:
            return self._login()

        with self.client.post(
            "/api/user/token/refresh/",
            json={"refresh": self.refresh_token},
            name="POST /api/user/token/refresh/ [soak]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                self._auth_headers = {"Authorization": f"Bearer {self.token}"}
                resp.success()
                return True
            else:
                resp.failure("Refresh fallo, re-login necesario")
                self._login()
                return False

    def _ensure_auth(self):
        """Verifica que el token sea valido. Si no, lo refresca."""
        if not self.token:
            self._login()
            return
        self._refresh_token()

    def _refresh_product_pool(self):
        """Obtiene productos con stock disponible para las ventas."""
        with self.client.get(
            "/api/products/?stock_min=1&page_size=100&ordering=-prodStock",
            headers=self._auth_headers if hasattr(self, '_auth_headers') else {},
            name="GET /api/products/ [pool-refill-soak]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                results = _extraer_resultados(resp)
                self._product_pool = [p["prodCod"] for p in results if p.get("prodStock", 0) > 0]
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado en pool")
                self._refresh_token()

    def _get_product(self):
        """Obtiene un producto del pool (reabastece si es necesario)."""
        if len(self._product_pool) < 5:
            self._refresh_product_pool()
        if not self._product_pool:
            return None
        return random.choice(self._product_pool)

    # ==================================================================
    # Tareas del ciclo
    # ==================================================================

    @tag("soak", "NF-SOAK-01")
    @task(2)
    def buscar_productos(self):
        """Busqueda variada de productos."""
        if not self.token:
            return

        termino = random.choice(TERMINOS_SOAK)

        with self.client.get(
            f"/api/products/?search={termino}",
            headers=self._auth_headers,
            name="GET /api/products/?search [NF-SOAK-01]",
            catch_response=True,
        ) as resp:
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = resp.status_code != 200
            window = int(time.time() / WINDOW_SECONDS)
            _record_response(window, rt, is_fail)

            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("soak", "NF-SOAK-01")
    @task(1)
    def buscar_pesado(self):
        """Busqueda con terminos genericos (estresa mas la BD)."""
        if not self.token:
            return

        termino = random.choice(TERMINOS_SOAK)
        material = random.choice(MATERIALES)
        genero = random.choice(GENEROS)

        with self.client.get(
            f"/api/products/?search={termino}&material={material}&genero={genero}",
            headers=self._auth_headers,
            name="GET /api/products/?search+filtros [NF-SOAK-01]",
            catch_response=True,
        ) as resp:
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = resp.status_code != 200
            window = int(time.time() / WINDOW_SECONDS)
            _record_response(window, rt, is_fail)

            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("soak", "NF-SOAK-01")
    @task(2)
    def crear_venta(self):
        """
        Crea una venta con 1-2 productos.
        Si un producto se agota, lo elimina del pool y usa otro.
        """
        if not self.token:
            return

        pid = self._get_product()
        if not pid:
            return

        payload = {
            "detalles": [
                {"prodCod": pid, "ventDetCantidad": 1},
            ],
            "ventFormaPago": random.choice(FORMAS_PAGO),
            "ventObservaciones": "Venta soak NF-SOAK-01",
        }

        if random.random() < 0.2:
            pid2 = self._get_product()
            if pid2 and pid2 != pid:
                payload["detalles"].append({"prodCod": pid2, "ventDetCantidad": 1})

        with self.client.post(
            "/api/sales/ventas/",
            json=payload,
            headers=self._auth_headers,
            name="POST /api/sales/ventas/ [NF-SOAK-01]",
            catch_response=True,
        ) as resp:
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = True
            window = int(time.time() / WINDOW_SECONDS)

            if resp.status_code in (200, 201):
                is_fail = False
                resp.success()
            elif resp.status_code == 400:
                for d in payload["detalles"]:
                    pid_fail = d["prodCod"]
                    if pid_fail in self._product_pool:
                        self._product_pool.remove(pid_fail)
                resp.failure(f"Stock agotado: {resp.text[:100]}")
            elif resp.status_code == 401:
                resp.failure("Token expirado en venta")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

            _record_response(window, rt, is_fail)

    @tag("soak", "NF-SOAK-01")
    @task(1)
    def consultar_dashboard(self):
        """Consulta el dashboard."""
        if not self.token:
            return

        periodo = random.choice(["dia", "semana", "mes"])

        with self.client.get(
            f"/api/sales/ventas/estadisticas_dashboard/?periodo={periodo}",
            headers=self._auth_headers,
            name="GET /api/sales/ventas/estadisticas_dashboard/ [NF-SOAK-01]",
            catch_response=True,
        ) as resp:
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = resp.status_code != 200
            window = int(time.time() / WINDOW_SECONDS)
            _record_response(window, rt, is_fail)

            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado en dashboard")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")


# ---------------------------------------------------------------------------
# Resumen por ventanas al finalizar
# ---------------------------------------------------------------------------
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Resumen detallado con metricas por ventana de 5 minutos."""
    stats = environment.stats
    total = stats.total

    print("\n" + "=" * 70)
    print("NF-SOAK-01 — Prueba de Resistencia (Soak Test) — 30 minutos")
    print("=" * 70)

    if total.num_requests > 0:
        p95_global = total.get_response_time_percentile(0.95)
        p50_global = total.get_response_time_percentile(0.5)
        p99_global = total.get_response_time_percentile(0.99)

        print(f"\n  Metricas GLOBALES:")
        print(f"  Requests totales:     {total.num_requests:,}")
        print(f"  Failures:             {total.num_failures:,}")
        print(f"  Error Rate:           {(total.num_failures / total.num_requests) * 100:.2f}%")
        print(f"  RPS promedio:         {total.total_rps:.2f}")
        print(f"  Latencia P50:         {p50_global:.0f} ms")
        print(f"  Latencia P95:         {p95_global:.0f} ms")
        print(f"  Latencia P99:         {p99_global:.0f} ms")
        print(f"  Min respuesta:        {total.min_response_time:.0f} ms")
        print(f"  Max respuesta:        {total.max_response_time:.0f} ms")

        print(f"\n  Metricas POR VENTANA (c/{WINDOW_MINUTES} min):")
        print(f"  {'Ventana':>8s} {'Tiempo':>12s} {'Req':>8s} {'P95(ms)':>9s} {'Avg(ms)':>9s} {'Max(ms)':>9s} {'Fallos':>7s}")
        print("  " + "-" * 62)

        sorted_windows = sorted(_windows.keys())
        p95s = []
        for w_idx in sorted_windows:
            w = _windows[w_idx]
            wp95 = _calcular_p95(w["times"])
            wavg = w["total_time"] / w["count"] if w["count"] > 0 else 0
            start_str = time.strftime("%H:%M:%S", time.localtime(w["start"]))
            print(f"  {w_idx:>8d} {start_str:>12s} {w['count']:>8d} {wp95:>8.0f}ms {wavg:>8.0f}ms {w['max_time']:>8.0f}ms {w['failures']:>7d}")
            p95s.append((w_idx, wp95))

        print()
        # Detectar degradacion: comparar P95 de primera vs ultima ventana
        if len(p95s) >= 2:
            first_p95 = p95s[0][1]
            last_p95 = p95s[-1][1]
            degradacion = last_p95 - first_p95
            pct = (degradacion / first_p95) * 100 if first_p95 > 0 else 0
            print(f"  Degradacion P95:       {first_p95:.0f}ms -> {last_p95:.0f}ms ({pct:+.1f}%)")
            if pct > 20:
                print("  ESTADO: POSIBLE DEGRADACION (P95 subio >20%)")
                print("  Revisar: conexiones BD, consultas lentas, uso de memoria.")
            elif pct < -10:
                print("  ESTADO: MEJORA (P95 bajo durante la prueba)")
            else:
                print("  ESTADO: ESTABLE (sin degradacion significativa)")
        else:
            print("  No hay suficientes ventanas para detectar degradacion.")

        print()
        criterio_memoria = "Monitorear con: docker stats --format 'table {{.Name}}\t{{.MemUsage}}'"
        print(f"  Criterio memoria: {criterio_memoria}")
        print("  No debe haber crecimiento sostenido de memoria.")
    else:
        print("  No se registraron requests.")

    print("=" * 70)
