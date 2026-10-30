# I - PREMIS v3 XML-Generator (Digital Preservation)

Dieses Skript ist das zentrale Dokumentationswerkzeug im Archivierungsworkflow. Es generiert eine valide PREMIS v3 (Preservation Metadata: Implementation Strategies) XML-Datei, die den gesamten Lebenszyklus eines digitalen Objekts – von der physischen Quelle bis zum fertigen Archivpaket – normgerecht und maschinenlesbar dokumentiert.

Das Skript verfügt über eine intelligente "Medien-Weiche", die automatisch erkennt, ob es sich um USB-Sticks (FTK), Disketten (Greaseweazle), Festplatten (ddrescue) oder optische Datenträger (Redumper) handelt, und extrahiert die entsprechenden forensischen Metadaten direkt aus den jeweiligen Logs.

## Struktur

    I_PREMIS_XML_Generator/
    |-- README.md                          <-- Diese Datei
    |-- premis-v3-0.xsd                    <-- Offizielles PREMIS v3 XML-Schema (Library of Congress)
    `-- win/
        `-- I_PREMIS_XML_Generator.py      <-- Ausführbare Python-Datei

## Hauptfunktionen

* **Automatisierte Medien-Erkennung (Forensic Context):**
  * **FTK-Parser:** Extrahiert Hardware-Informationen (z. B. Tableau Write-Blocker), Seriennummern und Verifikations-Hashes aus forensischen USB-Images.
  * **Redumper-Parser:** Liest Metadaten aus Audio-CD/DVD-Rips (Redumper) und übernimmt die Hardware-Kennung des optischen Laufwerks.
  * **Greaseweazle-Parser:** Dokumentiert Flux-Stream-Parameter, Heads/Cylinders und Host-Tools für Disketten-Images.
  * **ddrescue-Support:** Erkennt HDD-Clones anhand von Mapfiles.
* **Normdaten-Integration (GND & LOBID) mit erweiterter manueller Eingabe:**
  * Interaktive Suche nach Urhebern in der Deutschen Nationalbibliothek (DNB) via SRU-Schnittstelle.
  * **LOBID-Fallback:** Nutzt bei Erreichbarkeitsproblemen der DNB automatisch die lobid-gnd API (hbz), um Namen, Lebensdaten und Berufe zur Identifikation zu verknüpfen.
  * **Manueller Eintrag:** Erlaubt das Anlegen von Urhebern ohne GND-Nummer (generiert lokale IDs) und mit optionalem Sterbejahr zur automatischen Berechnung der urheberrechtlichen Schutzfrist.
* **Hierarchische PREMIS-Struktur:**
  * **Objects:** Dokumentiert Träger-Fotos (Stufe 0), Disk-Images (Stufe 1), extrahierte Originaldateien (Stufe 2) und den technischen Index (Stufe 3).
  * **Events:** Protokolliert Imaging, Extraktion, Metadaten-Erfassung, Virus-Check, Konvertierung und Packaging.
  * **Agents:** Verknüpft Software-Tools (Siegfried, Brunnhilde, ClamAV, Python-Skripte), Hardware und Personen (Urheber).
  * **Rights:** Erstellt Copyright-Statements basierend auf den Urheberdaten, inklusive automatischer Berechnung der Schutzfrist (70 Jahre post mortem auctoris, endend am 31.12. des 70. Folgejahres) und XSD-konformer Ausgabe von `copyrightNote` gefolgt von `copyrightApplicableDates` (`startDate`/`endDate`).
* **ClamAV-Virus-Check-Integration:**
  * Liest `viruscheck-log.txt` aus Stufe 2 (Brunnhilde-Report) oder Stufe 5.
  * Erstellt ein PREMIS-Event `virus check` mit ClamAV-Agent (Engine-Version, gescannte und infizierte Dateien).
  * Speichert die Log-Datei selbst als PREMIS-Objekt (Artefakt) mit SHA-256-Hash.
  * Normalisiert ClamAV-Datumsformate (`2026:08:12` → ISO-8601).
