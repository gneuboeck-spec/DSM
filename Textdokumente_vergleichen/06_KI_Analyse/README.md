# 06 - KI-Analyse

Ergänzt die syntaktische Analyse um eine semantische Ebene. Dieses Skript nutzt ein vortrainiertes KI-Sprachmodell, um kurze Texte (wie Abstracts, Zusammenfassungen, Rezensionen oder Einleitungen) zu erkennen und den in Schritt 05 gebildeten Hauptdokumentengruppen zuzuordnen.

## Struktur

    06_KI_Analyse/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- 06_KI_Analyse.py               <-- Ausführbare Python-Datei

## Funktionsweise

1. **Modell-Laden**: Lädt `paraphrase-multilingual-mpnet-base-v2` (mehrsprachig, optimiert für semantische Ähnlichkeit) in einen zentralen Cache (`~/.ki_model_cache`).
2. **Basis-Embeddings**: Erstellt Vektorrepräsentationen der Basisdokumente aus Schritt 05.
3. **Intelligente Filterung**: Prüft nur Dokumente, die entweder:
   - Ein Trigger-Wort im Namen haben (siehe unten), **oder**
   - Innerhalb einer konfigurierbaren Längengrenze liegen (Standard: 100 bis 5.000 Zeichen).
4. **Kosinus-Ähnlichkeit**: Berechnet die semantische Nähe des Kandidaten zu allen Basis-Embeddings und wählt die ähnlichste Gruppe aus.
5. **Schwellenwert-Prüfung**: Wenn die höchste Ähnlichkeit den eingestellten Threshold überschreitet, wird das Dokument als Kurztext der Gruppe zugeordnet.

## Einstellungs-Dialog

Beim Start öffnet sich ein GUI-Fenster zur Anpassung der Parameter.

| Parameter | Standard | Bedeutung |
|-----------|----------|-----------|
| `SEMANTIC_THRESHOLD_DEFAULT` | 0.55 (55%) | Mindest-Ähnlichkeit für eine Zuordnung |
| `MIN_TEXT_LENGTH_DEFAULT` | 100 Zeichen | Kürzere Dokumente werden nicht geprüft |
| `MAX_TEXT_LENGTH_DEFAULT` | 5.000 Zeichen | Längere Dokumente werden nur bei Trigger-Wort geprüft |

Der Dialog enthält zusätzlich zwei Hilfe-Buttons:
- **Ablauf**: Erklärt in Textform den 6-Phasen-Ablauf (Modell-Laden → Basis-Extraktion → Embeddings → Kandidatenfilterung → Kosinus-Ähnlichkeit → Zuordnung).
- **Hilfe**: Detaillierte Erklärungen aller Parameter.

## Trigger-Wörter

Folgende Wörter werden im Dateinamen (in Kleinbuchstaben) gesucht. Ist eines vorhanden, wird das Dokument auch dann geprüft, wenn es länger als die Maximallänge ist:

`abstract`, `zusammenfassung`, `summary`, `review`, `rezension`, `einleitung`, `aufsatz`, `essay`, `beitrag`, `article`

## Ausgabe

Das Skript schreibt **drei Dateien** in das Ausgabeverzeichnis:

| Datei | Inhalt |
|-------|--------|
| `versionen_analyse_mit_ki.csv` | Rohdaten aller Zuordnungen (UTF-8 mit BOM, Semikolon als Trenner) |
| `versionen_analyse_mit_ki_farbig.xlsx` | Farbig kodierte Excel-Tabelle mit klickbaren Hyperlinks, Auto-Filter, eingefrorener Kopfzeile |
| `log_ki_analyse_<YYYYMMDD_HHMMSS>.txt` | Vollständige Konsolenausgabe (per `Tee`-Klasse) |

### Neue Spalten gegenüber Schritt 05

Die Ausgabedateien enthalten zusätzlich:

| Spalte | Inhalt |
|--------|--------|
| `Dokumententyp` | `Kurztext` (wenn KI-Zuordnung erfolgreich) oder leer |
| `KI_Gefundene_Gruppe` | Name der zugeordneten Gruppe (`GRUPPE_001`, …) |
| `KI_Semantische_Aehnlichkeit` | Prozentwert der höchsten Ähnlichkeit (z. B. `78.42%`) |
| `KI_Ergebnis` | Klartext-Beschreibung der Zuordnung oder Begründung, warum nicht zugeordnet |

### Mögliche Werte in `KI_Ergebnis`

- `✅ Kurztext-Zuordnung: GRUPPE_001` – erfolgreich zugeordnet
- `❌ Keine passende Gruppe (32.1%)` – niedrigste Ähnlichkeit unter dem Threshold
- `⚠️ Nicht geprüft (kein Trigger/außerhalb 100-5000 Zeichen)` – Filter hat das Dokument ausgeschlossen
- `⚠️ Kein Text extrahierbar` – Datei konnte nicht gelesen werden
- `⚠️ Datei nicht gefunden` – Pfad in der CSV existiert nicht mehr
- `⏭️ Übersprungen (Analyse-Ausgabedatei)` – Log-Dateien und Analyse-CSVs werden ignoriert

### Farbkodierung in der Excel-Datei

- **20 Pastellfarben**: jede Gruppe bekommt eine eigene Farbe (identisch zu Schritt 05)
- **Gelb (`FFEB99`)**: Kurztexte (KI-zugeordnet)
- **Grau (`F2F2F2`)**: nicht gruppierte Dokumente
- **Hyperlinks**: in der Spalte `Relativer_Pfad` klickbar

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Python-Pakete** (in `requirements.txt` enthalten):
  - `sentence-transformers` – für die semantische Analyse
  - `torch` – Backend für sentence-transformers (wird automatisch mitinstalliert)
  - `pymupdf` – für PDF-Textextraktion
  - `python-docx` – für `.docx`-Textextraktion
  - `openpyxl` – für die Excel-Ausgabe
- **Externe Tools:** keine (im Gegensatz zu Schritt 05 wird LibreOffice hier nicht benötigt, da nur direkte Textformate gelesen werden).

Installation:

    pip install -r requirements.txt

**Hinweis zum ersten Start:** Das KI-Modell (`paraphrase-multilingual-mpnet-base-v2`) wird beim ersten Lauf aus dem Internet heruntergeladen (ca. 400 MB) und im Cache-Verzeichnis `~/.ki_model_cache` gespeichert. Nachfolgende Läufe laden das Modell aus dem Cache und sind deutlich schneller.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

### Über das Menü (empfohlen)

1. `Start.bat` im Root doppelklicken
2. Im Hauptmenü `T` (Textdokumente_vergleichen) eingeben
3. Im Dialog Eingabeverzeichnis (Quelle) und Ausgabeverzeichnis wählen
4. Im Menü das Skript `06_KI_Analyse.py` auswählen
5. Im Einstellungsdialog die Parameter prüfen oder Standardwerte nutzen

### Direkt über die Kommandozeile

    python 06_KI_Analyse.py <eingabe_verzeichnis> <ausgabe_verzeichnis>

**Beispiel:**

    python 06_KI_Analyse.py "C:\Daten\MeineSammlung" "C:\Daten\Logs"

### Vorbedingung

Das Skript liest die Datei `versionen_analyse.csv` aus dem **Ausgabeverzeichnis**. Diese muss zuvor von `05_Dokumente_vergleichen.py` erzeugt worden sein. Fehlt die Datei, bricht das Skript mit einer entsprechenden Meldung ab.

## Ablauf

1. **Modell laden**: `sentence-transformers` wird initialisiert; das Modell wird aus dem Cache geladen (oder beim ersten Lauf heruntergeladen).
2. **Basisgruppen identifizieren**: Aus der CSV werden alle Gruppen entnommen und deren Basisdokumente (markiert durch `(Basis)`) identifiziert.
3. **Basis-Embeddings erstellen**: Für jede Basis wird der Text extrahiert (gekürzt auf 3.000 Zeichen für die KI) und in einen Vektor umgewandelt.
4. **Kandidaten filtern**: Für jede nicht-gruppierte Datei wird geprüft, ob sie ein Trigger-Wort im Namen hat oder ob ihre Länge im Fenster `[MIN_TEXT_LENGTH, MAX_TEXT_LENGTH]` liegt.
5. **Kosinus-Ähnlichkeit**: Für die Kandidaten wird ein Embedding erstellt und mit allen Basis-Embeddings verglichen. Die höchste Ähnlichkeit gewinnt.
6. **Zuordnung**: Überschreitet die höchste Ähnlichkeit den Threshold, wird das Dokument als Kurztext der Gruppe zugeordnet.
7. **Export**: Alle Zeilen werden in eine neue CSV und XLSX geschrieben; ein Log wird erstellt.

## Detaillierte Hinweise

### Textextraktion

Die Funktion `extract_text_simple()` liest:
- `.txt` → direktes Einlesen
- `.docx` → via `python-docx`
- `.pdf` → via `pymupdf`
- `.odt` / `.ods` / `.odf` → direkt aus dem ZIP (`content.xml`)
- Alle anderen Formate: kein Text (werden als `Nicht geprüft` markiert)

Im Gegensatz zu Schritt 05 wird **kein LibreOffice-Fallback** verwendet. Das ist bewusst, da die KI-Analyse sich auf Textformate konzentriert.

### Cache-Verzeichnis

Das Skript legt ein `.ki_conversion_cache`-Verzeichnis im Eingabeverzeichnis an. Dieses dient allerdings nur der Konsistenz zu Schritt 05 – tatsächlich werden in diesem Skript keine Konvertierungen gecacht.

### Log-Dateien und Analyse-Ausgaben

Dateien, deren Name mit `log_` beginnt oder `versionen_analyse` enthält, werden **nicht** von der KI geprüft. Das verhindert, dass die eigenen Ausgabedateien zu falschen Zuordnungen führen.

### Fehlerbehandlung

- Fehlende Argumente → Fehlermeldung und Beenden.
- Fehlende CSV aus Schritt 05 → Fehlermeldung und Beenden.
- Ladefehler des KI-Modells → Fehlermeldung mit Installationstipp und Beenden.
- Fehlende Dateien werden als `⚠️ Datei nicht gefunden` markiert, aber der Lauf wird fortgesetzt.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT