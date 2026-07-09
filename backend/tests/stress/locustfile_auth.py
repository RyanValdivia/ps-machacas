""" NF-STRESS-04: Pico de 100 logins simultáneosn  """
from locust import HttpUser, task, between, tag
import itertools

import os
import json
from pathlib import Path

# Cargar variables desde backend/.env o backend/.env.example (soporte local)
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

# Pool de credenciales de prueba (deben existir en la BD).
# Se lee desde variable de entorno TEST_USERS_JSON.
test_users_raw = os.getenv("TEST_USERS_JSON")
if not test_users_raw:
    raise OSError(
        "TEST_USERS_JSON no está definida. "
        "Define la variable con un JSON array de credenciales. "
        "Ej: export TEST_USERS_JSON='[{\"usuNom\":\"admin\",\"usuContra\":\"admin123\"}]'"
    )
TEST_USERS = json.loads(test_users_raw)

user_pool = itertools.cycle(TEST_USERS)


class StressAuthUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @tag("login", "stress")
    @task
    def login_task(self):

        # Arrange: Tomar siguiente credencial del pool
        creds = next(user_pool)

        # Act: POST contra el endpoint JWT
        with self.client.post(
            "/api/user/token/",
            json=creds,
            name="POST /api/user/token/ [login]",
            catch_response=True,
        ) as response:
            # Assert: Verificar que el login fue exitoso
            if response.status_code != 200:
                response.failure(
                    f"Login falló para {creds['usuNom']}: HTTP {response.status_code}"
                )
                return

            data = response.json()
            if "access" in data and "refresh" in data:
                response.success()
            else:
                response.failure(
                    f"Respuesta 200 sin tokens para {creds['usuNom']}"
                )
