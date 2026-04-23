# Skript K: Master-Index & Multi-Source Integrity Validator (LZA)

Dieses Skript ist das finale Kontroll- und Indexierungswerkzeug in Phase 4 (LZA-Paketierung). Es führt eine tiefgehende Metadaten-Extraktion über den gesamten Inhalt der Stufe 5 (LZA) durch und erstellt das lückenlose digitale Inventar (.index). Das Kernstück ist der Multi-Source-Fixity-Check: Jede Datei im Paket wird live gegen bis zu sechs historische Quellen aus allen Vorstufen validiert, um die absolute Unveränderlichkeit der Daten zu beweisen.

---

## Hauptfunktionen

*   **Multi-Source Integritätsprüfung (Triple-Algo):**
    *   Abgleich gegen **SHA-512** (Imaging-Logs), **MD5** (Siegfried-Forensik) und **SHA-256** (Extraktion/Index/PREMIS).
    *   Namespace-agnostische PREMIS-Analyse: Findet Hashes von .raw-Tracks in XML-Strukturen unabhängig von Namespaces.
*   **Status-Kategorisierung im Inventar:**
    *   `verified`: Identität über die gesamte Prozesskette mathematisch bewiesen.
    *   `CORRUPTED_OR_MODIFIED`: Abweichung erkannt (Soll/Ist-Alarm im Terminal und Log).
    *   `new_file`: Legitimes Derivat (z. B. PDF/A), das erst im Workflow entstanden ist.
*   **Revisionssicheres Archiv-Protokoll:**
    *   Erzeugt das finale Integritäts-Log (5_[ID]_LZA_integrity.log) im logfiles-Ordner.
*   **Tiefenanalyse & Harmonisierung:**
    *   Bündelt Metadaten von ExifTool, Siegfried, FFprobe, Hachoir und YARA in einem einheitlichen XML-Schema.
    *   Validiert die technische Lesbarkeit aller archivierten Objekte.

---

## TREE-Struktur & Dateipfade (Phase 4)

Das Skript arbeitet im fertig konsolidierten LZA-Staging-Ordner. Es liest historische Hashes aus den Protokollen und erzeugt den finalen Index:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 5_[ID]_LZA/                            <-- ARBEITSBEREICH (Finales Staging)
    ├── 01_[ID].img                        <-- Objekt (Image)
    ├── 3_files/                           <-- Objekte (Nutzdaten & Derivate)
    │   └── ...
    ├── 5_[ID]_LZA.index                   <-- ZIEL (Finaler Master-Index)
    └── logfiles/                          <-- QUELLEN & ZIEL FÜR LOGS
        ├── 1_[ID]_image-log.csv           <-- Quelle: SHA-512 (Images)
        ├── 01_[ID]_image-log.txt          <-- Quelle: SHA-512 (.raw Tracks)
        ├── 2_[ID]_..._brunnhilde/         <-- Quelle: MD5 (siegfried.csv)
        ├── 2_[ID]_..._summary.json        <-- Quelle: SHA-256 (Extraktion)
        ├── 3_[ID]_for-transfer.index      <-- Quelle: SHA-256 (VL-Stand)
        ├── 5_[ID]_LZA_premis.xml          <-- Quelle: SHA-256 (Erhaltungsdaten)
        └── 5_[ID]_LZA_integrity.log       <-- ZIEL: Finaler Integritäts-Beweis

---

## Technische Voraussetzungen

Zusätzlich zu Python 3.10+ müssen folgende Tools im System-Pfad verfügbar sein:
1. ExifTool (exiftool.exe)
2. Siegfried (sf.exe)
3. FFmpeg/FFprobe (ffprobe.exe)
4. Hachoir (hachoir-metadata.exe)
5. YARA (mit gültiger rules.yar)

---

## Ausführung

Das Skript wird über die Kommandozeile mit AC-Nummer und Datenträger-ID gestartet:

    python Skript_K_MasterIndex_LZA.py %AC_NUMBER% %DISK_ID%

### Ablauf der Finalisierung

1. **Hash-Aggregation:** Das Skript lädt alle Soll-Hashes aus den 6 Referenzdateien (CSV, JSON, Index, XML, TXT).
2. **Paket-Scan:** Jede Datei in Stufe 5 (Images, files, logs) wird erfasst.
3. **Fixity-Beweis:** Live-Berechnung der Prüfsummen und Vergleich mit der historischen Liste.
4. **Inventarisierung:** Erstellung des .index-Files mit harmonisierten Metadaten.
5. **Abschluss:** Das Integritäts-Log wird als finaler Beweis für die "Chain of Custody" in den logfiles-Ordner geschrieben.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT