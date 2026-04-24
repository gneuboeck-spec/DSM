# Skript K: Master-Index & Multi-Source Integrity Validator (LZA-Stufe)

Dieses Skript ist das finale Kontroll- und Indexierungswerkzeug in Phase 4 (LZA-Paketierung). Es führt eine tiefgehende Metadaten-Extraktion über den gesamten Inhalt der Stufe 5 (LZA) durch und erstellt ein lückenloses digitales Inventar (.index). Das Kernstück ist der Multi-Source-Fixity-Check: Jede Datei im Paket wird live gegen bis zu sechs historische Dokumentationsquellen aus allen vorherigen Prozessstufen validiert, um die absolute Unveränderlichkeit der Daten vor der Archivierung zu beweisen.

---

## Hauptfunktionen

*   **Multi-Source Integritätsprüfung (Triple-Algo):**
    *   **SHA-512 Abgleich:** Verifiziert Images und Tracks gegen das Imaging-Log (CSV/TXT).
    *   **SHA-256 Abgleich:** Validiert Nutzdaten gegen die Brunnhilde-Zusammenfassung, den technischen Vor-Index und die PREMIS-Erhaltungsmetadaten.
    *   **MD5 Abgleich:** Prüft Dateien gegen den originalen Siegfried-Forensik-Bericht.
*   **Status-Kategorisierung im Inventar:**
    *   `verified`: Identität über die gesamte Prozesskette mathematisch bewiesen.
    *   `CORRUPTED_OR_MODIFIED`: Abweichung erkannt (Alarm-Ausgabe mit detailliertem Soll/Ist-Vergleich im Terminal).
    *   `new_file`: Legitimes Derivat (z. B. PDF/A), das erst im Workflow entstanden ist.
*   **Revisionssicheres Archiv-Protokoll:**
    *   Erzeugt das finale Integritäts-Log (5_[ID]_LZA_integrity.log) im logfiles-Ordner der Stufe 5.
*   **Tiefenanalyse & Harmonisierung:**
    *   Bündelt Metadaten von ExifTool, Siegfried, FFprobe, Hachoir und YARA in einem einheitlichen XML-Schema.

---

## TREE-Struktur & Dateipfade (Phase 4)

Das Skript arbeitet im fertig konsolidierten LZA-Staging-Ordner. Es scannt alle Objekte und gleicht sie mit den Protokollen im logfiles-Ordner ab:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
└── 5_[ID]_LZA/                            <-- ARBEITSBEREICH (Eingabe)
    ├── 01_[ID].img (oder .001 / .bin)     <-- OBJEKT (Gegen SHA-512 geprüft)
    ├── 3_files/                           <-- OBJEKTE (Gegen SHA-256/MD5 geprüft)
    │   └── ... (Originale & Derivate)
    ├── 5_[ID]_LZA.index                   <-- ZIEL (Finaler Master-Index)
    └── logfiles/                          <-- QUELLEN & ZIEL FÜR LOGS
        ├── 1_[ID]_image-log.csv           <-- Quelle: SHA-512 (Spalte: SHA-512-Hash)
        ├── 01_[ID]_image-log.txt          <-- Quelle: SHA-512 (Sektion: SHA-512-Hashes)
        ├── 2_[ID]_extracted-files_brunnhilde/
        │   └── files_collection_report/
        │       └── siegfried.csv          <-- Quelle: MD5 (Spalte: md5)
        ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- Quelle: SHA-256 (Feld: sha256)
        ├── 3_[ID]_for-transfer.index      <-- Quelle: SHA-256 (Tag: sha256)
        ├── 5_[ID]_LZA_premis.xml          <-- Quelle: SHA-256 (Tag: messageDigest)
        └── 5_[ID]_LZA_integrity.log       <-- ZIEL: Finaler Fixity-Beweis

---

## Technische Voraussetzungen

Zusätzlich zu Python 3.10+ müssen folgende Tools im System-Pfad erreichbar sein:
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

1. **Multi-Source Loading:** Das Skript lädt alle Soll-Hashes aus den 6 Referenzdateien gleichzeitig in einen intelligenten Speicher.
2. **Paket-Scan:** Jede Datei in Stufe 5 (Images, Nutzdaten, Logs) wird erfasst.
3. **Hybrid-Validierung:** Je nach Verfügbarkeit in den Quellen werden SHA-256, SHA-512 und MD5 live berechnet und verglichen.
4. **Detail-Reporting:** Bei Abweichungen wird exakt dokumentiert, welcher Wert (z.B. MD5) aus welcher Quelle nicht mit dem aktuellen Scan übereinstimmt.
5. **Abschluss:** Das Integritäts-Log wird als finaler Beweis für die lückenlose Kette ("Chain of Custody") erstellt.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT