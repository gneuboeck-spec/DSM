# Skript L: Final Archiving (BagIt, METS & TAR)

Dieses Skript bildet den krönenden Abschluss des Datenverarbeitungs-Workflows. Es transformiert den vorbereiteten Staging-Ordner (Stufe 5) in ein normgerechtes Archival Information Package (AIP). Dabei wird ein BagIt-Container erstellt, eine METS-Steuerungsdatei generiert und alles in ein finales TAR-Archiv versiegelt. 

Nach erfolgreicher Archivierung bereinigt das Skript die gesamte Arbeitsumgebung und hinterlässt lediglich das fertige Archiv-Paket sowie den perfekt kuratierten VL-Ordner für den Import in das Ziel-Repository.

---

## Hauptfunktionen

*   **BagIt-Containerisierung:** Verwandelt die LZA-Stufe in einen BagIt-Bag. Alle Nutzdaten und Logs werden sicher in das Unterverzeichnis `data/` migriert, während Prüfsummen-Manifeste die Integrität garantieren.
*   **Tag-File Placement:** Positioniert den finalen Master-Index (.index) auf der Root-Ebene des Bags, um einen sofortigen Zugriff auf das Inventar zu ermöglichen.
*   **METS-Generierung:** Erstellt eine `mets.xml`, welche die beschreibenden Metadaten (Index) und die erhaltungsspezifischen Metadaten (PREMIS) logisch miteinander verknüpft.
*   **TAR-Archivierung:** Verpackt den gesamten Container in ein flaches, unkomprimiertes TAR-Archiv. Der Name folgt dem Schema: `[AC]_[ID]_[TIMESTAMP].tar`.
*   **Workflow-Finalisierung (Cleanup):**
    *   Löscht die temporären Arbeitsstufen 0, 1, 2, 3 und den Bag-Staging-Ordner (Stufe 5).
    *   **Repository-Erhalt:** Die Stufe 4 (VL) bleibt als gebrauchsfertiges Resultat für den direkten Import in das Bestandsführungssystem erhalten.

---

## TREE-Struktur & Das "Duale Output"-Ergebnis

Nach Abschluss dieses Skripts ist die Verzeichnisstruktur bereinigt. Es bleiben exakt zwei essentielle Ergebnisse für die Institution übrig:

Documents/data/[AC-Nummer]/[Datenträger-ID]/

├── 4_[ID]_VL/                          <-- ERGEBNIS 1: DAS AKTIVE REPOSITORY
│   ├── files/                          <-- Bereinigte Nutzdaten & Derivate (PDF/A, TIFF)
│   ├── 2_[ID]_extracted-files.content  <-- Inhaltsbericht (Technisch/Physisch)
│   ├── 2_[ID]_extracted-files_tree.txt <-- Struktur-Übersicht
│   ├── 3_[ID]_for-transfer.index       <-- Technisches Inventar (Index)
│   └── 3_[ID]_for-transfer_integrity.log <-- Fixity-Nachweis (Beweiskette)

└── [AC]_[ID]_[ZEITSTEMPEL].tar         <-- ERGEBNIS 2: DER TRESOR (AIP)
    └── (Interner BagIt-Aufbau)
        ├── data/                       <-- Nutzdaten, forensische Images & alle Prozesslogs
        ├── 5_[ID]_LZA.index            <-- Master-Index (Tag-File)
        ├── mets.xml                    <-- METS-Manifest (Steuerdatei)
        ├── bagit.txt                   <-- BagIt-Deklaration
        └── manifest-sha256.txt         <-- Kryptografische Versiegelung

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt `bagit` für die Containerisierung und `colorama` für die Statusanzeige.
    pip install bagit colorama

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    python Skript_L_Final_Archiving.py AC_12345 ID_001

### Ablauf der Finalisierung

1. **Bag-Erstellung:** Der LZA-Ordner wird in einen Bag verwandelt.
2. **Struktur-Fix:** Der Master-Index wird an die Wurzel verschoben; die `mets.xml` wird generiert.
3. **Manifest-Update:** Alle Prüfsummen des Bags werden aktualisiert, um die neu hinzugefügten Steuerdateien einzuschließen.
4. **Verpacken:** Das gesamte Verzeichnis wird in eine TAR-Datei geschrieben.
5. **Große Bereinigung:** Sobald das TAR-Archiv sicher geschrieben wurde, entfernt das Skript alle dezentralen Arbeitsstufen (0, 1, 2, 3) sowie den temporären Bag-Ordner.
6. **Abschluss:** Übrig bleiben das Archiv-AIP (Tresor) und der VL-Ordner (aktives Repository).

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT