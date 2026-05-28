@echo off
echo ========================================
echo Verificacion de estructura para Tauri
echo ========================================
echo.

set "BINARIES_DIR=binaries"
set "POSTGRES_DIR=%BINARIES_DIR%\postgres"
set "DJANGO_EXE=%BINARIES_DIR%\django_server.exe"

echo [1] Verificando directorio binaries...
if exist "%BINARIES_DIR%" (
    echo    OK - Directorio binaries existe
) else (
    echo    ERROR - Directorio binaries NO existe
    exit /b 1
)

echo.
echo [2] Verificando PostgreSQL...
if exist "%POSTGRES_DIR%" (
    echo    OK - Directorio postgres existe
) else (
    echo    ERROR - Directorio postgres NO existe
    exit /b 1
)

if exist "%POSTGRES_DIR%\bin" (
    echo    OK - Directorio postgres\bin existe
) else (
    echo    ERROR - Directorio postgres\bin NO existe
    exit /b 1
)

if exist "%POSTGRES_DIR%\bin\postgres.exe" (
    echo    OK - postgres.exe existe
) else (
    echo    ERROR - postgres.exe NO existe
    exit /b 1
)

if exist "%POSTGRES_DIR%\bin\initdb.exe" (
    echo    OK - initdb.exe existe
) else (
    echo    ERROR - initdb.exe NO existe
    exit /b 1
)

if exist "%POSTGRES_DIR%\bin\pg_ctl.exe" (
    echo    OK - pg_ctl.exe existe
) else (
    echo    ERROR - pg_ctl.exe NO existe
    exit /b 1
)

if exist "%POSTGRES_DIR%\lib" (
    echo    OK - Directorio postgres\lib existe
) else (
    echo    ADVERTENCIA - Directorio postgres\lib NO existe (puede causar problemas)
)

if exist "%POSTGRES_DIR%\share" (
    echo    OK - Directorio postgres\share existe
) else (
    echo    ADVERTENCIA - Directorio postgres\share NO existe (puede causar problemas)
)

echo.
echo [3] Verificando Django...
if exist "%DJANGO_EXE%" (
    echo    OK - django_server.exe existe
) else (
    echo    ADVERTENCIA - django_server.exe NO existe
)

echo.
echo [4] Listando estructura completa...
dir /s /b binaries

echo.
echo ========================================
echo Verificacion COMPLETADA
echo ========================================
echo Puedes proceder con: npm run tauri build
