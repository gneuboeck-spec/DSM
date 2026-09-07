@echo off
title Python Arbeitsumgebung
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

echo.
echo ========================================
echo   Python Arbeitsumgebung wird gestartet
echo ========================================
echo.

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0menu.py" (
    echo FEHLER: menu.py wurde nicht gefunden.
    echo Erwarteter Pfad:
    echo %~dp0menu.py
    pause
    exit /b 1
)

echo Starte das Menue...
echo.

REM --- Menue starten (ohne Parameter) ---
python "%~dp0menu.py"

echo.
echo Das Menue wurde beendet.
pause