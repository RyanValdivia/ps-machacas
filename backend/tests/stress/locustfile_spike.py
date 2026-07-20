"""
locustfile_spike.py — Prueba de Pico + Persistencia (Spike Test).

Objetivo:
  Evaluar como el sistema maneja un aumento BRUSCO y MASIVO de carga
  en pocos segundos, y si se recupera correctamente cuando la carga
  vuelve a niveles normales.

Escenario:
  - Rampa rapida: 0 a 200 usuarios en 30 segundos (spawn-rate ~7 users/s)
  - Mantener pico: 200 usuarios durante 5 minutos
  - Carga mixta: busquedas (50%), ventas (30%), dashboard (20%)

Metricas:
  - Tiempo hasta que el sistema empieza a fallar (punto de quiebre)
  - Latencia P95 durante el pico vs despues del pico
  - Error Rate durante el pico
  - Recuperacion: las metricas vuelven a la normalidad al bajar la carga
  - Capacidad de rechazar gracefulmente cuando los recursos se agotan

Criterios de aceptacion:
  - El sistema no debe caerse (debe seguir respondiendo, aunque sea con errores)
  - Los errores deben ser graceful (HTTP 429, 503, 400 — no conexiones rechazadas)
  - Al reducir la carga, las metricas deben volver a niveles pre-pico
  - P95 durante pico < 8s (tolerancia alta para el pico)
  - Error Rate durante pico < 20%

Ejecucion:
  locust -f tests/stress/locustfile_spike.py
         --users 200 --spawn-rate 7 --run-time 6m
         --html tests/stress/report_spike.html --headless
         --host http://localhost:8000

  Nota: spawn-rate=7 significa ~28s para alcanzar 200 usuarios.
  Luego se mantiene 200 usuarios por ~5m30s.

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

# Spike test: aumento BRUSCO de carga (0 a 200 usuarios en ~30s, spawn-rate
# ~7 users/s) que luego se mantiene en el pico (200 usuarios) durante ~5
# minutos. A diferencia del soak test, aquí interesa la velocidad del
# aumento y si el sistema se recupera al bajar la carga, no la duración.
# _classify_phase() separa cada respuesta en fase "ramping" (primeros 45s,
# mientras suben los usuarios) o "peak" (resto), para poder comparar
# latencia/errores de una fase contra la otra en el reporte final.
# Único User class (SpikeUser) con 3 tareas mezcladas: búsquedas (peso 5),
# ventas (peso 3), dashboard (peso 2).
# Éxito esperado: el sistema no se cae (sigue respondiendo, aunque con
# errores), los errores durante el pico son "graceful" (400/429/503, no
# conexiones rechazadas), Error Rate en pico < 20% y P95 en pico < 8s (ver
# hook on_quitting). Errores masivos o timeouts durante el pico indican
# que el sistema no soporta el aumento brusco de carga.

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
# Tracking de fases (rampa, pico, recuperacion)
# ---------------------------------------------------------------------------
_phase_lock = threading.Lock()
_phase_stats = {
    "ramping": {"count": 0, "failures": 0, "total_time": 0, "times": []},
    "peak": {"count": 0, "failures": 0, "total_time": 0, "times": []},
}


def _classify_phase():
    """Clasifica la fase actual basada en el tiempo transcurrido."""
    elapsed = time.time() - _test_start_time
    if elapsed < 45:
        return "ramping"
    return "peak"


def _record_phase_response(phase, response_time, is_failure):
    with _phase_lock:
        s = _phase_stats[phase]
        s["count"] += 1
        s["total_time"] += response_time
        s["times"].append(response_time)
        if is_failure:
            s["failures"] += 1


_test_start_time = time.time()


TERMINOS_SPIKE = [
    "PEGASUS", "VIPSUAL", "SEED", "METAL", "NEGRO",
    "a", "e", "LUXOTTICA", "RAY-BAN", "ACETATO",
]

FORMAS_PAGO = ["EFECTIVO", "YAPE", "VISA"]


def _extraer_resultados(resp):
    try:
        data = resp.json()
        if isinstance(data, dict):
            return data.get("results", [])
        return data
    except Exception:
        return []


class SpikeUser(HttpUser):
    """
    Usuario de prueba de pico.

    Cada usuario ejecuta una mezcla de:
    - Busqueda de productos (50% del peso)
    - Creacion de venta (30% del peso)
    - Consulta de dashboard (20% del peso)

    El token se obtiene al inicio. Si expira, se refresca.
    """

    wait_time = between(0.5, 2.0)

    def on_start(self):
        creds = _next_credentials()
        self.token = None
        self.refresh_token = None
        self._product_pool = []

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login-spike]",
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
        self._fetch_pool()

    def _fetch_pool(self):
        with self.client.get(
            "/api/products/?stock_min=1&page_size=50&ordering=-prodStock",
            headers=self._auth_headers,
            name="GET /api/products/ [pool-spike]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                results = _extraer_resultados(resp)
                self._product_pool = [p["prodCod"] for p in results if p.get("prodStock", 0) > 0]
                resp.success()
            elif resp.status_code == 401:
                self._refresh_token()

    def _refresh_token(self):
        if self.refresh_token:
            with self.client.post(
                "/api/user/token/refresh/",
                json={"refresh": self.refresh_token},
                name="POST /api/user/token/refresh/ [spike]",
                catch_response=True,
            ) as resp:
                if resp.status_code == 200:
                    data = resp.json()
                    self.token = data.get("access")
                    self._auth_headers = {"Authorization": f"Bearer {self.token}"}

    @tag("spike")
    @task(5)
    def buscar_productos(self):
        """Busqueda de productos (tarea principal)."""
        if not self.token:
            return

        termino = random.choice(TERMINOS_SPIKE)

        with self.client.get(
            f"/api/products/?search={termino}",
            headers=self._auth_headers,
            name="GET /api/products/?search [SPIKE]",
            catch_response=True,
        ) as resp:
            phase = _classify_phase()
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = resp.status_code != 200
            _record_phase_response(phase, rt, is_fail)

            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("spike")
    @task(3)
    def crear_venta(self):
        """Creacion de venta."""
        if not self.token or not self._product_pool:
            return

        pid = random.choice(self._product_pool)

        payload = {
            "detalles": [{"prodCod": pid, "ventDetCantidad": 1}],
            "ventFormaPago": random.choice(FORMAS_PAGO),
            "ventObservaciones": "Venta spike test",
        }

        with self.client.post(
            "/api/sales/ventas/",
            json=payload,
            headers=self._auth_headers,
            name="POST /api/sales/ventas/ [SPIKE]",
            catch_response=True,
        ) as resp:
            phase = _classify_phase()
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = True

            if resp.status_code in (200, 201):
                is_fail = False
                resp.success()
            elif resp.status_code == 400:
                if pid in self._product_pool:
                    self._product_pool.remove(pid)
                resp.failure(f"Stock agotado: {resp.text[:100]}")
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

            _record_phase_response(phase, rt, is_fail)

    @tag("spike")
    @task(2)
    def consultar_dashboard(self):
        """Consulta al dashboard."""
        if not self.token:
            return

        periodo = random.choice(["dia", "semana", "mes"])

        with self.client.get(
            f"/api/sales/ventas/estadisticas_dashboard/?periodo={periodo}",
            headers=self._auth_headers,
            name="GET /api/sales/ventas/estadisticas_dashboard/ [SPIKE]",
            catch_response=True,
        ) as resp:
            phase = _classify_phase()
            rt = resp.elapsed.total_seconds() * 1000
            is_fail = resp.status_code != 200
            _record_phase_response(phase, rt, is_fail)

            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._refresh_token()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")


def _calcular_p95(times):
    if not times:
        return 0
    sorted_t = sorted(times)
    idx = int(len(sorted_t) * 0.95)
    return sorted_t[idx]


# ---------------------------------------------------------------------------
# Evento de inicio
# ---------------------------------------------------------------------------
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global _test_start_time
    _test_start_time = time.time()
    print("\n" + "=" * 60)
    print("PRUEBA DE PICO (SPIKE TEST)")
    print("=" * 60)
    print("  Rampa:     0 -> 200 usuarios en ~30s")
    print("  Pico:      200 usuarios durante ~5m")
    print("  Carga:     50% busquedas, 30% ventas, 20% dashboard")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Evento de finalizacion
# ---------------------------------------------------------------------------
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.stats
    total = stats.total

    print("\n" + "=" * 70)
    print("NF-SPIKE-01 — Prueba de Pico + Persistencia")
    print("=" * 70)

    if total.num_requests > 0:
        p95_global = total.get_response_time_percentile(0.95)
        print(f"\n  Metricas GLOBALES:")
        print(f"  Requests totales:       {total.num_requests:,}")
        print(f"  Failures:               {total.num_failures:,}")
        print(f"  Error Rate:             {(total.num_failures / total.num_requests) * 100:.2f}%")
        print(f"  RPS promedio:           {total.total_rps:.2f}")
        print(f"  Latencia P95 global:    {p95_global:.0f} ms")

        print(f"\n  Desglose por FASE:")
        print(f"  {'Fase':12s} {'Req':>8s} {'Fallos':>8s} {'Error%':>8s} {'P95(ms)':>9s} {'Avg(ms)':>9s}")
        print("  " + "-" * 54)

        for phase_name in ["ramping", "peak"]:
            ps = _phase_stats[phase_name]
            if ps["count"] > 0:
                pp95 = _calcular_p95(ps["times"])
                pavg = ps["total_time"] / ps["count"]
                err_pct = (ps["failures"] / ps["count"]) * 100
                print(f"  {phase_name:12s} {ps['count']:>8d} {ps['failures']:>8d} {err_pct:>7.1f}% {pp95:>8.0f}ms {pavg:>8.0f}ms")

        print()
        ramping = _phase_stats["ramping"]
        peak = _phase_stats["peak"]

        if ramping["count"] > 0 and peak["count"] > 0:
            ramp_p95 = _calcular_p95(ramping["times"])
            peak_p95 = _calcular_p95(peak["times"])
            ramp_err = (ramping["failures"] / ramping["count"]) * 100
            peak_err = (peak["failures"] / peak["count"]) * 100

            print(f"  Variacion P95 (rampa -> pico):  {ramp_p95:.0f} -> {peak_p95:.0f} ms")
            print(f"  Variacion Error (rampa -> pico): {ramp_err:.1f}% -> {peak_err:.1f}%")
            print()

            if peak_err < 20:
                print(f"  Criterio Error < 20% durante pico: OK ({peak_err:.1f}%)")
            else:
                print(f"  Criterio Error < 20% durante pico: FALL ({peak_err:.1f}%)")
            if peak_p95 < 8000:
                print(f"  Criterio P95 < 8s durante pico:    OK ({peak_p95:.0f}ms)")
            else:
                print(f"  Criterio P95 < 8s durante pico:    FALL ({peak_p95:.0f}ms)")
    else:
        print("  No se registraron requests.")

    print("=" * 70)
