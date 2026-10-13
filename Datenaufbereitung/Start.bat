@echo off
chcp 65001 >nul
title Datenaufbereitung Menue

:: Dynamische Suche nach Python
set "PY_EXE="

:: 1. PRIORITÄT: Neue Installation (Systemweit)
if exist "C:\Program Files\Python313\python.exe" (
    set "PY_EXE=C:\Program Files\Python313\python.exe"
    goto :RUN_MENU
)

:: 2. FALLBACK: Alte Installation (User-spezifisch)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :RUN_MENU
)

:: 3. FALLBACK: Launcher 'py'
where py >nul 2>&1
if %errorlevel%==0 (
    set "PY_EXE=py -3.13"
    goto :RUN_MENU
)

echo [FEHLER] Kein geeignetes Python gefunden!
pause
exit /b 1

:RUN_MENU
echo Starte Menue mit: %PY_EXE%
"%PY_EXE%" Menu.py
pause