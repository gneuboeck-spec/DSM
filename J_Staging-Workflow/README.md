# Skript J: Staging-Workflow & LZA-Strukturierung

Dieses Skript ist der strategische "Organisator" des Workflows. Es dient der finalen Konsolidierung aller Projektdaten vor der Archivierung. Es führt die dezentralen Arbeitsergebnisse aus den Stufen 0 bis 3 zusammen, vervollständigt die Metadaten in der VL-Stufe (Stufe 4) und bereitet die LZA-Stufe (Stufe 5) für die abschließende Indexierung und PREMIS-Erstellung vor.

Das Skript automatisiert den Umzug und die standardkonforme Umbenennung von Dateien, um eine saubere Archivstruktur zu gewährleisten.

---

## Hauptfunktionen

*   **Vervollständigung der VL-Stufe (Stage 4):**
    *   Kopiert Hardware-Fotos (.tif) aus Stufe 0 in den VL-Ordner.
    *   Synchronisiert Inhaltsübersichten (.content und _tree.txt) aus Stufe 2 für das aktive Repository.
*   **Restrukturierung der LZA-Stufe (Stage 5):**
    *   **Zentralisierung der Protokolle:** Sammelt alle Log-Ordner und Einzelberichte aus den Stufen 0, 1, 2 und 3 und mergt sie in den zentralen Ordner `5_[ID]_LZA/logfiles`.
    *   **Integration der Nutzdaten:** Verschiebt den "files"-Ordner aus Stufe 3 in die Archivstufe und benennt ihn zur eindeutigen Identifikation in `3_files` um.
    *   **Image-Migration:** Verschiebt forensische Disk-Images aus Stufe 1 direkt in die Wurzel der LZA-Stufe.
    *   **Forensik-Berichte:** Integriert Brunnhilde-Zusammenfassungen und JSON-Statistiken in den LZA-Logbereich.
*   **Sicherheitslogik:** Nutzt eine interaktive Abfrage vor dem Start und schützt bestehende Daten durch eine "Safe-Move"-Logik, die Namenskollisionen verhindert.

---

## TREE-Struktur & Datenfluss (Phase 4)

Das Skript steuert die Transformation der Arbeitsordner in die finale Archivstruktur:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_..._picture-carrier/     ──┐
├── 1_..._image-LZA/           ──┼─► [Verschieben & Konsolidieren]
├── 2_..._extracted-files/     ──┤
├── 3_..._for-transfer/        ──┘
│
├── 4_[ID]_VL/                          <-- REPOSITORY-STUFE (Kopie)
│   ├── *.tif (Hardware-Fotos)
│   ├── 2_[ID]_extracted-files.content
│   └── 2_[ID]_extracted-files_tree.txt
│
└── 5_[ID]_LZA/                         <-- ARCHIV-STAGING (Ziel)
    ├── 01_[ID].img (Disk-Image)
    ├── 3_files/ (Nutzdaten, ehemals Stage 3/files)
    └── logfiles/                       <-- Zentraler Log-Pool
        ├── *.tif (Originalfotos)
        ├── 1_[ID]_image-log.csv
        ├── 2_[ID]_..._brunnhilde/
        └── (Alle weiteren Prozess-Logs)

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt colorama für die farbliche Statusanzeige.
    pip install colorama

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf:
    python Skript_J_Staging.py AC_0001 ID_001

### Ablauf der Ausführung

1.  **Initialisierung:** Das Skript sucht nach dem Quell-Nutzdatenordner in Stufe 3.
2.  **VL-Vervollständigung:** Fotos und Inhaltsberichte werden nach Stufe 4 kopiert. Dies stellt sicher, dass das aktive Repository alle Dokumente für die Verzeichnung enthält.
3.  **LZA-Konsolidierung:** 
    *   Alle Arbeitslogs werden in den zentralen Stufe-5-Logordner verschoben.
    *   Die forensischen Images werden in das Stufe-5-Hauptverzeichnis migriert.
    *   Die Nutzdaten werden als `3_files` in das Archivpaket eingebunden.
4.  **Abschluss:** Die Stufen 0 bis 3 sind nach dem Durchlauf konsolidiert, und Stufe 5 ist bereit für den Master-Index (Skript K) und das finale Packaging.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT