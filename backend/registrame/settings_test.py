import os

from registrame.settings import *  # noqa: F401,F403

_test_db_engine = os.environ.get("DB_ENGINE", "django.db.backends.sqlite3")

if "postgresql" in _test_db_engine:
    DATABASES = {
        "default": {
            "ENGINE": _test_db_engine,
            "NAME": os.environ.get("DB_NAME", "test_db"),
            "USER": os.environ.get("DB_USER", "test"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "test"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "TEST": {
                "NAME": "test_db",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
