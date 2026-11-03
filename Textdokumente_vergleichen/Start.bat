@echo off
chcp 65001 >nul
title Python Arbeitsumgebung
setlocal

REM ==============================================================================
REM 🔧 ANSI ESCAPE CODES FÜR FARBEN (Konsistenz mit Python-Skripten)
REM ==============================================================================
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "RESET=%ESC%[0m"

REM --- In den Ordner wechseln, in dem diese Batch-Datei liegt ---
cd /d "%~dp0"

echo.
echo %MAGENTA%========================================%RESET%
echo %CYAN%  Python Arbeitsumgebung wird gestartet%RESET%
echo %MAGENTA%========================================%RESET%
echo.

REM --- Prüfung: Gibt es die Menu.py? ---
if not exist "%~dp0Menu.py" (
    echo %RED%[FEHLER] Menu.py wurde nicht gefunden.%RESET%
    echo %WHITE%Erwarteter Pfad:%RESET%
    echo %YELLOW%%~dp0Menu.py%RESET%
    echo %YELLOW%Drücken Sie eine Taste zum Beenden...%RESET%
    pause >nul
    exit /b 1
)

REM --- Dynamische Suche nach Python ---
set "PY_EXE="

REM 1. PRIORITÄT: Systemweite Installation
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

echo %RED%[FEHLER] Kein geeignetes Python gefunden!%RESET%
echo %YELLOW%Bitte installieren Sie Python 3.13 oder fügen Sie es zum PATH hinzu.%RESET%
pause
exit /b 1

:RUN_MENU
echo %GREEN%[OK]%RESET% %CYAN%Starte Menü mit:%RESET% %WHITE%%PY_EXE%%RESET%
echo %MAGENTA%---------------------------------------------------%RESET%
"%PY_EXE%" "%~dp0Menu.py"

echo.
echo %GREEN%Das Menü wurde beendet.%RESET%
echo %YELLOW%Drücken Sie eine Taste zum Schließen...%RESET%
pause >nul