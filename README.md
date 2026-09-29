# DSM - Digitale Datenrettung & Langzeitarchivierung (LZA)

Dieses Repository enthält die Skriptsammlung für den Master-Workflow zur digitalen Datenrettung und Langzeitarchivierung. Die Skripte automatisieren die lückenlose Beweiskette (Chain of Custody) und die Transformation der Daten von der physischen Quelle bis zum versiegelten Archivpaket.

## Schnellstart & Nutzung

Die Arbeitsumgebung wird zentral über den **Workflow Launcher** gestartet.

1. Doppelklick auf `Workflow_Launcher_start.bat` im Hauptverzeichnis.
2. Eingabe der initialen Parameter (AC-Nummer und Datenträger-ID).
3. Das grafische Menü (`Python_Skript_Starter_menu.py`) öffnet sich und listet alle verfügbaren Skripte aus den Unterordnern auf.
4. Das gewünschte Skript kann durch Eingabe der entsprechenden Ziffer gestartet werden. Die Parameter werden automatisch an das Skript übergeben.

*Hinweis: Bestimmte Zusatzmodule (z. B. "Textdokumente_vergleichen") verfügen über eigene Startskripte. Beim Aufruf dieser Module über das Hauptmenü wird stattdessen ein separates Fenster geöffnet, das interaktiv nach einem Eingabe- und Ausgabe-Verzeichnis fragt, anstatt AC/Disk-ID zu verwenden.*

*Hinweis: Für die Ausführung wird eine Python-Umgebung mit den entsprechenden Abhängigkeiten (ExifTool, FFprobe, Siegfried, YARA, RapidFuzz, Sentence-Transformers etc.) benötigt.*

### Repository-Updates (Git)

Für die Synchronisation mit GitHub (Pull, Commit, Push) steht eine Hilfsdatei `git-update.bat` im Root-Verzeichnis bereit.

5. **Doppelklick auf `git-update.bat`** für ein automatisiertes Update:
   * Das Skript holt zunächst aktuelle Änderungen vom Server (`git pull`).
   * Es fügt alle lokalen Änderungen hinzu (`git add -A`).
   * Es erstellt einen Commit mit Zeitstempel.
   * Es lädt die Änderungen hoch (`git push`).

*Hinweis für die Zusammenarbeit: Bei paralleler Arbeit mehrerer Personen am Repository ist die Reihenfolge Pull → Commit → Push entscheidend. Sollten Konflikte auftreten, müssen diese manuell (z. B. via GitHub Desktop oder VS Code) gelöst werden.*

## Repository-Struktur

Das Repository ist so aufgebaut, dass jedes Skript (oder jede Skript-Gruppe) einen eigenen Ordner mit zugehöriger Dokumentation (`README.md`) und den eigentlichen Python-Dateien (im Unterordner `win/`) besitzt.

Skripte/
├── Workflow_Launcher_start.bat       <-- Startpunkt für die Arbeitsumgebung
├── Python_Skript_Starter_menu.py     <-- Zentrales Auswahlmenü
├── git-update.bat                    <-- Hilfs-Skript für Git-Updates (Pull/Commit/Push)
├── A_Analyse_Skript_Brunnhilde_Fixity/
│   ├── README.md
│   └── win/
│       ── A_Analyse_Skript_Brunnhilde_Fixity.py
├── Textdokumente_vergleichen/        <-- Eigenständiges Vergleichs-Modul
│   ├── README.md
│   ├── start.bat                     <-- Eigenständiger Starter (fragt nach Verzeichnissen)
│   ├── menu.py                       <-- Eigenes GUI-Menü für diesen Ordner
│   └── win/
│       └── ...
├── B_.../
│   ├── README.md
│   └── win/
│       └── ...
├── G_Metadata_Extraction_Indexing_filetrove/
│   ├── README.md
│   └── win/
│       ├── G_Metadata_Extraction_Indexing_filetrove.py
│       └── rules.yar                 <-- YARA-Regeln für die Dateiformat-Identifizierung
└── ...

---

## MASTER-WORKFLOW: Digitale Datenrettung & Langzeitarchivierung (LZA)

Dieses Dokument beschreibt die lückenlose Beweiskette (Chain of Custody) und die Transformation der Daten von der physischen Quelle bis zum versiegelten Archivpaket. Der Workflow basiert auf den Skripten A bis L und folgt dem "Dualen Output"-Prinzip.

================================================================================
PHASE 1: ERFASSUNG & ANALYSE (STUFE 0, 1, 2)
================================================================================

Ziel: Physische Dokumentation, Bit-Identität sichern und forensische Analyse.

### TREE-STRUKTUR (PHASE 1):

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/          
│   ├── *.tif                                    <-- Hardware-Fotos
│   └── 0_[ID]_carrier-description.xml           <-- Physische Beschreibung
├── 1_[ID]_image-LZA/                
│   ├── 01_[ID].img (oder .001 / .bin)           <-- Forensisches Image
│   └── logfiles/
│       ├── 1_[ID]_image-log.csv                 <-- Metadaten (SHA-512)
│       └── 01_[ID]_image-log.txt                <-- Text-Protokoll (SHA-512)
└── 2_[ID]_extracted-files/          
    ├── files/                                   <-- Die extrahierten Originaldaten
    ├── 2_[ID]_extracted-files.content           <-- Zusammenfassungs-XML (Skript B)
    └── 2_[ID]_extracted-files_brunnhilde/       <-- Ergebnis-Container (Skript A)
        ├── 2_[ID]_..._summary.json              <-- Fixity-Referenz (SHA-256)
        ├── 2_[ID]_..._tree.txt                  <-- Struktur-Bericht
        └── files_collection_report/             <-- Forensische Detail-Logs

================================================================================
PHASE 2: REPARATUR & NORMALISIERUNG (STUFE 3)
================================================================================

Ziel: Dateifehler beheben und Erhaltungs-Derivate (Digital Twins) erzeugen.

### TREE-STRUKTUR (PHASE 2):

Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 3_[ID]_for-transfer/             
    ├── files/                                   <-- KOPIE aus Stufe 2
    │   ├── dokument.doc                         <-- Reparatur: Endung korrigiert
    │   ├── dokument.doc.odt                     <-- ODF-Zwischenschritt
    │   └── dokument.doc.pdf                     <-- PDF/A Archiv-Derivat
    ├── 3_[ID]_for-transfer_repair-file-extension.log <-- Reparatur-Protokoll
    └── 3_[ID]_for-transfer_all-conversions.log  <-- Konvertierungs-Protokoll

### Erweiterte Dateiendungen-Erkennung (Skript C)

Das Reparatur-Skript nutzt eine mehrstufige Erkennungslogik mit folgenden Features:

**1. PRONOM-basierte Erkennung (Siegfried):**
- Analyse der Magic Bytes und binären Signaturen
- Manuelle Zuordnung für spezifische PRONOM-IDs
- Korrektur von ODT/ODS/ODP-Verwechslungen durch ZIP-Struktur-Analyse

**2. Spezialisierte Fallback-Erkennung:**
- **Magic Bytes**: Direkte Erkennung von PSD (`8BPS`) und FLV (`FLV`)
- **MusicXML**: Signatur-Prüfung auf `<score-partwise>` oder `<score-timewise>`
- **Flat XML**: Erkennung von FODT, FODS, FODP durch `office:mimetype`-Attribute
- **Office Open XML**: ZIP-Struktur-Analyse (word/, xl/, ppt/ Ordner)
- **Markdown**: Syntax-Analyse mit 13 Indikatoren (Überschriften, Links, Listen, Code-Blöcke, etc.)
- **CSV**: Strenge Erkennung (nur für Textdateien, mind. 5 Zeilen mit ≥2 konsistenten Trennzeichen)
- **MIME-Typ-Korrekturen**: Verhindert Falscherkennung von XML als XSL, RTF-Erkennung, etc.

**3. Intelligente Filter:**
- CSV- und Markdown-Erkennung nur für Textdateien (verhindert Falscherkennung binärer Dateien)
- Automatische Löschung von Windows-Systemdateien ohne archivischen Wert
- Debug-Ausgaben zur Analyse der gefundenen Dateien

================================================================================
PHASE 3: KURATIERUNG & VL-REPRESENTATION (STUFE 4 / VL)
================================================================================

Ziel: Bereinigung für das aktive Repository und Integritäts-Check.

### TREE-STRUKTUR (PHASE 3):

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 4_[ID]_VL/                      
│   ├── files/                                   <-- KOPIE aus Stufe 3
│   │   └── (Bereinigung: Systemmüll & technische Artefakte gelöscht)
│   ├── *.tif                                    <-- Kopie aus Stufe 0
│   ├── 2_[ID]_extracted-files.content           <-- Kopie aus Stufe 2
│   ├── 2_[ID]_extracted-files_tree.txt          <-- Kopie aus Stufe 2
│   ├── 3_[ID]_for-transfer.index                <-- Technischer Index (Stufe 4 Stand)
│   └── 3_[ID]_for-transfer_integrity.log        <-- Fixity-Beweis gegen Phase 1
└── (Logs aus Bereinigung: 4_[ID]_VL_delete-all.log, 4_[ID]_VL_delete-converted-odfs.log, 4_[ID]_VL_delete-converted-wavs.log wandern nach Stufe 5/logfiles)

================================================================================
PHASE 4: ARCHIV-VERSIEGELUNG (STUFE 5 / LZA)
================================================================================

Ziel: Konsolidierung aller Beweise und Erstellung des finalen AIP.

### TREE-STRUKTUR (PHASE 4):

TREE-STRUKTUR (VOR DER TAR-VERSIEGELUNG):
5_[ID]_LZA/
├── image/                                       <-- UMZUG aus Stufe 1
├── 3_files/                                     <-- UMZUG aus Stufe 3/files
├── 5_[ID]_LZA.index                             <-- Finaler Master-Index
└── logfiles/                                    <-- DER PROZESS-BEWEIS (Audit Trail)
    ├── 1_[ID]_image-log.csv / 01_[ID]_image-log.txt
    ├── 2_[ID]_extracted-files_brunnhilde-summary.json
    ├── 2_[ID]_extracted-files_brunnhilde.tar.gz <-- komprimiert (Skript L)
    ├── 3_[ID]_for-transfer.index                <-- Technischer Vor-Index
    ├── 3_[ID]_for-transfer_integrity.log        <-- Fixity-Beweis Phase 3
    ├── 4_[ID]_VL_delete-all.log                 <-- Bereinigung Phase 3 (Skript E)
    ├── 4_[ID]_VL_delete-converted-odfs.log      <-- Artefakt-Bereinigung (Skript F)
    ├── 4_[ID]_VL_delete-converted-wavs.log      <-- Artefakt-Bereinigung (Skript F)
    ├── 5_[ID]_LZA_premis.xml                    <-- Erhaltungs-Metadaten
    └── 5_[ID]_LZA_integrity.log                 <-- Finaler Fixity-Beweis (Skript K)

================================================================================
DAS ENDERGEBNIS (Dualer Output)
================================================================================

Nach dem letzten Skript (L) sind die Ordner 0, 1, 2 und 3 gelöscht. Stufe 5 wird in einen BagIt-Container verpackt und als `[Datenträger-ID]` umbenannt.

1. REPOSITORY (Ordner 4_[ID]_VL):
   Bereinigte Nutzdaten, Derivate und Dokumentation für den Katalog-Import.

2. ARCHIV-TRESOR (BagIt-konformer Ordner `[ID]/`):
   Forensische Bit-Kopien und die lückenlose Beweiskette mit `bag-info.txt`, `manifest-sha256.txt` und allen Daten im `data/`-Unterordner.

---

## ZUSATZMODUL: Textdokumente vergleichen

Dieser Unterordner enthält eine eigenständige Skriptsammlung zur syntaktischen und semantischen Analyse von Textdokumenten. Im Gegensatz zum Haupt-Workflow (der strikt mit AC-Nummer und Datenträger-ID arbeitet), fragt dieses Modul beim Start interaktiv über ein GUI nach einem **Eingabe-Verzeichnis** (zu analysierende Dokumente) und einem **Ausgabe-Verzeichnis** (für die Ergebnisse).

### Funktionen des Moduls:

1. **Dubletten-Erkennung (Binär + Inhaltlich)**:
   - **Binäre Dubletten**: Identische Dateien (gleiche Größe + SHA-256 Hash)
   - **Inhaltliche Dubletten**: Dokumente in verschiedenen Formaten (.doc, .docx, .pdf, .odt, .rtf) mit identischem Textinhalt
   - Intelligente Text-Normalisierung (Unicode, Trennstriche, Seitenkennungen)
   - Prioritätsliste für das Behalten des Originals (PDF > DOCX > ODT > RTF > TXT > MD)

2. **Text-Extraktion**: 
   - Automatisches Auslesen von reinem Text aus verschiedenen Formaten (.doc, .docx, .pdf, .odt, .txt, .rtf, etc.)
   - Direkte Python-Bibliotheken für gängige Formate (pypdf, docx, odf, striprtf)
   - LibreOffice als Fallback für komplexe oder alte Formate (.doc, .wpd, .pages, .epub)
   - Intelligenter Cache-System zur Vermeidung wiederholter Konvertierungen

3. **Syntaktischer Vergleich**: 
   - Hochperformanter, paralleler Vergleich von Dokumentenpaaren (unter Nutzung der C++-Engine `rapidfuzz` und Jaccard-Index-Filterung)
   - Dreistufige Filter-Logik: Wort-Overlap → Längenverhältnis → Zeichen-für-Zeichen-Vergleich
   - Intelligentes Bucketing (logarithmische Längen-Kategorien) für 95% weniger Vergleiche
   - Union-Find-Algorithmus zur effizienten Gruppenbildung
   - Multiprocessing über alle CPU-Kerne

4. **Gruppenbildung & Metriken**: 
   - Automatische Gruppierung zusammengehöriger Dokumente
   - Berechnung von Änderungsprozentsätzen (Zeichen/Wörter) gegenüber einem ermittelten Basisdokument (z. B. das älteste Dokument)
   - Smart Sampling (Anfang + Ende) für lange Dokumente

5. **KI-Semantische Analyse** (optional): 
   - Nutzung von Sentence-Transformers (`paraphrase-multilingual-mpnet-base-v2`) zur Erkennung inhaltlicher Ähnlichkeit
   - Kosinus-Ähnlichkeit für semantische Vektoren
   - Trigger-Wort-Erkennung (abstract, zusammenfassung, summary, etc.)
   - Intelligente Filterung (nur Kurztexte oder Dateien mit Trigger-Wörtern)

6. **Visualisierung**:
   - Interaktive Matplotlib-Diagramme (Zeitstrahl, Dateigrößen, Text-Änderungen, KI-Ähnlichkeit)
   - Gesamtübersicht und Einzelgruppen-Ansichten
   - Dynamische Formatierung basierend auf Datenmenge

7. **Export**: 
   - Generierung einer übersichtlichen, farbig formatierten Excel-Tabelle (`versionen_analyse_farbig.xlsx`)
   - CSV-Datei mit allen Metadaten, Gruppierungsergebnissen und Änderungsmetriken
   - Farbige Hervorhebung pro Gruppe (Pastellfarben)
   - Spezielle Markierung für Kurztexte (gelb)

### Nutzung des Moduls:

1. Im Hauptmenü den Buchstaben für `[ORDNER] Textdokumente_vergleichen` eingeben (z. B. `T`).
2. Es öffnet sich ein separates Terminal-Fenster mit dem eigenen `start.bat` und `menu.py` des Moduls.
3. Wählen Sie über den Datei-Explorer den Quell- und Zielordner aus.
4. Passen Sie bei Bedarf die Schwellenwerte (Ähnlichkeit, Längenverhältnis, Wort-Overlap, etc.) im GUI-Dialog an oder nutzen Sie die Standardwerte.
5. Nach Abschluss der Analyse und dem Schließen des Unter-Menüs kehren Sie automatisch zum Haupt-Workflow-Menü zurück.

---

## Erweiterte Features & Verbesserungen

### Automatische ClamAV-Updates
Das Brunnhilde-Analyse-Skript erkennt automatisch, wenn die Virendefinitionen älter als 7 Tage sind und öffnet ein Administrator-Fenster für das Update (`freshclam.exe`), während die Analyse mit den bisherigen Definitionen weiterläuft.

### Integritäts-Checks über alle Phasen
Das System führt mehrstufige Integritäts-Checks durch:
- **Phase 1 → Phase 3**: Vergleich der SHA-256 Hashes aus Stufe 2 mit den Dateien in Stufe 4
- **Phase 3 → Phase 4**: Finaler Integritäts-Check aller Dateien in Stufe 5 gegen alle vorherigen Referenzen (SHA-512, SHA-256, MD5)
- Detaillierte Protokollierung aller Abweichungen

### PREMIS v3 Konformität
Das PREMIS-Generator-Skript erstellt standardkonforme XML-Dateien mit:
- Automatische Erkennung des Quellmediums (USB-Stick, CD/DVD, Diskette, Festplatte)
- GND-Integration für Urheber (DNB SRU + lobid-gnd Fallback)
- ClamAV-Virus-Check-Events
- XSD-Validierung gegen das offizielle Schema der Library of Congress

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT
Gesamt-Workflow-Dokumentation V1.9 (Ergänzt um erweiterte Dateiendungen-Erkennung, Dubletten-Finder und detaillierte Feature-Beschreibungen)