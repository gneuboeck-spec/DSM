# D - Master-Konvertierungsskript (All-in-One)

Dieses Skript ist das zentrale Werkzeug zur Konvertierung und Normalisierung von Dateien für die Langzeitarchivierung. Es vereint die Funktionalitäten spezialisierter Einzel-Skripte für Audio, Bild, Text/Office und Video in einem einzigen, umfassenden Workflow. Das Ziel ist es, für jede unterstützte Quelldatei standardisierte, archivsichere Derivate zu erstellen.

Zusätzlich enthält es eine Vorverarbeitungsstufe für Outlook-Express-Dateien (`.dbx`): Diese werden entpackt, und die enthaltenen E-Mails werden als `.eml`-Dateien samt Anhängen extrahiert, bevor sie in den regulären Konvertierungslauf übergehen.

## Struktur

    D_Master_Konvertierungsskript/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- D_Master_Konvertierungsskript.py   <-- Ausführbare Python-Datei

## Hauptfunktionen

* **Duale Normalisierungs-Strategie ("Digital Twin"):** Erzeugt für jede Quelldatei archivwürdige Formate (z. B. PDF/A, TIFF, WAV, MP3/MKV).
* **DBX-Vorverarbeitung (Stufe 0):** Entpackt Outlook-Express-Dateien (`.dbx`) über `DbxConv.exe`, konvertiert sie zu MBOX und extrahiert E-Mails als `.eml` plus Anhänge.
* **Intelligente Fehler-Zusammenfassung:** Falls Konvertierungen fehlschlagen, werden diese am Ende des Laufs exklusiv im Terminal (in Rot) und am Ende des Logfiles zusammengefasst. So müssen Fehler nicht mühsam im gesamten Log gesucht werden.
* **Fortschrittsanzeige:** Visualisiert den aktuellen Stand der Stapelverarbeitung inklusive Prozentangaben und einem dynamischen Fortschrittsbalken für Audio-Konvertierungen.
* **PDF/A-Vorerkennung:** Dateien, die bereits PDF/A-konform sind (XMP-Marker `pdfaid:part` / `pdfaid:conformance`), werden erkannt und nicht erneut konvertiert.
* **Windows-Pfad-Fix:** Enthält eine Speziallogik für LibreOffice (Nutzung eines temporären Verzeichnisses), um Probleme mit dem Windows-Zeichenlimit (260 Zeichen) bei tief verschachtelten Ordnerstrukturen zu umgehen.
* **Namenskonvention:** Alle Derivate folgen dem Schema `Originalname.originalendung.zielendung` (z. B. `Dokument.doc.pdf`), um die Provenienz lückenlos zu dokumentieren.
* **Dubletten-Schutz:** Erkennt bereits existierende abgeleitete Dateien und verhindert unnötige Neukonvertierungen.

## TREE-Struktur & Dateipfade

Das Skript arbeitet rekursiv innerhalb der Transfer-Stufe (Stufe 3). Der Projektpfad wird vom Menü übergeben (`sys.argv[3]` oder Umgebungsvariable `DATA_PATH`):

    [Projektpfad]/
    `-- 3_[Datenträger-ID]_for-transfer/
        |-- files/                                   <-- ARBEITSBEREICH (Quelle & Ziel)
        |   |-- Dokument.doc                         <-- Original
        |   |-- Dokument.doc.odt                     <-- Derivat (Bearbeitungskopie)
        |   |-- Dokument.doc.pdf                     <-- Derivat (Visuelle Erhaltung / PDF/A)
        |   |-- Audio.mp3                            <-- Original
        |   `-- Audio.mp3.wav                        <-- Derivat (Archivmaster)
        |-- 3_[ID]_for-transfer_all-conversions.log  <-- ZIEL (Log mit exklusiver Fehlersummary am Ende)
        `-- 3_[ID]_for-transfer_tree.txt             <-- ZIEL (Verzeichnisstruktur nach Konvertierung)

## Technische Voraussetzungen

Damit dieses Skript funktioniert, müssen folgende Programme installiert sein. Wenn sie im System-PATH liegen, werden sie automatisch gefunden; ansonsten greifen die angegebenen Fallback-Pfade.

| Tool | Aufruf | Fallback-Pfad |
|------|--------|----------------|
| FFmpeg | `ffmpeg.exe` | (muss im PATH liegen) |
| FFprobe | `ffprobe.exe` | (muss im PATH liegen) |
| ImageMagick | `magick.exe` | (muss im PATH liegen) |
| Ghostscript | `gswin64c.exe` | (muss im PATH liegen) |
| Inkscape | `inkscape.exe` | `C:\Program Files\Inkscape\bin\inkscape.exe` |
| LibreOffice | `soffice.exe` | `C:\Program Files\LibreOffice\program\soffice.exe` |
| DbxConv | `DbxConv.exe` | (muss im PATH liegen, z. B. `C:\Program Files\dbxconv\`) |

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

### Python-Module

Das Skript verwendet ausschließlich Module der Python-Standardbibliothek: `os`, `sys`, `subprocess`, `re`, `datetime`, `pathlib`, `shutil`, `time`, `glob`, `tempfile`, `mailbox`, `email`. Es sind keine externen Python-Pakete erforderlich.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `4` (D_Master_Konvertierungsskript) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "D_Master_Konvertierungsskript.py" AC_0001 CD_01 "C:\Pfad\zum\Datenordner"

### Ablauf der Ausführung

1. **Validierung:** Prüfung der Pfade und Erreichbarkeit aller 7 externen Tools.
2. **DBX-Vorverarbeitung (Stufe 0):** Suche nach `.dbx`-Dateien und Entpacken über `DbxConv.exe`; Extraktion der E-Mails (`.eml`) und Anhänge.
3. **Indexierung:** Alle relevanten Dateien im `files`-Ordner werden identifiziert und gefiltert (Ausschluss von bereits abgeleiteten Dateien).
4. **Verarbeitung:** Die Dateien werden nacheinander konvertiert (Audio → Bild → Text/Office → Video).
5. **Fehler-Reporting:** Nach Abschluss erfolgt die exklusive Auflistung aller Problemfälle im Terminal und im Log.
6. **Tree-Generierung:** Erstellung einer aktuellen `tree.txt` des Transfer-Ordners.
7. **Abschluss:** Das Skript bietet an, den `for-transfer`-Ordner direkt im Explorer zu öffnen.

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

### Bildkonvertierung

| Quelltyp | Werkzeug | Zielformat |
|----------|----------|-------------|
| Rasterbilder (`.jpg`, `.png`, `.bmp`, `.webp`, `.heic`, `.tga`, `.gif`, `.jfif`) | ImageMagick | `.tiff` |
| Vektorgrafiken (`.eps`, `.ai`) | Ghostscript | `.pdf` |
| SVG / WMF | Inkscape | `.pdf` |

### Video-Prüfung (Archivformat-Erkennung)

Bei `.mkv`-Dateien prüft das Skript über `ffprobe`, ob Video-Codec `ffv1` und Audio-Codec `flac` (oder gar kein Audio) verwendet werden. Falls ja, wird die Konvertierung übersprungen. Andernfalls wird neu kodiert.

### Verarbeitungsreihenfolge

Das Skript verarbeitet Dateien in folgender Priorität:

1. Audio (`ext in SOURCE_AUDIO_EXTENSIONS`)
2. Bild (`ext in VALID_IMAGE_EXTENSIONS`)
3. Text/Office (`ext in VALID_TEXT_EXTENSIONS`)
4. Video (`ext in SOURCE_VIDEO_EXTENSIONS`)

### Fehler-Zusammenfassung (Error Summary)

Am Ende der Verarbeitung wird geprüft, ob Einträge in der globalen Liste `conversion_errors` vorhanden sind. Falls ja, wird eine formatierte, rot hervorgehobene Warnung ausgegeben, die Dateinamen und den konkreten Fehlergrund auflistet. Diese Zusammenfassung wird ebenfalls ans Ende der Log-Datei angehängt.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j` wird unter Windows `os.startfile(destination_folder)` aufgerufen. Andere Plattformen werden in diesem Skript nicht unterstützt.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT