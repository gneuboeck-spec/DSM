@echo off
chcp 65001 >nul
setlocal
title Git Update (Pull, Add, Commit, Push)

cd /d "%~dp0"

echo ========================================
echo   Git Update: Pull, Add, Commit, Push
echo   ----------------------------------------
echo   Verwendet auf Rechner A (Test-Rechner).
echo   Auf anderen Rechnern bitte nur dann,
echo   wenn dort bewusst Aenderungen gepusht
echo   werden sollen.
echo ========================================
echo.

REM --- Prüfung: Sind wir in einem Git-Repo? ---
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Dieser Ordner ist kein Git-Repository.
    pause
    exit /b 1
)

echo [1/5] Hole aktuelle Aenderungen vom Server...
git pull
if errorlevel 1 (
    echo.
    echo FEHLER beim Pull! Bitte Konflikte manuell loesen.
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
pause