* **Schema-Validierung & XSD-Compliance:**
  * Erzwingt die strikte Einhaltung der Element-Reihenfolge (Objects → Events → Agents → Rights).
  * Integrierte Live-Validierung gegen das offizielle PREMIS-Schema der Library of Congress (LOC). Dreistufiger Fallback: direkter Abruf, Abruf mit Browser-User-Agent, lokale Datei `premis-v3-0.xsd`.
  * Erwartete FileTrove-/Greaseweazle-Erweiterungs-Warnungen werden herausgefiltert, damit nur echte PREMIS-Fehler angezeigt werden.

## TREE-Struktur & Dateipfade (Zustand während Phase 4)

Das Skript aggregiert Daten aus allen bisherigen Projektstufen, um die lückenlose Provenienz zu beweisen. Der Projektpfad wird vom Menü übergeben (`sys.argv[3]` oder Umgebungsvariable `DATA_PATH`):

    [Projektpfad]/
    |-- 0_[ID]_picture-carrier/          <-- QUELLE (Hardware-Fotos .tif)
    |-- 1_[ID]_image-LZA/                <-- QUELLE (Disk-Images .img / .001 / .bin / .dd)
    |   `-- logfiles/                    <-- QUELLE (Imaging-Logs .txt / .csv)
    |-- 2_[ID]_extracted-files/          <-- QUELLE (Siegfried.csv & Brunnhilde-Berichte)
    |-- 3_[ID]_for-transfer/             <-- QUELLE (Technischer Index .index)
    `-- 5_[ID]_LZA/                      <-- ARBEITSBEREICH & ZIEL (Archiv-Staging)
        `-- logfiles/                    <-- ZIEL (Hier wird die Dokumentation erstellt)
            `-- 5_[ID]_LZA_premis.xml    <-- Das finale PREMIS-Hauptdokument

## Technische Voraussetzungen

* **Windows 10/11**
* **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
* **Python-Pakete:** `lxml`, `requests`, `urllib3` (in `requirements.txt` enthalten; Installation: `pip install -r requirements.txt`)
* **Standardbibliothek:** `sys`, `re`, `os`, `csv`, `subprocess`, `hashlib`, `glob`, `xml.etree.ElementTree`, `pathlib`, `datetime`

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `9` (I_PREMIS_XML_Generator) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "I_PREMIS_XML_Generator.py" AC_0001 ID_001 "C:\Pfad\zum\Datenordner"

Das Skript erwartet zwingend mindestens zwei Argumente (AC-Nummer, Datenträger-ID). Ohne diese bricht es mit Fehlermeldung ab.

### Ablauf der Ausführung

1. **Urheber-Wahl:** Das Skript bittet um die Eingabe eines Namens und sucht diesen in der GND. Ein passender Eintrag kann interaktiv ausgewählt werden. Bei manueller Eingabe sind GND-Nummer und Sterbejahr optional; bei Angabe des Sterbejahres wird die Schutzfrist automatisch berechnet.
2. **Referenz-Analyse:** Imaging-Logs in Stufe 1 werden gescannt, um den Medientyp (USB, CD, Floppy, HDD) zu bestimmen.
3. **Objekt-Erstellung:** Hashes und Metadaten aller Objekte (aus Stufe 0, 1, 2 und 3) werden als PREMIS-Objekte angelegt.
4. **Virus-Check:** Sofern eine `viruscheck-log.txt` existiert, wird ein `virus check`-Event erstellt und die Log-Datei als Objekt verknüpft.
5. **Event-Verknüpfung:** Die gesamte Kette (Imaging → Extraktion → Metadaten → Konvertierung → Packaging) wird dokumentiert.
6. **Reihenfolge-Fix:** Das Skript sortiert alle XML-Elemente XSD-konform um (Objects → Events → Agents → Rights).
7. **Validierung:** Die finale Datei wird gegen den LOC-Standard geprüft (mit lokalem Fallback auf `premis-v3-0.xsd`) und in Stufe 5 gespeichert.

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur

    [Projektpfad]/
    |-- 0_[Datenträger-ID]_picture-carrier/          <-- QUELLE (Hardware-Fotos .tif)
    |-- 1_[Datenträger-ID]_image-LZA/                <-- QUELLE (Disk-Images)
    |   `-- logfiles/                                <-- QUELLE (Imaging-Logs)
    |-- 2_[Datenträger-ID]_extracted-files/          <-- QUELLE (Brunnhilde-Berichte)
    |   `-- 2_[ID]_extracted-files_brunnhilde/
    |       `-- files_collection_report/
    |           `-- siegfried.csv                    <-- QUELLE (Dateiliste)
    |-- 3_[Datenträger-ID]_for-transfer/             <-- QUELLE (Technischer Index)
    |   `-- 5_[ID]_LZA.index                         <-- wird gesucht
    `-- 5_[Datenträger-ID]_LZA/                      <-- ZIEL
        `-- logfiles/                                <-- ZIEL
            |-- 5_[ID]_LZA_premis.xml                <-- finale PREMIS-Datei
            `-- 5_[ID]_LZA_derivation-image.img      <-- wird gesucht (falls vorhanden)
                `-- *.log                            <-- wird gesucht (Packaging-Log)

### Medienerkennung (automatische Weiche)

Das Skript analysiert den `logfiles`-Ordner in Stufe 1 in folgender Reihenfolge:

| Gefundene Datei/Inhalt | Modus | Media Type | Besonderheiten |
|------------------------|-------|------------|----------------|
| `*image-log.txt` mit "Exterro" oder "FTK" | `usb_stick` | FTK Imager | extrahiert Tableau-WriteBlocker, Drive Model, Serial, Examiner, Acquisition Date, MD5/SHA1 aus Verification Results |
| `*image-log.txt` mit "redumper" | `optical_disc` | Redumper | extrahiert Laufwerk, Erstellungsdatum, MD5/SHA1 aus `<rom>`-Tag |
| `*image-log.txt` (sonstige) | `floppy` | Greaseweazle | extrahiert User, Host Tools, SHA-256, Cylinders, Heads |
| `*.map`-Datei im LZA-Hauptordner (eine Ebene über logfiles) | `hdd` | ddrescue | kein detailliertes Parsing, nur Erkennung |
| Keine der oben genannten | `unknown` | Standard | Fallback mit leeren Werten |

**Fallback-Verhalten für logfiles-Ordner:** Wenn der `logfiles`-Unterordner in Stufe 1 fehlt, sucht das Skript die Log-Datei direkt im Hauptordner der Stufe 1, erstellt den `logfiles`-Ordner und verschiebt die Datei dorthin.

### GND-/LOBID-Suche (Urheber-Auswahl)

**Ablauf:**

1. Benutzer gibt Namen ein (z. B. "Brigitte Hamann").
2. Zuerst wird die **DNB SRU-Schnittstelle** abgefragt (Timeout: 1 Sekunde).
3. Bei Erfolglosigkeit oder Verbindungsfehler → **lobid-gnd API** (Timeout: 15 Sekunden).
4. Ergebnisse werden als nummerierte Liste angezeigt.
5. Benutzer wählt Nummer, `m` (manueller Eintrag), `s` (neue Suche) oder `x` (ohne GND fortfahren).

**Extrahiert bei DNB:** GND-ID, Name, Lebensdaten, Typ (Person/Körperschaft/Ort/Werk), Berufe/Info.

**Extrahiert bei lobid:** GND-ID, Name, Geburts-/Todesdatum, Berufe (aus `professionOrOccupation`).

**Manueller Eintrag (`m`):**
* **Name:** Erforderlich (Format: Familienname, Vorname).
* **GND-Nummer:** Optional. Wenn leer gelassen, wird eine lokale ID generiert (z. B. `local_Max_Mustermann`) und `creator_gnd_id` bleibt `None`.
* **Sterbejahr:** Optional (4-stellig, z. B. 1950). Wenn angegeben, wird das `copyright_end_date` automatisch auf den 31.12. des 70. Folgejahres berechnet. Dies führt zur korrekten Generierung von `<copyrightApplicableDates>` mit `startDate` und `endDate` im PREMIS-XML.

**Fallback (`x`):** Bei `x` wird `creator_gnd_id = None` gesetzt, Agent-ID wird aus dem eingegebenen Namen generiert, keine automatische Schutzfristberechnung.

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

Innerhalb von `copyrightInformation` (Rights):

1. `copyrightStatus`
2. `copyrightJurisdiction`
3. `copyrightNote` (MUSS vor `copyrightApplicableDates` stehen laut XSD)
4. `copyrightApplicableDates` (enthält `startDate` und `endDate`, falls Sterbejahr bekannt)

### Erzeugte Events (Übersicht)

| Event-ID | Typ | Beschreibung |
|----------|-----|---------------|
| `evt_imaging_[ID]` | `creation` | Disk Imaging (verknüpft Carrier mit Image) |
| `evt_extraction_[ID]` | `extraction` | Brunnhilde Extraktion (verknüpft Image mit extrahierten Dateien) |
| `evt_metadata_extraction_[ID]` | `metadata extraction` | Extraktion aus Siegfried/Index |
| `evt_virus_check_[ID]` | `virus check` | ClamAV-Virus-Scan (sofern Log vorhanden) |
| `evt_conversion_[ID]` | `migration` | PDF-Konvertierung (sofern Derivate existieren) |
| `evt_packaging_[ID]` | `creation` | Finales Packaging (verknüpft alle archivierten Dateien mit Archiv-Image) |

### Verwendete Agenten (Default)

| Agent-ID | Name | Typ |
|----------|------|-----|
| `WBR` | Wienbibliothek im Rathaus | organization |
| `SW_Brunnhilde` | Brunnhilde File Characterization Tool | software |
| `SW_InternalPythonScripts_Conversion` | Internal Python Conversion Scripts | software |
| `SW_InternalPythonScripts_Metadata` | Internal Python Metadata Extraction Scripts | software |

Zusätzlich werden dynamisch Agenten für Hardware (Tableau, optisches Laufwerk), Werkzeuge (FTK Imager, Redumper, Greaseweazle) und ClamAV (mit Versionsnummer) erstellt.

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
* Dreistufiger Abruf: (1) direkt, (2) mit Browser-User-Agent, (3) lokale Datei `premis-v3-0.xsd` im Skript-Ordner.
* Erwartete FileTrove-/Greaseweazle-Erweiterungs-Namespace-Warnungen werden herausgefiltert.
* Bei echten Fehlern: Ausgabe von Zeilennummer und Fehlermeldung.
* Bei Erfolg: grüne Bestätigung.

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| `path_step5_lza` existiert nicht | FATALER FEHLER + `sys.exit(1)` |
| Weniger als 2 Kommandozeilen-Argumente | Fehlermeldung + `sys.exit(1)` |
| Keine Objekte in `xml_objects` | Warnung + Minimal-Objekt wird erstellt (damit XML valide bleibt) |
| GND-Suche schlägt komplett fehl | Benutzer kann ohne GND fortfahren (`creator_gnd_id = None`) |
| XSD-Validierung schlägt fehl | Fehlermeldung mit Details, Skript läuft weiter (kein Abbruch) |

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Ordner öffnen? (j/n):`. Bei `j`:

* **Windows** → `subprocess.Popen(['explorer', str(target_path)])`
* **macOS** → `subprocess.run(["open", str(target_path)])`
* **Linux/andere** → `subprocess.run(["xdg-open", str(target_path)])`

### Wichtige Einschränkungen

* `.tiff`-Dateien werden nicht als Hardware-Fotos erkannt (nur `.tif`).
* Redumper-Parser sucht nach `<rom name="...">`-Tag im Log.
* FTK-Parser extrahiert Hashes nur aus dem Abschnitt "Image Verification Results".
* Greaseweazle-Parser setzt `has_flux_stream = True` und erzeugt ein Flux-Stream-Set-`representation`.
* ddrescue-Erkennung basiert nur auf Existenz von `.map`-Dateien (kein Inhalts-Parsing).
* DNB-SRU-Abfrage hat ein Timeout von nur 1 Sekunde. Das ist sehr kurz und kann dazu führen, dass der lobid-gnd-Fallback häufiger genutzt wird als beabsichtigt. Bei Bedarf in `_search_dnb_sru()` anpassen.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT