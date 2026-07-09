""" NF-STRESS-01/03/05 y NF-REC-01: carga sobre el flujo de Punto de Venta (login + búsqueda + venta) """
from locust import HttpUser, task, between, tag
import os
from pathlib import Path

env_file = Path(__file__).resolve().parents[2] / ".env"
if not env_file.exists():
    env_file = Path(__file__).resolve().parents[2] / ".env.example"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

VENDEDOR_USER = os.getenv("TEST_VENDEDOR_USER", "vendedor1")
VENDEDOR_PASS = os.getenv("TEST_VENDEDOR_PASS", "Admin123!")
# Producto "LUNA-PERS" (seed id=1): venta personalizada, no valida ni descuenta stock,
# por lo que sostiene ejecuciones largas/concurrentes sin agotar inventario.
PRODUCT_ID = int(os.getenv("TEST_PRODUCT_ID", "1"))


class VendedorPOS(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "/api/user/token/",
            json={"usuNom": VENDEDOR_USER, "usuContra": VENDEDOR_PASS},
            name="POST /api/user/token/ [login]",
        )
        if response.status_code == 200:
            self.headers = {"Authorization": f"Bearer {response.json()['access']}"}
        else:
            self.headers = {}

    @tag("search", "stress")
    @task(3)
    def buscar_productos(self):
        self.client.get(
            "/api/products/?search=PEGASUS",
            headers=self.headers,
            name="/api/products/?search=[term]",
        )

    @tag("venta", "stress", "recoverability")
    @task(1)
    def crear_venta(self):
        with self.client.post(
            "/api/sales/ventas/",
            json={
                "ventFormaPago": "EFECTIVO",
                "detalles": [
                    {
                        "prodCod": PRODUCT_ID,
                        "ventDetCantidad": 1,
                        "ventDetPrecioUni": "20.00",
                        "ventDetDescuento": 0,
                    }
                ],
            },
            headers=self.headers,
            name="POST /api/sales/ventas/ [venta]",
            catch_response=True,
        ) as response:
            # Bajo NF-REC-01 se espera que las peticiones fallen mientras la BD está
            # caída (5xx/conexión rechazada): no se marca la carga como colapsada,
            # solo se registra para el reporte de error rate.
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")
