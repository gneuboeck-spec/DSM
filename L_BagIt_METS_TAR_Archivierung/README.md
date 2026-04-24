# Skript L: Final Archiving (BagIt, METS & TAR-Versiegelung)

Dieses Skript bildet den krönenden Abschluss des digitalen Archivierungsworkflows. Es transformiert den vorbereiteten Staging-Ordner (Stufe 5) in ein normgerechtes Archival Information Package (AIP). Dabei wird ein BagIt-Container erstellt, eine METS-Steuerungsdatei generiert und alles in ein finales TAR-Archiv versiegelt. 

Nach erfolgreicher Archivierung führt das Skript eine umfassende Bereinigung durch: Es löscht die temporären Arbeitsstufen 0, 1, 2, 3 und 5, während die perfekt kuratierte VL-Stufe (Stufe 4) als aktives Repository erhalten bleibt.

---

## Hauptfunktionen

*   **BagIt-Containerisierung:** Verwandelt die LZA-Stufe in einen BagIt-Bag. Alle Nutzdaten und Logs wandern in das Unterverzeichnis data/, während kryptografische Manifeste die Integrität jeder einzelnen Datei garantieren.
*   **Tag-File Placement:** Positioniert den finalen Master-Index (.index) außerhalb des Datenverzeichnisses auf der Root-Ebene des Bags, um einen schnellen Zugriff auf das Inventar zu ermöglichen.
*   **METS-Generierung:** Erstellt eine mets.xml im Bag-Root. Diese Datei verknüpft den beschreibenden Master-Index (DMD) und die erhaltungsspezifischen PREMIS-Metadaten (AMD) logisch miteinander.
*   **TAR-Versiegelung:** Verpackt den gesamten Container in ein flaches, unkomprimiertes TAR-Archiv. Der Dateiname ist eindeutig durch AC-Nummer, Datenträger-ID und Zeitstempel definiert.
*   **Große Workflow-Bereinigung:**
    *   Löscht die leeren Arbeits-Hüllen der Stufen 0, 1, 2 und 3.
    *   Entfernt den temporären Bag-Staging-Ordner (Stufe 5) nach erfolgreicher TAR-Erstellung.
*   **Duales Output-Prinzip:** Die Stufe 4 (VL) bleibt als gebrauchsfertiges Resultat (Active Repository) für den direkten Import in das Bestandsführungssystem auf der Festplatte erhalten.

---

## TREE-Struktur & Das "Duale Ergebnis"

Nach Abschluss von Skript L sieht die Projektstruktur wie folgt aus (Ordner 0, 1, 2, 3 und 5 wurden gelöscht):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/

├── 4_[ID]_VL/                                     <-- ERGEBNIS 1: AKTIVES REPOSITORY
│   ├── files/                                     <-- Bereinigte Nutzdaten & Derivate
│   ├── 2_[ID]_extracted-files.content             <-- Inhaltsbericht (XML)
│   ├── 2_[ID]_extracted-files_tree.txt            <-- Strukturbericht (Text)
│   ├── 3_[ID]_for-transfer.index                  <-- Technisches Inventar (Vorstufe)
│   └── 3_[ID]_for-transfer_integrity.log          <-- Fixity-Nachweis (Phase 3)

└── [AC]_[ID]_[ZEITSTEMPEL].tar                    <-- ERGEBNIS 2: DER TRESOR (AIP)
    └── (Interner Aufbau des Bags)
        ├── data/                                  <-- Archivierte Nutzdaten & Logs
        │   ├── 3_files/                           <-- Alle extrahierten Originale & Derivate
        │   └── logfiles/
        │       ├── *.tif                          <-- Originalfotos der Hardware
        │       ├── 1_[ID]_image-log.csv           <-- Imaging Metadaten (SHA-512)
        │       ├── 01_[ID]_image-log.txt          <-- Imaging Text-Log (KryoFlux/GW)
        │       ├── 2_[ID]_extracted-files.content <-- XML Summary (Archiv-Kopie)
        │       ├── 2_[ID]_extracted-files_tree.txt <-- Text Tree (Archiv-Kopie)
        │       ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- Forensik-Zusammenfassung
        │       ├── 2_[ID]_extracted-files_brunnhilde/ <-- Ordner mit Detailberichten
        │       ├── 3_[ID]_for-transfer.index      <-- Technischer Vor-Index
        │       ├── 3_[ID]_for-transfer_all-conversions.log <-- Normalisierungs-Protokoll
        │       ├── 3_[ID]_for-transfer_repair-file-extension.log <-- Reparatur-Protokoll
        │       ├── 3_[ID]_for-transfer_integrity.log <-- Fixity-Beweis (Phase 3)
        │       ├── 5_[ID]_LZA_premis.xml          <-- Erhaltungsmetadaten (PREMIS)
        │       └── 5_[ID]_LZA_integrity.log       <-- Finaler Fixity-Beweis (Phase 4)
        ├── 5_[ID]_LZA.index                       <-- Master-Index (Tag-File)
        ├── mets.xml                               <-- METS-Steuerdatei (Tag-File)
        ├── bagit.txt                              <-- BagIt-Deklaration
        ├── bag-info.txt                           <-- Metadaten zum Bag
        └── manifest-sha256.txt                    <-- Digitale Versiegelung
```
---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt bagit für die Containerisierung und colorama für die Statusanzeige.
    pip install bagit colorama

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    python Skript_L_Final_Archiving.py AC_0001 ID_001

### Ablauf der Finalisierung

1. Sicherheitsabfrage: Der Benutzer muss den Start bestätigen.
2. Bagging: Der Ordner Stufe 5 wird in einen Bag verwandelt (Umzug der Daten nach data/).
3. Index-Fix: Der Master-Index wird aus dem Datenordner auf die oberste Bag-Ebene verschoben.
4. METS-Erstellung: Die mets.xml wird generiert und referenziert den Index und die PREMIS-Datei.
5. Manifest-Update: Der Bag berechnet seine Prüfsummen neu, um die Tag-Files (Index & METS) einzuschließen.
6. Archivierung: Das gesamte Paket wird in eine TAR-Datei geschrieben.
7. Bereinigung: Nach erfolgreichem Schreibvorgang werden alle redundanten Ordner (0, 1, 2, 3, 5) gelöscht.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT