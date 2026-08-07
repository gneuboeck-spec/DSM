# I - PREMIS v3 XML-Generator (Digital Preservation)

Dieses Skript ist das zentrale Dokumentationswerkzeug im Archivierungsworkflow. Es generiert eine valide PREMIS v3 (Preservation Metadata: Implementation Strategies) XML-Datei, die den gesamten Lebenszyklus eines digitalen Objekts – von der physischen Quelle bis zum fertigen Archivpaket – normgerecht und maschinenlesbar dokumentiert. 

Das Skript verfügt über eine intelligente "Medien-Weiche", die automatisch erkennt, ob es sich um USB-Sticks (FTK), Disketten (Greaseweazle), Festplatten (ddrescue) oder optische Datenträger (Redumper) handelt, und extrahiert die entsprechenden forensischen Metadaten direkt aus den jeweiligen Logs.

---

## Hauptfunktionen

* **Automatisierte Medien-Erkennung (Forensic Context):**
  * **FTK-Parser:** Extrahiert Hardware-Informationen (z. B. Tableau Write-Blocker), Seriennummern und Verifikations-Hashes aus forensischen USB-Images.
  * **Redumper-Parser:** Liest Metadaten aus Audio-CD/DVD-Rips (Redumper) und übernimmt die Hardware-Kennung des optischen Laufwerks.
  * **Greaseweazle-Parser:** Dokumentiert Flux-Stream-Parameter, Heads/Cylinders und Host-Tools für Disketten-Images.
  * **ddrescue-Support:** Erkennt HDD-Clones anhand von Mapfiles.
* **Normdaten-Integration (GND & LOBID):**
  * Interaktive Suche nach Urhebern in der Deutschen Nationalbibliothek (DNB) via SRU-Schnittstelle.
  * **LOBID-Fallback:** Nutzt bei Erreichbarkeitsproblemen der DNB automatisch die lobid-gnd API (hbz), um Namen, Lebensdaten und Berufe zur Identifikation zu verknüpfen.
* **Hierarchische PREMIS-Struktur:**
  * **Objects:** Dokumentiert Träger-Fotos (Stufe 0), Disk-Images (Stufe 1), extrahierte Originaldateien (Stufe 2) und den technischen Index (Stufe 3).
  * **Events:** Protokolliert Imaging, Extraktion, Metadaten-Erfassung, Konvertierung und Packaging.
  * **Agents:** Verknüpft Software-Tools (Siegfried, Brunnhilde, Python-Skripte), Hardware und Personen (Urheber).
  * **Rights:** Erstellt Copyright-Statements basierend auf den Urheberdaten.
* **Schema-Validierung & XSD-Compliance:**
  * Erzwingt die strikte Einhaltung der Element-Reihenfolge (Objects → Events → Agents → Rights).
  * Integrierte Live-Validierung gegen das offizielle PREMIS-Schema der Library of Congress (LOC).

---

## TREE-Struktur & Dateipfade (Zustand während Phase 4)

Das Skript aggregiert Daten aus allen bisherigen Projektstufen, um die lückenlose Provenienz zu beweisen:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/          <-- QUELLE (Hardware-Fotos .tif)
├── 1_[ID]_image-LZA/                <-- QUELLE (Disk-Images .img / .001 / .bin / .dd)
│   └── logfiles/                    <-- QUELLE (Imaging-Logs .txt / .csv)
├── 2_[ID]_extracted-files/          <-- QUELLE (Siegfried.csv & Brunnhilde-Berichte)
├── 3_[ID]_for-transfer/             <-- QUELLE (Technischer Index .index)
└── 5_[ID]_LZA/                      <-- ARBEITSBEREICH & ZIEL (Archiv-Staging)
    └── logfiles/                    <-- ZIEL (Hier wird die Dokumentation erstellt)
        └── 5_[ID]_LZA_premis.xml    <-- Das finale PREMIS-Hauptdokument
```

---

## Technische Voraussetzungen

* **Python:** Version 3.10 oder neuer empfohlen.
* **Bibliotheken:** Benötigt `lxml` (für XML-Sortierung/Validierung), `requests` (für GND-Abfragen) und `urllib3`.
  ```bash
  pip install lxml requests urllib3
  ```

---

## Ausführung

Das Skript wird im normalen Arbeitsablauf über den zentralen **Workflow Launcher** (`Workflow_Launcher_start.bat`) und das darauf folgende **Auswahlmenü** gestartet. Die benötigten Parameter (AC-Nummer und Datenträger-ID) werden dabei automatisch vom Menü an das Skript übergeben.

Für manuelle Tests oder Debugging kann das Skript auch direkt über die Kommandozeile aufgerufen werden. Es erwartet zwingend zwei Argumente: die AC-Nummer und die Datenträger-ID.

**Beispiel für einen manuellen Aufruf:**

```bat
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=ID_001
python "J_generate_premis_win.py" %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1. **Urheber-Wahl:** Das Skript bittet um die Eingabe eines Namens und sucht diesen in der GND. Ein passender Eintrag kann interaktiv ausgewählt werden.
2. **Referenz-Analyse:** Imaging-Logs in Stufe 1 werden gescannt, um den Medientyp (USB, CD, Floppy, HDD) zu bestimmen.
3. **Objekt-Erstellung:** Hashes und Metadaten aller Objekte (aus Stufe 0, 1, 2 und 3) werden als PREMIS-Objekte angelegt.
4. **Event-Verknüpfung:** Die gesamte Kette (Imaging → Extraktion → Metadaten → Konvertierung) wird dokumentiert.
5. **Reihenfolge-Fix:** Das Skript sortiert alle XML-Elemente XSD-konform um (Objects → Events → Agents → Rights).
6. **Validierung:** Die finale Datei wird live gegen den LOC-Standard geprüft und in Stufe 5 gespeichert.

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur

```text
~/Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[Datenträger-ID]_picture-carrier/          <-- QUELLE (Hardware-Fotos .tif)
├── 1_[Datenträger-ID]_image-LZA/                <-- QUELLE (Disk-Images)
│   └── logfiles/                                <-- QUELLE (Imaging-Logs)
├── 2_[Datenträger-ID]_extracted-files/          <-- QUELLE (Brunnhilde-Berichte)
│   └── 2_[ID]_extracted-files_brunnhilde/
│       └── files_collection_report/
│           └── siegfried.csv                    <-- QUELLE (Dateiliste)
├── 3_[Datenträger-ID]_for-transfer/             <-- QUELLE (Technischer Index)
│   └── 5_[ID]_LZA.index                         <-- wird gesucht
└── 5_[Datenträger-ID]_LZA/                      <-- ZIEL
    └── logfiles/                                <-- ZIEL
        ├── 5_[ID]_LZA_premis.xml                <-- finale PREMIS-Datei
        └── 5_[ID]_LZA_derivation-image.img      <-- wird gesucht (falls vorhanden)
            └── *.log                            <-- wird gesucht (Packaging-Log)
```

### Medienerkennung (automatische Weiche)

Das Skript analysiert den `logfiles`-Ordner in Stufe 1 in folgender Reihenfolge:

| Gefundene Datei/Inhalt | Modus | Media Type | Besonderheiten |
|------------------------|-------|------------|----------------|
| `*image-log.txt` mit "Exterro" oder "FTK" | `usb_stick` | FTK Imager | extrahiert Tableau-WriteBlocker, Drive Model, Serial, Examiner, Acquisition Date, MD5/SHA1 aus Verification Results |
| `*image-log.txt` mit "redumper" | `optical_disc` | Redumper | extrahiert Laufwerk, Erstellungsdatum, MD5/SHA1 aus `<rom>`-Tag |
| `*image-log.txt` (sonstige) | `floppy` | Greaseweazle | extrahiert User, Host Tools, SHA-256, Cylinders, Heads |
| `*.map`-Datei im LZA-Hauptordner (eine Ebene über logfiles) | `hdd` | ddrescue | kein detailliertes Parsing, nur Erkennung |
| Keine der oben genannten | `unknown` | Standard | Fallback mit leeren Werten |

### GND-/LOBID-Suche (Urheber-Auswahl)

**Ablauf:**
1. Benutzer gibt Namen ein (z. B. "Brigitte Hamann").
2. Zuerst wird die **DNB SRU-Schnittstelle** abgefragt.
3. Bei Erfolglosigkeit oder Verbindungsfehler → **lobid-gnd API**.
4. Ergebnisse werden als nummerierte Liste angezeigt.
5. Benutzer wählt Nummer oder `s` (neue Suche) oder `x` (ohne GND fortfahren).

**Extrahiert bei DNB:** GND-ID, Name, Lebensdaten, Typ (Person/Körperschaft/Ort/Werk), Berufe/Info.  
**Extrahiert bei lobid:** GND-ID, Name, Geburts-/Todesdatum, Berufe (aus `professionOrOccupation`).

**Fallback:** Bei `x` wird `creator_gnd_id = None` gesetzt, Agent-ID wird aus dem eingegebenen Namen generiert.

### PREMIS-Objekt-Typen

| Typ | Verwendung | Beispiele |
|-----|------------|-----------|
| `representation` | Träger, Flux-Stream-Set, Archivpaket | `[ID]_carrier`, `[ID]_flux-stream-set` |
| `file` | Einzeldateien | Fotos (.tif), Disk-Images (.img/.001/.bin/.dd), extrahierte Dateien, Derivate |

### PREMIS-Element-Reihenfolge

Das Skript erzwingt zwingend folgende Reihenfolge (XSD-konform):
1. `object` (alle)
2. `event` (alle)
3. `agent` (alle)
4. `rights` (alle)

Innerhalb von `object` gilt:
1. `objectIdentifier`
2. `preservationLevel`
3. `significantProperties`
4. `objectCharacteristics`
5. `originalName`
6. `relationship`

Innerhalb von `event`:
1. `eventIdentifier`
2. `eventType`
3. `eventDateTime`
4. `eventOutcomeInformation`
5. `linkingAgentIdentifier`
6. `linkingObjectIdentifier`

### Erzeugte Events (Übersicht)

| Event-ID | Typ | Beschreibung |
|----------|-----|---------------|
| `evt_imaging_[ID]` | `creation` | Disk Imaging (verknüpft Carrier mit Image) |
| `evt_extraction_[ID]` | `extraction` | Brunnhilde Extraktion (verknüpft Image mit extrahierten Dateien) |
| `evt_metadata_extraction_[ID]` | `metadata extraction` | Extraktion aus Siegfried/Index |
| `evt_conversion_[ID]` | `migration` | PDF-Konvertierung (sofern Derivate existieren) |
| `evt_packaging_[ID]` | `creation` | Finales Packaging (verknüpft alle archivierten Dateien mit Archiv-Image) |

### Verwendete Agenten (Default)

| Agent-ID | Name | Typ |
|----------|------|-----|
| `WBR` | Wienbibliothek im Rathaus | organization |
| `SW_Brunnhilde` | Brunnhilde File Characterization Tool | software |
| `SW_InternalPythonScripts_Conversion` | Internal Python Conversion Scripts | software |
| `SW_InternalPythonScripts_Metadata` | Internal Python Metadata Extraction Scripts | software |

### Dateiformat-Identifikation (PRONOM)

| Objekt | Format | PRONOM-ID |
|--------|--------|------------|
| TIF-Foto | Tagged Image File Format | `fmt/353` |
| Disk-Image (generisch) | Raw Disk Image | `x-fmt/263` |
| PDF-Derivat | PDF Derivative | aus Siegfried übernommen |
| Flux-Stream | Greaseweazle Raw Flux Stream | (keine PRONOM-ID) |

### Quellen für extrahierte Dateien (Stufe 2)

Das Skript verwendet folgende Priorität:
1. **Index-Datei:** `3_[ID]_for-transfer/5_[ID]_LZA.index` (bevorzugt, da enthält SHA-256, Größe, PRONOM-ID, Creator-Tool).
2. **Siegfried-CSV:** `2_[ID]_extracted-files/.../siegfried.csv` (Fallback, enthält Dateiname, Größe, PRONOM-ID).
3. **Ableitung:** Original-Extraktionen werden über Pfad-Präfix erkannt (wenn Dateipfad mit einem Original-Extraktionspfad beginnt).

### Integritätsprüfung (XML-Validierung)

Nach dem Schreiben der PREMIS-Datei führt das Skript eine Live-Validierung durch:
* Lädt das offizielle XSD-Schema von `https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd`.
* Validiert die erzeugte XML dagegen.
* Bei Fehlern: Ausgabe von Zeilennummer und Fehlermeldung.
* Bei Erfolg: grüne Bestätigung.

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| `path_step5_lza` existiert nicht | FATALER FEHLER + `sys.exit(1)` |
| Keine Kommandozeilen-Argumente | Fehlermeldung + `sys.exit(1)` |
| Keine Objekte in `xml_objects` | Warnung + Minimal-Objekt wird erstellt (damit XML valide bleibt) |
| GND-Suche schlägt komplett fehl | Benutzer kann ohne GND fortfahren (`creator_gnd_id = None`) |
| XSD-Validierung schlägt fehl | Fehlermeldung mit Details, Skript läuft weiter (kein Abbruch) |

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Ordner öffnen? (j/n):`. Bei `j`:
* **Windows** → `subprocess.Popen(['explorer', str(target_path)])`
* **macOS** → `subprocess.run(["open", str(target_path)])`
* **Linux/andere** → `subprocess.run(["xdg-open", str(target_path)])`

### Abhängigkeiten

**Erforderliche Python-Pakete:**
* `lxml` (für XML-Verarbeitung, Sortierung, XSD-Validierung)
* `requests` (für GND-/lobid-API-Abfragen)
* `urllib3` (für Retry-Strategie bei DNB)

**Standardbibliothek:** `sys`, `re`, `os`, `csv`, `subprocess`, `hashlib`, `glob`, `xml.etree.ElementTree`, `pathlib`, `datetime`

### Wichtige Einschränkungen

* `.tiff`-Dateien werden nicht als Hardware-Fotos erkannt (nur `.tif`).
* Redumper-Parser sucht nach `<rom name="...">`-Tag im Log.
* FTK-Parser extrahiert Hashes nur aus dem Abschnitt "Image Verification Results".
* Greaseweazle-Parser setzt `has_flux_stream = True` und erzeugt ein Flux-Stream-Set-`representation`.
* ddrescue-Erkennung basiert nur auf Existenz von `.map`-Dateien (kein Inhalts-Parsing).

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT