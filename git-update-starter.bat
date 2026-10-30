@echo off
REM Speichere den Ordner, in dem diese Starter-Datei liegt
set "SCRIPT_DIR=%~dp0"

REM Kopiere die echte Bat-Datei in den Temp-Ordner
copy "%SCRIPT_DIR%git-update.bat" "%TEMP%\git-update-temp.bat" /Y >nul

REM Führe die Kopie aus und übergebe den echten Ordner als Parameter
call "%TEMP%\git-update-temp.bat" "%SCRIPT_DIR%"

REM Lösche die Kopie wieder
del "%TEMP%\git-update-temp.bat" >nul