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
* **Fortschrittsanzeige:** Visualisiert den aktuellen Stand der Stapelverarbeitung inklusive Prozentangaben und einem dynamischen Fortschrittsbalken für Audio-Konvertierungen. Vor jeder Log-Ausgabe wird die aktuelle Konsolenzeile robust bereinigt, damit der Fortschrittsbalken nicht mit anderen Meldungen kollidiert.
* **PDF/A-Vorerkennung:** Dateien, die bereits PDF/A-konform sind (XMP-Marker `pdfaid:part` / `pdfaid:conformance` bzw. der String `PDF/A` in den ersten 2 MB), werden erkannt und nicht erneut konvertiert.
* **Windows-Pfad-Fix:** Enthält eine Speziallogik für LibreOffice (Nutzung eines temporären Verzeichnisses), um Probleme mit dem Windows-Zeichenlimit (260 Zeichen) bei tief verschachtelten Ordnerstrukturen zu umgehen. Für Video-Konvertierungen wird zusätzlich der Long-Path-Prefix `\\?\` verwendet.
* **Namenskonvention:** Alle Derivate folgen dem Schema `Originalname.originalendung.zielendung` (z. B. `Dokument.doc.pdf`), um die Provenienz lückenlos zu dokumentieren. **Ausnahme:** Native LibreOffice-Formate (`.odt`, `.ods`, `.odp`, `.ott`, `.ots`, `.otp`) erhalten kein doppeltes `.odt.pdf`, sondern direkt `dateiname.pdf`.
* **Dubletten-Schutz:** Erkennt bereits existierende abgeleitete Dateien und verhindert unnötige Neukonvertierungen. Vor der Verarbeitung einer Quelldatei werden alte, zugehörige Derivate (`.mp3`, `.wav`, `.tiff`, `.pdf`, `.mkv`, ggf. `.odt`/`.ods`/`.odp`) gezielt gelöscht, damit keine veralteten Artefakte verbleiben.
* **R3D-Toleranz & Fehlerrobustheit:** FFmpeg läuft mit `-err_detect ignore_err`, sodass beschädigte Videodateien (z. B. R3D) nicht den gesamten Lauf abbrechen. Bei Fehlern wird eine temporäre Zieldatei automatisch entfernt.

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
2. **DBX-Vorverarbeitung (Stufe 0):** Suche nach `.dbx`-Dateien und Entpacken über `DbxConv.exe`; Extraktion der E-Mails (`.eml`) und Anhänge in einen Unterordner `<dbx-name>_extracted/`.
3. **Indexierung:** Alle relevanten Dateien im `files`-Ordner werden identifiziert und gefiltert (Ausschluss von bereits abgeleiteten Dateien und von Dateien, die mit `.` oder `~` beginnen).
4. **Verarbeitung:** Die Dateien werden nacheinander konvertiert (Audio → Bild → Text/Office → Video). Vor jeder Datei werden alte Derivate entfernt.
5. **Fehler-Reporting:** Nach Abschluss erfolgt die exklusive Auflistung aller Problemfälle im Terminal (rot) und im Log.
6. **Tree-Generierung:** Erstellung einer aktuellen `tree.txt` des Transfer-Ordners via `cmd /c tree ... /A /F`.
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
| Text/Office (Fremdformat) | `datei.doc` | `datei.doc.odt` und `datei.doc.pdf` |
| Text/Office (nativ LO) | `datei.odt` | nur `datei.pdf` |
| PDF | `datei.pdf` | `dateipdf.pdf` (siehe Hinweis unten) |
| Video | `datei.mov` | `datei.mov.mkv` (FFV1/FLAC) |

**Hinweis zum PDF-Sonderfall:** Bei einer Quelldatei `datei.pdf` wird als Zielname `dateipdf.pdf` gebildet (also `name + "pdf" + ".pdf"`), um eine Kollision mit dem Original zu vermeiden. Bereits PDF/A-konforme Dateien werden komplett übersprungen.

### Ausschlusslogik für abgeleitete Dateien

Eine Datei wird **übersprungen**, wenn ihr Name (ohne Endung) mit einer bekannten Quell-Endung endet **und** die aktuelle Endung nicht `.pdf` ist.

* *Beispiel:* `dokument.doc.odt` → wird übersprungen (weil `dokument.doc` auf `.doc` endet).
* *Ausnahme:* `dokument.doc.pdf` → wird verarbeitet (weil die Endung `.pdf` ist und dies das finale Archivderivat darstellt).

Zusätzlich werden Dateien übersprungen, deren Name mit `.` oder `~` beginnt (versteckte oder temporäre Dateien).

### Vorab-Löschung alter Derivate

Vor der Verarbeitung einer Quelldatei entfernt das Skript gezielt alte, zugehörige Derivate im selben Ordner:

- `datei.ext.mp3`, `datei.ext.wav`, `datei.ext.tiff`, `datei.ext.pdf`, `datei.ext.mkv`
- bei Text-Office-Fremdformaten zusätzlich `datei.ext.odt` / `.ods` / `.odp`

So wird sichergestellt, dass keine veralteten Konvertierungsartefakte liegen bleiben.

### Audio-Konvertierung mit Fortschrittsbalken

Bei Audio-Dateien wird die Dauer vorab mit `ffprobe` ermittelt. Während der Konvertierung zeigt ein dynamischer Fortschrittsbalken den Status an (z. B. `[########        ] 20.0%`).

### Bildkonvertierung

| Quelltyp | Werkzeug | Zielformat |
|----------|----------|-------------|
| Rasterbilder (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`, `.heic`, `.tga`, `.gif`, `.jfif`) | ImageMagick | `.tiff` |
| Vektorgrafiken (`.eps`, `.ai`) | Ghostscript | `.pdf` |
| SVG / WMF | Inkscape | `.pdf` (mit `--export-text-to-path` und PDF-Version 1.5) |

### Text/Office-Konvertierung

1. **PDF/A-Vorprüfung:** Ist die Quelle bereits PDF/A, wird sie übersprungen.
2. **Native LibreOffice-Formate** (`.odt`, `.ods`, `.odp`, `.ott`, `.ots`, `.otp`): direkter PDF/A-Export ohne Zwischenschritt.
3. **Fremdformate:** Konvertierung zu ODF (`.odt`/`.ods`/`.odp`) via LibreOffice, danach PDF/A-Export. Falls der Standardfilter scheitert, gibt es zwei Fallbacks:
   - StarWriter-Import (`--infilter=StarWriter 5.0`) für `.sdw`-Dateien
   - Umbenennung zu `_temp.doc` mit erneuter Auto-Detection
4. **Scheitert auch die ODF-Erstellung** (z. B. bei Draw/Impress), wird ein direkter PDF/A-Export aus dem Original versucht.
5. **PDF/A-Export** erfolgt mit dem Filter-String `pdf:<ExportFilter>:SelectPdfVersion=2` in ein temporäres Verzeichnis (Windows-Pfad-Limit-Fix) und wird anschließend an den Zielort verschoben.

### Video-Prüfung (Archivformat-Erkennung)

Bei `.mkv`-Dateien prüft das Skript über `ffprobe`, ob Video-Codec `ffv1` und Audio-Codec `flac` (oder gar kein Audio) verwendet werden. Falls ja, wird die Konvertierung übersprungen. Andernfalls wird neu kodiert.

Für die Konvertierung werden die absoluten Pfade unter Windows mit dem Long-Path-Prefix `\\?\` versehen. FFmpeg läuft mit `-err_detect ignore_err`, um beschädigte Dateien zu tolerieren. Sollte Ein- und Ausgabepfad identisch sein (bereits `.mkv`), wird in eine temporäre Datei `_temp_convert.mkv` konvertiert und anschließend ersetzt.

### DBX-/E-Mail-Verarbeitung (Stufe 0)

* Für jede gefundene `.dbx`-Datei ruft das Skript `DbxConv.exe -mbxrd -dn -ic -senddate <datei>` auf.
* Die entstehende `.mbx`-Datei wird zu `.mbox` umbenannt und mit dem Python-Modul `mailbox` gelesen.
* Für jede E-Mail wird:
  - der Dateiname aus `Datum (YYYY-MM-DD-HH-MM-SS)` + `Subject` gebildet (sanitized für Windows)
  - die Mail als `.eml` gespeichert
  - jeder Anhang als separate Datei mit Präfix `<base_name>_<anhangname>` extrahiert
* Fehler bei der DBX-Konvertierung oder beim MBOX-Parsing landen in der `conversion_errors`-Liste.

### Fehler-Zusammenfassung (Error Summary)

Am Ende der Verarbeitung wird geprüft, ob Einträge in der globalen Liste `conversion_errors` vorhanden sind. Falls ja, wird eine formatierte, rot hervorgehobene Warnung ausgegeben, die Dateinamen und den konkreten Fehlergrund auflistet. Diese Zusammenfassung wird ebenfalls ans Ende der Log-Datei angehängt.

### Log-Datei

Die Log-Datei wird unter `3_[ID]_for-transfer/3_[ID]_for-transfer_all-conversions.log` erstellt. Bei jedem Start wird eine eventuell vorhandene alte Log-Datei gelöscht. Jeder Eintrag erhält einen Zeitstempel `[YYYY-MM-DD HH:MM:SS]`. Vor jeder Ausgabe wird die aktuelle Konsolenzeile robust bereinigt (zur sauberen Trennung von Fortschrittsbalken und Log-Meldungen).

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| AC-Nummer oder Datenträger-ID fehlt (`sys.argv[1]`/`[2]`) | `FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.` + `sys.exit(1)` |
| Quell-Ordner `files` nicht gefunden | Fehlermeldung + `setup_and_validate_paths` gibt `None` zurück, Lauf endet |
| Benötigte externe Tools nicht im PATH | Auflistung der fehlenden Tools + Hinweis auf PATH-Einrichtung, Lauf endet |
| Einzelne Konvertierung schlägt fehl | Datei landet in `conversion_errors`, Verarbeitung läuft weiter |
| Tree-Erstellung schlägt fehl | Warnung/Fehlermeldung im Log, Lauf wird beendet |

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j` wird unter Windows `os.startfile(destination_folder)` aufgerufen. Andere Plattformen werden in diesem Skript nicht unterstützt (das Skript ist insgesamt Windows-zentriert, u. a. wegen `cmd /c tree`, `os.startfile` und der `\\?\`-Pfadlogik).

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT