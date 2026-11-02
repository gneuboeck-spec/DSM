# Skriptsammlung WIENBIBLIOTHEK

Zentrale Arbeitsumgebung für die digitale Datenrettung und Langzeitarchivierung. Die Skriptsammlung ist modular aufgebaut und in drei Hauptbereiche unterteilt, die über ein zentrales Startmenü erreichbar sind.

## Gesamtstruktur

    Skriptsammlung/
    |-- Start.bat                          <-- Haupt-Startpunkt (Doppelklick hier)
    |-- Menu.py                            <-- Zentrales Auswahlmenü
    |-- requirements.txt                   <-- Python-Abhängigkeiten (optional, siehe unten)
    |-- EXTERNE_TOOLS.md                   <-- Externe Programme (nicht über pip installierbar)
    |-- git-sync.bat                       <-- Nur Pull (Stand holen) mit erweiterten Sicherheitsfunktionen
    |-- git-update.bat                     <-- Pull + Commit + Push (Änderungen hochladen) mit intelligenter Fehlerbehandlung
    |-- git-sync-starter.bat               <-- Starter für git-sync.bat (vermeidet Dateisperren bei Selbst-Updates)
    |-- git-update-starter.bat             <-- Starter für git-update.bat (vermeidet Dateisperren bei Selbst-Updates)
    |-- README.md                          <-- Diese Datei
    |
    |-- Datenaufbereitung/                 <-- Haupt-Workflow (Skripte A-L)
    |   |-- Start.bat
    |   |-- Menu.py
    |   |-- requirements.txt
    |   |-- README.md
    |   |-- A_Analyse_Skript_Brunnhilde_Fixity/
    |   |-- B_XML_Zusammenfassungs_Generator_content/
    |   |-- C_Reparatur_von_Dateiendungen/
    |   |-- D_Master_Konvertierungsskript/
    |   |-- E_VL_Bereinigung_Vorbereitung_Archivierung/
    |   |-- F_Zwischendateien_ODF_WAV_löschen/
    |   |-- G_Metadata_Extraction_Indexing_filetrove/
    |   |-- H_VL_Export/
    |   |-- I_PREMIS_XML_Generator/
    |   |-- J_Staging-Workflow/
    |   |-- K_Master_Index_Metadaten_Generator_LZA/
    |   `-- L_BagIt_METS_TAR_Archivierung/
    |
    |-- Textdokumente_vergleichen/         <-- Vergleichs-Modul
    |   |-- Start.bat
    |   |-- Menu.py
    |   |-- requirements.txt
    |   |-- README.md
    |   |-- 01_Dateiendungen_reparieren/
    |   |-- 02_Duplikatenfinder/
    |   |-- 03_Analyse_Skript_Brunnhilde_Fixity/
    |   |-- 04_Bereinigungsskript/
    |   |-- 05_Dokumente_vergleichen/
    |   |-- 06_KI_Analyse/
    |   `-- 07_Visualisierung/
    |
    `-- Tools/                             <-- Hilfs-Skripte
        |-- Start.bat
        |-- Menu.py
        |-- requirements.txt
        |-- README.md
        `-- PREMIS_Validierung/

## Aufbau eines Skript-Ordners

Jedes einzelne Skript ist in einem eigenen Unterordner gekapselt. Dieser enthält immer eine `README.md` mit der Dokumentation des Skripts sowie einen Unterordner `win/`, in dem sich die eigentliche Python-Datei befindet. Der Name der Python-Datei entspricht dabei dem Namen des übergeordneten Skript-Ordners.

Beispiel am Skript `A_Analyse_Skript_Brunnhilde_Fixity`:

    A_Analyse_Skript_Brunnhilde_Fixity/
    |-- README.md                          <-- Dokumentation des Skripts
    `-- win/
        `-- A_Analyse_Skript_Brunnhilde_Fixity.py   <-- Ausführbare Python-Datei

Dieses Muster gilt einheitlich für alle Skripte in allen drei Hauptbereichen.

## Die drei Hauptbereiche

### 1. Datenaufbereitung

Enthält die komplette Pipeline für die digitale Datenrettung und Langzeitarchivierung. Die Skripte A bis L bilden den Master-Workflow.

    Datenaufbereitung/
    |-- Start.bat
    |-- Menu.py
    |-- requirements.txt
    |-- README.md
    |-- A_Analyse_Skript_Brunnhilde_Fixity/
    |   |-- README.md
    |   `-- win/
    |       `-- A_Analyse_Skript_Brunnhilde_Fixity.py
    |-- B_XML_Zusammenfassungs_Generator_content/
    |   |-- README.md
    |   `-- win/
    |       `-- B_XML_Zusammenfassungs_Generator_content.py
    |-- C_Reparatur_von_Dateiendungen/
    |   |-- README.md
    |   `-- win/
    |       `-- C_Reparatur_von_Dateiendungen.py
    |-- D_Master_Konvertierungsskript/
    |   |-- README.md
    |   `-- win/
    |       `-- D_Master_Konvertierungsskript.py
    |-- E_VL_Bereinigung_Vorbereitung_Archivierung/
    |   |-- README.md
    |   `-- win/
    |       `-- E_VL_Bereinigung_Vorbereitung_Archivierung.py
    |-- F_Zwischendateien_ODF_WAV_löschen/
    |   |-- README.md
    |   `-- win/
    |       `-- F_Zwischendateien_ODF_WAV_löschen.py
    |-- G_Metadata_Extraction_Indexing_filetrove/
    |   |-- README.md
    |   `-- win/
    |       |-- G_Metadata_Extraction_Indexing_filetrove.py
    |       `-- rules.yar                  <-- YARA-Regeln für Dateiformat-Identifizierung
    |-- H_VL_Export/
    |   |-- README.md
    |   `-- win/
    |       `-- H_VL_Export.py
    |-- I_PREMIS_XML_Generator/
    |   |-- README.md
    |   |-- premis-v3-0.xsd                <-- Offizielles PREMIS v3 XML-Schema (Library of Congress)
    |   `-- win/
    |       `-- I_PREMIS_XML_Generator.py
    |-- J_Staging-Workflow/
    |   |-- README.md
    |   `-- win/
    |       `-- J_Staging-Workflow.py
    |-- K_Master_Index_Metadaten_Generator_LZA/
    |   |-- README.md
    |   `-- win/
    |       |-- K_Master_Index_Metadaten_Generator_LZA.py
    |       `-- rules.yar                  <-- YARA-Regeln für Dateiformat-Identifizierung
    `-- L_BagIt_METS_TAR_Archivierung/
        |-- README.md
        `-- win/
            `-- L_BagIt_METS_TAR_Archivierung.py

**Start:** Hauptmenü → `D`
**Parameter:** AC-Nummer und Datenträger-ID

### 2. Textdokumente_vergleichen

Eigenständiges Modul zur syntaktischen und semantischen Analyse von Textdokumenten.

    Textdokumente_vergleichen/
    |-- Start.bat
    |-- Menu.py
    |-- requirements.txt
    |-- README.md
    |-- 01_Dateiendungen_reparieren/
    |   |-- README.md
    |   `-- win/
    |       `-- 01_Dateiendungen_reparieren.py
    |-- 02_Duplikatenfinder/
    |   |-- README.md
    |   `-- win/
    |       `-- 02_Duplikatenfinder.py
    |-- 03_Analyse_Skript_Brunnhilde_Fixity/
    |   |-- README.md
    |   `-- win/
    |       `-- 03_Analyse_Skript_Brunnhilde_Fixity.py
    |-- 04_Bereinigungsskript/
    |   |-- README.md
    |   `-- win/
    |       `-- 04_Bereinigungsskript.py
    |-- 05_Dokumente_vergleichen/
    |   |-- README.md
    |   `-- win/
    |       `-- 05_Dokumente_vergleichen.py
    |-- 06_KI_Analyse/
    |   |-- README.md
    |   `-- win/
    |       `-- 06_KI_Analyse.py
    `-- 07_Visualisierung/
        |-- README.md
        `-- win/
            `-- 07_Visualisierung.py

**Start:** Hauptmenü → `T`
**Parameter:** Eingabe- und Ausgabe-Verzeichnis (über GUI-Dialog)

### 3. Tools

Sammlung von Hilfs-Skripten und Utilities.

    Tools/
    |-- Start.bat
    |-- Menu.py
    |-- requirements.txt
    |-- README.md
    `-- PREMIS_Validierung/
        |-- README.md
        |-- premis-v3-0.xsd                <-- Offizielles PREMIS v3 XML-Schema
        `-- win/
            `-- PREMIS_Validierung.py

**Start:** Hauptmenü → `O`

## Schnellstart

1. **Doppelklick auf `Start.bat`** im Hauptverzeichnis
2. Das Hauptmenü öffnet sich mit drei Bereichen:
   - **D** - Datenaufbereitung (Haupt-Workflow)
   - **T** - Textdokumente_vergleichen
   - **O** - Tools
3. Buchstaben eingeben, um den gewünschten Bereich zu starten
4. Im gewählten Bereich werden alle verfügbaren Skripte aufgelistet
5. Nach Beenden des Unterbereichs kehrt man automatisch zum Hauptmenü zurück

## Zentrale Dateien im Root

### Start.bat

Der Einstiegspunkt der Arbeitsumgebung. Wechselt in das eigene Verzeichnis, prüft ob `Menu.py` vorhanden ist und startet das Hauptmenü. Der zu verwendende Python-Interpreter wird dynamisch ermittelt (siehe Abschnitt "Python-Interpreter" unten).

### Menu.py

Das zentrale Auswahlmenü. Zeigt die drei Hauptbereiche an und startet beim Auswählen die jeweilige `Start.bat` des gewählten Unterordners als separaten Prozess. Nach Beenden des Unterbereichs kehrt man automatisch zum Hauptmenü zurück.

### requirements.txt

Enthält die Python-Abhängigkeiten für das gesamte Projekt. Installation:

    pip install -r requirements.txt

Wichtig: Diese Datei enthält **nur Python-Pakete**. Externe Programme (Siegfried, FFmpeg, LibreOffice usw.) sind **nicht** hier gelistet, sondern in `EXTERNE_TOOLS.md`.

### EXTERNE_TOOLS.md

Zentrale Dokumentation aller externen Programme, die von den Skripten aufgerufen werden und **nicht** über `pip` installierbar sind (z. B. Siegfried, ClamAV, FFmpeg, ImageMagick, Ghostscript, Inkscape, LibreOffice, ExifTool, DbxConv, Hachoir).

Die Datei enthält:

- Referenz-Rechner und seine Installationspfade
- Versionen und Download-Quellen
- Hinweise zu PATH-Pflicht und Fallback-Pfaden
- Empfohlene Reihenfolge beim Aufsetzen eines neuen Rechners
- Übersicht, welche Programme welches Skript benötigt

Diese Dokumentation ist die **verbindliche Referenz** für das Einrichten neuer Rechner.

### git-sync.bat

Sicheres Skript zum Holen des aktuellen Standes vom Server (nur `git pull`). Es ist auf allen Rechnern der Standard, auf denen nur mit der Skriptsammlung gearbeitet wird, da es keine eigenen Änderungen hochladen kann.

**Erweiterte Sicherheitsfunktionen:**
- **Automatische Sicherung:** Erstellt vor der Operation optional ein Backup der lokalen Dateien (ohne den `.git`-Ordner) in einem zeitgestempelten Ordner im übergeordneten Verzeichnis.
- **Optionale URL-Änderung:** Ermöglicht das sichere Umleiten des Repositories auf eine neue Remote-URL (z. B. bei einem Umzug).
- **Optionaler Benutzerwechsel:** Ermöglicht das temporäre Ändern von `user.name` und `user.email` für Commits. Gespeicherte Credentials werden dabei gezielt gelöscht, um eine saubere, erneute Authentifizierung (z. B. via Browser) zu erzwingen.
- **Sicherer Abbruch:** Falls der Pull fehlschlägt (z. B. wegen unverknüpfter Historien bei einem neuen Repository), bricht das Skript sicher ab und führt **keinen** Push aus.

### git-update.bat

Automatisiertes Git-Update-Skript zum Hochladen eigener Änderungen. Führt folgende Schritte aus:

1. **Pull**: Holt aktuelle Änderungen vom Server.
2. **Add**: Fügt alle lokalen Änderungen hinzu (`git add -A`).
3. **Commit**: Erstellt Commit mit Zeitstempel (nur wenn es tatsächlich Änderungen gibt).
4. **Push**: Lädt Änderungen hoch.

**Erweiterte Sicherheits- und Komfortfunktionen:**
- **Automatische Sicherung:** Wie bei `git-sync.bat` wird optional ein vollständiges Backup vor Änderungen erstellt.
- **Optionale URL- & Benutzeränderung:** Bietet dieselben sicheren Umschaltmöglichkeiten für Remote-URL und Git-Identität wie das Sync-Skript.
- **Intelligenter Force-Push-Fallback:** Erkennt das Skript, dass `git pull` fehlschlägt (typischerweise, weil das Ziel-Repository auf dem Server neu und leer ist oder eine unverknüpfte Historie hat), bricht es nicht einfach ab. Stattdessen warnt es den Benutzer und bietet einen geführten, sicheren `git push --force --set-upstream origin main` an, um das leere Remote-Repository mit dem lokalen Stand zu initialisieren. Dies verhindert stille Abstürze und macht Repository-Umzüge kinderleicht.

**Verwendung:**
- Auf dem Test-Rechner (Rechner A), um geprüfte Änderungen zentral bereitzustellen.
- Auf anderen Rechnern nur dann, wenn dort bewusst Änderungen gepusht werden sollen.

### git-sync-starter.bat & git-update-starter.bat

Um das Problem zu umgehen, dass Windows eine laufende `.bat`-Datei sperrt und sie sich daher nicht selbst per `git pull` aktualisieren kann (das sogenannte "Henne-Ei-Problem"), wurden diese Starter-Skripte eingeführt.

**Funktionsweise:**
1. Die Starter-Datei kopiert die eigentliche `git-sync.bat` oder `git-update.bat` in den temporären Windows-Ordner (`%TEMP%`).
2. Sie führt die Kopie von dort aus.
3. Da die Originaldatei im Projektordner während der Ausführung nicht gesperrt ist, kann sie von `git pull` problemlos überschrieben werden, falls sie auf dem Server aktualisiert wurde.
4. Nach der Ausführung wird die temporäre Kopie automatisch gelöscht.

**Wichtig:** Auf allen Rechnern sollten ab sofort **ausschließlich** die `*-starter.bat` Dateien per Doppelklick gestartet werden, um einen reibungslosen, sperrfreien Workflow über mehrere Rechner hinweg zu gewährleisten.

## Python-Interpreter

Die Skriptsammlung nutzt eine Fallback-Kette, um auf jedem Rechner den passenden Python-Interpreter zu finden. Die `Start.bat`-Dateien suchen in dieser Reihenfolge:

1. `C:\Program Files\Python313\python.exe` (systemweite Installation)
2. `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (User-Installation)
3. `py -3.13` (Python-Launcher)

Die `Menu.py`-Dateien verwenden `sys.executable`, um die Subskripte mit demselben Interpreter zu starten, mit dem das Menü selbst läuft. Damit ist es egal, wo Python installiert ist – alle Skripte laufen konsistent mit derselben Installation.

## Externe Abhängigkeiten

Neben den Python-Paketen aus `requirements.txt` benötigen einige Skripte **eigenständige Programme**, die nicht über `pip` installiert werden können. Sie müssen separat installiert und – je nach Programm – im Windows-PATH eingetragen sein.

Die vollständige Liste mit Pfaden, Versionen, Quellen und Hinweisen ist in der Datei **`EXTERNE_TOOLS.md`** dokumentiert. Dort steht für jedes Programm:

- Aufruf-Name (`sf`, `clamscan`, `ffmpeg`, `magick`, `gswin64c`, `inkscape`, `soffice`, `exiftool`, `DbxConv`, `hachoir-metadata`)
- Installationspfad auf dem Referenzrechner (A)
- Version
- Download-Quelle
- Ob eine PATH-Eintragung zwingend erforderlich ist oder ein Fallback-Pfad im Skript existiert

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

## Systemvoraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher
- **Git** (für Versionskontrolle)
- **Externe Programme** gemäß `EXTERNE_TOOLS.md`

## Aufsetzen auf einem neuen Rechner

1. **Python 3.13** installieren (systemweit oder als User-Installation).
2. **Git** installieren.
3. Repository klonen oder vorhandenen Ordner kopieren.
4. Python-Pakete installieren:

       pip install -r requirements.txt

5. **Externe Programme installieren** – gemäß der Anleitung in `EXTERNE_TOOLS.md`. Wenn möglich, dieselben Versionen und Installationspfade wie auf dem Referenzrechner (A).
6. **Neue Konsole öffnen**, damit PATH-Änderungen wirksam werden.
7. **Optional: `setup-check.bat` ausführen** – prüft, welche der externen Programme auf diesem Rechner fehlen.
8. `git-sync-starter.bat` ausführen, um den aktuellen Stand zu holen (bei erstem Umzug ggf. die URL-Änderungsfunktion nutzen).
9. `Start.bat` doppelklicken und Bereiche testen.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT