# B - XML-Zusammenfassungs-Generator (.content)

Dieses Skript ist ein spezialisiertes Werkzeug zur Automatisierung der Berichterstellung innerhalb eines digitalen Archivierungsworkflows. Es sammelt Informationen aus zwei unterschiedlichen Quellen – einer manuell erstellten XML-Beschreibung des physischen Datenträgers und einem automatisch generierten HTML-Analysebericht von Brunnhilde – und führt sie zu einer einzigen, strukturierten XML-Zusammenfassungsdatei (`.content`) zusammen.

Diese `.content`-Datei dient als zentrale Übersicht über den Inhalt und die technischen Eigenschaften eines archivierten Datenträgers.

## Struktur

    B_XML_Zusammenfassungs_Generator_content/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- B_XML_Zusammenfassungs_Generator_content.py   <-- Ausführbare Python-Datei

## Hauptfunktionen

1. **Einlesen der Datenträger-Beschreibung:**
   * Quelle: Eine XML-Datei (`0_[ID]_carrier-description.xml`), die manuell erstellte Metadaten über den physischen Datenträger enthält (Typ, Beschriftung, Zustand).
   * Aktion: Das Skript integriert diese deskriptiven Daten in die finale Zusammenfassung.

2. **Einlesen des Analyse-Berichts:**
   * Quelle: Ein HTML-Bericht (`report.html`), der zuvor vom Analyse-Tool Brunnhilde erstellt wurde.
   * Aktion: Das Skript parst diesen Bericht mit BeautifulSoup 4, um statistische Daten zu extrahieren (Dateianzahl, Gesamtgröße, Zeitspanne, Dateiformate nach PRONOM).

3. **Erstellung der XML-Zusammenfassung:**
   * Ziel: Eine neue XML-Datei mit der Endung `.content` im Stufe-2-Verzeichnis.
   * Aktion: Erstellt eine saubere, maschinenlesbare Übersicht. Ein Überschreiben existierender Dateien wird vom Skript verhindert.

## TREE-Struktur & Dateipfade

