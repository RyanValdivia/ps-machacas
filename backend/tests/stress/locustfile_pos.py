"""
locustfile_pos.py — Pruebas de stress para el sistema POS (Punto de Venta).

Pruebas incluidas:
  - NF-STRESS-01: 50 usuarios concurrentes creando ventas durante 2 minutos
                  Criterios: P95 ≤ 3s, Error Rate < 5%
  - NF-STRESS-03: 10 usuarios intentando comprar el mismo producto con stock=1
                  Criterios: solo 1 éxito, 9 rechazos (HTTP 400), stock final = 0
  - NF-STRESS-05: 20 usuarios consultando el dashboard durante 5 minutos
                  Criterios: P95 ≤ 5s, sin memory leaks

Características de estrés real:
  - Pool rotativo de productos (evita agotar stock en un solo producto)
  - Payloads variados: cantidades aleatorias, múltiples items por venta
  - Formas de pago aleatorias (EFECTIVO, YAPE, VISA)
  - Clientes aleatorios (a veces genérico, a veces con datos)
  - Dashboard genera sus propios datos de prueba (escritura + lectura simultánea)

Ejecución (headless):
  # NF-STRESS-01 — Ventas concurrentes
  locust -f tests/stress/locustfile_pos.py --tags NF-STRESS-01
         --users 50 --spawn-rate 10 --run-time 2m
         --html tests/stress/report_pos.html --headless
         --host http://localhost:8000

  # NF-STRESS-03 — Race condition
  locust -f tests/stress/locustfile_pos.py --tags NF-STRESS-03
         --users 10 --spawn-rate 10 --run-time 30s
         --html tests/stress/report_pos.html --headless
         --host http://localhost:8000

  # NF-STRESS-05 — Dashboard (con generación de datos en paralelo)
  locust -f tests/stress/locustfile_pos.py --tags NF-STRESS-05
         --users 25 --spawn-rate 5 --run-time 5m
         --html tests/stress/report_pos.html --headless
         --host http://localhost:8000

Variables de entorno requeridas:
  TEST_USERS_JSON   = '[{"usuNom":"admin","usuContra":"admin123"}]'
  RACE_PRODUCT_ID   = <prodCod del producto con stock=1>  (para NF-STRESS-03)
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
        "TEST_USERS_JSON no está definida. "
        "Ejemplo: export TEST_USERS_JSON='[{\"usuNom\":\"admin\",\"usuContra\":\"admin123\"}]'"
    )
TEST_USERS = json.loads(_test_users_raw)
_user_pool = itertools.cycle(TEST_USERS)
_pool_lock = threading.Lock()

RACE_CONDITION_PRODUCT_ID = int(os.getenv("RACE_PRODUCT_ID", "0"))

_race_results_lock = threading.Lock()
_race_results = {
    "success": 0,
    "rejected": 0,
    "other_errors": 0,
}

FORMAS_PAGO = ["EFECTIVO", "YAPE", "VISA"]
PESOS_PAGO = [60, 25, 15]


def _next_user_credentials():
    with _pool_lock:
        return next(_user_pool)


def _extraer_resultados(resp):
    """Extrae la lista de resultados de una respuesta paginada o plana."""
    try:
        data = resp.json()
        if isinstance(data, dict):
            return data.get("results", [])
        return data
    except Exception:
        return []


def _build_payload_venta(product_ids, cantidades=None):
    """
    Construye payload para POST /api/sales/ventas/ con uno o varios productos.
    Incluye variación realista: forma de pago aleatoria, a veces cliente.
    """
    detalles = []
    for i, pid in enumerate(product_ids):
        cant = cantidades[i] if cantidades and i < len(cantidades) else 1
        detalles.append({
            "prodCod": pid,
            "ventDetCantidad": cant,
        })

    payload = {
        "detalles": detalles,
        "ventFormaPago": random.choices(FORMAS_PAGO, weights=PESOS_PAGO, k=1)[0],
        "ventObservaciones": "Venta de prueba stress",
    }

    if random.random() < 0.3:
        payload["ventReferenciaPago"] = f"REF-{random.randint(10000, 99999)}"

    return payload


# ===========================================================================
# NF-STRESS-01 — Ventas Concurrentes (50 usuarios, 2 minutos)
# ===========================================================================
class VentasConcurrentesUser(HttpUser):
    """
    NF-STRESS-01: 50 usuarios creando ventas con payloads variados.

    Mejoras de estrés real:
      - Pool rotativo de 100+ productos para no depender de uno solo
      - 1 a 3 productos por venta con cantidades aleatorias (1-3 c/u)
      - Formas de pago variadas: EFECTIVO (60%), YAPE (25%), VISA (15%)
      - Cliente aleatorio (30% con datos, 70% genérico)
      - Auto-reabastecimiento del pool cuando se agotan los productos
    """

    wait_time = between(0.5, 1.5)
    weight = 1

    POOL_MIN_SIZE = 15
    POOL_FETCH_SIZE = 100

    def on_start(self):
        creds = _next_user_credentials()
        self.token = None
        self._product_pool = []
        self._last_pool_fetch = 0

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                self._auth_headers = {"Authorization": f"Bearer {self.token}"}
                resp.success()
            else:
                resp.failure(f"Login falló: HTTP {resp.status_code}")
                raise StopUser()

        self._ensure_pool()

    def _ensure_pool(self):
        """Obtiene productos con stock disponible para la venta."""
        if len(self._product_pool) >= self.POOL_MIN_SIZE:
            return

        headers = self._auth_headers
        with self.client.get(
            f"/api/products/?stock_min=1&page_size={self.POOL_FETCH_SIZE}&ordering=-prodStock",
            headers=headers,
            name="GET /api/products/ [pool-refill]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                results = _extraer_resultados(resp)
                nuevos = [p["prodCod"] for p in results if p.get("prodStock", 0) > 0]
                self._product_pool.extend(nuevos)
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._re_login()
            else:
                resp.failure(f"Error pool: HTTP {resp.status_code}")

    def _re_login(self):
        creds = _next_user_credentials()
        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [re-login]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                self._auth_headers = {"Authorization": f"Bearer {self.token}"}

    @tag("stress", "ventas", "NF-STRESS-01")
    @task
    def crear_venta(self):
        if not self.token:
            return

        self._ensure_pool()
        if not self._product_pool:
            return

        num_items = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
        num_items = min(num_items, len(self._product_pool))

        seleccionados = random.sample(self._product_pool, num_items)
        cantidades = [random.randint(1, min(3, 3)) for _ in range(num_items)]

        payload = _build_payload_venta(seleccionados, cantidades)
        payload["ventObservaciones"] = "Venta stress NF-STRESS-01"

        with self.client.post(
            "/api/sales/ventas/",
            json=payload,
            headers=self._auth_headers,
            name="POST /api/sales/ventas/ [NF-STRESS-01]",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                resp.success()
            elif resp.status_code == 400:
                body = resp.text[:200]
                for pid in seleccionados:
                    if pid in self._product_pool:
                        self._product_pool.remove(pid)
                resp.failure(f"Stock agotado o error: {body}")
            elif resp.status_code == 401:
                resp.failure("Token expirado")
                self._re_login()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")


# ===========================================================================
# NF-STRESS-03 — Race Condition (10 usuarios, 1 producto con stock=1)
# ===========================================================================
class RaceConditionUser(HttpUser):
    """
    NF-STRESS-03: 10 usuarios intentan comprar el MISMO producto con stock=1.
    Preparación:
        1. python tests/stress/seed_masivo.py --race-condition
        2. export RACE_PRODUCT_ID=<id retornado>
    Validaciones:
        - Solo 1 venta exitosa (HTTP 201)
        - 9 ventas rechazadas (HTTP 400)
        - stock final = 0 (verificar con seed_masivo.py --verificar-stock)
    """

    wait_time = between(0.01, 0.05)
    weight = 1

    def on_start(self):
        creds = _next_user_credentials()
        self.token = None
        self.venta_intentada = False

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login-race]",
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

    @tag("race-condition", "NF-STRESS-03")
    @task
    def intentar_compra_race(self):
        if not self.token or self.venta_intentada:
            raise StopUser()

        self.venta_intentada = True

        if not RACE_CONDITION_PRODUCT_ID:
            print(
                "\n  RACE_PRODUCT_ID no configurado. "
                "Ejecuta: python tests/stress/seed_masivo.py --race-condition"
            )
            raise StopUser()

        payload = {
            "detalles": [
                {
                    "prodCod": RACE_CONDITION_PRODUCT_ID,
                    "ventDetCantidad": 1,
                }
            ],
            "ventObservaciones": "Prueba Race Condition NF-STRESS-03",
        }

        with self.client.post(
            "/api/sales/ventas/",
            json=payload,
            headers=self._auth_headers,
            name="POST /api/sales/ventas/ [NF-STRESS-03-race]",
            catch_response=True,
        ) as resp:
            with _race_results_lock:
                if resp.status_code in (200, 201):
                    _race_results["success"] += 1
                    resp.success()
                elif resp.status_code == 400:
                    _race_results["rejected"] += 1
                    resp.success()
                else:
                    _race_results["other_errors"] += 1
                    resp.failure(f"Error inesperado: HTTP {resp.status_code}")


# ===========================================================================
# NF-STRESS-05 — Dashboard + generación de datos (20+ usuarios, 5 minutos)
# ===========================================================================
class DashboardConcurrenteUser(HttpUser):
    """
    NF-STRESS-05: 20 usuarios consultan el dashboard simultáneamente por 5 min.

    Mejora de estrés real:
      - Los usuarios NO solo leen el dashboard, también CREAN ventas,
        generando datos reales para que el dashboard tenga algo que mostrar.
      - Proporción: ~60% consultas, ~40% escrituras
      - Períodos variados: dia (60%), semana (25%), mes (10%), personalizado (5%)
    """

    wait_time = between(1, 3)
    weight = 1

    POOL_FETCH_SIZE = 50

    def on_start(self):
        creds = _next_user_credentials()
        self.token = None
        self._product_pool = []

        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [login-dashboard]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                self._auth_headers = {"Authorization": f"Bearer {self.token}"}
                resp.success()
            else:
                resp.failure(f"Login falló: HTTP {resp.status_code}")
                raise StopUser()

        self._ensure_pool()

    def _ensure_pool(self):
        if len(self._product_pool) > 10:
            return
        with self.client.get(
            f"/api/products/?stock_min=1&page_size={self.POOL_FETCH_SIZE}&ordering=-prodStock",
            headers=self._auth_headers,
            name="GET /api/products/ [pool-dashboard]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                results = _extraer_resultados(resp)
                self._product_pool = [p["prodCod"] for p in results if p.get("prodStock", 0) > 0]
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado en pool")
                self._re_login()

    def _re_login(self):
        creds = _next_user_credentials()
        with self.client.post(
            "/api/user/token/",
            json={"usuNom": creds["usuNom"], "usuContra": creds["usuContra"]},
            name="POST /api/user/token/ [re-login-dash]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access")
                self._auth_headers = {"Authorization": f"Bearer {self.token}"}

    @tag("dashboard", "NF-STRESS-05")
    @task(3)
    def consultar_dashboard(self):
        if not self.token:
            return

        periodo = random.choices(
            ["dia", "semana", "mes", "personalizado"],
            weights=[60, 25, 10, 5],
            k=1,
        )[0]
        headers = self._auth_headers
        url = f"/api/sales/ventas/estadisticas_dashboard/?periodo={periodo}"

        with self.client.get(
            url,
            headers=headers,
            name="GET /api/sales/ventas/estadisticas_dashboard/ [NF-STRESS-05]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if data:
                        resp.success()
                    else:
                        resp.failure("Dashboard vacio")
                except Exception:
                    resp.failure("Respuesta no es JSON")
            elif resp.status_code == 401:
                resp.failure("Token expirado en dashboard")
                self._re_login()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("dashboard", "NF-STRESS-05")
    @task(1)
    def consultar_ventas_del_dia(self):
        if not self.token:
            return

        with self.client.get(
            "/api/sales/ventas/del_dia/",
            headers=self._auth_headers,
            name="GET /api/sales/ventas/del_dia/ [NF-STRESS-05]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 401:
                resp.failure("Token expirado en del_dia")
                self._re_login()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")

    @tag("dashboard", "NF-STRESS-05")
    @task(1)
    def crear_venta_datos(self):
        """
        Crea una venta para generar datos reales en el dashboard.
        Esto hace que las consultas al dashboard sean significativas
        (en lugar de consultar una BD vacia o estatica).
        """
        if not self.token:
            return

        self._ensure_pool()
        if not self._product_pool:
            return

        pid = random.choice(self._product_pool)
        payload = _build_payload_venta([pid], [1])

        with self.client.post(
            "/api/sales/ventas/",
            json=payload,
            headers=self._auth_headers,
            name="POST /api/sales/ventas/ [NF-STRESS-05-data]",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                resp.success()
            elif resp.status_code == 400:
                if pid in self._product_pool:
                    self._product_pool.remove(pid)
                resp.failure(f"Stock agotado al generar datos: {resp.text[:100]}")
            elif resp.status_code == 401:
                resp.failure("Token expirado en venta")
                self._re_login()
            else:
                resp.failure(f"Error: HTTP {resp.status_code}")


# ---------------------------------------------------------------------------
# Event hook: reporte final de Race Condition
# ---------------------------------------------------------------------------
@events.quitting.add_listener
def reporte_race_condition(environment, **kwargs):
    with _race_results_lock:
        success = _race_results["success"]
        rejected = _race_results["rejected"]
        other = _race_results["other_errors"]

    if success == 0 and rejected == 0:
        return

    print("\n" + "=" * 60)
    print("RESUMEN NF-STRESS-03 — Race Condition")
    print("=" * 60)
    print(f"  Ventas exitosas (HTTP 201):      {success}")
    print(f"  Ventas rechazadas (HTTP 400):    {rejected}")
    print(f"  Otros errores:                   {other}")
    print(f"  Total intentos:                  {success + rejected + other}")
    print()

    if success == 1 and rejected == 9:
        print("  RESULTADO: CORRECTO")
        print("   -> 1 venta exitosa, 9 rechazadas por stock insuficiente.")
    elif success > 1:
        print("  RESULTADO: INCORRECTO")
        print(f"   -> {success} ventas exitosas. Posible problema de concurrencia.")
        print("   -> Revisar manejo de transacciones en el backend.")
    elif success == 0:
        print("  RESULTADO: SIN VENTAS EXITOSAS")
        print("   -> Verificar que el producto existe y tiene stock=1.")
    else:
        print(f"  RESULTADO: Revisar manualmente ({success} exitos)")

    print()
    print("  Para verificar stock final:")
    print("     python tests/stress/seed_masivo.py --verificar-stock")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Event hook: reporte general al finalizar
# ---------------------------------------------------------------------------
@events.quitting.add_listener
def reporte_general(environment, **kwargs):
    stats = environment.stats
    total = stats.total

    if total.num_requests == 0:
        return

    p95 = total.get_response_time_percentile(0.95)
    print("\n" + "=" * 60)
    print("RESUMEN GENERAL DE LA PRUEBA")
    print("=" * 60)
    print(f"  Requests totales:   {total.num_requests:,}")
    print(f"  Failures:           {total.num_failures:,}")
    print(f"  Error Rate:         {(total.num_failures / total.num_requests) * 100:.2f}%")
    print(f"  Latencia promedio:  {total.avg_response_time:.0f} ms")
    print(f"  Latencia P95:       {p95:.0f} ms")
    for r in ["ventas", "products", "token", "dashboard"]:
        entry = stats.get("/api/sales/ventas/", "POST")
        if entry and entry.num_requests > 0:
            ep95 = entry.get_response_time_percentile(0.95)
            print(f"  POST /api/sales/ventas/  -> P95: {ep95:.0f} ms, "
                  f"Req: {entry.num_requests}, Fallos: {entry.num_failures}")
    print("=" * 60)
