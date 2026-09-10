@echo off
title Python Arbeitsumgebung
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

REM --- Fragt einmalig nach den Werten ---
echo --- Bitte geben Sie die initialen Werte ein ---
set /p ac_number="AC-Nummer eingeben: "
set /p disk_id="Datentraeger-ID eingeben: "

echo.

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0Python_Skript_Starter_menu.py" (
    echo FEHLER: Python_Skript_Starter_menu.py wurde nicht gefunden.
    pause
    exit /b 1
)

REM --- Menue starten und Werte uebergeben ---
python "%~dp0Python_Skript_Starter_menu.py" "%ac_number%" "%disk_id%"

echo.
echo Das Menue wurde beendet.
pause