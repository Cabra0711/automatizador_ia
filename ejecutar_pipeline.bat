@echo off
REM ============================================================================
REM Script ejecutor del pipeline de automatización para Talento Andino S.A.S.
REM Invocado por Power Automate Desktop o por consola.
REM Retorna exit code 0 en éxito, 1 en error.
REM ============================================================================

cd /d "%~dp0"
echo [%DATE% %TIME%] Iniciando ejecucion del pipeline desde batch...>> ejecucion_log.txt

IF EXIST "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) ELSE (
    python main.py
)

SET SALIDA_CODE=%ERRORLEVEL%

IF %SALIDA_CODE% EQU 0 (
    echo [%DATE% %TIME%] EXITO: Pipeline ejecutado correctamente con codigo %SALIDA_CODE%>> ejecucion_log.txt
    exit /b 0
) ELSE (
    echo [%DATE% %TIME%] ERROR: El pipeline fallo con codigo %SALIDA_CODE%>> ejecucion_log.txt
    exit /b %SALIDA_CODE%
)
