@echo off
chcp 65001 >nul
title Python Arbeitsumgebung - Hauptmenü
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

REM --- Optionale Eingabe der Werte (Enter zum Überspringen) ---
echo --- Optionale initiale Werte ---
echo (Enter drücken zum Überspringen)
echo (Kann später über "N" im Menü eingegeben werden)
echo.
set /p ac_number="AC-Nummer eingeben (oder Enter zum Überspringen): "
set /p disk_id="Datentraeger-ID eingeben (oder Enter zum Überspringen): "

echo.

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0Python_Skript_Starter_menu.py" (
    echo FEHLER: Python_Skript_Starter_menu.py wurde nicht gefunden.
    pause
    exit /b 1
)

REM --- Menue starten und Werte uebergeben (können leer sein) ---
python "%~dp0Python_Skript_Starter_menu.py" "%ac_number%" "%disk_id%"

echo.
echo Das Menue wurde beendet.
pause