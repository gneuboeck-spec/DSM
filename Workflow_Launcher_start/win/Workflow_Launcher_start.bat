@echo off
title Python Arbeitsumgebung

REM --- Fragt einmalig nach den Werten und startet dann die Arbeitsumgebung ---

echo --- Bitte geben Sie die initialen Werte ein ---
set /p ac_number="AC-Nummer eingeben: "
set /p disk_id="Datentraeger-ID eingeben: "
echo Werte wurden gespeichert. Starte die Arbeitsumgebung...
echo.


REM --- DIES IST IHR FUNKTIONIERENDER BEFEHLSBLOCK, ERWEITERT UM DIE ÜBERGABE DER WERTE ---
REM Startet ein neues, sauberes CMD-Fenster und übergibt ihm die exakte
REM Befehlskette, die auf Ihrem System nachweislich funktioniert.

start "Python Arbeitsumgebung" cmd /k "cd /d "C:\Users\digit\Desktop\Skripte" && C:\Users\digit\.venv\Scripts\activate && echo. && echo KONTROLLPUNKT: Die VENV ist aktiv. Druecken Sie eine Taste, um das Menue zu starten. && pause > nul && python menu.py "%ac_number%" "%disk_id%""