# DSM - Digitale Datenrettung & Langzeitarchivierung (LZA)

Dieses Repository enthält die Skriptsammlung für den Master-Workflow zur digitalen Datenrettung und Langzeitarchivierung. Die Skripte automatisieren die lückenlose Beweiskette (Chain of Custody) und die Transformation der Daten von der physischen Quelle bis zum versiegelten Archivpaket.

## Schnellstart & Nutzung

Die Arbeitsumgebung wird zentral über den **Workflow Launcher** gestartet.

1. Doppelklick auf `Workflow_Launcher_start.bat` im Hauptverzeichnis.
2. Eingabe der initialen Parameter (AC-Nummer und Datenträger-ID).
3. Das grafische Menü (`Python_Skript_Starter_menu.py`) öffnet sich und listet alle verfügbaren Skripte aus den Unterordnern auf.
4. Das gewünschte Skript kann durch Eingabe der entsprechenden Ziffer gestartet werden. Die Parameter werden automatisch an das Skript übergeben.

*Hinweis: Für die Ausführung wird eine Python-Umgebung mit den entsprechenden Abhängigkeiten (ExifTool, FFprobe, Siegfried, YARA etc.) benötigt.*

## Repository-Struktur

Das Repository ist so aufgebaut, dass jedes Skript (oder jede Skript-Gruppe) einen eigenen Ordner mit zugehöriger Dokumentation (`README.md`) und den eigentlichen Python-Dateien (im Unterordner `win/`) besitzt.

```text
Skripte/
├── Workflow_Launcher_start.bat       <-- Startpunkt für die Arbeitsumgebung
├── Python_Skript_Starter_menu.py     <-- Zentrales Auswahlmenü
├── A_Analyse_Skript_Brunnhilde_Fixity/
│   ├── README.md
│   └── win/
│       └── A_Analyse_Skript_Brunnhilde_Fixity.py
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
```

---

## MASTER-WORKFLOW: Digitale Datenrettung & Langzeitarchivierung (LZA)

Dieses Dokument beschreibt die lückenlose Beweiskette (Chain of Custody) und die Transformation der Daten von der physischen Quelle bis zum versiegelten Archivpaket. Der Workflow basiert auf den Skripten A bis L und folgt dem "Dualen Output"-Prinzip.

================================================================================
PHASE 1: ERFASSUNG & ANALYSE (STUFE 0, 1, 2)
================================================================================

Ziel: Physische Dokumentation, Bit-Identität sichern und forensische Analyse.

### TREE-STRUKTUR (PHASE 1):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
── 0_[ID]_picture-carrier/          
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
```

================================================================================
PHASE 2: REPARATUR & NORMALISIERUNG (STUFE 3)
================================================================================

Ziel: Dateifehler beheben und Erhaltungs-Derivate (Digital Twins) erzeugen.

### TREE-STRUKTUR (PHASE 2):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 3_[ID]_for-transfer/             
    ├── files/                                   <-- KOPIE aus Stufe 2
    │   ├── dokument.doc                         <-- Reparatur: Endung korrigiert
    │   ├── dokument.doc.odt                     <-- ODF-Zwischenschritt
    │   ── dokument.doc.pdf                     <-- PDF/A Archiv-Derivat
    ├── 3_[ID]_for-transfer_repair-file-extension.log <-- Reparatur-Protokoll
    └── 3_[ID]_for-transfer_all-conversions.log  <-- Konvertierungs-Protokoll
```

================================================================================
PHASE 3: KURATIERUNG & VL-REPRESENTATION (STUFE 4 / VL)
================================================================================

Ziel: Bereinigung für das aktive Repository und Integritäts-Check.

### TREE-STRUKTUR (PHASE 3):

```text
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
```

================================================================================
PHASE 4: ARCHIV-VERSIEGELUNG (STUFE 5 / LZA)
================================================================================

Ziel: Konsolidierung aller Beweise und Erstellung des finalen AIP.

### TREE-STRUKTUR (PHASE 4):

```text
TREE-STRUKTUR (VOR DER TAR-VERSIEGELUNG):
5_[ID]_LZA/
├── 01_[ID].img                                  <-- UMZUG aus Stufe 1
── 3_files/                                     <-- UMZUG aus Stufe 3/files
├── 5_[ID]_LZA.index                             <-- Finaler Master-Index
├── mets.xml                                     <-- METS-Steuerdatei
└── logfiles/                                    <-- DER PROZESS-BEWEIS (Audit Trail)
    ├── 1_[ID]_image-log.csv / 01_[ID]_image-log.txt
    ├── 2_[ID]_extracted-files_brunnhilde-summary.json
    ├── 2_[ID]_extracted-files_brunnhilde/       <-- kompletter Ordner mit Detailberichten
    ├── 3_[ID]_for-transfer.index                <-- Technischer Vor-Index
    ├── 3_[ID]_for-transfer_integrity.log        <-- Fixity-Beweis Phase 3
    ├── 4_[ID]_VL_delete-all.log                 <-- Bereinigung Phase 3 (Skript E)
    ├── 4_[ID]_VL_delete-converted-odfs.log      <-- Artefakt-Bereinigung (Skript F)
    ├── 4_[ID]_VL_delete-converted-wavs.log      <-- Artefakt-Bereinigung (Skript F)
    ├── 5_[ID]_LZA_premis.xml                    <-- Erhaltungs-Metadaten
    ── 5_[ID]_LZA_integrity.log                 <-- Finaler Fixity-Beweis (Skript K)
```

================================================================================
DAS ENDERGEBNIS (Dualer Output)
================================================================================

Nach dem letzten Skript (L) sind die Ordner 0, 1, 2, 3 und 5 gelöscht.

1. REPOSITORY (Ordner 4_[ID]_VL):
   Bereinigte Nutzdaten, Derivate und Dokumentation für den Katalog-Import.

2. ARCHIV-TRESOR (Datei [AC]_[ID]_[ZEIT].tar):
   Forensische Bit-Kopien und die lückenlose Beweiskette (BagIt-konform).

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT
Gesamt-Workflow-Dokumentation V1.6 (Angepasst an neue Repository-Struktur)