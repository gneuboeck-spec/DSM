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
* Windows-Optimierung: Enthält Workarounds für die manuelle Erstellung der tree.txt-Datei unter Windows (CMD-basiert).

---

## TREE-Struktur & Dateipfade

Das Skript erwartet die Datenstruktur unter ~/Documents/data/. Die Ergebnisse werden im Extraktions-Ordner (Stufe 2) abgelegt:

```text
[AC-Nummer]/[Datenträger-ID]/
└── 2_[Datenträger-ID]_extracted-files/
    ├── files/                                  <-- QUELLE (Eingabe: Zu analysierende Dateien)
    │   └── ... (Ihre Nutzdaten)
    ├── 2_[ID]_extracted-files_brunnhilde/      <-- DETAIL-BERICHTE (Brunnhilde Output-Ordner)
    ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- ZIEL (Zentrale Hash- & Formatliste)
    └── 2_[ID]_extracted-files_tree.txt         <-- ZIEL (Verzeichnisstruktur)
```
---

## Technische Voraussetzungen

Stellen Sie sicher, dass folgende Programme installiert sind:

1. Python 3.10+ (inkl. Modul Brunnhilde: pip install brunnhilde)
2. Siegfried (identifiziert Dateiformate via PRONOM)
3. ClamAV (optional für Virenscans)

---

## Konfiguration im Skript

Passen Sie die Installationspfade der Tools am Anfang der Python-Datei an:

SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
CLAMAV_DIR = r"C:\Program Files\ClamAV"

---

## Ausführung

Das Skript benötigt zwingend zwei Argumente: die AC-Nummer und die Datenträger-ID. Diese können über eine start.bat übergeben werden:

@echo off
set AC_NUMBER=AC_12345
set DISK_ID=ID_001
python analyse_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1. Validierung: Prüfung von Argumenten, Ordnern sowie der Existenz von sf.exe und clamscan.exe.
2. SHA-256 Hashing: Erstellt Prüfsummen für alle Dateien im Ordner files/.
3. Brunnhilde-Ausführung: Analyse der Dateiformate und Echtzeit-Überwachung des ClamAV-Status (Warnung bei veralteten Signaturen).
4. Tree-Workaround: Manuelle Erstellung der tree.txt innerhalb des Berichtsordners.
5. Parsing & JSON: Zusammenfassung der CSV-Ergebnisse (Formate, Warnungen, Viren) in der zentralen JSON-Datei.
6. Finalisierung: Verschieben der tree.txt in die übergeordnete Ebene (2_[ID]_extracted-files).
7. Abschluss: Optionale Abfrage, ob der Zielordner im Windows Explorer geöffnet werden soll.

---


## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Eingabestruktur (streng erforderlich)

Das Skript setzt zwingend folgende Ordnerstruktur voraus. Die zu analysierenden Dateien MÜSSEN bereits in `files/` liegen:

~/Documents/data/[AC-Nummer]/[Datenträger-ID]/2_[DatentrÃ¤ger-ID]_extracted-files/files/
  └── (Ihre zu analysierenden Dateien und Unterordner)

Fehlt dieses `files/`-Verzeichnis oder ist es leer, bricht das Skript mit einer Fehlermeldung ab.

### Fehlerfälle und Abbruchbedingungen

Das Skript prüft beim Start:
- Existenz von `files/` und dem übergeordneten `…_extracted-files/`
- `sf.exe` im konfigurierten `SIEGFRIED_DIR` (falls angegeben)
- `clamscan.exe` im konfigurierten `CLAMAV_DIR` (falls angegeben)

Bei Fehlern erscheint eine rote Fehlermeldung (`\033[91m`), das Skript wird mit `return None` bzw. `sys.exit(1)` beendet.

### Temporäres Verzeichnis für Brunnhilde

Wenn in der Funktion `extract_brunnhilde_info` der Parameter `brunnhilde_output_dir` leer ist oder `None`, erzeugt das Skript ein temporäres Verzeichnis (mit `tempfile.mkdtemp`). Dieses wird nach der Analyse **automatisch gelöscht**. Der Regelfall (aus `setup_and_validate_analysis_paths`) verwendet jedoch ein festes Verzeichnis.

### Pfad-Erweiterung für Brunnhilde

Brunnhilde wird mit erweiterter Umgebungsvariable `PATH` aufgerufen: Die Ordner von Siegfried und ClamAV werden vorne an `PATH` angehängt. Dadurch findet Brunnhilde die Kommandozeilenwerkzeuge, auch wenn sie nicht systemweit installiert sind.

### Exakter ClamAV-Live-Check

Das Skript überwacht die Ausgabe von Brunnhilde **zeilenweise** auf die Zeichenkette `"older than 7 days"` (Groß-/Kleinschreibung wird ignoriert). Sobald diese Zeile erscheint, wird sofort eine Update-Anleitung ausgegeben – **ohne dass der Scan abbricht**.

### SHA-256-Fehlerbehandlung

`calculate_sha256()` fängt alle Ausnahmen ab und schreibt dann `f"Error: {str(e)}"` in das SHA-256-Feld. Im JSON erscheint also kein korrekter Hash, sondern ein Fehlertext.

### Aufbau der erzeugten JSON-Datei

Die finale `*-summary.json` enthält folgende Felder:

| Feld | Inhalt |
|------|--------|
| `file_fixity_sha256` | Liste von `{"file": "relativer Pfad", "sha256": "Hash oder Fehlertext"}` |
| `brunhilde_format_summary` | JSON-String des `formats.csv` von Brunnhilde |
| `brunhilde_mime_type_summary` | JSON-String des `mimetypes.csv` |
| `structured_siegfried_warnings` | Dictionary: Dateipfad → Liste der Warnungszeilen aus `siegfried_warnings.csv` |
| `structured_unidentified_files` | Liste der Dateipfade aus `unidentified.csv` |
| `brunhilde_clamav_infected_files` | Anzahl infizierter Dateien (als String) aus `virus_scan_log.txt` |
| `brunhilde_clamav_virus_details` | JSON-String der Liste `[Datei, Virusname]` (nur wenn Infizierte > 0) |
| `brunhilde_clamav_status` | Nur wenn kein Log gefunden: `"Kein virus_scan_log.txt gefunden."` |

### Manuelle `tree.txt`-Erstellung (Windows)

Das Skript verwendet nicht `tree.exe`, sondern direkt `cmd /c tree "…" /A /F > "tree.txt"`. Dies wird unabhängig vom Erfolg von Brunnhilde ausgeführt. Falls der Befehl fehlschlägt, erscheint eine Warnung, das Skript wird aber **fortgesetzt**.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n)`. Bei `j`:
- **Windows** → `os.startfile(destination_folder)`
- **macOS** → `open`
- **Linux/andere** → `xdg-open`

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT