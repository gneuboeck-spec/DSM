@echo off
chcp 65001 >nul
title Python Arbeitsumgebung - Hauptmenü
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0menu.py" (
    echo FEHLER: menu.py wurde im Hauptverzeichnis nicht gefunden.
    pause
    exit /b 1
)

REM --- Hauptmenue starten ---
python "%~dp0menu.py"

echo.
echo Das Hauptmenü wurde beendet.
pause