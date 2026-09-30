@echo off
chcp 65001 >nul
echo ========================================
echo   Git Update: Pull, Add, Commit, Push
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Hole aktuelle Änderungen vom Server...
git pull

if %errorlevel% neq 0 (
    echo FEHLER beim Pull! Bitte Konflikte manuell lösen.
    pause
    exit /b 1
)

echo.
echo [2/4] Füge alle Änderungen hinzu...
git add -A

echo.
echo [3/4] Erstelle Commit...
git commit -m "Automatisches Update: %date% %time%"

echo.
echo [4/4] Lade Änderungen hoch...
git push

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ERFOLG! Alle Änderungen sind online.
    echo ========================================
) else (
    echo.
    echo FEHLER beim Push!
)

pause