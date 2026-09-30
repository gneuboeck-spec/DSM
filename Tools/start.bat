@echo off
title Python Tools
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0menu.py" (
    echo FEHLER: menu.py wurde nicht gefunden.
    pause
    exit /b 1
)

REM --- Menue starten (ohne AC/Disk-ID, da Tools diese nicht benötigen) ---
python "%~dp0menu.py"

echo.
echo Das Tools-Menue wurde beendet.
pause