@echo off
chcp 65001 >nul
setlocal
title Git Sync (nur Pull)

cd /d "%~dp0"

echo ========================================
echo   Git Sync: Nur Pull (keine eigenen Aenderungen)
echo ========================================
echo.

REM --- 0. Automatische Sicherung ---
echo SICHERHEITSHINWEIS: Es wird empfohlen, vor Repository-Aenderungen
echo eine Sicherung Ihrer lokalen Dateien zu erstellen.
echo.
choice /C JN /M "Automatische Sicherung erstellen"
if errorlevel 2 goto :SKIP_BACKUP

echo Erstelle Sicherung...
set TIMESTAMP=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=%~dp0..\Sicherung_Git_%TIMESTAMP%

mkdir "%BACKUP_DIR%" 2>nul
robocopy "%~dp0." "%BACKUP_DIR%" /E /XD .git Sicherung_* /NFL /NDL /NJH /NJS
echo Sicherung erfolgreich erstellt in: %BACKUP_DIR%
echo.

:SKIP_BACKUP

REM --- 1. Optional: Remote-URL aendern ---
echo Aktuelle Remote-URL (origin):
git remote get-url origin 2>nul || echo (Keine Remote-URL gefunden)
echo.
choice /C JN /M "Moechten Sie die Git-Remote-URL (origin) aendern"
if errorlevel 2 goto :SKIP_REMOTE_CHANGE
if errorlevel 1 goto :SET_REMOTE_URL

:SET_REMOTE_URL
echo.
set /p NEW_REMOTE_URL="Neue Git-Remote-URL (z.B. https://github.com/user/repo.git): "
if "%NEW_REMOTE_URL%"=="" (
    echo Keine Aenderung vorgenommen.
) else (
    git remote set-url origin "%NEW_REMOTE_URL%"
    echo Remote-URL erfolgreich auf "%NEW_REMOTE_URL%" geaendert.
)
echo.

:SKIP_REMOTE_CHANGE

REM --- 2. Optional: Anderen Git-Benutzer verwenden ---
set USE_CUSTOM_USER=0
set ORIGINAL_USER_NAME=
set ORIGINAL_USER_EMAIL=

echo Hinweis: Wenn Sie einen anderen Git-Benutzer verwenden,
echo werden gespeicherte Credentials geloescht und neu abgefragt.
echo.
choice /C JN /M "Moechten Sie einen anderen Git-Benutzer verwenden"
if errorlevel 2 goto :SKIP_USER_CHANGE
if errorlevel 1 goto :SET_CUSTOM_USER

:SET_CUSTOM_USER
echo.
for /f "delims=" %%i in ('git config user.name 2^>nul') do set ORIGINAL_USER_NAME=%%i
for /f "delims=" %%i in ('git config user.email 2^>nul') do set ORIGINAL_USER_EMAIL=%%i

if "%ORIGINAL_USER_NAME%"=="" set ORIGINAL_USER_NAME=NICHT_GEFUNDEN
if "%ORIGINAL_USER_EMAIL%"=="" set ORIGINAL_USER_EMAIL=NICHT_GEFUNDEN

echo Aktueller Benutzer: %ORIGINAL_USER_NAME% ^<%ORIGINAL_USER_EMAIL%^>
echo.

set /p GIT_USER_NAME="Neuer Git Benutzername: "
set /p GIT_USER_EMAIL="Neue Git E-Mail: "

if "%GIT_USER_NAME%"=="" goto :USER_ERROR
if "%GIT_USER_EMAIL%"=="" goto :USER_ERROR

echo.
echo Setze Git-Benutzer: %GIT_USER_NAME% ^<%GIT_USER_EMAIL%^>
git config user.name "%GIT_USER_NAME%"
git config user.email "%GIT_USER_EMAIL%"

echo Loesche gespeicherte Credentials fuer erneute Authentifizierung...
cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://gitlab.com >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://bitbucket.org >nul 2>&1

set USE_CUSTOM_USER=1
echo Fertig. Neue Credentials werden bei der naechsten Operation abgefragt.
echo.
goto :SKIP_USER_CHANGE

:USER_ERROR
echo FEHLER: Benutzername und E-Mail duerfen nicht leer sein.
if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
pause
exit /b 1

:SKIP_USER_CHANGE

REM --- 3. Pruefung: Sind wir in einem Git-Repo? ---
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Dieser Ordner ist kein Git-Repository.
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

set FORCE_PUSH_REQUIRED=0

echo [1/2] Hole aktuelle Aenderungen vom Server...
git pull
if errorlevel 1 (
    echo.
    echo WARNUNG: Pull fehlgeschlagen!
    echo Moegliche Ursache: Das neue Repository ist leer oder hat eine unverknuepfte Historie.
    echo.
    choice /C JN /M "Moechten Sie trotzdem fortfahren und das Remote-Repository mit Ihrem lokalen Stand ueberschreiben (Force Push)?"
    if errorlevel 2 (
        echo Vorgang abgebrochen.
        if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
        pause
        exit /b 1
    )
    echo Fortfahren mit lokalem Stand. Force-Push wird ausgefuehrt.
    set FORCE_PUSH_REQUIRED=1
)

if %FORCE_PUSH_REQUIRED%==1 (
    echo.
    echo ACHTUNG: Fuehre Force-Push aus (ueberschreibt Remote-Repository)!
    for /f "delims=" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
    if "%CURRENT_BRANCH%"=="" set CURRENT_BRANCH=main
    git push --force origin "%CURRENT_BRANCH%"
    
    if errorlevel 1 (
        echo.
        echo FEHLER beim Force-Push!
        if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
        pause
        exit /b 1
    )
)

echo.
echo [2/2] Aktueller Stand:
git --no-pager status -sb

echo.
echo ========================================
echo   SYNC ABGESCHLOSSEN.
echo ========================================

if %USE_CUSTOM_USER%==1 (
    echo.
    choice /C JN /M "Moechten Sie die geaenderte Git-Benutzerkonfiguration beibehalten"
    if errorlevel 2 call :RESTORE_CONFIG
)

pause
exit /b 0

:RESTORE_CONFIG
echo.
echo Stelle originale Git-Benutzerkonfiguration wieder her...
if not "%ORIGINAL_USER_NAME%"=="NICHT_GEFUNDEN" git config user.name "%ORIGINAL_USER_NAME%"
if not "%ORIGINAL_USER_EMAIL%"=="NICHT_GEFUNDEN" git config user.email "%ORIGINAL_USER_EMAIL%"
echo Fertig.
exit /b 0