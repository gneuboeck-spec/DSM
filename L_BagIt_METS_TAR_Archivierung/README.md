# Finalisierungs-Skript (BagIt, METS & TAR-Archivierung)

Dieses Skript bildet den abschließenden Schritt im digitalen Archivierungsworkflow. Es verpackt alle konsolidierten Daten der LZA-Stufe (Stufe 5) in einen standardisierten BagIt-Container, generiert eine METS-Steuerungsdatei und erstellt ein finales, transportfähiges TAR-Archiv. Zudem bereinigt es die Arbeitsumgebung von redundanten Staging-Ordnern.

Das Skript stellt sicher, dass das Archivpaket sowohl für Menschen als auch für Maschinen (Archivsysteme) eindeutig interpretierbar und integer bleibt.

---

## Hauptfunktionen

*   **BagIt-Containerisierung:** Verwandelt den LZA-Ordner in einen BagIt-Bag. Alle Nutzdaten und Logs wandern in das Unterverzeichnis `data/`, während Prüfsummen-Manifeste auf der obersten Ebene erstellt werden.
*   **Master-Index als Tag-File:** Positioniert den zuvor erstellten Master-Index (`.index`) auf der Root-Ebene des Bags, um einen schnellen Zugriff auf das Inventar ohne Durchsuchen der Datenstruktur zu ermöglichen.
*   **Automatische METS-Generierung:** Erstellt eine `mets.xml` im Bag-Root. Diese Datei verknüpft den Master-Index (DMD) und die PREMIS-Datei (AMD) logisch miteinander und definiert die Struktur des AIP (Archival Information Package).
*   **TAR-Verpackung:** Erstellt ein flaches, unkomprimiertes TAR-Archiv des gesamten Bags. Der Dateiname enthält die AC-Nummer, die Datenträger-ID und einen Zeitstempel.
*   **Smarte Bereinigung (Cleanup):**
    *   Löscht den temporären Arbeitsordner der Stufe 5 nach erfolgreicher TAR-Erstellung.
    *   Entfernt die redundanten Staging-Stufen 0, 1, 2 und 3.
    *   **Erhalt der VL-Stufe:** Die Stufe 4 (VL) bleibt als Arbeitskopie und Referenz für die weitere Bearbeitung auf dem System erhalten.

---

## Technische Voraussetzungen

*   **Python:** Version 3.10 oder neuer empfohlen.
*   **Bibliotheken:**
    *   `bagit`: Für die Erstellung des BagIt-Containers.
    *   `colorama`: Für die farbliche Statusanzeige.
    ```bash
    pip install bagit colorama
    ```

---

## Erwartete Ordnerstruktur

Das Skript erwartet die fertig strukturierte LZA-Stufe (erstellt durch den Staging-Workflow) im Pfad:

    Documents/data/[AC-Nummer]/[Datenträger-ID]/
    ├── 0_... / 1_... / 2_... / 3_... (werden nach Erfolg gelöscht)
    ├── 4_[ID]_VL/ (bleibt erhalten)
    ├── 5_[ID]_LZA/ (Eingabe für Bagging)
    └── [AC]_[ID]_[TIMESTAMP].tar (ZIELDATEI)

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python final_archiver.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. **Bagging:** Das Skript ruft `bagit.make_bag` auf. Dabei werden Metadaten (Contact-Name, ZPH-ID) in die `bag-info.txt` geschrieben.
2. **Tag-File Placement:** Der Master-Index wird aus dem Datenverzeichnis auf die Root-Ebene verschoben.
3. **METS-Erstellung:** Die `mets.xml` wird generiert und referenziert die Pfade innerhalb des Bags (z.B. `data/logfiles/premis.xml`).
4. **Manifest-Update:** Die BagIt-Manifeste werden aktualisiert, um die neu hinzugefügten Tag-Files (Index & METS) abzusichern.
5. **Archivierung:** Der gesamte Bag wird in eine TAR-Datei geschrieben.
6. **Cleanup:** Sobald das TAR-Archiv sicher auf der Festplatte liegt, werden die temporären Ordner der Stufen 0, 1, 2, 3 und 5 gelöscht.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT