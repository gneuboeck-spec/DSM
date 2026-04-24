# Skript G: Deep Metadata Extraction & Multi-Source Integrity Validator (filetrove)

Dieses Skript ist das zentrale technische Prüfwerkzeug in Phase 3 (Kuratierung & Bereinigung). Es kombiniert eine hochgradig automatisierte Metadaten-Extraktion mit einer lückenlosen Integritätsprüfung (Fixity-Check). Das Skript beweist mathematisch die Unveränderlichkeit der Daten, indem es aktuelle Prüfsummen live berechnet und gegen bis zu sechs verschiedene Dokumentationsquellen aus allen vorherigen Prozessstufen (Imaging, Forensik, Extraktion) validiert.

---

## Hauptfunktionen

*   **Multi-Source Integritätsprüfung (Triple-Algo):**
    *   Validiert Dateien flexibel gegen **SHA-512** (Imaging-Logs), **SHA-256** (Forensik/Index/PREMIS) und **MD5** (Siegfried-Berichte).
    *   Gleicht den Ist-Zustand jeder Datei in Stufe 4 live gegen die historischen Soll-Werte ab.
    *   Status-Kategorisierung:
        *   `verified`: Identität über alle verfügbaren Quellen bestätigt.
        *   `CORRUPTED_OR_MODIFIED`: Abweichung erkannt (Alarm-Ausgabe mit Soll/Ist-Vergleich).
        *   `new_file`: Rechtmäßiges Derivat (z. B. PDF/A-Konvertierung), für das keine Vorstufen-Hashes existieren.
*   **Detailliertes Integritäts-Protokoll (.log):**
    *   Erzeugt ein revisionssicheres Audit-Log (3_[ID]_for-transfer_integrity.log), das jede erfolgreiche Prüfung und jeden Fehler detailliert dokumentiert.
*   **Tiefgehende Metadaten-Extraktion:**
    *   Bündelt Informationen von ExifTool, Siegfried, FFprobe, Hachoir und YARA.
    *   Harmonisiert Tool-Tags in ein konsistentes, XML-basiertes Index-Schema (.index).
*   **Duale Archiv-Dokumentation:**
    *   Speichert die primären Berichte in Stufe 5 (LZA) und legt automatisch eine identische Arbeitskopie in Stufe 4 (VL) ab.

---

## TREE-Struktur & Dateipfade (Phase 3)

Das Skript verknüpft die gesamte bisherige Beweiskette. Hier ist die Übersicht der Datenflüsse:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 1_[ID]_image-LZA/logfiles/
│   ├── 1_[ID]_image-log.csv            <-- QUELLE (SHA-512)
│   └── 01_[ID]_image-log.txt           <-- QUELLE (SHA-512 / Greaseweazle)
├── 2_[ID]_extracted-files/
│   ├── 2_[ID]_..._summary.json         <-- QUELLE (SHA-256)
│   └── 2_[ID]_..._brunnhilde/
│       └── ... /siegfried.csv          <-- QUELLE (MD5)
├── 4_[ID]_VL/                          <-- ARBEITSBEREICH (Eingabe)
│   ├── files/                          <-- Hier liegen die zu prüfenden Dateien
│   ├── 3_[ID]_for-transfer.index       <-- ZIEL (Kopie des finalen Index)
│   └── 3_[ID]_for-transfer_integrity.log <-- ZIEL (Kopie des Audit-Logs)
└── 5_[ID]_LZA/logfiles/                <-- ZIEL (Primäre Dokumentation)
    ├── 3_[ID]_for-transfer.index       <-- ZIEL (Primärer Master-Index)
    └── 3_[ID]_for-transfer_integrity.log <-- ZIEL (Primärer Fixity-Beweis)
```
---

## Technische Voraussetzungen

Zusätzlich zu Python 3.10+ (Module: mutagen, PyPDF2, Pillow, yara-python) müssen folgende Tools erreichbar sein:
1. ExifTool (exiftool.exe)
2. Siegfried (sf.exe)
3. FFmpeg/FFprobe (ffprobe.exe)
4. Hachoir (hachoir-metadata.exe)
5. YARA (mit gültiger rules.yar)

---

## Ausführung

Das Skript wird über die Kommandozeile oder das zentrale Menü gestartet:

    python Skript_G_filetrove.py %AC_NUMBER% %DISK_ID%

### Ablauf der Validierung

1. **Initialisierung:** Das Skript lädt alle verfügbaren Hashes aus den 6 Quellen (CSV, JSON, Index, XML, TXT) in den Speicher.
2. **Fixity-Check:** Jede Datei im VL-Ordner wird live gehasht (SHA-256, bei Bedarf 512/MD5) und sofort verglichen.
3. **Extraktion:** Parallel dazu erfolgt die tiefe Metadaten-Analyse und Validierung (Lesbarkeit).
4. **Finalisierung:** Der technische Index und das menschenlesbare Integritäts-Log werden erzeugt und stufenübergreifend verteilt.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT