# Staging-Workflow Skript (Vorbereitung für LZA & Master-Index)

Dieses Skript dient der finalen Konsolidierung und Strukturierung aller Projektdaten vor der Übergabe in die Langzeitarchivierung (LZA). Es führt die Arbeitsergebnisse aus den Stufen 0 bis 3 zusammen, vervollständigt die Metadaten in der VL-Stufe (Stufe 4) und bereitet die LZA-Stufe (Stufe 5) für die Erstellung des Master-Index und der PREMIS-Dokumentation vor.

Das Skript automatisiert den Umzug und die Umbenennung von Dateien, um eine konsistente Archivstruktur gemäß dem internen Standard zu gewährleisten.

---

## Hauptfunktionen

*   Vervollständigung der VL-Stufe (Stage 4):
    *   Kopiert automatisch Objektaufnahmen (.tif) aus Stufe 0 in den VL-Ordner.
    *   Synchronisiert Inhaltsübersichten (.content und _tree.txt) aus Stufe 2.
    *   Verifiziert das Vorhandensein des technischen Index.
*   Restrukturierung der LZA-Stufe (Stage 5):
    *   Zentralisierung aller Log-Dateien: Sammelt Logfiles aus den Stufen 0, 1, 2 und 3 und verschiebt sie in einen zentralen Unterordner `5_[ID]_LZA/logfiles`.
    *   Umzug der Nutzdaten: Verschiebt den "files"-Ordner aus Stufe 3 nach Stufe 5 und benennt ihn in `3_files` um.
    *   Image-Konsolidierung: Verschiebt die Disk-Images aus Stufe 1 direkt in die Wurzel von Stufe 5.
    *   Forensik-Integration: Verschiebt Brunnhilde-Berichte und Zusammenfassungen aus Stufe 2 in den LZA-Logordner.
*   Sicherheitsmechanismen: Nutzt eine interaktive Sicherheitsabfrage vor dem Start und schützt bestehende Daten durch eine "Safe-Move"-Logik (Vermeidung von Datenverlust bei Namenskollisionen).

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt colorama für die farbliche Statusanzeige in der Konsole.
    pip install colorama

---

## Erwartete Ordnerstruktur

Das Skript ist der "Organisator", der die Datenflüsse zwischen den Stufen steuert:

    Documents/data/[AC-Nummer]/[Datenträger-ID]/
    ├── 0_..._picture-carrier/     --> (Inhalt wird nach 5/logfiles verschoben)
    ├── 1_..._image-LZA/           --> (Inhalt wird nach 5 verschoben)
    ├── 2_..._extracted-files/     --> (Berichte werden nach 4 kopiert & nach 5 verschoben)
    ├── 3_..._for-transfer/        --> (files wird zu 5/3_files, Rest nach 5/logfiles)
    ├── 4_..._VL/                  --> (Wird mit Fotos und Berichten vervollständigt)
    └── 5_..._LZA/                 --> (ZIEL: Strukturierte Archiv-Stufe)

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python staging_workflow.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Das Skript prüft die Existenz der Basisordner und sucht den Quell-Nutzdatenordner in Stufe 3.
2. VL-Sync (Schritt 1): Fotos und Inhaltsberichte werden nach Stufe 4 kopiert. Dies dient der Dokumentation in der Bereinigungsstufe.
3. LZA-Konsolidierung (Schritt 2):
   - Alle dezentralen Log-Ordner werden in den zentralen LZA-Logordner gemergt.
   - Originalbilder der Hardware werden archivsicher in den Log-Bereich verschoben.
   - Die extrahierten Dateien werden als `3_files` in die Archivstufe integriert.
   - Disk-Images werden auf die oberste Ebene von Stufe 5 verschoben.
4. Abschluss: Die Stufen 0 bis 3 sind nach dem Durchlauf weitestgehend geleert bzw. konsolidiert, und Stufe 5 ist bereit für die finalen Indexierungsskripte.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT