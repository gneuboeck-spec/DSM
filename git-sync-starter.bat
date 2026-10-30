@echo off
set "SCRIPT_DIR=%~dp0"
copy "%SCRIPT_DIR%git-sync.bat" "%TEMP%\git-sync-temp.bat" /Y >nul
call "%TEMP%\git-sync-temp.bat" "%SCRIPT_DIR%"
del "%TEMP%\git-sync-temp.bat" >nul