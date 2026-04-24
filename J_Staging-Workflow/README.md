# Skript J: Staging-Workflow & LZA-Strukturierung

Dieses Skript ist der strategische "Organisator" des Workflows. Es dient der finalen Konsolidierung aller dezentralen Arbeitsergebnisse vor der Archivierung. Es führt die Daten aus den Stufen 0 bis 3 zusammen, vervollständigt die Dokumentation in der VL-Stufe (Stufe 4) und bereitet die LZA-Stufe (Stufe 5) für die abschließende Indexierung und PREMIS-Erstellung vor.

Das Skript automatisiert den Umzug und die standardkonforme Umbenennung von Dateien, um eine saubere Archivstruktur zu gewährleisten und die ursprünglichen Arbeitsordner leerzuräumen.

---

## Hauptfunktionen

*   **Vervollständigung der VL-Stufe (Stage 4):**
    *   Kopiert Hardware-Fotos (.tif) aus Stufe 0 in den VL-Ordner.
    *   Kopiert Inhaltsberichte (.content und _tree.txt) aus Stufe 2 in den VL-Ordner.
*   **Restrukturierung der LZA-Stufe (Stage 5):**
    *   **Zentralisierung der Protokolle:** Sammelt alle Log-Dateien aus den Stufen 0, 1, 2 und 3 und verschiebt sie gesammelt in den Ordner 5_[ID]_LZA/logfiles.
    *   **Integration der Nutzdaten:** Verschiebt den "files"-Ordner aus Stufe 3 in die Archivstufe und benennt ihn zur eindeutigen Identifikation in 3_files um.
    *   **Image-Migration:** Verschiebt forensische Disk-Images aus Stufe 1 direkt in die Wurzel der LZA-Stufe.
    *   **Bereinigung der Arbeitsstufen:** Nach dem erfolgreichen Verschieben (Move-Logik) sind die ursprünglichen Ordner 0, 1, 2 und 3 leergeräumt.
*   **Sicherheitslogik:** Beinhaltet eine interaktive Abfrage vor dem Start und nutzt eine "Safe-Move"-Funktion, die bestehende Zielordner bei Bedarf überschreibt, um einen sauberen Stand zu garantieren.

---

## TREE-Struktur & Datenfluss (Phase 4)

Das Skript transformiert die dezentralen Arbeitsordner in die finale Archivstruktur von Stufe 5:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/

├── 4_[ID]_VL/                                     <-- [SCHRITT 1: KOPIEREN]
│   ├── *.tif (Hardware-Fotos)                     <-- Kopie aus Stufe 0
│   ├── 2_[ID]_extracted-files.content             <-- Kopie aus Stufe 2
│   └── 2_[ID]_extracted-files_tree.txt            <-- Kopie aus Stufe 2
│
└── 5_[ID]_LZA/                                    <-- [SCHRITT 2: ZIELSTRUKTUR]
    ├── 01_[ID].img (oder .001 / .bin)             <-- Umzug aus Stufe 1
    ├── 3_files/                                   <-- Umzug & Umbenennung aus Stufe 3/files
    └── logfiles/                                  <-- Zentraler Dokumentations-Pool
        ├── *.tif (Originalfotos der Hardware)     <-- Umzug aus Stufe 0
        ├── 0_[ID]_carrier-description.xml         <-- Umzug aus Stufe 0
        ├── 1_[ID]_image-log.csv                   <-- Umzug aus Stufe 1
        ├── 01_[ID]_image-log.txt                  <-- Umzug aus Stufe 1
        ├── 2_[ID]_extracted-files.content         <-- Umzug aus Stufe 2
        ├── 2_[ID]_extracted-files_tree.txt        <-- Umzug aus Stufe 2
        ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- Umzug aus Stufe 2
        ├── 2_[ID]_extracted-files_brunnhilde/     <-- Umzug aus Stufe 2
        ├── 3_[ID]_for-transfer_all-conversions.log <-- Umzug aus Stufe 3
        └── 3_[ID]_for-transfer_repair-file-extension.log <-- Umzug aus Stufe 3
```
(Die Ordner 0, 1, 2 und 3 sind nach diesem Schritt leer.)

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt colorama für die Statusanzeige.
    pip install colorama

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf:
    python Skript_J_Staging.py AC_0001 ID_001

### Ablauf der Ausführung

1.  **Sicherheitsabfrage:** Der Benutzer muss das Staging explizit bestätigen.
2.  **VL-Export (Schritt 1):** Fotos und Inhaltsberichte werden nach Stufe 4 kopiert. Dies stellt sicher, dass das aktive Repository (VL) alle Dokumente für die Verzeichnung enthält, bevor die Quellordner geleert werden.
3.  **LZA-Staging (Schritt 2):** 
    *   Alle Log-Dateien aus 0, 1, 2 und 3 werden im zentralen Ordner `5/logfiles` zusammengeführt.
    *   Forensische Images werden nach 5 migriert.
    *   Die Nutzdaten (der `files`-Ordner) werden als `3_files` in die Archivstufe verschoben.
4.  **Abschluss:** Die Arbeitsordner 0-3 sind nach dem Durchlauf leer, und Stufe 5 enthält die komplette, archivfähige Struktur für den Master-Index (Skript K).

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT