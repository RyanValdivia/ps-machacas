@echo off
echo ========================================
echo Construyendo instalador Tauri
echo ========================================
echo.

cd /d "%~dp0.."

echo [1] Verificando estructura...
if not exist "src-tauri\binaries\postgres\bin\postgres.exe" (
    echo ERROR: postgres.exe no encontrado
    pause
    exit /b 1
)
echo    OK - PostgreSQL encontrado

echo.
echo [2] Ejecutando build...
call npm run tauri build

echo.
echo ========================================
echo Build finalizado
echo ========================================
pause