Das Skript verknüpft Daten aus verschiedenen Verarbeitungsstufen. Die Existenz des Transfer-Ordners (Stufe 3) wird ebenfalls validiert:

    [AC-Nummer]/[Datenträger-ID]/
    |-- 0_[ID]_picture-carrier/
    |   `-- 0_[ID]_carrier-description.xml          <-- QUELLE 1 (Manuelle Beschreibung)
    |-- 2_[ID]_extracted-files/
    |   |-- 2_[ID]_extracted-files_brunnhilde/
    |   |   `-- files_collection_report/
    |   |       `-- report.html                     <-- QUELLE 2 (Brunnhilde-Analyse)
    |   `-- 2_[ID]_extracted-files.content          <-- ZIEL (Zusammenfassungsbericht)
    `-- 3_[ID]_for-transfer/                        <-- VALIDIERUNG (Muss existieren)

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Python-Pakete:** `beautifulsoup4` (in `requirements.txt` enthalten; Installation: `pip install -r requirements.txt`)
- Alle weiteren Module (`xml.etree.ElementTree`, `subprocess`, `platform`, `sys`, `pathlib`, `os`) sind Teil der Python-Standardbibliothek.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `2` (B_XML_Zusammenfassungs_Generator_content) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript auch direkt über die Kommandozeile aufgerufen werden:

    python "B_XML_Zusammenfassungs_Generator_content.py" AC_12345 ID_001 "C:\Pfad\zum\Datenordner"

Wird das Skript ohne Argumente gestartet (z. B. per Doppelklick), fragt es interaktiv nach AC-Nummer und Datenträger-ID. Dabei wird jedoch keine erneute Pfadvalidierung durchlaufen.

### Ablauf der Ausführung

1. **Validierung:** Prüfung der Argumente sowie Verifizierung aller Quellpfade und des Transfer-Ordners.
2. **XML-Parsing:** Einlesen der physischen Carrier-Metadaten.
3. **HTML-Parsing:** Extraktion der statistischen Daten und Format-Listen aus dem Brunnhilde-Bericht.
4. **XML-Generierung:** Erstellung der `.content`-Datei mit strukturierter Einrückung.
5. **Abschluss:** Optionale Abfrage, ob der Zielordner im Explorer geöffnet werden soll.

## Detaillierte Hinweise zum Skriptverhalten

### Exakte Pfadstruktur (streng erforderlich)

Das Skript erwartet die oben definierte Dateistruktur. Weicht ein Pfad ab, bricht das Skript mit einer roten Fehlermeldung ab.

Der `3_…_for-transfer`-Ordner **muss existieren**, wird aber vom Skript nicht beschrieben oder verändert – er dient nur als Validierungsprüfung, dass die Verarbeitungsstufe 3 bereits erreicht wurde.

### Fallback bei manuellem Aufruf

Wenn das Skript **nicht** mit zwei Kommandozeilen-Argumenten gestartet wird (z. B. direkt per Doppelklick ohne Batch), fragt es interaktiv nach AC-Nummer und Datenträger-ID. Dabei wird **keine erneute Pfadvalidierung durchlaufen**; die Abfrage ersetzt nur die fehlenden `sys.argv`.

### Extrahierte Felder aus der HTML-Datei

Das Skript sucht in `report.html` nach **exakt diesen Textmustern** in `<p><strong>…</strong></p>`:

| Gesuchter Text | Ergebnisvariable |
|----------------|------------------|
| `Total files:` | `total_files` |
| `Total size:` | `total_size` |
| `Earliest date:` | `earliest_date` |
| `Latest date:` | `latest_date` |

Falls eines dieser Muster nicht gefunden wird, bleibt die entsprechende Variable leer (`""`).

### Verarbeitung der "File format versions"-Tabelle

Das Skript sucht nach einer `<h2>`-Überschrift mit dem exakten Text **"File format versions"**. Die unmittelbar folgende `<table>` wird ausgewertet.

- **Erkannte Formate** werden in `file_format_versions` gespeichert (mit `PronomID`, `FileFormatType`, `FileFormatVersion`, `Number`).
- **Unidentified files** werden erkannt, wenn die erste Tabellenspalte leer ist **und** die zweite Spalte den Text `"UNKNOWN"` enthält. Deren Anzahl landet in `unidentified_count`.
- Alle anderen Zeilen werden ignoriert.

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| XML-Parsefehler | Fehlermeldung + `exit(1)` |
| XML- oder HTML-Datei fehlt | rote Fehlermeldung + `exit()` |
| `base_path` existiert nicht | rote Fehlermeldung + `exit()` |
| `for-transfer`-Ordner fehlt | rote Fehlermeldung + `exit()` |
| **Ziel-`.content`-Datei existiert bereits** | **Abbruch ohne Überschreiben** (rote Meldung + `exit()`) |

Die letzte Zeile ist besonders wichtig: Das Skript schützt existierende Ausgaben vor versehentlichem Überschreiben.

### Aufbau der erzeugten `.content`-XML

Die Ausgabedatei hat folgende Struktur (vereinfacht):

    <?xml version="1.0" encoding="UTF-8"?>
    <DataCarrierSummary ID="[disk_archive_ID]">
        <CarrierDescription>
            <CarrierType>...</CarrierType>
            <CarrierInscription>...</CarrierInscription>
            <CarrierBranding>...</CarrierBranding>
            <CarrierCondition>...</CarrierCondition>
            <CarrierDescriptionNote>...</CarrierDescriptionNote>
        </CarrierDescription>
        <FileStatistic>
            <NumberOfFiles>
                <TotalNumber>[total_files]</TotalNumber>
                <IdentifiedFileFormatVersions>
                    <FileFormatVersion>...</FileFormatVersion>  <!-- mehrfach -->
                </IdentifiedFileFormatVersions>
                <UnidentifiedFileFormats>
                    <Number>[unidentified_count]</Number>
                </UnidentifiedFileFormats>
            </NumberOfFiles>
            <FileSize>
                <TotalSize>[total_size]</TotalSize>
            </FileSize>
            <DateEarliestCreated>[earliest_date]</DateEarliestCreated>
            <DateLatestModified>[latest_date]</DateLatestModified>
        </FileStatistic>
    </DataCarrierSummary>

Die Einrückung erfolgt mit vier Leerzeichen (`ET.indent(space="    ")`).

### Plattformabhängiges Öffnen des Zielordners

Nach erfolgreicher Erstellung fragt das Skript: `Zielordner oeffnen? (j/n)`. Bei `j`:

- **Windows** → `os.startfile(str(destination_folder))`
- **macOS** → `subprocess.run(["open", str(destination_folder)])`
- **Linux/andere** → `subprocess.run(["xdg-open", str(destination_folder)])`

Die Umwandlung des `Path`-Objekts in einen String ist zwingend erforderlich – das Skript macht das korrekt.

## Lizenz

Copyright (c) 2025 Florian Lüftner <florian.lueftner@posteo.com>
Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Florian Lüftner
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT