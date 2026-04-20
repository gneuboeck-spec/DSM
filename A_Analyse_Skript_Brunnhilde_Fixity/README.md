# Automatisches Analyse-Skript (Brunnhilde & Fixity)

Dieses Skript automatisiert die Analyse von Dateisammlungen mithilfe des digitalen Archivierungs-Tools Brunnhilde. Es berechnet kryptografische Prüfsummen (SHA-256), integriert Siegfried zur Dateiformat-Identifikation und nutzt optional ClamAV für Virenscans.

Das Skript ist für die wiederholte Anwendung in einer vordefinierten Ordnerstruktur konzipiert und wird über Kommandozeilenargumente gesteuert, typischerweise durch eine Start-Datei (start.bat).

---

## Hauptfunktionen

* Vollständige Automatisierung: Führt den gesamten Analyseprozess von Brunnhilde mit einem einzigen Befehl aus.
* SHA-256 Fixity-Check: Berechnet automatisch SHA-256 Prüfsummen für alle Dateien im Quellverzeichnis und bettet diese direkt in den JSON-Bericht ein.
* Dynamische Pfad-Konfiguration: Alle Pfade werden zur Laufzeit basierend auf einer AC-Nummer und einer Datenträger-ID generiert.
* Integration externer Tools: Nutzt Siegfried (Format-Erkennung) und ClamAV (Virenscan) innerhalb des Brunnhilde-Workflows.
* Zusammenfassender Bericht: Erstellt eine strukturierte JSON-Datei, die alle wichtigen Ergebnisse (Hashes, Formate, Warnungen, Virenfunde) bündelt.
* Windows-Optimierung: Enthält Workarounds für die manuelle Erstellung der tree.txt-Datei unter Windows.

---

## Technische Voraussetzungen

Stellen Sie sicher, dass folgende Programme installiert sind:

1. Python 3.10+ (inkl. Modul Brunnhilde: pip install brunnhilde)
2. Siegfried (identifiziert Dateiformate via PRONOM)
3. ClamAV (optional für Virenscans)

---

## Konfiguration im Skript

Passen Sie die Pfade am Anfang der Python-Datei an:

    SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
    CLAMAV_DIR = ""  # Optional, z. B.: r"C:\Program Files\ClamAV"

### Erwartete Ordnerstruktur

Das Skript erwartet die Daten im Documents-Ordner unter:
Documents/data/[AC-Nummer]/[Datenträger-ID]/2_[Datenträger-ID]_extracted-files/files/

---

## Ausführung

Nutzen Sie eine start.bat, um die Argumente (AC-Nummer und Datenträger-ID) zu übergeben:

    @echo off
    set AC_NUMBER=AC_12345
    set DISK_ID=ID_001
    python analyse_skript.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Prüfung von Argumenten, Ordnern und sf.exe.
2. SHA-256 Hashing: Erstellt Prüfsummen für alle Dateien im Ordner files/.
3. Brunnhilde-Ausführung: Analyse der Dateiformate.
4. Tree-Workaround: Erstellung der tree.txt (Verzeichnisstruktur).
5. Parsing & JSON: Zusammenfassung aller Daten in einer JSON-Datei.
6. Finalisierung: Verschieben der Berichte in den Hauptordner des Datenträgers.
7. Abschluss: Option zum Öffnen des Zielordners im Explorer.

---

## Generierte Berichte

Im Ordner 2_[Datenträger-ID]_extracted-files/ finden Sie nach Abschluss:

* 2_[Datenträger-ID]_extracted-files_brunnhilde/: Der vollständige Berichtsordner.
* 2_[Datenträger-ID]_extracted-files_brunnhilde-summary.json: Die zentrale JSON-Zusammenfassung (inkl. Hashes).
* 2_[Datenträger-ID]_extracted-files_tree.txt: Die Verzeichnisstruktur als Textdatei.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT