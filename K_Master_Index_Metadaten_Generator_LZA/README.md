# Skript K: Master-Index & Multi-Source Integrity Validator (LZA-Stufe)

Dieses Skript ist das finale Kontroll- und Indexierungswerkzeug in Phase 4 (LZA-Paketierung). Es führt eine tiefgehende Metadaten-Extraktion über den gesamten Inhalt der Stufe 5 (LZA) durch und erstellt ein lückenloses digitales Inventar (.index). Das Kernstück ist der Multi-Source-Fixity-Check: Jede Datei im Paket wird live gegen bis zu sechs historische Dokumentationsquellen aus allen vorherigen Prozessstufen validiert, um die absolute Unveränderlichkeit der Daten vor der Archivierung zu beweisen.

---

## Hauptfunktionen

*   **Multi-Source Integritätsprüfung (Triple-Algo):**
    *   **SHA-512 Abgleich:** Verifiziert Images und Tracks gegen das Imaging-Log (CSV/TXT).
    *   **SHA-256 Abgleich:** Validiert Nutzdaten gegen die Brunnhilde-Zusammenfassung, den technischen Vor-Index und die PREMIS-Erhaltungsmetadaten.
    *   **MD5 Abgleich:** Prüft Dateien gegen den originalen Siegfried-Forensik-Bericht.
*   **Status-Kategorisierung im Inventar:**
    *   `verified`: Identität über die gesamte Prozesskette mathematisch bewiesen.
    *   `CORRUPTED_OR_MODIFIED`: Abweichung erkannt (Alarm-Ausgabe mit detailliertem Soll/Ist-Vergleich im Terminal).
    *   `new_file`: Legitimes Derivat (z. B. PDF/A), das erst im Workflow entstanden ist.
*   **Revisionssicheres Archiv-Protokoll:**
    *   Erzeugt das finale Integritäts-Log (5_[ID]_LZA_integrity.log) im logfiles-Ordner der Stufe 5.
*   **Tiefenanalyse & Harmonisierung:**
    *   Bündelt Metadaten von ExifTool, Siegfried, FFprobe, Hachoir und YARA in einem einheitlichen XML-Schema.

---

## TREE-Struktur & Dateipfade (Phase 4)

Das Skript arbeitet im fertig konsolidierten LZA-Staging-Ordner. Es scannt alle Objekte und gleicht sie mit den Protokollen im logfiles-Ordner ab:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 5_[ID]_LZA/                            <-- ARBEITSBEREICH (Eingabe)
    ├── 01_[ID].img (oder .001 / .bin)     <-- OBJEKT (Gegen SHA-512 geprüft)
    ├── 3_files/                           <-- OBJEKTE (Gegen SHA-256/MD5 geprüft)
    │   └── ... (Originale & Derivate)
    ├── 5_[ID]_LZA.index                   <-- ZIEL (Finaler Master-Index)
    └── logfiles/                          <-- QUELLEN & ZIEL FÜR LOGS
        ├── 1_[ID]_image-log.csv           <-- Quelle: SHA-512 (Spalte: SHA-512-Hash)
        ├── 01_[ID]_image-log.txt          <-- Quelle: SHA-512 (Sektion: SHA-512-Hashes)
        ├── 2_[ID]_extracted-files_brunnhilde/
        │   └── files_collection_report/
        │       └── siegfried.csv          <-- Quelle: MD5 (Spalte: md5)
        ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- Quelle: SHA-256 (Feld: sha256)
        ├── 3_[ID]_for-transfer.index      <-- Quelle: SHA-256 (Tag: sha256)
        ├── 5_[ID]_LZA_premis.xml          <-- Quelle: SHA-256 (Tag: messageDigest)
        └── 5_[ID]_LZA_integrity.log       <-- ZIEL: Finaler Fixity-Beweis
```
---

## Technische Voraussetzungen

Zusätzlich zu Python 3.10+ müssen folgende Tools im System-Pfad erreichbar sein:
1. ExifTool (exiftool.exe)
2. Siegfried (sf.exe)
3. FFmpeg/FFprobe (ffprobe.exe)
4. Hachoir (hachoir-metadata.exe)
5. YARA (mit gültiger rules.yar)

---

## Ausführung

Das Skript wird über die Kommandozeile mit AC-Nummer und Datenträger-ID gestartet:

    python Skript_K_MasterIndex_LZA.py %AC_NUMBER% %DISK_ID%

### Ablauf der Finalisierung

1. **Multi-Source Loading:** Das Skript lädt alle Soll-Hashes aus den 6 Referenzdateien gleichzeitig in einen intelligenten Speicher.
2. **Paket-Scan:** Jede Datei in Stufe 5 (Images, Nutzdaten, Logs) wird erfasst.
3. **Hybrid-Validierung:** Je nach Verfügbarkeit in den Quellen werden SHA-256, SHA-512 und MD5 live berechnet und verglichen.
4. **Detail-Reporting:** Bei Abweichungen wird exakt dokumentiert, welcher Wert (z.B. MD5) aus welcher Quelle nicht mit dem aktuellen Scan übereinstimmt.
5. **Abschluss:** Das Integritäts-Log wird als finaler Beweis für die lückenlose Kette ("Chain of Custody") erstellt.

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur (Stufe 5 LZA)

Das Skript erwartet folgende vollständig konsolidierte Struktur nach Ausführung von Skript J (Staging):

```text
~/Documents/data/[AC_number]/[disk_archive_ID]/
└── 5_[disk_archive_ID]_LZA/                      <-- BASE_DIR (wird rekursiv gescannt)
    ├── 01_[ID].img / *.001 / *.bin / *.dd        <-- Disk-Images
    ├── 3_files/                                  <-- Nutzdaten (Originale & Derivate)
    ├── [andere Dateien/Ordner aus Stufe 1-3]     <-- werden ebenfalls gescannt
    ├── 5_[ID]_LZA.index                          <-- ZIEL (Master-Index)
    └── logfiles/                                 <-- QUELLE für Referenz-Hashes + ZIEL für Log
        ├── 1_[ID]_image-log.csv
        ├── 01_[ID]_image-log.txt
        ├── 2_[ID]_extracted-files_brunnhilde/
        │   └── files_collection_report/
        │       └── siegfried.csv
        ├── 2_[ID]_extracted-files_brunnhilde-summary.json
        ├── 3_[ID]_for-transfer.index
        ├── 5_[ID]_LZA_premis.xml
        └── 5_[ID]_LZA_integrity.log              <-- ZIEL (finales Integritäts-Log)
```

### Referenzquellen für Integritätsprüfung (load_all_lza_reference_hashes)

Das Skript durchsucht den `logfiles`-Ordner in Stufe 5 nach folgenden Quellen (Reihenfolge irrelevant, da alle in ein Dictionary geladen werden):

| Quelle | Pfad (relativ zu `5_[ID]_LZA/logfiles/`) | Enthält | Schlüssel im Dictionary |
|--------|------------------------------------------|---------|------------------------|
| Imaging Log (TXT) | `01_[ID]_image-log.txt` | SHA-512 für `.raw`-Dateien (Greaseweazle) | `sha512` |
| Imaging Log (CSV) | `1_[ID]_image-log.csv` | SHA-512 (Spalte `SHA-512-Hash`), Dateiname (Spalte `Dateiname`) | `sha512` |
| Brunnhilde JSON | `2_[ID]_extracted-files_brunnhilde-summary.json` | SHA-256 im Feld `file_fixity_sha256` (Unterfeld `sha256`), Dateiname (Unterfeld `file`) | `sha256` |
| Siegfried CSV | `2_[ID]_extracted-files_brunnhilde/files_collection_report/siegfried.csv` | MD5 (Spalte `md5`), Dateiname (Spalten `filename` oder `file`) | `md5` |
| Technischer Index | `3_[ID]_for-transfer.index` (XML) | SHA-256 im Tag `<sha256>`, Dateiname im Attribut `name` des `<file>`-Tags | `sha256` |
| PREMIS XML | `5_[ID]_LZA_premis.xml` | SHA-256 im Tag `<premis:messageDigest>`, Dateiname aus `<premis:objectIdentifierValue>` (Pfad → nur Dateiname) | `sha256` |

**Wichtig:** Alle Vergleiche erfolgen **nur über den reinen Dateinamen** (`file_path.name.lower()`), nicht über den vollständigen Pfad.

### Integritätsstatus im XML-Index

Jede Datei erhält ein `<integrity_status>`-Element mit einem der drei Werte:

| Wert | Bedeutung | Bedingung |
|------|-----------|-----------|
| `verified` | Mindestens ein Hash-Algorithmus stimmt mit einer Referenzquelle überein | `errors`-Liste leer, `matches`-Liste nicht leer |
| `CORRUPTED_OR_MODIFIED` | Kein Referenz-Hash stimmt überein, aber Referenz existiert | `errors`-Liste nicht leer |
| `new_file` | Keine Referenz-Hashes für diese Datei gefunden | Dateiname nicht in `REFERENCE_HASHES` |

### Integritäts-Log (`5_[ID]_LZA_integrity.log`)

Das Log wird im Ordner `5_[ID]_LZA/logfiles/` erstellt und enthält:

| Abschnitt | Inhalt |
|-----------|--------|
| Kopfzeile | Projekt, ID, Datum |
| Bei Fehlern | Detaillierte Soll/Ist-Gegenüberstellung für SHA-256, SHA-512, MD5 (nur die in der Referenz vorhandenen) |
| Statistik | Anzahl verifizierte, neue, fehlerhafte Dateien |
| Liste | Vollständige Liste aller verifizierten Dateien (sortiert) |

### Metadaten-Extraktoren (identisch mit Skript G)

Das Skript verwendet die gleichen Extraktoren wie Skript G:
- `get_file_info` (alle Dateien)
- `run_siegfried` (alle Dateien)
- `extract_image_info` (bei MIME-Typ `image/*`, außer SVG)
- `extract_metadata_exiftool` (alle Dateien)
- `extract_metadata_ffprobe` (alle Dateien)
- `extract_mutagen_info` (alle Dateien)
- `extract_pdf_info` (nur `.pdf`)
- `extract_sam_specific` (nur `.sam`)
- `extract_musicxml_info` (nur `.mxl`)

### YARA-Regeln

- Regeldatei fest konfiguriert unter `YARA_RULES_FILE`
- Bei `csv`-Regel: Überspringen wenn `sam`, `eml` oder `tiff` ebenfalls matchen (Konfliktvermeidung)
- Gefundene Regeln fließen in die `<validity>`-Bestimmung ein

### Validierungslogik für `<validity>`

Das Element `<validity>` erhält `Yes` oder `No` basierend auf:

| Dateityp | Prüfung |
|----------|---------|
| `.pdf` | `PdfReader(file_path)` ohne Exception |
| `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp` | Magic-Header `PK` + `ZipFile.testzip() is None` |
| MIME-Typ `image/*` | `Image.open().verify()` ohne Exception |
| MIME-Typ `audio/*` oder `video/*` | `duration` oder `ffprobe_format_duration` vorhanden |
| `.mxl` | `document_title` oder `document_creator_tool` vorhanden |
| YARA-Match auf `SAM`, `EML`, `CSV`, `HTML`, `XHTML`, `TXT`, `ZIP_ARCHIVE` | `True` |
| Fallback | Wenn keine der obigen Bedingungen zutrifft, aber mehr als 5 Metadaten-Schlüssel extrahiert wurden → `Yes` |

### Vereinheitlichung von Metadaten-Schlüsseln (`unify_metadata_keys`)

- Schlüssel werden mit `sanitize_tag()` bereinigt (Leerzeichen, Doppelpunkte, Bindestriche, Punkte, Schrägstriche → `_`)
- Synonyme werden auf bevorzugte Schlüssel gemappt (z. B. `imagewidth`, `image_width`, `width` → `image_width`)
- Für `document_creator_tool` wird `is_likely_software_tool()` angewendet
- Datumsfelder werden mit `format_date_to_iso()` normalisiert
- Nicht gemappte Schlüssel bleiben erhalten (außer Blockliste `TAGS_TO_REMOVE`)

### XML-Ausgabe (`.index`)

- Root-Element: `<filetrove>`
- Pro Datei ein `<file>`-Element mit Attributen `path`, `name`, `extension`
- Metadaten alphabetisch sortiert
- Werte werden mit `sanitize_for_xml()` von ungültigen XML-Steuerzeichen befreit
- Blocklisten (`TAGS_TO_REMOVE` + `additional_blocklist`) filtern unerwünschte Tags

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| `BASE_DIR` (`5_[ID]_LZA`) existiert nicht | rote Meldung + `sys.exit(1)` |
| YARA-Regeldatei nicht gefunden | rote Meldung + `sys.exit(1)` |
| YARA-Regeln können nicht kompiliert werden | rote Meldung + `sys.exit(1)` |
| Externes Tool nicht gefunden (ExifTool, Siegfried, FFprobe, Hachoir) | rote Meldung + `return None` → `sys.exit(1)` |
| Einzelne Datei kann nicht verarbeitet werden | Fehlermeldung, Datei wird mit `<file error="...">` im XML vermerkt, Skript fährt fort |
| Keine Dateien verarbeitet | Abbruch ohne XML-Erstellung |

### Ausgabe-Dateien

| Datei | Pfad | Inhalt |
|-------|------|--------|
| Master-Index | `5_[ID]_LZA/5_[ID]_LZA.index` | XML mit Metadaten aller Dateien in Stufe 5 |
| Integritäts-Log | `5_[ID]_LZA/logfiles/5_[ID]_LZA_integrity.log` | Textprotokoll der Hash-Validierung |

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(destination_folder)`
- **macOS** → `subprocess.run(["open", destination_folder])`
- **Linux/andere** → `subprocess.run(["xdg-open", destination_folder])`

### Abhängigkeiten

**Externe Python-Pakete:**
- `mutagen`
- `PyPDF2`
- `Pillow`
- `yara-python`
- `chardet`

**Externe Tools (müssen im System-PATH oder an festen Pfaden verfügbar sein):**
- ExifTool (`EXIFTOOL_PATH`)
- Siegfried (`SIEGFRIED_PATH`)
- FFprobe (`FFPROBE_PATH`)
- Hachoir (`HACHOIR_METADATA_PATH`)

**Standardbibliothek:** `os`, `sys`, `csv`, `hashlib`, `json`, `subprocess`, `datetime`, `re`, `xml.etree.ElementTree`, `pathlib`, `zipfile`, `tempfile`, `shutil`

### Unterschiede zu Skript G (filetrove)

| Aspekt | Skript G | Skript K (Master-Index) |
|--------|----------|-------------------------|
| Basis-Verzeichnis | `4_[ID]_VL/` | `5_[ID]_LZA/` (komplette Stufe) |
| Referenz-Hashes | aus Stufe 1, 2, 3 (über `load_reference_hashes`) | aus allen sechs Quellen im `logfiles`-Ordner von Stufe 5 (über `load_all_lza_reference_hashes`) |
| SHA-512 Unterstützung | nein (nur über CSV) | ja (auch aus TXT-Log von Greaseweazle) |
| PREMIS als Quelle | nein | ja (liest SHA-256 aus `5_[ID]_LZA_premis.xml`) |
| Log-Ablage | `3_[ID]_for-transfer_integrity.log` (plus Kopie nach VL) | `5_[ID]_LZA_integrity.log` (nur in LZA/logfiles) |
| Ausgabe-Index | `3_[ID]_for-transfer.index` (plus Kopie nach VL) | `5_[ID]_LZA.index` (nur in LZA) |

### Wichtige Einschränkungen

- `.tiff`-Dateien werden nicht als Bilder erkannt (nur `.tif` für Hardware-Fotos)
- Die Hash-Referenzen werden **nur über den reinen Dateinamen** abgeglichen (nicht über Pfad)
- SHA-512 aus Greaseweazle-TXT-Log wird nur für `.raw`-Dateien extrahiert (Regex: `([\w\d\._-]+\.raw):\s*([a-fA-F0-9]{128})`)
- PREMIS-XML wird nur gelesen, wenn es den Namespace `http://www.loc.gov/premis/v3` verwendet

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT