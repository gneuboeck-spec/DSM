# SETUP_WINDOWS.md - Vollständige Installationsanleitung für Neue Rechner (Windows 10/11)

Diese Anleitung richtet die exakte Umgebung von Rechner A/B auf einem neuen Windows-Rechner ein. 
Bitte befolge die Schritte strikt in dieser Reihenfolge. Abweichungen führen zu versteckten Fehlern (insb. Tkinter, PATH-Konflikte mit LibreOffice/Inkscape, fehlende Signaturen).

## Phase 1: Vorbereitung & Bereinigung
Ziel: Eine saubere Basis schaffen, bevor irgendetwas installiert wird.

1. Windows Store Alias deaktivieren (KRITISCH!):
   - Öffne Einstellungen -> Apps -> Erweiterte App-Einstellungen -> Anwendungsalias.
   - Schalte 'python.exe' und 'python3.exe' auf AUS.
   - (Sonst fängt Windows jeden Aufruf von python ab und öffnet den Store, statt dein lokales Python zu starten.)

2. Alte Python-Reste entfernen (Falls bereits vorhanden):
   - Einstellungen -> Apps -> Installierte Apps.
   - Deinstalliere ALLE Einträge mit "Python" im Namen (inkl. Launcher).
   - Falls Fehler beim Deinstallieren ("Error 0x80070643"):
     a) Lade den "Microsoft Program Install and Uninstall troubleshooter" herunter.
     b) Wähle "Deinstallation", suche nach Python und lasse es bereinigen.
   - Lösche manuell folgende Ordner im Explorer:
     C:\Users\[DeinUser]\AppData\Local\Programs\Python
     C:\Program Files\Python313 (falls vorhanden)
     C:\Program Files (x86)\Python313 (falls vorhanden)

3. Neustart:
   - Starte den PC neu. Dies ist zwingend, um Registry-Caches und gesperrte DLLs freizugeben.

## Phase 2: Software-Installation (Grundgerüst)
Ziel: Die Kernkomponenten installieren.

4. Git for Windows installieren:
   - Download: https://git-scm.com/download/win
   - Installiere mit Standard-Einstellungen ("Use Git from the Windows Command Prompt").

5. Python 3.13.x (64-bit) installieren:
   - Download: https://www.python.org/downloads/windows/
   - Wähle die neueste stabile 3.13er Version (z.B. 3.13.16 oder höher). NICHT 3.14 oder 3.15!
   - Starte den Installer.
   - ✅ Hake ganz unten "Add python.exe to PATH" an.
   - Klicke auf "Customize installation".
   - Lass ALLE Häkchen aktiviert (besonders "tcl/tk and IDLE" und "pip"). Weiter.
   - Bei Advanced Options:
     - ❌ Haken bei "Install for all users" NICHT setzen (User-Installation ist sicherer).
     - ✅ Haken bei "Precompile standard library" setzen (empfohlen für Performance).
   - Installieren klicken.

6. Externe Tools installieren (Pflicht für volle Funktionalität):
   Diese Tools müssen in den Standardpfaden liegen, damit die Skripte sie finden.

   a) Siegfried:
      - Download: https://github.com/richardlehane/siegfried/releases
      - Entpacke sf.exe nach: C:\Program Files\Siegfried\

   b) ClamAV:
      - Download: https://www.clamav.net/downloads (Wähle .msi x64)
      - Installiere nach: C:\Program Files\ClamAV\

   c) FFmpeg:
      - Download: https://ffmpeg.org/download.html (Empfohlen: Gyan.dev Builds)
      - Entpacke bin-Ordner-Inhalt nach: C:\Program Files\FFmpeg\bin\

   d) ImageMagick:
      - Download: https://imagemagick.org/script/download.php#windows
      - Installiere nach: C:\Program Files\ImageMagick-[Version]-Q16-HDRI\
      - Wichtig: Während Installation "Add application directory to your system path" anhaken.

   e) Ghostscript:
      - Download: https://ghostscript.com/releases/gsdnld.html
      - Installiere nach: C:\Program Files\gs\gs[Version]\bin\
      - Wichtig: Während Installation "Add to PATH" anhaken.

   f) Inkscape (Optional, falls SVG/PDF Konvertierung genutzt wird):
      - Download: https://inkscape.org/release/
      - Installiere nach: C:\Program Files\Inkscape\bin\

   g) LibreOffice (Für Dokumentkonvertierungen):
      - Download: https://de.libreoffice.org/download/download/
      - Installiere nach: C:\Program Files\LibreOffice\program\

   h) ExifTool (Metadaten):
      - Download: https://exiftool.org/
      - Entpacke exiftool(-k).exe umbenannt zu exiftool.exe nach: C:\Program Files\ExifTool\

   i) DbxConv (Outlook PST/DBX Converter):
      - Download: https://www.ukrebs-software.de/english/dbxconv/dbxconv.html
      - Entpacke nach: C:\Program Files\dbxconv\

## Phase 3: System-PATH konfigurieren (KRITISCH!)
Ziel: Sicherstellen, dass Windows IMMER das richtige Python findet und die externen Tools aufrufen kann.

7. Umgebungsvariablen öffnen:
   - Win + R -> sysdm.cpl -> Erweitert -> Umgebungsvariablen.

8. Benutzer-Pfad bearbeiten:
   - Wähle im oberen Bereich ("Benutzervariablen für [User]") die Variable Path -> Bearbeiten.

9. Pfade hinzufügen UND priorisieren:
   Füge diese Pfade hinzu (falls noch nicht vorhanden) und schiebe sie GANZ NACH OBEN:
   
   a) C:\Users\[DeinUser]\AppData\Local\Programs\Python\Python313\
   b) C:\Users\[DeinUser]\AppData\Local\Programs\Python\Python313\Scripts\
   
   Stelle sicher, dass diese beiden Einträge über allen anderen stehen (insbesondere vor LibreOffice, Inkscape, WindowsApps).

10. Tool-Pfade prüfen/hinzufügen:
    Prüfe, ob folgende Pfade im PATH sind. Falls nicht, füge sie hinzu (Position egal, solange sie da sind):
    - C:\Program Files\Siegfried
    - C:\Program Files\ClamAV
    - C:\Program Files\FFmpeg\bin
    - C:\Program Files\ImageMagick-[Version]-Q16-HDRI
    - C:\Program Files\gs\gs[Version]\bin
    - C:\Program Files\Inkscape\bin
    - C:\Program Files\LibreOffice\program
    - C:\Program Files\ExifTool
    - C:\Program Files\dbxconv

11. Bestätigen und Neues CMD öffnen:
    - OK klicken.
    - Schließe alle alten CMD-Fenster.
    - Öffne ein brandneues CMD-Fenster.

## Phase 4: Repository & Python-Pakete
Ziel: Code holen und Bibliotheken installieren.

12. Repo klonen:
    cd /d C:\Users\[DeinUser]\Desktop
    if exist Skripte rmdir /s /q Skripte
    git clone https://github.com/ChristianeFritze/DSM.git Skripte
    cd Skripte

13. Pip sicherstellen (Workaround):
    Auch wenn "Add to PATH" gehakt wurde, erkennt cmd pip manchmal nicht sofort. Nutze diesen Befehl zur Sicherheit:
    python -m ensurepip --upgrade

14. Alle Anforderungen installieren:
    python -m pip install -r requirements.txt
    (Hinweis: Dies dauert einige Minuten. Warte bis "Successfully installed" erscheint. Ignoriere Warnungen bezüglich Scripts not on PATH.)

## Phase 5: Externe Tools initialisieren (SIGNATUREN!)
Ziel: Brunnhilde/Siegfried und ClamAV benötigen lokale Datenbanken, sonst stürzen sie ab.

15. Siegfried-Signaturen aktualisieren:
    Öffne ein CMD (beliebiges Verzeichnis) und führe aus:
    "C:\Program Files\Siegfried\sf.exe" -update
    
    Erwartete Ausgabe: "... writing C:\Users\[DeinUser]\AppData\Local\siegfried\default.sig ..."
    
    (Alternative: Falls kein Internetzugriff möglich ist, kopiere die Datei default.sig vom Referenzrechner A nach C:\Users\[DeinUser]\AppData\Local\siegfried\)

16. ClamAV-Signaturen aktualisieren:
    Öffne ein CMD als Administrator und führe aus:
    cd /d "C:\Program Files\ClamAV"
    freshclam.exe
    
    Erwartete Ausgabe: Update successful. Die Dateien main.cvd etc. sollten aktualisiert sein.

## Phase 6: Finaler Funktionstest

17. Verifizierung der Kernkomponenten:
    Führe diese Befehle im neuen CMD aus:
    
    :: 1. Python & Tkinter
    python -c "import tkinter; print('TKINTER OK')"
    
    :: 2. Brunnhilde
    python -c "import brunnhilde; print('BRUNNHILDE OK')"
    
    :: 3. Externe Tools gefunden?
    where sf
    where clamscan
    where ffmpeg
    where magick
    where gswin64c
    where soffice
    where inkscape
    where exiftool
    
    Jede Zeile sollte einen gültigen Pfad unter C:\Program Files\... zurückgeben.

18. Starttest des Menüs:
    cd /d C:\Users\[DeinUser]\Desktop\Skripte
    Start.bat
    
    Drücke d (Datenaufbereitung).
    Wähle Skript 1 (A_Analyse_Skript_Brunnhilde_Fixity.py).
    
    ERWARTUNG:
    - Es öffnet sich ein grafisches Fenster zur AC-Ordner-Auswahl (danke Tkinter!).
    - Nach Auswahl eines Testordners startet die Analyse.
    - Keine Fehlermeldung regarding signature files or missing executables.

## Wichtige Hinweise für die Wartung

- start.bat Dateien: Enthalten dynamische Suchlogik. Nicht hartcodiert anpassen. Sie funktionieren auf allen Rechnern gleich.
- Requirements: Immer nur vom Master-Rechner (A) via pip freeze > requirements.txt aktualisieren und pushen. Installiere nie Pakete manuell auf Zielrechnern, außer du testest etwas kurzfristig.
- Pfade: Alle externen Tools müssen zwingend in C:\Program Files\<ToolName> liegen, damit die automatische Erkennung in den Skripten funktioniert.
- PATH-Hygiene: Prüfe nach Updates von Inkscape/LibreOffice/Git, ob sich deren python.exe wieder vorgedrängelt hat. Dein User-Python (AppData...) muss immer an Position 1 und 2 im PATH stehen.
- Firewall/Antivirus: Manche Antivirenprogramme blockieren den automatischen Download der Siegfried/ClamAV Signaturen. Falls Step 15/16 fehlschlagen, deaktiviere AV kurzzeitig oder lade die .sig/.cvd Dateien manuell herunter und kopiere sie in die jeweiligen AppData-Ordner.