# 02 - Duplikatenfinder

Dieses Skript identifiziert und entfernt Dateidubletten in einem Verzeichnis. Es erkennt sowohl **binäre Dubletten** (identische Dateien, SHA-256-basiert) als auch **inhaltliche Dubletten** (Dokumente mit gleichem Textinhalt, aber unterschiedlichen Formaten wie `.pdf`, `.docx`, `.odt` etc.). Es ist der empfohlene erste Schritt in der Pipeline, um den Datenbestand zu verschlanken und nachfolgende Textvergleiche drastisch zu beschleunigen.

## Struktur

    02_Duplikatenfinder/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- 02_Duplikatenfinder.py         <-- Ausführbare Python-Datei

## Funktionsweise

### 1. Binäre Dubletten-Erkennung

1. **Größen-Filter**: Gruppiert alle Dateien nach ihrer exakten Byte-Größe (nur Dateien gleicher Größe können Dubletten sein).
2. **SHA-256-Hashing**: Berechnet Prüfsummen nur für die potenziellen Dubletten (Chunk-Größe: 8 MB), was extrem ressourcenschonend ist.
3. **Gruppierung**: Fasst Dateien mit identischem Größe+Hash zu einer Dubletten-Gruppe zusammen.

### 2. Inhaltliche Dubletten-Erkennung (pro Dokument)

4. **Textextraktion**: Aus allen Dokumentenformaten wird der reine Text extrahiert – zuerst über Python-Bibliotheken (schnell), bei Bedarf über LibreOffice als Fallback.
5. **Normalisierung**: Der Text wird maximal normalisiert (Unicode-NFKC, Kleinschreibung, Trennstrich-Reparatur, Entfernen aller Nicht-Alphanumerik, Seitenkennungen wie `page123`/`seite123`, abschließende Ziffern).
6. **Content-Hash**: Aus dem normalisierten Text wird ein SHA-256-Hash gebildet. Dokumente mit gleichem Content-Hash gelten als inhaltlich identisch und werden zu einer gemeinsamen Gruppe zusammengeführt – auch über Formatgrenzen hinweg.
7. **Original-Auswahl**: Innerhalb einer Gruppe gewinnt das Format mit der höchsten Priorität (siehe `FORMAT_PRIORITAET`).

### 3. Vorschau & Löschung

8. **Vorschau-Modus**: Erstellt eine **XLSX-Datei mit klickbaren Hyperlinks** und eine CSV-Backup-Datei, und öffnet die XLSX automatisch zur Kontrolle.
9. **Sichere Löschung**: Löscht nach expliziter Bestätigung alle Duplikate, behält aber immer genau eine Datei pro Gruppe als "Original". Schreibgeschützte Dateien werden automatisch entsperrt.

## Bevorzugtes Original-Format

Innerhalb einer Dubletten-Gruppe wird das Original nach folgender Priorität behalten (erster Treffer gewinnt):

| Priorität | Formate |
|-----------|---------|
| 1 | `.pdf`, `.pdfa` |
| 2 | `.docx`, `.doc` |
| 3 | `.odt` |
| 4 | `.rtf` |
| 5 | `.txt` |
| 6 | `.md` |
| – | alle anderen (z. B. `.html`, `.xml`, `.fodt`, `.csv`) landen am Ende |

## Konfiguration

Öffne die Datei und passe bei Bedarf folgende Variablen an:

    DRY_RUN = False          # Auf True setzen, um das Skript nur zu simulieren, ohne Dateien zu löschen
    CHUNK_SIZE = 8 * 1024 * 1024   # Chunk-Größe für SHA-256-Hashing (Standard: 8 MB)

Die Format-Priorität kann in der Liste `FORMAT_PRIORITAET` angepasst werden.

## Abhängigkeiten

**Zwingend erforderlich:**

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **`openpyxl`** – wird für die XLSX-Erstellung mit klickbaren Hyperlinks benötigt. Das Skript bricht ohne `openpyxl` mit einer Installationsanleitung ab.
- **Standardbibliothek:** `os`, `sys`, `hashlib`, `csv`, `stat`, `subprocess`, `tkinter`, `pathlib`, `collections`, `datetime`, `re`, `logging`, `tempfile`, `unicodedata`, `shutil`

**Optional (je nach verwendetem Dateiformat):**

- `pypdf` – für PDF-Textextraktion
- `python-docx` – für `.docx`-Textextraktion
- `odfpy` – für `.odt`-Textextraktion
- `striprtf` – für `.rtf`-Textextraktion

**Extern:**

- **LibreOffice** (empfohlen) – als Fallback für exotische/alte Formate (`.doc`, `.xls`, `.ppt`, `.pages`, `.wpd`, `.epub`, …). Das Skript sucht automatisch an den Standard-Installationspfaden unter Windows, Linux und macOS.

Installation der Python-Pakete:

    pip install -r requirements.txt

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Verwendung

### Über das Menü (empfohlen)

1. `Start.bat` im Root doppelklicken
2. Im Hauptmenü `T` (Textdokumente_vergleichen) eingeben
3. Im Dialog Eingabeverzeichnis (Quelle) und Ausgabeverzeichnis (Logs) wählen
4. Im Menü das Skript `02_Duplikatenfinder.py` auswählen

### Direkt über die Kommandozeile

    python 02_Duplikatenfinder.py <quellverzeichnis> <log_verzeichnis>

**Beispiel:**

    python 02_Duplikatenfinder.py "C:\Daten\MeineSammlung" "C:\Daten\Logs"

### Ablauf

1. Das Skript scannt das Quellverzeichnis rekursiv.
2. Es werden binäre und (falls Dokumente vorhanden) inhaltliche Dubletten ermittelt.
3. Eine **Vorschau-XLSX** (mit klickbaren Links) und eine **Vorschau-CSV** werden erstellt; die XLSX wird automatisch geöffnet.
4. Ein Dialog fragt, ob die als "VORGEMERKT" markierten Dateien wirklich gelöscht werden sollen.
5. Nach Bestätigung werden die Duplikate gelöscht und ein **finales Log** (`duplikaten_GELÖSCHT_*.xlsx` und `*.csv`) wird geschrieben.
6. Auf Wunsch wird am Ende das bereinigte Quellverzeichnis geöffnet.

## Log-Dateien

Für Vorschau und Final-Log werden **jeweils zwei Dateien** erstellt:

- eine **XLSX-Datei** mit klickbaren Hyperlinks (wird automatisch geöffnet),
- eine **CSV-Datei** als Rohdaten-Backup.

Beide enthalten folgende Spalten:

| Spalte | Bedeutung |
|--------|-----------|
| `Gruppe_ID` | Eindeutige Gruppenkennung (`GRUPPE_001`, …) |
| `Typ` | `Binäre Dublette` oder `Inhaltliche Dublette` |
| `Dateiname` | Name der Datei |
| `Relativer_Pfad` | Pfad relativ zum Quellverzeichnis (in XLSX als klickbarer Hyperlink) |
| `Dateigröße` | Lesbare Größe (KB/MB/GB) |
| `SHA256` | Hash der Gruppe (binär oder Content-Hash) |
| `Aktion` | `BEHALTEN (Original)`, `GELÖSCHT (Duplikat)`, `ZUM LÖSCHEN VORGEMERKT`, `FEHLER: …` |

**Dateinamen:**

- Vorschau: `duplikaten_VORSCHAU_<Ordnername>_<YYYYMMDD_HHMMSS>.xlsx` und `.csv`
- Final: `duplikaten_GELÖSCHT_<Ordnername>_<YYYYMMDD_HHMMSS>.xlsx` und `.csv`

## Hinweise & Sicherheit

- **Erst Vorschau prüfen!** Vor dem endgültigen Löschen wird immer eine Vorschau-Datei erstellt und geöffnet. Prüfe diese gründlich – besonders bei inhaltlichen Dubletten, bei denen das bevorzugte Format möglicherweise nicht deinen Erwartungen entspricht.
- **`DRY_RUN = True`** führt einen kompletten Testlauf durch, ohne irgendetwas zu löschen. Die Aktionen werden als `GELÖSCHT (Simulation)` protokolliert.
- **Ausnahmen**: Dateien ohne aussagekräftigen Textinhalt (weniger als 50 Zeichen) werden nicht in die inhaltliche Dubletten-Erkennung einbezogen (`NO_MEANINGFUL_TEXT`).
- **Konflikte mit dem Original**: Das Skript löscht grundsätzlich nur Dateien ab Position 2 jeder Gruppe – die bevorzugte Datei bleibt immer erhalten.
- **Backup empfohlen**: Bei produktiven Läufen vorab ein Backup des Quellverzeichnisses anlegen.

## Pipeline-Kontext

Dieses Skript ist für den **ersten Schritt** einer mehrstufigen Aufräum-Pipeline gedacht. Nach der binären und inhaltlichen Dubletten-Bereinigung können weitere Skripte (z. B. für OCR, Metadaten-Anreicherung, Klassifizierung) auf dem verschlankten Bestand aufsetzen.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT