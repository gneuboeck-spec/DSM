@echo off
chcp 65001 >nul
setlocal
title Git Sync (nur Pull)

cd /d "%~dp0"

echo ========================================
echo   Git Sync: Nur Pull (keine eigenen Aenderungen)
echo ========================================
echo.

REM --- Prüfung: Sind wir in einem Git-Repo? ---
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Dieser Ordner ist kein Git-Repository.
    pause
    exit /b 1
)

echo [1/2] Hole aktuelle Aenderungen vom Server...
git pull
if errorlevel 1 (
    echo.
    echo FEHLER beim Pull! Bitte Konflikte manuell loesen.
    pause
    exit /b 1
)

echo.
echo [2/2] Aktueller Stand:
git --no-pager status -sb

echo.
echo ========================================
echo   SYNC ABGESCHLOSSEN.
echo ========================================
pause