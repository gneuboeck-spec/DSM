@echo off
chcp 65001 >nul
setlocal
title Git Update (Pull, Add, Commit, Push)

cd /d "%~dp0"

echo ========================================
echo   Git Update: Pull, Add, Commit, Push
echo ========================================
echo.

REM --- Optional: Anderen Git-Benutzer verwenden? ---
set USE_CUSTOM_USER=0
set ORIGINAL_USER_NAME=
set ORIGINAL_USER_EMAIL=

echo Hinweis: Wenn Sie einen anderen Git-Benutzer verwenden,
echo werden gespeicherte Credentials geloescht und bei der
echo naechsten Operation neu abgefragt.
echo.
choice /C JN /M "Moechten Sie einen anderen Git-Benutzer verwenden"
if errorlevel 2 goto :SKIP_USER_CHANGE
if errorlevel 1 goto :SET_CUSTOM_USER

:SET_CUSTOM_USER
echo.
echo Bitte geben Sie die Git-Benutzerdaten ein:
echo -------------------------------------------

REM Aktuelle Konfiguration speichern
for /f "delims=" %%i in ('git config user.name 2^>nul') do set ORIGINAL_USER_NAME=%%i
for /f "delims=" %%i in ('git config user.email 2^>nul') do set ORIGINAL_USER_EMAIL=%%i

if "%ORIGINAL_USER_NAME%"=="" set ORIGINAL_USER_NAME=NICHT_GEFUNDEN
if "%ORIGINAL_USER_EMAIL%"=="" set ORIGINAL_USER_EMAIL=NICHT_GEFUNDEN

echo Aktueller Benutzer: %ORIGINAL_USER_NAME% ^<%ORIGINAL_USER_EMAIL%^>
echo.

set /p GIT_USER_NAME="Neuer Git Benutzername: "
set /p GIT_USER_EMAIL="Neue Git E-Mail: "

if "%GIT_USER_NAME%"=="" (
    echo FEHLER: Benutzername darf nicht leer sein.
    pause
    exit /b 1
)
if "%GIT_USER_EMAIL%"=="" (
    echo FEHLER: E-Mail darf nicht leer sein.
    pause
    exit /b 1
)

echo.
echo Setze Git-Benutzer: %GIT_USER_NAME% ^<%GIT_USER_EMAIL%^>
git config user.name "%GIT_USER_NAME%"
git config user.email "%GIT_USER_EMAIL%"

REM Gespeicherte HTTPS-Credentials loeschen
echo.
echo Loesche gespeicherte Credentials...
cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://gitlab.com >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://bitbucket.org >nul 2>&1

set USE_CUSTOM_USER=1
echo Fertig. Bei der naechsten Git-Operation werden neue Credentials abgefragt.
echo.

:SKIP_USER_CHANGE

REM --- Pruefung: Sind wir in einem Git-Repo? ---
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Dieser Ordner ist kein Git-Repository.
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

echo [1/5] Hole aktuelle Aenderungen vom Server...
git pull
if errorlevel 1 (
    echo.
    echo FEHLER beim Pull! Bitte Konflikte manuell loesen.
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

echo.
echo [2/5] Pruefe auf Aenderungen...
git add -A
git diff --cached --quiet
if errorlevel 1 goto :HAS_CHANGES
echo.
echo Keine Aenderungen vorhanden - nichts zu committen.
goto :PUSH_ONLY

:HAS_CHANGES
echo.
echo [3/5] Erstelle Commit...
git commit -m "Automatisches Update: %date% %time%"
if errorlevel 1 (
    echo.
    echo FEHLER beim Commit!
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

:PUSH_ONLY
echo.
echo [4/5] Lade Aenderungen hoch...
git push
if errorlevel 1 (
    echo.
    echo FEHLER beim Push!
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

echo.
echo [5/5] Status:
git --no-pager status -sb

echo.
echo ========================================
echo   ERFOLG! Alle Aenderungen sind online.
echo ========================================

REM Falls Custom User verwendet wurde, fragen ob Konfiguration beibehalten
if %USE_CUSTOM_USER%==1 (
    echo.
    choice /C JN /M "Moechten Sie die geaenderte Git-Konfiguration beibehalten"
    if errorlevel 2 call :RESTORE_CONFIG
)

pause
exit /b 0

:RESTORE_CONFIG
echo.
echo Stelle originale Git-Konfiguration wieder her...
if not "%ORIGINAL_USER_NAME%"=="NICHT_GEFUNDEN" git config user.name "%ORIGINAL_USER_NAME%"
if not "%ORIGINAL_USER_EMAIL%"=="NICHT_GEFUNDEN" git config user.email "%ORIGINAL_USER_EMAIL%"
echo Fertig.
exit /b 0