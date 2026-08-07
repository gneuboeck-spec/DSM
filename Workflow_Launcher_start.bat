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
echo Werte wurden gespeichert. Starte die Arbeitsumgebung...
echo.

set "VENV_ACTIVATE=C:\Users\digit\.venv\Scripts\activate.bat"

REM --- Pruefung: Gibt es die globale VENV? ---
if not exist "%VENV_ACTIVATE%" (
    echo FEHLER: Die globale VENV wurde nicht gefunden.
    echo Erwarteter Pfad:
    echo %VENV_ACTIVATE%
    pause
    exit /b 1
)

REM --- Pruefung: Gibt es die menu.py? ---
if not exist "%~dp0Python_Skript_Starter_menu.py" (
    echo FEHLER: Python_Skript_Starter_menu.py wurde nicht gefunden.
    echo Erwarteter Pfad:
    echo %~dp0Python_Skript_Starter_menu.py
    pause
    exit /b 1
)

echo Gefundene Umgebung: globale VENV unter C:\Users\digit\.venv
echo Pfad: %VENV_ACTIVATE%
echo.

REM --- VENV aktivieren ---
call "%VENV_ACTIVATE%"

echo.
echo KONTROLLPUNKT: Die VENV ist aktiv.
echo Druecken Sie eine Taste, um das Menue zu starten.
pause >nul

REM --- Menue starten und Werte uebergeben ---
python "%~dp0Python_Skript_Starter_menu.py" "%ac_number%" "%disk_id%"

echo.
echo Das Menue wurde beendet.
pause