# Master-Konvertierungsskript (All-in-One)

Dieses Skript ist das zentrale Werkzeug zur Konvertierung und Normalisierung von Dateien für die Langzeitarchivierung. Es vereint die Funktionalitäten spezialisierter Einzel-Skripte für Audio, Bild, Text/Office und Video in einem einzigen, umfassenden Workflow. Das Ziel ist es, für jede unterstützte Quelldatei standardisierte, archivsichere Derivate zu erstellen.

Das Skript ist als integraler Bestandteil eines automatisierten Archivierungsworkflows konzipiert und wird über eine Start-Datei (start.bat) mit dynamischen Pfaden gesteuert.

---

## Hauptfunktionen

*   **Duale Normalisierungs-Strategie ("Digital Twin"):** Erzeugt für jede Quelldatei archivwürdige Formate (z.B. PDF/A, TIFF, WAV, MP4).
*   **Intelligente Fehler-Zusammenfassung:** Falls Konvertierungen fehlschlagen, werden diese am Ende des Laufs exklusiv im Terminal (in Rot) und am Ende des Logfiles zusammengefasst. So müssen Fehler nicht mühsam im gesamten Log gesucht werden.
*   **Fortschrittsanzeige:** Visualisiert den aktuellen Stand der Stapelverarbeitung inklusive Prozentangaben und Fortschrittsbalken für Audio.
*   **Windows-Pfad-Fix:** Enthält eine Speziallogik für LibreOffice, um das Windows-Zeichenlimit (260 Zeichen) bei tief verschachtelten Ordnerstrukturen zu umgehen.
*   **Namenskonvention:** Alle Derivate folgen dem Schema "Originalname.originalendung.zielendung", um die Provenienz lückenlos zu dokumentieren.
*   **Dubletten-Schutz:** Erkennt bereits existierende Derivate und verhindert unnötige Neukonvertierungen.

---

## TREE-Struktur & Dateipfade

Das Skript arbeitet rekursiv innerhalb der Transfer-Stufe (Stufe 3):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 3_[Datenträger-ID]_for-transfer/
    ├── files/                                   <-- ARBEITSBEREICH (Quelle & Ziel)
    │   ├── Dokument.doc                         <-- Original
    │   ├── Dokument.doc.odt                     <-- Derivat (Bearbeitungskopie)
    │   ├── Dokument.doc.pdf                     <-- Derivat (Visuelle Erhaltung)
    │   ├── Audio.mp3                            <-- Original
    │   └── Audio.mp3.wav                        <-- Derivat (Archivmaster)
    └── 3_[ID]_for-transfer_all-conversions.log  <-- ZIEL (Log mit exklusiver Fehlersummary am Ende)
```
---

## Technische Voraussetzungen

Damit dieses Skript funktioniert, müssen folgende Programme installiert sein:

1.  Python: Version 3.10+ empfohlen.
2.  FFmpeg: ffmpeg.exe und ffprobe.exe im System-PATH.
3.  ImageMagick: magick.exe im System-PATH.
4.  Ghostscript: gswin64c.exe im System-PATH.
5.  Inkscape: Installiert unter C:\Program Files\Inkscape\bin\inkscape.exe.
6.  LibreOffice: Installiert unter C:/Program Files/LibreOffice/program/soffice.exe.

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Kommandozeilenargumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python master_converter.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Prüfung der Pfade und Erreichbarkeit aller 5 externen Tools.
2. Indexierung: Alle relevanten Dateien werden identifiziert und gefiltert.
3. Verarbeitung: Die Dateien werden nacheinander konvertiert (Audio -> Bild -> Text -> Video).
4. Fehler-Reporting: Nach Abschluss erfolgt die exklusive Auflistung aller Problemfälle im Terminal und im Log.
5. Abschluss: Das Skript bietet an, den "for-transfer"-Ordner direkt im Explorer zu öffnen.

---

## Detaillierte Hinweise zum Skriptverhalten

### Exakte Dateinamenskonvention für Derivate

Das Skript verwendet folgende Benennungsschemata:

| Dateityp | Original | Ziel-Derivat(e) |
|----------|----------|------------------|
| Audio (nicht MP3/WAV) | `datei.flac` | `datei.flac.mp3` und `datei.flac.wav` |
| Audio (MP3) | `datei.mp3` | nur `datei.mp3.wav` |
| Audio (WAV) | `datei.wav` | nur `datei.wav.mp3` |
| Bild (alle) | `datei.jpg` | `datei.jpg.tiff` (Raster) oder `datei.jpg.pdf` (Vektor/Ghostscript) |
| Text/Office | `datei.doc` | `datei.doc.odt` und `datei.doc.pdf` |
| PDF | `datei.pdf` | nur `datei.pdf.pdf` (via LibreOffice PDF/A) |
| Video | `datei.mov` | `datei.mov.mp4` |

### Ausschlusslogik für abgeleitete Dateien

Eine Datei wird **übersprungen**, wenn:
- Der Dateiname (ohne Endung) mit einer Quell-Endung endet **und** die aktuelle Endung nicht `.pdf` ist
  - Beispiel: `dokument.doc.odt` → übersprungen (weil `dokument.doc` auf `.doc` endet)
  - Ausnahme: `dokument.doc.pdf` → wird verarbeitet (weil Endung `.pdf` ist)

Ein weiterer Filter überspringt Dateien, deren Name mit `.` oder `~` beginnt (versteckte/temporäre Dateien).

### Audio-Konvertierung mit Fortschrittsbalken

Bei Audio-Dateien wird die Dauer mit `ffprobe` ermittelt. Während der Konvertierung zeigt ein dynamischer Fortschrittsbalken den Fortschritt an: [########] 20.0%


### Verarbeitungsreihenfolge

Das Skript verarbeitet Dateien in folgender Priorität (definiert durch die Reihenfolge der `if/elif`-Abfragen):
1. Audio (`ext in SOURCE_AUDIO_EXTENSIONS`)
2. Bild (`ext in VALID_IMAGE_EXTENSIONS`)
3. Text/Office (`ext in VALID_TEXT_EXTENSIONS`)
4. Video (`ext in SOURCE_VIDEO_EXTENSIONS`)

### Erwartete Ordnerstruktur

🚨 ACHTUNG: Folgende Dateien konnten NICHT korrekt konvertiert werden:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 Datei: problem.mp3
 Grund: Audio-Konvertierung (FFmpeg) unvollständig oder fehlgeschlagen.

### Verarbeitungsreihenfolge

Das Skript verarbeitet Dateien in folgender Priorität (definiert durch die Reihenfolge der `if/elif`-Abfragen):
1. Audio (`ext in SOURCE_AUDIO_EXTENSIONS`)
2. Bild (`ext in VALID_IMAGE_EXTENSIONS`)
3. Text/Office (`ext in VALID_TEXT_EXTENSIONS`)
4. Video (`ext in SOURCE_VIDEO_EXTENSIONS`)

### Erwartete Ordnerstruktur

~/Documents/data/[AC_number]/[disk_archive_ID]/
└── 3_[disk_archive_ID]_for-transfer/
    ├── files/                                    <-- QUELLE & ZIEL (rekursive Verarbeitung)
    └── 3_[disk_archive_ID]_for-transfer_all-conversions.log   <-- LOG-DATEI

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(destination_folder)`
- **macOS/Linux** → nicht implementiert

### Abhängigkeiten (zusätzlich)

Das Skript verwendet nur Module der Python-Standardbibliothek: `os`, `sys`, `subprocess`, `re`, `datetime`, `pathlib`, `shutil`, `time`, `glob`, `tempfile`. Keine externen Python-Pakete erforderlich.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT