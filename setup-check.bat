@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Setup-Check: Externe Tools

REM ==========================================================================
REM  setup-check.bat
REM  Prueft, ob alle externen Programme vorhanden sind, die die Skripte
REM  der Skriptsammlung benoetigen. Quelle: EXTERNE_TOOLS.md
REM  Ausgabe: Uebersicht mit OK / FEHLT je Programm
REM ==========================================================================

cd /d "%~dp0"

echo.
echo ========================================================
echo   SETUP-CHECK: Externe Tools und Python
echo ========================================================
echo.
echo   Quelle der Liste: EXTERNE_TOOLS.md
echo   Dieser Check aendert nichts. Er prueft nur.
echo.

set /a ok_count=0
set /a fail_count=0

REM ==========================================================================
REM  1. PYTHON
REM ==========================================================================
echo --------------------------------------------------------
echo   Python-Interpreter
echo --------------------------------------------------------

set "PYTHON_FOUND="
set "PYTHON_PATH="

if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_PATH=C:\Program Files\Python313\python.exe"
    set "PYTHON_FOUND=1"
)
if not defined PYTHON_FOUND (
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        set "PYTHON_FOUND=1"
    )
)
if not defined PYTHON_FOUND (
    where py >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_PATH=py -3.13"
        set "PYTHON_FOUND=1"
    )
)

if defined PYTHON_FOUND (
    echo   [OK]    Python gefunden:
    echo            !PYTHON_PATH!
    for /f "tokens=*" %%v in ('!PYTHON_PATH! --version 2^>^&1') do echo            %%v
    set /a ok_count+=1
) else (
    echo   [FEHLT] Python 3.13 wurde nicht gefunden.
    echo            Erwartet unter "C:\Program Files\Python313\" oder
    echo            "%%LOCALAPPDATA%%\Programs\Python\Python313\" oder via "py -3.13".
    set /a fail_count+=1
)
echo.

REM ==========================================================================
REM  2. PYTHON-PAKETE (requirements.txt)
REM ==========================================================================
echo --------------------------------------------------------
echo   Python-Pakete (requirements.txt)
echo --------------------------------------------------------

set "REQ_FILE=%~dp0requirements.txt"

if not exist "!REQ_FILE!" (
    echo   [SKIP]  requirements.txt nicht gefunden unter:
    echo            !REQ_FILE!
    goto :REQ_DONE
)

if not defined PYTHON_FOUND (
    echo   [SKIP]  Python nicht gefunden - Paket-Pruefung uebersprungen.
    goto :REQ_DONE
)

echo   [INFO]  Pruefe Pakete aus requirements.txt...
echo           ^(das kann einen Moment dauern^)
echo.
"!PYTHON_PATH!" -m pip install --dry-run -r "!REQ_FILE!" >nul 2>&1
if !errorlevel!==0 (
    echo   [OK]    Alle Pakete aus requirements.txt sind installiert.
    set /a ok_count+=1
) else (
    echo   [INFO]  Einige Pakete aus requirements.txt fehlen moeglicherweise.
    echo            Installation:
    echo                "!PYTHON_PATH!" -m pip install -r requirements.txt
    set /a fail_count+=1
)

:REQ_DONE
echo.

REM ==========================================================================
REM  3. EXTERNE PROGRAMME
REM ==========================================================================
echo --------------------------------------------------------
echo   Externe Programme
echo --------------------------------------------------------

call :CHECK_TOOL "Siegfried" "sf"
call :CHECK_TOOL "ClamAV" "clamscan"
call :CHECK_TOOL "FFmpeg" "ffmpeg"
call :CHECK_TOOL "FFprobe" "ffprobe"
call :CHECK_TOOL "ImageMagick" "magick"
call :CHECK_TOOL "Ghostscript" "gswin64c"
call :CHECK_TOOL "Inkscape" "inkscape"
call :CHECK_TOOL "LibreOffice" "soffice"
call :CHECK_TOOL "ExifTool" "exiftool"
call :CHECK_TOOL "DbxConv" "DbxConv.exe"
call :CHECK_TOOL "Hachoir" "hachoir-metadata"

echo.

REM ==========================================================================
REM  4. GIT
REM ==========================================================================
echo --------------------------------------------------------
echo   Git
echo --------------------------------------------------------
call :CHECK_TOOL "Git" "git"
echo.

REM ==========================================================================
REM  5. ZUSAMMENFASSUNG
REM ==========================================================================
echo ========================================================
echo   ZUSAMMENFASSUNG
echo ========================================================
echo.
echo   Gefunden:    !ok_count!
echo   Fehlend:     !fail_count!
echo.

if !fail_count! GTR 0 (
    echo   ^>^> Bitte die fehlenden Programme installieren.
    echo   ^>^> Details siehe EXTERNE_TOOLS.md
    echo   ^>^> Nach der Installation: neue Konsole oeffnen
    echo      ^(PATH-Aenderungen wirken erst in neuen Sitzungen^).
) else (
    echo   ^>^> Alle Programme gefunden. Setup ist vollstaendig.
)

echo.
pause
exit /b 0

REM ==========================================================================
REM  Hilfsfunktion: prueft ein Programm via "where"
REM  Parameter 1 = Anzeigename
REM  Parameter 2 = Aufruf-Name fuer "where"
REM ==========================================================================
:CHECK_TOOL
set "TOOL_LABEL=%~1"
set "TOOL_CMD=%~2"
set "FIRST_PATH="

for /f "delims=" %%p in ('where %TOOL_CMD% 2^>nul') do (
    if not defined FIRST_PATH set "FIRST_PATH=%%p"
)

if defined FIRST_PATH (
    echo   [OK]    %TOOL_LABEL% ^(%TOOL_CMD%^)
    echo            !FIRST_PATH!
    set /a ok_count+=1
) else (
    echo   [FEHLT] %TOOL_LABEL% ^(%TOOL_CMD%^)
    echo            ^(kein "where %TOOL_CMD%" Treffer im PATH^)
    set /a fail_count+=1
)
exit /b 0