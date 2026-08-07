# D - Master-Konvertierungsskript (All-in-One)

Dieses Skript ist das zentrale Werkzeug zur Konvertierung und Normalisierung von Dateien für die Langzeitarchivierung. Es vereint die Funktionalitäten spezialisierter Einzel-Skripte für Audio, Bild, Text/Office und Video in einem einzigen, umfassenden Workflow. Das Ziel ist es, für jede unterstützte Quelldatei standardisierte, archivsichere Derivate zu erstellen.

Das Skript ist als integraler Bestandteil eines automatisierten Archivierungsworkflows konzipiert und wird über den Workflow Launcher mit dynamischen Pfaden gesteuert.

---

## Hauptfunktionen

* **Duale Normalisierungs-Strategie ("Digital Twin"):** Erzeugt für jede Quelldatei archivwürdige Formate (z. B. PDF/A, TIFF, WAV, MP3/MKV).
* **Intelligente Fehler-Zusammenfassung:** Falls Konvertierungen fehlschlagen, werden diese am Ende des Laufs exklusiv im Terminal (in Rot) und am Ende des Logfiles zusammengefasst. So müssen Fehler nicht mühsam im gesamten Log gesucht werden.
* **Fortschrittsanzeige:** Visualisiert den aktuellen Stand der Stapelverarbeitung inklusive Prozentangaben und einem dynamischen Fortschrittsbalken für Audio-Konvertierungen.
* **Windows-Pfad-Fix:** Enthält eine Speziallogik für LibreOffice (Nutzung eines temporären Verzeichnisses), um Probleme mit dem Windows-Zeichenlimit (260 Zeichen) bei tief verschachtelten Ordnerstrukturen zu umgehen.
* **Namenskonvention:** Alle Derivate folgen dem Schema `Originalname.originalendung.zielendung` (z. B. `Dokument.doc.pdf`), um die Provenienz lückenlos zu dokumentieren.
* **Dubletten-Schutz:** Erkennt bereits existierende abgeleitete Dateien und verhindert unnötige Neukonvertierungen.

---

## TREE-Struktur & Dateipfade

Das Skript arbeitet rekursiv innerhalb der Transfer-Stufe (Stufe 3):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 3_[Datenträger-ID]_for-transfer/
    ├── files/                                   <-- ARBEITSBEREICH (Quelle & Ziel)
    │   ├── Dokument.doc                         <-- Original
    │   ├── Dokument.doc.odt                     <-- Derivat (Bearbeitungskopie)
    │   ├── Dokument.doc.pdf                     <-- Derivat (Visuelle Erhaltung / PDF/A)
    │   ├── Audio.mp3                            <-- Original
    │   └── Audio.mp3.wav                        <-- Derivat (Archivmaster)
    ├── 3_[ID]_for-transfer_all-conversions.log  <-- ZIEL (Log mit exklusiver Fehlersummary am Ende)
    └── 3_[ID]_for-transfer_tree.txt             <-- ZIEL (Verzeichnisstruktur nach Konvertierung)
```

---

## Technische Voraussetzungen

Damit dieses Skript funktioniert, müssen folgende Programme installiert und im System-PATH verfügbar sein (oder fest hinterlegt):

1. **Python:** Version 3.10+ empfohlen.
2. **FFmpeg:** `ffmpeg.exe` und `ffprobe.exe` im System-PATH.
3. **ImageMagick:** `magick.exe` im System-PATH.
4. **Ghostscript:** `gswin64c.exe` im System-PATH.
5. **Inkscape:** Installiert unter `C:\Program Files\Inkscape\bin\inkscape.exe`.
6. **LibreOffice:** Installiert unter `C:\Program Files\LibreOffice\program\soffice.exe`.

---

## Ausführung

Das Skript wird im normalen Arbeitsablauf über den zentralen **Workflow Launcher** (`Workflow_Launcher_start.bat`) und das darauf folgende **Auswahlmenü** gestartet. Die benötigten Parameter (AC-Nummer und Datenträger-ID) werden dabei automatisch vom Menü an das Skript übergeben.

Für manuelle Tests oder Debugging kann das Skript auch direkt über die Kommandozeile aufgerufen werden. Es erwartet zwei Argumente: die AC-Nummer und die Datenträger-ID.

**Beispiel für einen manuellen Aufruf:**

```bat
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python "D_Master_Konvertierungsskript.py" %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1. **Validierung:** Prüfung der Pfade und Erreichbarkeit aller 6 externen Tools.
2. **Indexierung:** Alle relevanten Dateien im `files`-Ordner werden identifiziert und gefiltert (Ausschluss von bereits abgeleiteten Dateien).
3. **Verarbeitung:** Die Dateien werden nacheinander konvertiert (Audio → Bild → Text/Office → Video).
4. **Fehler-Reporting:** Nach Abschluss erfolgt die exklusive Auflistung aller Problemfälle im Terminal und im Log.
5. **Tree-Generierung:** Erstellung einer aktuellen `tree.txt` des Transfer-Ordners.
6. **Abschluss:** Das Skript bietet an, den `for-transfer`-Ordner direkt im Explorer zu öffnen.

---

## Detaillierte Hinweise zum Skriptverhalten

### Exakte Dateinamenskonvention für Derivate

Das Skript verwendet folgende Benennungsschemata:

| Dateityp | Original | Ziel-Derivat(e) |
|----------|----------|------------------|
| Audio (nicht MP3/WAV) | `datei.flac` | `datei.flac.mp3` und `datei.flac.wav` |
| Audio (MP3) | `datei.mp3` | nur `datei.mp3.wav` |
| Audio (WAV) | `datei.wav` | nur `datei.wav.mp3` |
| Bild (Raster) | `datei.jpg` | `datei.jpg.tiff` |
| Bild (Vektor/Ghostscript) | `datei.eps` | `datei.eps.pdf` |
| Text/Office | `datei.doc` | `datei.doc.odt` und `datei.doc.pdf` |
| PDF | `datei.pdf` | nur `datei.pdf.pdf` (via LibreOffice PDF/A-Export) |
| Video | `datei.mov` | `datei.mov.mkv` (FFV1/FLAC) |

### Ausschlusslogik für abgeleitete Dateien

Eine Datei wird **übersprungen**, wenn:
- Der Dateiname (ohne Endung) mit einer Quell-Endung endet **und** die aktuelle Endung nicht `.pdf` ist.
  - *Beispiel:* `dokument.doc.odt` → wird übersprungen (weil `dokument.doc` auf `.doc` endet).
  - *Ausnahme:* `dokument.doc.pdf` → wird verarbeitet (weil die Endung `.pdf` ist und dies das finale Archivderivat darstellt).

Zusätzlich werden Dateien übersprungen, deren Name mit `.` oder `~` beginnt (versteckte oder temporäre Dateien).

### Audio-Konvertierung mit Fortschrittsbalken

Bei Audio-Dateien wird die Dauer vorab mit `ffprobe` ermittelt. Während der Konvertierung zeigt ein dynamischer Fortschrittsbalken den Status an (z. B. `[########        ] 20.0%`).

### Verarbeitungsreihenfolge

Das Skript verarbeitet Dateien in folgender Priorität (definiert durch die Reihenfolge der `if/elif`-Abfragen):
1. Audio (`ext in SOURCE_AUDIO_EXTENSIONS`)
2. Bild (`ext in VALID_IMAGE_EXTENSIONS`)
3. Text/Office (`ext in VALID_TEXT_EXTENSIONS`)
4. Video (`ext in SOURCE_VIDEO_EXTENSIONS`)

### Fehler-Zusammenfassung (Error Summary)

Am Ende der Verarbeitung wird geprüft, ob Einträge in der globalen Liste `conversion_errors` vorhanden sind. Falls ja, wird eine formatierte, rot hervorgehobene Warnung ausgegeben, die Dateinamen und den konkreten Fehlergrund auflistet. Diese Zusammenfassung wird ebenfalls ans Ende der Log-Datei angehängt.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(destination_folder)`
- **macOS/Linux** → nicht implementiert (da `os.startfile` plattformspezifisch ist).

### Abhängigkeiten (zusätzlich)

Das Skript verwendet ausschließlich Module der Python-Standardbibliothek: `os`, `sys`, `subprocess`, `re`, `datetime`, `pathlib`, `shutil`, `time`, `glob`, `tempfile`. Es sind keine externen Python-Pakete (wie `pip install ...`) erforderlich.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT