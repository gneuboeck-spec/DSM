# G - Metadata Extraction, Indexing & Multi-Source Integrity Validator (filetrove)

Dieses Skript ist das zentrale technische Prüfwerkzeug in Phase 3 (Kuratierung & Bereinigung). Es kombiniert eine hochgradig automatisierte Metadaten-Extraktion mit einer lückenlosen Integritätsprüfung (Fixity-Check). Das Skript beweist mathematisch die Unveränderlichkeit der Daten, indem es aktuelle Prüfsummen live berechnet und gegen bis zu drei verschiedene Dokumentationsquellen aus allen vorherigen Prozessstufen (Imaging, Forensik, Extraktion) validiert.

## Struktur

    G_Metadata_Extraction_Indexing_filetrove/
    |-- README.md                          <-- Diese Datei
    `-- win/
        |-- G_Metadata_Extraction_Indexing_filetrove.py   <-- Ausführbare Python-Datei
        `-- rules.yar                      <-- YARA-Regeln für Dateiformat-Identifizierung

## Hauptfunktionen

* **Multi-Source Integritätsprüfung (Triple-Algo):**
  * Validiert Dateien flexibel gegen **SHA-512** (Imaging-Logs), **SHA-256** (Forensik/Index) und **MD5** (Siegfried-Berichte).
  * Gleicht den Ist-Zustand jeder Datei in Stufe 4 live gegen die historischen Soll-Werte ab.
  * Status-Kategorisierung:
    * `verified`: Identität über alle verfügbaren Quellen bestätigt.
    * `CORRUPTED_OR_MODIFIED`: Abweichung erkannt (Alarm-Ausgabe mit Soll/Ist-Vergleich).
    * `new_file`: Rechtmäßiges Derivat (z. B. PDF/A-Konvertierung), für das keine Vorstufen-Hashes existieren.
* **Detailliertes Integritäts-Protokoll (.log):**
  * Erzeugt ein revisionssicheres Audit-Log (`3_[ID]_for-transfer_integrity.log`), das jede erfolgreiche Prüfung und jeden Fehler detailliert dokumentiert.
* **Tiefgehende Metadaten-Extraktion:**
  * Bündelt Informationen von ExifTool, Siegfried, FFprobe, Hachoir, Mutagen, Pillow und YARA.
  * Harmonisiert Tool-Tags in ein konsistentes, alphabetisch sortiertes XML-basiertes Index-Schema (`.index`).
* **Duale Archiv-Dokumentation:**
  * Speichert die primären Berichte in Stufe 5 (LZA) und legt automatisch eine identische Arbeitskopie in Stufe 4 (VL) ab.

## TREE-Struktur & Dateipfade (Phase 3)

Das Skript verknüpft die gesamte bisherige Beweiskette. Der Projektpfad wird vom Menü übergeben (`sys.argv[3]` oder Umgebungsvariable `DATA_PATH`):

    [Projektpfad]/
    |-- 1_[ID]_image-LZA/logfiles/
    |   `-- 1_[ID]_image-log.csv            <-- QUELLE (SHA-512)
    |-- 2_[ID]_extracted-files/
    |   |-- 2_[ID]_extracted-files_brunnhilde-summary.json  <-- QUELLE (SHA-256)
    |   `-- 2_[ID]_extracted-files_brunnhilde/files_collection_report/siegfried.csv <-- QUELLE (MD5)
    |-- 4_[ID]_VL/                          <-- ARBEITSBEREICH (Eingabe)
    |   |-- files/                          <-- Hier liegen die zu prüfenden Dateien
    |   |-- 3_[ID]_for-transfer.index       <-- ZIEL (Kopie des finalen Index)
    |   `-- 3_[ID]_for-transfer_integrity.log <-- ZIEL (Kopie des Audit-Logs)
    `-- 5_[ID]_LZA/logfiles/                <-- ZIEL (Primäre Dokumentation)
        |-- 3_[ID]_for-transfer.index       <-- ZIEL (Primärer Master-Index)
        `-- 3_[ID]_for-transfer_integrity.log <-- ZIEL (Primärer Fixity-Beweis)

## Technische Voraussetzungen

Zusätzlich zu Python 3.13+ müssen folgende externe Python-Pakete installiert sein:

* `mutagen`
* `PyPDF2`
* `Pillow`
* `yara-python`
* `chardet`

Installation:

    pip install -r requirements.txt

Folgende externe Tools müssen im System-PATH oder an den im Skript konfigurierten Fallback-Pfaden verfügbar sein:

| Tool | Aufruf | Fallback-Pfad |
|------|--------|---------------|
| ExifTool | `exiftool` | `C:\Program Files\ExifTool\exiftool.exe` |
| Siegfried | `sf` | `C:\Program Files\Siegfried\sf.exe` |
| FFmpeg/FFprobe | `ffprobe` | `C:\Program Files\ffmpeg\ffprobe.exe` |
| Hachoir | `hachoir-metadata` | `C:\Users\digit\AppData\Local\Programs\Python\Python313\Scripts\hachoir-metadata.exe` |

**YARA-Regeln:** Die Datei `rules.yar` muss sich im selben Verzeichnis (`win/`) wie das Python-Skript befinden. Der Pfad wird dynamisch aus `SCRIPT_DIR` ermittelt.

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `7` (G_Metadata_Extraction_Indexing_filetrove) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "G_Metadata_Extraction_Indexing_filetrove.py" AC_0001 CD_01 "C:\Pfad\zum\Datenordner"

Werden keine Kommandozeilen-Argumente übergeben, fragt das Skript interaktiv nach AC-Nummer und Datenträger-ID. Der Projektpfad greift dann auf die Umgebungsvariable `DATA_PATH` oder auf `~/Documents/data/[AC]/[ID]` zurück.

### Ablauf der Validierung

1. **Initialisierung:** Das Skript lädt alle verfügbaren Hashes aus den Quellen (CSV, JSON) in den Speicher.
2. **Fixity-Check:** Jede Datei im VL-Ordner wird live gehasht (SHA-256, bei Bedarf 512/MD5) und sofort verglichen.
3. **Extraktion:** Parallel dazu erfolgt die tiefe Metadaten-Analyse und Validierung (Lesbarkeit).
4. **Finalisierung:** Der technische Index und das menschenlesbare Integritäts-Log werden erzeugt und stufenübergreifend verteilt.

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Referenzquellen für Integritätsprüfung

Das Skript sucht automatisch nach folgenden Dateien (Groß-/Kleinschreibung wird ignoriert):

| Quelle | Pfad (relativ zu `[Projektpfad]`) | Enthält |
|--------|-----------------------------------|---------|
| Imaging CSV | `1_[ID]_image-LZA/logfiles/1_[ID]_image-log.csv` | SHA-512 (Spalte `SHA-512-Hash`), Dateiname (Spalte `Dateiname`) |
| Brunnhilde JSON | `2_[ID]_extracted-files/2_[ID]_extracted-files_brunnhilde-summary.json` | SHA-256 im Feld `file_fixity_sha256` |
| Siegfried CSV | `2_[ID]_extracted-files/.../files_collection_report/siegfried.csv` | MD5 (Spalte `md5`), Dateiname (Spalten `filename` oder `file`) |

Fehlende Quellen werden ignoriert, vorhandene werden geladen.

### Integritätsstatus im XML-Index

Jede Datei erhält ein `<integrity_status>`-Element mit einem der drei Werte:

| Wert | Bedeutung |
|------|-----------|
| `verified` | Mindestens ein Referenz-Hash stimmt mit dem live berechneten Hash überein. |
| `CORRUPTED_OR_MODIFIED` | Kein Referenz-Hash stimmt überein; Abweichungen werden detailliert protokolliert. |
| `new_file` | Keine Referenz-Hashes für diese Datei gefunden (z. B. konvertierte Derivate). |

### Integritäts-Log (`*_integrity.log`)

Das Log wird im selben Ordner wie die `.index`-Datei erstellt und enthält:

* Projektname und Datum.
* Bei Fehlern: detaillierte Soll/Ist-Gegenüberstellung für SHA-512, SHA-256 und MD5.
* Anzahl der verifizierten, neuen und fehlerhaften Dateien.
* Vollständige Liste aller verifizierten Dateien (sortiert).

Das Log wird **sowohl nach Stufe 5 (LZA/logfiles) als auch nach Stufe 4 (VL)** kopiert.

### Metadaten-Extraktoren (Reihenfolge & Bedingungen)

| Extraktor | Ausgeführt für | Besonderheit |
|-----------|---------------|--------------|
| `get_file_info` | alle Dateien | liefert `size`, `filesystem_created_date`, `filesystem_modified_date`, `filesystem_accessed_date` |
| `run_siegfried` | alle Dateien | liefert `pronom_id`, `note`, `format_version`, `mime_type` |
| `extract_image_info` | wenn MIME-Typ mit `image/` beginnt | Pillow; SVGs werden übersprungen, um Fehler zu vermeiden |
| `extract_metadata_exiftool` | alle Dateien | liefert umfangreiche Metadaten; Schlüssel wie `SourceFile`, `FileName` werden gefiltert |
| `extract_metadata_ffprobe` | alle Dateien | liefert Format- und Stream-Informationen; Schlüssel `size` wird explizit ausgeschlossen |
| `extract_mutagen_info` | alle Dateien | liefert Audio-Technik (`sample_rate`, `channels`, `bits_per_sample`, `duration`) und Tags |
| `extract_pdf_info` | nur `.pdf` | liefert `pdf_num_pages` sowie Metadaten aus `/Keywords`, `/CreationDate`, `/ModDate`, `/Creator`, `/Producer` |
| `extract_sam_specific` | nur `.sam` | liefert `sam_line_count`, `sam_sample_text` (Zeichenkodierung wird mit `chardet` erkannt) |
| `extract_musicxml_info` | nur `.mxl` | entpackt ZIP, parst XML, liefert z. B. `score_partwiseidentificationencodingsoftware`, `document_encoding_date` |

### YARA-Regeln

Das Skript lädt die Datei `rules.yar`, die sich im selben Verzeichnis wie das Skript befindet, und kompiliert die darin enthaltenen Regeln. Bei der Verarbeitung jeder Datei:

1. Datei wird im Binärmodus gelesen.
2. `rules.match(data=file_data)` wird ausgeführt.
3. Gefundene Regeln werden nach Konfliktregeln gefiltert (z. B. `csv` wird ignoriert, wenn `sam`, `eml` oder `tiff` ebenfalls matchen).
4. Alle übrigen Regelnamen werden für die Validierungslogik herangezogen.

### Validierungslogik für `<validity>`

Das Element `<validity>` erhält den Wert `Yes` oder `No` basierend auf:

| Dateityp | Prüfung |
|----------|---------|
| `.pdf` | `PdfReader(file_path)` ohne Exception |
| `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp` | Magic-Header `PK` + `ZipFile.testzip() is None` |
| MIME-Typ `image/*` | `Image.open().verify()` ohne Exception |
| MIME-Typ `audio/*` oder `video/*` | `duration` oder `ffprobe_format_duration` vorhanden |
| `.mxl` | `document_title` oder `document_creator_tool` vorhanden |
| YARA-Match | Treffer auf `SAM`, `EML`, `CSV`, `HTML`, `XHTML`, `TXT` oder `ZIP_ARCHIVE` |
| Fallback | Wenn keine der obigen Bedingungen zutrifft, aber mehr als 5 Metadaten-Schlüssel extrahiert wurden → `Yes` |

### XML-Ausgabe (`.index`)

* Root-Element: `<filetrove>`
* Pro Datei ein `<file>`-Element mit Attributen `path`, `name`, `extension`
* Metadaten werden als Unterelemente **alphabetisch sortiert** eingefügt.
* Werte werden mit `sanitize_for_xml()` von ungültigen XML-Steuerzeichen befreit.
* Eine umfangreiche Blockliste (`TAGS_TO_REMOVE` + `additional_blocklist`) filtert unerwünschte Tags.
* Spezialbehandlung: `<colorspacedata>` mit Wert `RGB` wird entfernt.
* Binäre ASF/WMA-Attribute (`[ASFByteArrayAttribute`) werden übersprungen.

### Vereinheitlichung von Metadaten-Schlüsseln (`unify_metadata_keys`)

Das Skript führt eine umfangreiche Normalisierung durch:

* Schlüssel werden mit `sanitize_tag()` bereinigt (Leerzeichen, Doppelpunkte, Bindestriche, Punkte, Schrägstriche werden durch `_` ersetzt; nur alphanumerisch + `_` bleibt).
* Mehrere synonyme Schlüssel werden auf einen bevorzugten Schlüssel gemappt (z. B. `imagewidth`, `image_width`, `width`, `exifimagewidth` → `image_width`).
* Für `document_creator_tool` wird `is_likely_software_tool()` angewendet: Werte, die wie Personen- oder Institutionsnamen aussehen, werden verworfen; technische Werte (mit Versionsnummern, Pfaden, typischen Software-Schlüsselwörtern) werden behalten.
* Datumsfelder werden mit `format_date_to_iso()` normalisiert (unterstützt ExifTool-Format `YYYY:MM:DD HH:MM:SS` und PDF-Format `D:YYYYMMDDHHMMSS...`).
* Nicht gemappte Schlüssel bleiben erhalten (außer Blockliste).

### Sonderbehandlung von Bild- vs. Video-Dimensionen

Wenn die Datei als Video identifiziert wird (MIME-Typ beginnt mit `video/` oder Dateiendung in `known_video_suffixes`), werden `image_width` und `image_height` in `video_frame_width` bzw. `video_frame_height` umgewandelt und die ursprünglichen `image_*`-Schlüssel gelöscht.

### Löschung von falsch zugeordneten `duration` und `audio_channel_count`

Diese Felder werden aus der finalen Ausgabe entfernt, wenn der MIME-Typ nicht mit `audio/` oder `video/` beginnt und die Datei nicht zur Gruppe `audio` oder `video` gehört (ermittelt über `get_file_type_group()`).

### Verarbeitungsausschlüsse

Dateien werden übersprungen, wenn ihr Name mit `._` oder `~` beginnt.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:

* **Windows** → `os.startfile(destination_folder)`
* **macOS** → `subprocess.run(["open", destination_folder])`
* **Linux/andere** → `subprocess.run(["xdg-open", destination_folder])`

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT