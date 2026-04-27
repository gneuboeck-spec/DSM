# XML-Zusammenfassungs-Generator (.content)

Dieses Skript ist ein spezialisiertes Werkzeug zur Automatisierung der Berichterstellung innerhalb eines digitalen Archivierungsworkflows. Es sammelt Informationen aus zwei unterschiedlichen Quellen – einer manuell erstellten XML-Beschreibung des physischen Datenträgers und einem automatisch generierten HTML-Analysebericht von Brunnhilde – und führt sie zu einer einzigen, strukturierten XML-Zusammenfassungsdatei (.content) zusammen.

Diese .content-Datei dient als zentrale Übersicht über den Inhalt und die technischen Eigenschaften eines archivierten Datenträgers.

---

## Hauptfunktionen

1. **Einlesen der Datenträger-Beschreibung:**
   * Quelle: Eine XML-Datei (0_[ID]_carrier-description.xml), die manuell erstellte Metadaten über den physischen Datenträger enthält (Typ, Beschriftung, Zustand).
   * Aktion: Das Skript integriert diese deskriptiven Daten in die finale Zusammenfassung.

2. **Einlesen des Analyse-Berichts:**
   * Quelle: Ein HTML-Bericht (report.html), der zuvor vom Analyse-Tool Brunnhilde erstellt wurde.
   * Aktion: Das Skript parst diesen Bericht mit BeautifulSoup 4, um statistische Daten zu extrahieren (Dateianzahl, Gesamtgröße, Zeitspanne, Dateiformate nach PRONOM).

3. **Erstellung der XML-Zusammenfassung:**
   * Ziel: Eine neue XML-Datei mit der Endung .content im Stufe-2-Verzeichnis.
   * Aktion: Erstellt eine saubere, maschinenlesbare Übersicht. Ein Überschreiben existierender Dateien wird vom Skript verhindert.

---

## TREE-Struktur & Dateipfade

Das Skript verknüpft Daten aus verschiedenen Verarbeitungsstufen. Die Existenz des Transfer-Ordners (Stufe 3) wird ebenfalls validiert:

```text
[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/
│   └── 0_[ID]_carrier-description.xml          <-- QUELLE 1 (Manuelle Beschreibung)
├── 2_[ID]_extracted-files/
│   ├── 2_[ID]_extracted-files_brunnhilde/
│   │   └── files_collection_report/
│   │       └── report.html                     <-- QUELLE 2 (Brunnhilde-Analyse)
│   └── 2_[ID]_extracted-files.content          <-- ZIEL (Zusammenfassungsbericht)
└── 3_[ID]_for-transfer/                        <-- VALIDIERUNG (Muss existieren)
```
---

## Technische Voraussetzungen

* Python: Version 3.10 oder neuer empfohlen.
* Bibliotheken: Beautiful Soup 4 muss installiert sein:
    pip install beautifulsoup4

---

## Ausführung

Das Skript kann flexibel gestartet werden:

1. **Automatisiert (via Kommandozeile):** Übergabe der AC-Nummer und Datenträger-ID als Argumente (z.B. durch eine start.bat oder das Hauptmenü).
2. **Manuell:** Falls keine Argumente übergeben werden, fragt das Skript die benötigten Daten interaktiv ab.

Beispielhafter Aufruf:
    python content_generator.py AC_12345 ID_001

### Ablauf der Ausführung

1. **Validierung:** Prüfung der Argumente sowie Verifizierung aller Quellpfade und des Transfer-Ordners.
2. **XML-Parsing:** Einlesen der physischen Carrier-Metadaten.
3. **HTML-Parsing:** Extraktion der statistischen Daten und Format-Listen aus dem Brunnhilde-Bericht.
4. **XML-Generierung:** Erstellung der .content-Datei mit strukturierter Einrückung.
5. **Abschluss:** Optionale Abfrage, ob der Zielordner im Explorer geöffnet werden soll.

---

## Detaillierte Hinweise zum Skriptverhalten

### Exakte Pfadstruktur (streng erforderlich)

Das Skript erwartet folgende Dateipfade. Weicht nur einer ab, bricht das Skript mit einer roten Fehlermeldung ab:

Der `3_…_for-transfer`-Ordner **muss existieren**, wird aber vom Skript nicht beschrieben oder verändert – er dient nur als Validierungsprüfung, dass die Verarbeitungsstufe 3 erreicht ist.

### Fallback bei manuellem Aufruf

Wenn das Skript **nicht** mit zwei Kommandozeilen-Argumenten gestartet wird (z. B. direkt per Doppelklick), fragt es interaktiv nach AC‑Nummer und Datenträger‑ID. Das ist in der README korrekt erwähnt – allerdings wird dabei **keine erneute Pfadvalidierung durchlaufen**; die Abfrage ersetzt nur die fehlenden `sys.argv`.

### Extrahierte Felder aus der HTML‑Datei

Das Skript sucht in `report.html` nach **exakt diesen Textmustern** in `〈p〉〈strong〉…〈/strong〉〈/p〉`:

| Gesuchter Text | Ergebnisvariable |
|----------------|------------------|
| `Total files:` | `total_files` |
| `Total size:` | `total_size` |
| `Earliest date:` | `earliest_date` |
| `Latest date:` | `latest_date` |

Falls eines dieser Muster nicht gefunden wird, bleibt die entsprechende Variable leer (`""`).

### Verarbeitung der „File format versions“-Tabelle

Das Skript sucht nach einer `<h2>`-Überschrift mit dem exakten Text **„File format versions“**. Die unmittelbar folgende `<table>` wird ausgewertet.

- **Erkannte Formate** werden in `file_format_versions` gespeichert (mit `PronomID`, `FileFormatType`, `FileFormatVersion`, `Number`).
- **Unidentified files** werden erkannt, wenn die erste Tabellenspalte leer ist **und** die zweite Spalte den Text `"UNKNOWN"` enthält. Deren Anzahl landet in `unidentified_count`.
- Alle anderen Zeilen werden ignoriert.

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| XML‑Parsefehler | Fehlermeldung + `exit(1)` |
| XML‑ oder HTML‑Datei fehlt | rote Fehlermeldung + `exit()` |
| `base_path` existiert nicht | rote Fehlermeldung + `exit()` |
| `for-transfer`-Ordner fehlt | rote Fehlermeldung + `exit()` |
| **Ziel‑`.content`-Datei existiert bereits** | **Abbruch ohne Überschreiben** (rote Meldung + `exit()`) |

Die letzte Zeile ist besonders wichtig: Das Skript schützt existierende Ausgaben vor versehentlichem Überschreiben.

### Aufbau der erzeugten `.content`-XML

Die Ausgabedatei hat folgende Struktur (vereinfacht):

~/Documents/data/[AC_number]/[disk_archive_ID]/0_[disk_archive_ID]_picture-carrier/0_[disk_archive_ID]_carrier-description.xml
~/Documents/data/[AC_number]/[disk_archive_ID]/2_[disk_archive_ID]_extracted-files/2_[disk_archive_ID]_extracted-files_brunnhilde/files_collection_report/report.html
~/Documents/data/[AC_number]/[disk_archive_ID]/3_[disk_archive_ID]_for-transfer/

```xml
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

```

Die Einrückung erfolgt mit vier Leerzeichen (`ET.indent(space="    ")`).


### Plattformabhängiges Öffnen des Zielordners

Nach erfolgreicher Erstellung fragt das Skript: `Zielordner oeffnen? (j/n)`. Bei `j`:

- **Windows** → `os.startfile(str(destination_folder))`
- **macOS** → `subprocess.run(["open", str(destination_folder)])`
- **Linux/andere** → `subprocess.run(["xdg-open", str(destination_folder)])`

Die Umwandlung des `Path`-Objekts in einen String ist zwingend erforderlich – das Skript macht das korrekt.

### Abhängigkeiten (zusätzlich)

Neben `beautifulsoup4` werden keine weiteren externen Bibliotheken benötigt. `xml.etree.ElementTree`, `subprocess`, `platform`, `sys` und `pathlib` sind in der Python‑Standardbibliothek enthalten.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT