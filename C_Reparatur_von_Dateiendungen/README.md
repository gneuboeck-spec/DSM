# Skript zur Reparatur von Dateiendungen (Stufe 2 zu Stufe 3)

Dieses Skript ist ein spezialisiertes Werkzeug zur Wiederherstellung von Dateiendungen. Es analysiert den Inhalt jeder endungslosen Datei, um den korrekten Typ zu ermitteln, und benennt die Dateien entsprechend um. Ein besonderes Merkmal ist der automatisierte Workflow, der Daten von der Extraktionsstufe (Stufe 2) in die Transferstufe (Stufe 3) überführt.

---

## Hauptfunktionen

*   **Automatischer Datentransfer:** Wenn das Zielverzeichnis in Stufe 3 noch nicht existiert, kopiert das Skript automatisch alle Daten von Stufe 2 (`2_[ID]_extracted-files/files`) nach Stufe 3 (`3_[ID]_for-transfer/files`).
*   **Siegfried-Integration:** Nutzt Siegfried (`sf.exe`) unter dem fest hinterlegten Pfad `C:\Program Files\Siegfried\sf.exe` zur Identifizierung von Dateiformaten via PRONOM und MIME.
*   **Multimedia-Unterscheidung:** Verwendet `ffprobe.exe`, um bei MPEG-4-Dateien (`fmt/199`) zwischen Video (`.mp4`) und reinem Audio (`.m4a`) zu unterscheiden.
*   **Erweiterte Fallback-Logik:**
    *   **ZIP-Analyse:** Erkennt OpenDocument-Formate (`.odt`, `.ods`) innerhalb von ZIP-Containern.
    *   **XML-Prüfung:** Identifiziert "Flat XML" Dokumente.
    *   **Tabellen-Erkennung:** Erkennt CSV-Strukturen und SYLK-Dateien (`.slk`) anhand von Delimitern und Signaturen.
    *   **Text-Validierung:** Klassifiziert unbekannte Dateien als `.txt`, wenn der Inhalt überwiegend aus druckbaren Zeichen besteht (UTF-8/Latin-1).
*   **Protokollierung:** Erstellt ein detailliertes Log-File direkt im Stufe-3-Ordner zur vollständigen Nachvollziehbarkeit.

---

## TREE-Struktur & Dateipfade

Das Skript bildet die Brücke zwischen der Extraktion und der aktiven Bearbeitung:

```text
[AC-Nummer]/[Datenträger-ID]/
├── 2_[ID]_extracted-files/
│   └── files/                              <-- QUELLE (Daten aus der Extraktion)
└── 3_[ID]_for-transfer/                    <-- ZIEL (Arbeitsbereich für Stufe 3)
    ├── files/                              <-- Hier werden Endungen repariert
    └── 3_[ID]_for-transfer_repair-file-extension.log <-- LOG-DATEI
```
---

## Technische Voraussetzungen

1.  **Python:** Version 3.10 oder neuer empfohlen.
2.  **Siegfried:** Muss zwingend unter `C:\Program Files\Siegfried\sf.exe` installiert sein.
3.  **FFmpeg:** Die `ffprobe.exe` muss im System-PATH verfügbar sein.

---

## Ausführung

Das Skript kann auf zwei Arten gestartet werden:

1.  **Automatisiert (Empfohlen):** Übergabe der AC-Nummer und Datenträger-ID als Argumente via Kommandozeile oder `start.bat`.
    Beispiel: `python repair_extensions.py AC_0001 CD_01`
2.  **Interaktiv:** Falls keine Argumente übergeben werden, fragt das Skript die AC-Nummer und die ID beim Start manuell ab.

### Ablauf der Ausführung

1.  **Vorbereitung:** Falls der Ordner in Stufe 3 fehlt, wird der Inhalt von Stufe 2 komplett dorthin kopiert.
2.  **Validierung:** Prüfung der Pfade zu Siegfried und FFprobe.
3.  **Suche:** Rekursive Suche nach Dateien ohne Suffix im Ordner `Stage 3/files`.
4.  **Analyse & Rename:** Durchführung der Identifizierung. Falls die Zieldatei bereits existiert, erfolgt eine automatische Nummerierung (z.B. `datei_1.jpg`).
5.  **Logging:** Jede Aktion wird mit Zeitstempel und Quelle (z.B. "via PRONOM ID (Manuell)") im Log protokolliert.
6.  **Abschluss:** Ausgabe einer Zusammenfassung und optionale Abfrage zum Öffnen des Zielordners im Explorer.

---

## Detaillierte Hinweise zum Skriptverhalten

### Vollständiges PRONOM-Mapping

Das Skript enthält folgende direkte Zuordnungen von PRONOM-IDs zu Dateiendungen:

| PRONOM ID | Dateiendung |
|-----------|-------------|
| fmt/189, fmt/190, fmt/191, fmt/276 | `.pdf` |
| fmt/40, x-fmt/65 | `.doc` |
| fmt/612 | `.docx` |
| fmt/214 | `.xls` |
| fmt/595 | `.xlsx` |
| fmt/291 | `.odt` |
| fmt/290 | `.ods` |
| fmt/292 | `.odp` |
| fmt/353, fmt/354 | `.tif` |
| fmt/14, fmt/15 | `.jpg` |
| fmt/11 | `.png` |
| fmt/846 | `.cwk` |
| fmt/1439 | `.pages` |
| fmt/397 | `.mus` |
| fmt/279 | `.flac` |
| fmt/569 | `.mkv` |
| fmt/203 | `.ogg` |
| fmt/384 | `.mxf` |
| x-fmt/191 | `.sam` |
| x-fmt/18 | `.csv` |
| fmt/280 | `.tex` |
| fmt/596 | `.m4a` |

Zusätzlich gibt es eine manuelle Mapping-Tabelle für Formatnamen:
- `AppleWorks Word Processing` → `.cwk`
- `Ami Pro` → `.sam`

### Sonderbehandlung MPEG-4 (fmt/199)

Bei PRONOM-ID `fmt/199` prüft das Skript mit `ffprobe.exe`, ob ein Videostream vorhanden ist:
- **mit Videostream** → `.mp4`
- **ohne Videostream** → `.m4a`

### Erkennungsreihenfolge

Das Skript versucht in folgender Reihenfolge, eine Dateiendung zu bestimmen:

1. **Siegfried-basierte Erkennung** (aus `sf.exe -json`):
   - PRONOM-ID in der Mapping-Tabelle → Endung (Quelle: "PRONOM ID (Manuell)")
   - Sonderfall `fmt/199` → `.mp4` oder `.m4a` (Quelle: "MPEG-4 (mit/nur Audio)")
   - MIME-Typ (außer `text/plain`, `application/octet-stream`) → Endung via `mimetypes.guess_extension()` (Quelle: "MIME-Typ (Automatisch)")
   - Formatname in `format_name_to_ext_map` → Endung (Quelle: "Formatname (Manuell)")

2. **Fallback-Erkennung** (falls Siegfried nichts liefert):
   - ZIP-Prüfung mit `zipfile.is_zipfile()` und `mimetype`-Datei → `.odt` oder `.ods` (Quelle: "Fallback (ZIP-Mimetype)")
   - Flat XML-Prüfung auf `<office:document-content` oder `<office:document-spreadsheet` → `.odt` oder `.ods` (Quelle: "Fallback (Flat XML)")
   - Tabellenerkennung via `determine_text_table_extension()` → `.slk` (SYLK-Signatur) oder `.csv` (Delimiter `;`, `,`, `\t`, `|` mit Konsistenzprüfung)
   - Text-Erkennung via `is_likely_text_file()` (ASCII-Zeichen > 90%) → `.txt` (Quelle: "Fallback (Plain Text)")

3. **Keine Zuordnung möglich** → Logeintrag mit Siegfried-Informationen (Formatname, PRONOM-ID)

### Simulationsmodus

Im Skript existiert die globale Variable `DRY_RUN = False`. Bei `DRY_RUN = True` werden keine tatsächlichen Umbenennungen durchgeführt; alle Aktionen werden nur simuliert und mit `[SIMULATION]` im Log gekennzeichnet.

### Log-Datei

Die Log-Datei wird unter `3_[ID]_for-transfer/3_[ID]_for-transfer_repair-file-extension.log` erstellt. Jeder Eintrag enthält einen Zeitstempel `[YYYY-MM-DD HH:MM:SS]`. Folgende Ereignisse werden protokolliert:
- Skriptstart
- Gefundene Dateien ohne Endung
- Umbenennungen (mit Quellenangabe)
- Fehler beim Umbenennen
- Nicht zugeordnete Dateien (mit Siegfried-Ergebnis)
- Abschlussstatistik

### Namenskonflikte

Wenn eine Datei umbenannt wird und der Zielname bereits existiert, hängt das Skript automatisch `_1`, `_2`, usw. an den Dateinamen an (vor der Endung).

### Dateien, die ignoriert werden

Das Skript untersucht **nur Dateien ohne Dateiendung** (`file.suffix == ""`). Folgende Dateien werden übersprungen:
- Dateien mit einer vorhandenen Endung (z.B. `.txt`, `.jpg`)
- Versteckte Dateien (Name beginnt mit `.`)
- Verzeichnisse

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| Siegfried nicht unter `C:\Program Files\Siegfried\sf.exe` | rote Fehlermeldung + `sys.exit(1)` |
| `ffprobe.exe` nicht im PATH | rote Fehlermeldung + `sys.exit(1)` |
| Quell-Ordner Stufe 2 existiert nicht | rote Fehlermeldung + `sys.exit(1)` |
| Kopiervorgang von Stufe 2 nach Stufe 3 schlägt fehl | rote Fehlermeldung + `sys.exit(1)` |
| Log-Ordner existiert nicht | rote Fehlermeldung + `sys.exit(1)` |
| Analyse-Ordner in Stufe 3 existiert nicht | rote Fehlermeldung + `sys.exit(1)` |

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Analyse beendet. Zielordner öffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(config["analysis_folder"])`
- **macOS/Linux** → nicht implementiert (da `os.startfile` nur auf Windows funktioniert)

### Abhängigkeiten (zusätzlich)

Neben den in der README genannten Tools benötigt das Skript keine externen Python-Bibliotheken. Verwendet werden ausschließlich Module der Python-Standardbibliothek: `os`, `subprocess`, `json`, `sys`, `mimetypes`, `pathlib`, `shutil`, `datetime`, `zipfile`, `csv`.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT