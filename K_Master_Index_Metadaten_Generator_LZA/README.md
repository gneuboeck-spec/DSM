# Master-Index & Multi-Source Integrity Validator (LZA-Stufe)

Dieses Skript ist das finale Kontroll- und Indexierungswerkzeug im digitalen Archivierungsworkflow. Es führt eine tiefgehende Metadaten-Extraktion über den gesamten Inhalt der Stufe 5 (LZA) durch und erstellt ein lückenloses digitales Inventar (.index). Das herausragende Merkmal ist der integrierte Multi-Source-Fixity-Check, der die Integrität jeder Datei gegen bis zu sechs verschiedene Dokumentationsquellen aus allen vorherigen Prozessstufen mathematisch beweist.

Das Skript stellt sicher, dass kein Bit der Originaldaten während des Workflows (Extraktion, Reparatur, Bereinigung) verändert wurde.

---

## Hauptfunktionen

*   **Multi-Source Integritätsprüfung:**
    *   Abgleich gegen 6 Quellen: Imaging-Logs (CSV & TXT), Brunnhilde-Berichte (JSON & Siegfried-CSV), technischer Vor-Index (.index) und PREMIS-Erhaltungsmetadaten (.xml).
    *   **Triple-Algorithm Support:** Erkennt und validiert MD5, SHA-256 und SHA-512 gleichzeitig.
    *   **Namespace-agnostische PREMIS-Analyse:** Findet .raw-Track-Hashes in PREMIS-Dateien unabhängig von XML-Namespaces.
*   **Status-Kategorisierung im Master-Index:**
    *   verified: Die Datei ist absolut identisch mit den Werten aus der Erfassung (Imaging/Extraktion).
    *   CORRUPTED_OR_MODIFIED: Es wurde eine Abweichung festgestellt (Alarm-Meldung).
    *   new_file: Die Datei ist ein rechtmäßiges Derivat (z. B. PDF/A), für das keine Vorstufen-Hashes existieren können.
*   **Revisionssicheres Integritäts-Protokoll:**
    *   Erzeugt ein detailliertes Log (5_[ID]_LZA_integrity.log) im logfiles-Ordner.
    *   Dokumentiert im Fehlerfall exakt den Soll-Wert der Quelle und den Ist-Wert des aktuellen Scans.
*   **Tiefenanalyse (Metadata-Trove):**
    *   Bündelt technische Metadaten von Siegfried, ExifTool, FFprobe, Hachoir und YARA.
    *   Harmonisiert hunderte Tool-spezifische Tags in ein standardisiertes XML-Schema.
*   **Integrierte Validierung:** Prüft die technische Funktionalität (Lesbarkeit) von Dokumenten und Medienströmen.

---

## Technische Voraussetzungen

Zusätzlich zu Python 3.10+ müssen folgende Tools im System-Pfad erreichbar sein:
1. ExifTool (exiftool.exe)
2. Siegfried (sf.exe)
3. FFmpeg/FFprobe (ffprobe.exe)
4. Hachoir (hachoir-metadata.exe)
5. YARA (mit gültiger rules.yar)

---

## Verarbeitete Referenzquellen (logfiles/)

Das Skript scannt automatisch folgende Dateien für den Hash-Vergleich:
1.  **1_[ID]_image-log.csv:** SHA-512 (Images)
2.  **01_[ID]_image-log.txt:** SHA-512 (Greaseweazle .raw Tracks)
3.  **2_[ID]_extracted-files_brunnhilde/.../siegfried.csv:** MD5 (Forensik)
4.  **2_[ID]_extracted-files_brunnhilde-summary.json:** SHA-256 (Extraktion)
5.  **3_[ID]_for-transfer.index:** SHA-256 (Vor-Index)
6.  **5_[ID]_LZA_premis.xml:** SHA-256 (Archiv-Metadaten)

---

## Erwartete Ordnerstruktur

Das Skript arbeitet direkt in der finalen Archivstufe:

    Documents/data/[AC-Nummer]/[Datenträger-ID]/
    └── 5_[ID]_LZA/                    <-- ARBEITSVERZEICHNIS
        ├── 3_files/                    <-- Nutzdaten
        ├── [Images].img / .001         <-- Datenträger-Abbilder
        └── logfiles/                   <-- Quellen für Hashes & Ziel für Logs

---

## Ausführung

Das Skript wird über die Kommandozeile mit AC-Nummer und Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python master_index_lza.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1.  **Initialisierung:** Das Skript lädt alle verfügbaren Prüfsummen aus den 6 Referenzdateien in den Arbeitsspeicher.
2.  **Dateiscan:** Jede Datei in Stufe 5 wird erfasst.
3.  **Fixity-Validierung:** SHA-256, SHA-512 und MD5 werden (je nach Verfügbarkeit in den Quellen) live berechnet und verglichen.
4.  **Metadaten-Extraktion:** Technische Daten werden extrahiert und im XML-Format strukturiert.
5.  **Finalisierung:** 
    *   Der Master-Index (.index) wird in Stufe 5 gespeichert.
    *   Das Integritäts-Protokoll (.log) wird mit einer Erfolgsbestätigung oder einer detaillierten Alarmliste erstellt.
6.  **Abschluss:** Das Skript bietet das automatische Öffnen des LZA-Ordners an.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT