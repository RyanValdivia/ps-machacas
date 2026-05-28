#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django
import time

def create_database_if_not_exists():
    """Crea la base de datos registrame_db si no existe"""
    try:
        import psycopg2
        from psycopg2 import sql
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Esperar a que PostgreSQL esté listo
        max_retries = 10
        conn = None
        
        for i in range(max_retries):
            try:
                # CAMBIO: Intentar conectarse a 'postgres' primero
                try:
                    conn = psycopg2.connect(
                        dbname='postgres',
                        user='postgres',
                        password='',
                        host='127.0.0.1',
                        port='5433',
                        connect_timeout=3
                    )
                    print("[INFO] Conectado a base de datos 'postgres'")
                except psycopg2.OperationalError as e:
                    # Si 'postgres' no existe, conectarse a 'template1' que siempre existe
                    if 'database "postgres" does not exist' in str(e):
                        print("[INFO] Base de datos 'postgres' no existe, usando 'template1'")
                        conn = psycopg2.connect(
                            dbname='template1',
                            user='postgres',
                            password='',
                            host='127.0.0.1',
                            port='5433',
                            connect_timeout=3
                        )
                        
                        # Crear la base de datos 'postgres' también
                        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                        cursor = conn.cursor()
                        
                        try:
                            cursor.execute("CREATE DATABASE postgres")
                            print("[INFO] Base de datos 'postgres' creada")
                        except psycopg2.errors.DuplicateDatabase:
                            print("[INFO] Base de datos 'postgres' ya existe")
                        
                        cursor.close()
                    else:
                        raise
                
                break
                
            except psycopg2.OperationalError:
                if i < max_retries - 1:
                    print("[INFO] Esperando a PostgreSQL... ({}/{})".format(i+1, max_retries))
                    time.sleep(2)
                else:
                    raise
        
        if conn is None:
            raise Exception("No se pudo conectar a PostgreSQL")
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si registrame_db existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'registrame_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("[INFO] Creando base de datos 'registrame_db'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('registrame_db')
            ))
            print("[OK] Base de datos 'registrame_db' creada correctamente")
        else:
            print("[INFO] Base de datos 'registrame_db' ya existe")
        
        cursor.close()
        conn.close()
        time.sleep(1)
        return True
        
    except Exception as e:
        print("[ERROR] No se pudo conectar a PostgreSQL: {}".format(e))
        return False

def main():
    # Forzar codificación UTF-8
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registrame.settings')
    
    # Configurar el directorio base
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
        # Configurar directorio de medios en AppData cuando está empaquetado
        APPDATA_DIR = os.path.join(os.environ.get('APPDATA', ''), 'com.registrame.app')  # ← Cambiar nombre
        MEDIA_ROOT = os.path.join(APPDATA_DIR, 'media')
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        os.makedirs(os.path.join(MEDIA_ROOT, 'company'), exist_ok=True)  # ← AGREGAR ESTA LÍNEA
        print("[INFO] Directorio de medios: {}".format(MEDIA_ROOT))
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    print("[INFO] Directorio base: {}".format(BASE_DIR))
    
    # FORZAR variables de entorno para PostgreSQL
    os.environ['DB_ENGINE'] = 'django.db.backends.postgresql'
    os.environ['DB_NAME'] = 'registrame_db'
    os.environ['DB_USER'] = 'postgres'
    os.environ['DB_PASSWORD'] = ''
    os.environ['DB_HOST'] = '127.0.0.1'
    os.environ['DB_PORT'] = '5433'
    
    print("[INFO] Configuracion DB: postgresql://postgres@127.0.0.1:5433/registrame_db")
    
    # Verificar y crear la base de datos
    print("\n[INFO] Verificando conexion con PostgreSQL...")
    if not create_database_if_not_exists():
        print("[ERROR] No se pudo conectar a PostgreSQL. Cerrando...")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print("[OK] Usando PostgreSQL")
    
    try:
        django.setup()
        print("[OK] Django inicializado correctamente")
    except Exception as e:
        print("[ERROR] Error al inicializar Django: {}".format(e))
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    # Ejecutar migraciones
    from django.core.management import call_command
    
    print("\n[INFO] Aplicando migraciones...")
    print("[INFO] Esto puede tomar hasta 60 segundos en la primera ejecucion...")
    print("[INFO] Por favor espera hasta ver '[OK] Migraciones aplicadas'")
    print("=" * 60)
    
    try:
        call_command('migrate', '--noinput', verbosity=2)
        
        print("=" * 60)
        print("[OK] Migraciones aplicadas correctamente")
        print("=" * 60)
    except Exception as e:
        print("[ERROR] Error en migraciones: {}".format(e))
        import traceback
        traceback.print_exc()
        print("[WARNING] Continuando de todos modos...")
    
    # Pequeña pausa para asegurar que todo esté estable
    time.sleep(1)
    
    # Crear superusuario
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(usuEmail='admin@registrame.com').exists():
            print("\n[INFO] Creando usuario administrador...")
            User.objects.create_superuser(
                usuEmail='admin@registrame.com',
                password='admin123'
            )
            print("[OK] Usuario admin creado (email: admin@registrame.com, password: admin123)")
        else:
            print("[INFO] Usuario admin ya existe")
    except Exception as e:
        print("[WARNING] No se pudo crear superusuario: {}".format(e))
    
    # Iniciar servidor
    from django.core.management import execute_from_command_line
    
    sys.argv = [
        'manage.py',
        'runserver',
        '127.0.0.1:8000',
        '--noreload',
        '--insecure',
    ]
    
    print("\n" + "=" * 60)
    print("[INFO] Iniciando servidor en http://127.0.0.1:8000")
    print("[INFO] Servidor listo para recibir peticiones")
    print("=" * 60 + "\n")
    
    sys.stdout.flush()
    sys.stderr.flush()
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()