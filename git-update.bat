@echo off
chcp 65001 >nul
setlocal
title Git Update (Pull, Add, Commit, Push)

REM ==============================================================================
REM 🔧 ANSI ESCAPE CODES FÜR FARBEN
REM ==============================================================================
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"
set "RED=%ESC%[91m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"
set "WHITE=%ESC%[97m"
set "RESET=%ESC%[0m"

REM Wenn ein Pfad übergeben wurde (vom Starter), nutze diesen, sonst den eigenen Ordner
if "%~1"=="" (
    cd /d "%~dp0"
) else (
    cd /d "%~1"
)

echo.
echo %MAGENTA%========================================%RESET%
echo %CYAN%  Git Update: Pull, Add, Commit, Push%RESET%
echo %MAGENTA%========================================%RESET%
echo.

REM --- 0. Automatische Sicherung ---
echo %YELLOW%SICHERHEITSHINWEIS: Es wird empfohlen, vor Repository-Aenderungen%RESET%
echo %YELLOW%eine Sicherung Ihrer lokalen Dateien zu erstellen.%RESET%
echo.

:ASK_BACKUP
set "CHOICE_BACKUP="
set /p "CHOICE_BACKUP=%YELLOW%Automatische Sicherung erstellen? (J/N): %RESET%"
if /i "%CHOICE_BACKUP%"=="J" goto :DO_BACKUP
if /i "%CHOICE_BACKUP%"=="N" goto :SKIP_BACKUP
goto :ASK_BACKUP

:DO_BACKUP
echo %CYAN%Erstelle Sicherung...%RESET%
set TIMESTAMP=%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=%~dp0..\Sicherung_Git_%TIMESTAMP%

mkdir "%BACKUP_DIR%" 2>nul
robocopy "%~dp0." "%BACKUP_DIR%" /E /XD .git Sicherung_* /NFL /NDL /NJH /NJS
echo %GREEN%Sicherung erfolgreich erstellt in: %BACKUP_DIR%%RESET%
echo.

:SKIP_BACKUP

REM --- 1. Optional: Remote-URL aendern ---
echo %CYAN%Aktuelle Remote-URL (origin):%RESET%
git remote get-url origin 2>nul || echo %WHITE%(Keine Remote-URL gefunden)%RESET%
echo.

:ASK_REMOTE
set "CHOICE_REMOTE="
set /p "CHOICE_REMOTE=%YELLOW%Moechten Sie die Git-Remote-URL (origin) aendern? (J/N): %RESET%"
if /i "%CHOICE_REMOTE%"=="J" goto :SET_REMOTE_URL
if /i "%CHOICE_REMOTE%"=="N" goto :SKIP_REMOTE_CHANGE
goto :ASK_REMOTE

:SET_REMOTE_URL
echo.
set /p NEW_REMOTE_URL="%WHITE%Neue Git-Remote-URL (z.B. https://github.com/user/repo.git): %RESET%"
if "%NEW_REMOTE_URL%"=="" (
    echo %YELLOW%Keine Aenderung vorgenommen.%RESET%
) else (
    git remote set-url origin "%NEW_REMOTE_URL%"
    echo %GREEN%Remote-URL erfolgreich auf "%NEW_REMOTE_URL%" geaendert.%RESET%
)
echo.

:SKIP_REMOTE_CHANGE

REM --- 2. Optional: Anderen Git-Benutzer verwenden ---
set USE_CUSTOM_USER=0
set ORIGINAL_USER_NAME=
set ORIGINAL_USER_EMAIL=

echo %YELLOW%Hinweis: Wenn Sie einen anderen Git-Benutzer verwenden,%RESET%
echo %YELLOW%werden gespeicherte Credentials geloescht und neu abgefragt.%RESET%
echo.

:ASK_USER
set "CHOICE_USER="
set /p "CHOICE_USER=%YELLOW%Moechten Sie einen anderen Git-Benutzer verwenden? (J/N): %RESET%"
if /i "%CHOICE_USER%"=="J" goto :SET_CUSTOM_USER
if /i "%CHOICE_USER%"=="N" goto :SKIP_USER_CHANGE
goto :ASK_USER

:SET_CUSTOM_USER
echo.
for /f "delims=" %%i in ('git config user.name 2^>nul') do set ORIGINAL_USER_NAME=%%i
for /f "delims=" %%i in ('git config user.email 2^>nul') do set ORIGINAL_USER_EMAIL=%%i

if "%ORIGINAL_USER_NAME%"=="" set ORIGINAL_USER_NAME=NICHT_GEFUNDEN
if "%ORIGINAL_USER_EMAIL%"=="" set ORIGINAL_USER_EMAIL=NICHT_GEFUNDEN

echo %WHITE%Aktueller Benutzer: %ORIGINAL_USER_NAME% ^<%ORIGINAL_USER_EMAIL%^>%RESET%
echo.

set /p GIT_USER_NAME="%WHITE%Neuer Git Benutzername: %RESET%"
set /p GIT_USER_EMAIL="%WHITE%Neue Git E-Mail: %RESET%"

if "%GIT_USER_NAME%"=="" goto :USER_ERROR
if "%GIT_USER_EMAIL%"=="" goto :USER_ERROR

echo.
echo %CYAN%Setze Git-Benutzer: %GIT_USER_NAME% ^<%GIT_USER_EMAIL%^>%RESET%
git config user.name "%GIT_USER_NAME%"
git config user.email "%GIT_USER_EMAIL%"

echo %YELLOW%Loesche gespeicherte Credentials fuer erneute Authentifizierung...%RESET%
cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://gitlab.com >nul 2>&1
cmdkey /delete:LegacyGeneric:target=git:https://bitbucket.org >nul 2>&1

set USE_CUSTOM_USER=1
echo %GREEN%Fertig. Neue Credentials werden bei der naechsten Operation abgefragt.%RESET%
echo.
goto :SKIP_USER_CHANGE

:USER_ERROR
echo %RED%[FEHLER] Benutzername und E-Mail duerfen nicht leer sein.%RESET%
if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
pause
exit /b 1

:SKIP_USER_CHANGE

REM --- 3. Pruefung: Sind wir in einem Git-Repo? ---
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo %RED%[FEHLER] Dieser Ordner ist kein Git-Repository.%RESET%
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

set FORCE_PUSH_REQUIRED=0

echo %CYAN%[1/5] Hole aktuelle Aenderungen vom Server...%RESET%
git pull
if errorlevel 1 (
    echo.
    echo %RED%[WARNUNG] Pull fehlgeschlagen!%RESET%
    echo %YELLOW%Moegliche Ursache: Das neue Repository ist leer oder hat eine unverknuepfte Historie.%RESET%
    echo.
    
    :ASK_FORCE
    set "CHOICE_FORCE="
    set /p "CHOICE_FORCE=%YELLOW%Moechten Sie trotzdem fortfahren und das Remote-Repository mit Ihrem lokalen Stand ueberschreiben (Force Push)? (J/N): %RESET%"
    if /i "%CHOICE_FORCE%"=="J" goto :DO_FORCE_PUSH
    if /i "%CHOICE_FORCE%"=="N" goto :ABORT_FORCE
    goto :ASK_FORCE

    :DO_FORCE_PUSH
    echo %YELLOW%Fortfahren mit lokalem Stand. Force-Push wird ausgefuehrt.%RESET%
    set FORCE_PUSH_REQUIRED=1
    goto :CONTINUE_AFTER_PULL

    :ABORT_FORCE
    echo %CYAN%Vorgang abgebrochen.%RESET%
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

:CONTINUE_AFTER_PULL
echo.
echo %CYAN%[2/5] Pruefe auf Aenderungen...%RESET%
git add -A
git diff --cached --quiet
if errorlevel 1 goto :HAS_CHANGES
echo.
echo %GREEN%Keine Aenderungen vorhanden - nichts zu committen.%RESET%
goto :PUSH_ONLY

:HAS_CHANGES
echo.
echo %CYAN%[3/5] Erstelle Commit...%RESET%
git commit -m "Automatisches Update: %date% %time%"
if errorlevel 1 (
    echo.
    echo %RED%[FEHLER] Beim Commit!%RESET%
    if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
    pause
    exit /b 1
)

:PUSH_ONLY
echo.
echo %CYAN%[4/5] Lade Aenderungen hoch...%RESET%

if %FORCE_PUSH_REQUIRED%==1 (
    echo.
    echo %RED%ACHTUNG: Fuehre Force-Push auf Branch 'main' aus!%RESET%
    echo.
    echo %YELLOW%DRUECKEN SIE EINE TASTE, um den Befehl jetzt auszufuehren:%RESET%
    echo %WHITE%git push --force --set-upstream origin main%RESET%
    pause
    
    git push --force --set-upstream origin main
    
    echo.
    echo %YELLOW%--- Git-Ausgabe beendet. Druecken Sie eine Taste, um fortzufahren ---%RESET%
    pause
    
    if errorlevel 1 (
        echo.
        echo %RED%[FEHLER] KRITISCHER FEHLER beim Force-Push!%RESET%
        if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
        pause
        exit /b 1
    )
) else (
    git push
    if errorlevel 1 (
        echo.
        echo %RED%[FEHLER] Beim Push!%RESET%
        if %USE_CUSTOM_USER%==1 call :RESTORE_CONFIG
        pause
        exit /b 1
    )
)

:SYNC_SUCCESS
echo.
echo %CYAN%[5/5] Status:%RESET%
git --no-pager status -sb

echo.
echo %MAGENTA%========================================%RESET%
echo %GREEN%  ERFOLG! Alle Aenderungen sind online.%RESET%
echo %MAGENTA%========================================%RESET%

if %USE_CUSTOM_USER%==1 (
    echo.
    :ASK_RESTORE
    set "CHOICE_RESTORE="
    set /p "CHOICE_RESTORE=%YELLOW%Moechten Sie die geaenderte Git-Benutzerkonfiguration beibehalten? (J/N): %RESET%"
    if /i "%CHOICE_RESTORE%"=="J" goto :END_SUCCESS
    if /i "%CHOICE_RESTORE%"=="N" call :RESTORE_CONFIG & goto :END_SUCCESS
    goto :ASK_RESTORE
)

:END_SUCCESS
pause
exit /b 0

:RESTORE_CONFIG
echo.
echo %CYAN%Stelle originale Git-Benutzerkonfiguration wieder her...%RESET%
if not "%ORIGINAL_USER_NAME%"=="NICHT_GEFUNDEN" git config user.name "%ORIGINAL_USER_NAME%"
if not "%ORIGINAL_USER_EMAIL%"=="NICHT_GEFUNDEN" git config user.email "%ORIGINAL_USER_EMAIL%"
echo %GREEN%Fertig.%RESET%
exit /b 0