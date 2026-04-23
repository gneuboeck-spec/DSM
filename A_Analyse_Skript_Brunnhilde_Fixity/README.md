# Automatisches Analyse-Skript (Brunnhilde & Fixity)

Dieses Skript automatisiert die Analyse von Dateisammlungen mithilfe des digitalen Archivierungs-Tools Brunnhilde. Es berechnet kryptografische Prüfsummen (SHA-256), integriert Siegfried zur Dateiformat-Identifikation und nutzt optional ClamAV für Virenscans. 

Eine Besonderheit ist die Live-Überwachung des Virenscanners: Sollten die Virendefinitionen älter als 7 Tage sein, blendet das Skript sofort eine Update-Anleitung für Windows ein.

---

## Hauptfunktionen

* Vollständige Automatisierung: Führt den gesamten Analyseprozess von Brunnhilde mit einem einzigen Befehl aus.
* SHA-256 Fixity-Check: Berechnet automatisch SHA-256 Prüfsummen für alle Dateien im Quellverzeichnis und bettet diese direkt in den JSON-Bericht ein.
* Live-Virenschutz-Check: Überwacht den Status von ClamAV während der Ausführung und gibt bei veralteten Signaturen eine Anleitung zur Aktualisierung (freshclam) aus.
* Dynamische Pfad-Konfiguration: Alle Pfade werden zur Laufzeit basierend auf einer AC-Nummer und einer Datenträger-ID generiert.
* Zusammenfassender Bericht: Erstellt eine strukturierte JSON-Datei, die alle wichtigen Ergebnisse (Hashes, Formate, Warnungen, Virenfunde) bündelt.
* Windows-Optimierung: Enthält Workarounds für die manuelle Erstellung der tree.txt-Datei unter Windows.

---

## TREE-Struktur & Dateipfade

Das Skript arbeitet in der Extraktions-Phase (Stufe 2). Hier ist die Übersicht der betroffenen Pfade:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 2_[Datenträger-ID]_extracted-files/
    ├── files/                                  <-- QUELLE (Eingabe: Zu analysierende Dateien)
    │   └── ... (Ihre Nutzdaten)
    ├── 2_[ID]_extracted-files_brunnhilde/      <-- ZIEL (Ordner mit Detailberichten)
    ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- ZIEL (Zentrale Hash- & Formatliste)
    └── 2_[ID]_extracted-files_tree.txt         <-- ZIEL (Verzeichnisstruktur als Text)

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
    CLAMAV_DIR = r"C:\Program Files\ClamAV"

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
3. Brunnhilde-Ausführung: Analyse der Dateiformate und Live-Check des ClamAV-Status.
4. Tree-Workaround: Erstellung der tree.txt (Verzeichnisstruktur).
5. Parsing & JSON: Zusammenfassung aller Daten in einer JSON-Datei.
6. Finalisierung: Verschieben der Berichte in den Hauptordner des Datenträgers.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT