# 05 - Dokumente vergleichen

Das Kernstück der Pipeline. Dieses Skript führt hochperformante, mathematische Textvergleiche durch, um verschiedene Versionen desselben Dokuments zu identifizieren und zu Gruppen zusammenzufassen. Dies ermöglicht eine realistische Einschätzung des *einzigartigen* Textumfangs.

## Struktur

    05_Dokumente_vergleichen/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- 05_Dokumente_vergleichen.py    <-- Ausführbare Python-Datei

## Funktionsweise

1. **Textextraktion**: Liest Texte aus `.docx`, `.pdf`, `.odt`, `.txt` etc. (mit Cache-System für Konvertierungen).
2. **Fingerabdruck-Erstellung**: Erstellt Wortmengen (Jaccard-Index) und kürzt sehr lange Texte (Smart-Modus: Anfang + Ende), um RAM zu sparen.
3. **Längen-Bucketing**: Vergleicht nur Dokumente ähnlicher Länge, um die Rechenzeit von O(n²) drastisch zu reduzieren.
4. **Multiprocessing-Vergleich**: Prüft Paare parallel auf:
   - Wort-Overlap (Jaccard-Ähnlichkeit)
   - Längenverhältnis
   - Exakte Zeichen-Übereinstimmung (RapidFuzz / difflib)
5. **Union-Find-Algorithmus**: Bildet aus den Paar-Übereinstimmungen logische Dokumentengruppen und bestimmt ein "Basisdokument" (z. B. das älteste).

## Einstellungs-Dialog

Beim Start öffnet sich ein GUI-Fenster zur Anpassung aller Schwellenwerte. Leer gelassene Felder verwenden die Standardwerte.

| Parameter | Standard | Bedeutung |
|-----------|----------|-----------|
| `SIMILARITY_THRESHOLD` | 0.40 (40%) | Mindestens erforderliche exakte Zeichenübereinstimmung |
| `LENGTH_RATIO_THRESHOLD` | 0.35 (35%) | Maximale erlaubte Längendifferenz (ein Text darf max. 65% kürzer sein) |
| `WORD_OVERLAP_THRESHOLD` | 0.25 (25%) | Mindestens gemeinsamer Wortschatz (Jaccard-Index) |
| `MIN_TEXT_LENGTH` | 200 Zeichen | Texte unter dieser Länge werden ignoriert |
| `EXCERPT_THRESHOLD` | 0.80 (80%) | Ähnlichkeitsschwelle für Auszüge (kurze Texte, die stark abweichen) |
| `MAX_COMPARE_LENGTH` | 2.000.000 Zeichen | Maximale Textlänge für den Vergleich (Rest wird gekürzt) |
| Sampling-Modus | Standard | `Standard` (nur Anfang) oder `Smart` (Anfang + Ende) |
| `BASE_CRITERION` | `oldest` | Basisdokument-Auswahl: `oldest`, `newest`, `longest`, `shortest` |

Der Dialog enthält zusätzlich zwei Hilfe-Buttons:
- **Ablauf**: Erklärt in Textform den kompletten 7-Phasen-Ablauf (Textextraktion → Fingerabdrücke → Bucketing → Paralleler Vergleich → Union-Find → Metriken → Export).
- **Hilfe**: Detaillierte Erklärungen aller Parameter mit Beispielen und Empfehlungen zum Erhöhen/Senken.

## Ausgabe

Nach dem Lauf werden drei Dateien im Ausgabeverzeichnis abgelegt:

| Datei | Inhalt |
|-------|--------|
| `versionen_analyse.csv` | Rohdaten aller Zuordnungen und prozentualen Änderungen zum Basisdokument (UTF-8 mit BOM, Semikolon als Trenner) |
| `versionen_analyse_farbig.xlsx` | Farblich kodierte Excel-Tabelle (20 Pastellfarben pro Gruppe), **klickbare Hyperlinks** auf die Originaldateien, Auto-Filter, eingefrorene Kopfzeile |
| `log_dokumentenvergleich_<YYYYMMDD_HHMMSS>.txt` | Vollständige Konsolenausgabe (alle print-Ausgaben werden per `Tee`-Klasse mitgeschrieben) |

### Farbkodierung in der Excel-Datei

- **20 Pastellfarben**: jede Gruppe bekommt eine eigene Farbe
- **Gelb**: Kurztexte (weniger als 200 Zeichen)
- **Grau**: nicht gruppierte Dokumente
- **Hyperlinks**: in der Spalte `Relativer_Pfad` klickbar (öffnet die Datei im Standardprogramm)

### Spalten in CSV / XLSX

| Spalte | Inhalt |
|--------|--------|
| `Relativer_Pfad` | Pfad relativ zum Eingabeverzeichnis (als Hyperlink in XLSX) |
| `Dateiname` | Dateiname |
| `Dateityp` | Dateiendung |
| `Versions_Gruppe` | Gruppenzuordnung (`GRUPPE_001`, …) |
| `Basisdokument` | Relativer Pfad des Basisdokuments (oder `(Basis)` für das Basis selbst) |
| `Übereinstimmung_Zeichen` | Absolute Anzahl gleicher Zeichen mit dem Basisdokument |
| `Übereinstimmung_Wörter` | Absolute Anzahl gleicher Wörter mit dem Basisdokument |
| `Änderung_Zeichen_%` | Prozentuale Änderung der Zeichenanzahl vs. Basis |
| `Änderung_Wörter_%` | Prozentuale Änderung der Wortanzahl vs. Basis |
| `Letzte_Aenderung` | Änderungsdatum der Datei |
| `Dateigroesse_Bytes` | Dateigröße in Bytes |
| `Dokumententyp` | `Version` (gruppiert) oder leer |
| `KI_Gefundene_Gruppe` | (Reserviert für die nachfolgende KI-Analyse) |
| `KI_Semantische_Aehnlichkeit` | (Reserviert für die nachfolgende KI-Analyse) |
| `KI_Ergebnis` | (Reserviert für die nachfolgende KI-Analyse) |

Die drei KI-Spalten bleiben in diesem Skript leer und werden von Skript `06_KI_Analyse` befüllt.

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Python-Pakete** (in `requirements.txt` enthalten):
  - `python-docx` – für `.docx`-Textextraktion
  - `pymupdf` – für PDF-Extraktion (schnell)
  - `pdfplumber` – für PDF-Extraktion (Fallback)
  - `openpyxl` – für die Excel-Ausgabe mit Hyperlinks
  - `rapidfuzz` – C++-beschleunigter Textvergleich (dringend empfohlen)
  - `tqdm` – Fortschrittsbalken (optional, aber empfohlen)
- **Extern:** LibreOffice (für alte/komplexe Formate wie `.doc`, `.wpd`, `.pages`) – wird über `shutil.which()` gesucht, Fallback auf Standard-Installationspfade.

Installation:

    pip install -r requirements.txt

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

### Über das Menü (empfohlen)

1. `Start.bat` im Root doppelklicken
2. Im Hauptmenü `T` (Textdokumente_vergleichen) eingeben
3. Im Dialog Eingabeverzeichnis (Quelle) und Ausgabeverzeichnis wählen
4. Im Menü das Skript `05_Dokumente_vergleichen.py` auswählen
5. Im Einstellungsdialog die Parameter prüfen oder Standardwerte nutzen

### Direkt über die Kommandozeile

    python 05_Dokumente_vergleichen.py <eingabe_verzeichnis> <ausgabe_verzeichnis>

**Beispiel:**

    python 05_Dokumente_vergleichen.py "C:\Daten\MeineSammlung" "C:\Daten\Logs"

## Ablauf

1. **Textextraktion**: Alle unterstützten Dateien im Eingabeverzeichnis werden gelesen. Konvertierungen (z. B. `.doc` → `.txt`) werden im versteckten Ordner `.conversion_cache` zwischengespeichert.
2. **Einstellungsdialog**: Der Benutzer kann die Schwellenwerte anpassen oder Standardwerte nutzen.
3. **Fingerabdrücke**: Für jede Datei wird eine Wortmenge und ein gekürzter Text erstellt.
4. **Längen-Bucketing**: Dokumente werden in logarithmische Längen-Buckets einsortiert; nur Dokumente im selben oder benachbarten Bucket werden verglichen.
5. **Paralleler Vergleich**: Alle CPU-Kerne arbeiten an der Paarprüfung. Jedes Paar durchläuft drei Filter (Wort-Overlap, Längenverhältnis, Zeichenähnlichkeit).
6. **Union-Find**: Aus den Paar-Ergebnissen werden Dokumentengruppen gebildet.
7. **Metriken & Export**: Basisdokument pro Gruppe wählen, Änderungen berechnen, CSV + XLSX + Log schreiben.

## Detaillierte Hinweise

### Textextraktion

- `.docx` → `python-docx` (direkt), Fallback LibreOffice
- `.doc` → erst `python-docx` versuchen, dann LibreOffice
- `.pdf` → `pymupdf` (schnell), Fallback `pdfplumber`
- `.odt` / `.ods` / `.odf` → direkt aus dem ZIP (`content.xml`)
- `.rtf` → Regex-basierte Bereinigung
- `.xml`, `.xhtml`, `.fodt` → `xml.etree` mit Namespace-Behandlung
- `.txt`, `.md`, `.csv`, `.log`, `.tex`, `.rst` → direktes Einlesen

### Cache-System

Konvertierungen werden unter `.conversion_cache` (im Eingabeverzeichnis) zwischengespeichert. Der Cache-Dateiname enthält den Zeitstempel der Quelldatei, sodass bei Änderungen automatisch neu konvertiert wird. Das beschleunigt wiederholte Läufe enorm.

### Performance-Optimierungen

- **Längen-Bucketing**: Reduziert die Anzahl zu vergleichender Paare um ca. 95%.
- **Multiprocessing**: Nutzt alle CPU-Kerne via `multiprocessing.Pool`.
- **RapidFuzz**: C++-beschleunigter Textvergleich (falls installiert).
- **Smart Sampling**: Bei sehr langen Texten werden Anfang und Ende verglichen.

### Fehlerbehandlung

- Nicht lesbare Dateien werden übersprungen und im Log als „Dateien ohne Text" aufgeführt.
- Der Dialog prüft die Eingaben auf Wertebereiche (0.0–1.0 für Schwellenwerte, Mindestlängen).
- Bei fehlenden Argumenten wird eine Fehlermeldung ausgegeben und das Programm beendet.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT