@echo off
chcp 65001 >nul
title Python Tools
setlocal

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

REM --- Pruefung: Gibt es die Menu.py? ---
if not exist "%~dp0Menu.py" (
    echo FEHLER: Menu.py wurde nicht gefunden.
    pause
    exit /b 1
)

REM --- Dynamische Suche nach Python ---
set "PY_EXE="

REM 1. PRIORITAET: Systemweite Installation
if exist "C:\Program Files\Python313\python.exe" (
    set "PY_EXE=C:\Program Files\Python313\python.exe"
    goto :RUN_MENU
)

REM 2. FALLBACK: User-Installation
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :RUN_MENU
)

REM 3. FALLBACK: Launcher 'py'
where py >nul 2>&1
if %errorlevel%==0 (
    set "PY_EXE=py -3.13"
    goto :RUN_MENU
)

echo [FEHLER] Kein geeignetes Python gefunden!
pause
exit /b 1

:RUN_MENU
echo Starte Tools-Menue mit: %PY_EXE%
"%PY_EXE%" "%~dp0Menu.py"

echo.
echo Das Tools-Menue wurde beendet.
pause