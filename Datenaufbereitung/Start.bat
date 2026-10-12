@echo off
chcp 65001 >nul
title Python Arbeitsumgebung - Datenaufbereitung
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0menu.py" (
    echo FEHLER: menu.py wurde nicht gefunden.
    pause
    exit /b 1
)

REM --- Menue starten (ohne Argumente, die Ordnerauswahl passiert im Menü) ---
python "%~dp0menu.py"

echo.
echo Das Menue wurde beendet.
pause