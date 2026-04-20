# Deep Metadata Extraction & Integrity Verification (filetrove)

Dieses Skript ist das zentrale Werkzeug zur technischen Validierung und Erstellung des Master-Index für die Langzeitarchivierung. Es kombiniert eine tiefgehende Metadaten-Extraktion mit einer automatisierten Integritätsprüfung (Fixity-Check). Es beweist mathematisch, dass die Dateien während der Bearbeitung (Bereinigung, Reparatur) nicht verändert wurden, indem es aktuelle Prüfsummen live mit den Protokollen der Vorstufen (Imaging und Extraktion) vergleicht.

Das Skript scannt die fertigen Dateien in der VL-Stufe (Stufe 4) und dokumentiert die Ergebnisse revisionssicher für das Archiv (Stufe 5).

---

## Hauptfunktionen

*   Automatisierter Integritäts-Check (Fixity-Abgleich):
    *   Lädt beim Start automatisch vorhandene SHA-256 Hashes aus Stufe 1 (Imaging-Log CSV) und Stufe 2 (Brunnhilde-Zusammenfassung JSON).
    *   Vergleicht den Ist-Zustand jeder Datei in Stufe 4 live mit diesen Referenzwerten.
    *   Status-Kategorisierung:
        *   verified: Datei ist absolut identisch mit dem Original-Rip.
        *   CORRUPTED_OR_MODIFIED: Die Datei wurde seit der Extraktion verändert oder beschädigt (Alarm-Meldung).
        *   new_file: Die Datei ist ein neu erstelltes Derivat (z.B. PDF-Konvertierung) ohne alten Referenzwert.
*   Detailliertes Integritäts-Protokoll (.log):
    *   Erzeugt ein menschenlesbares Protokoll (3_[ID]_for-transfer_integrity.log), das jede erfolgreiche Verifizierung und jede Abweichung (mit Soll/Ist-Vergleich) auflistet.
*   Multi-Tool-Metadaten-Extraktion:
    *   Extrahiert technische Daten via Siegfried, ExifTool, FFprobe, Hachoir und YARA.
    *   Führt alle Ergebnisse in einer konsistenten, XML-basierten Indexdatei (.index) zusammen.
*   Integrierte Validierung: Prüft die Funktionalität der Dateien (z.B. Lesbarkeit von PDFs, Bild-Integrität) und vermerkt dies im <validity>-Tag.
*   Stufenübergreifender Workflow: Liest Daten aus Stufe 4, speichert den Master-Index primär in Stufe 5 ab und legt eine Arbeitskopie zurück in Stufe 4.

---

## Technische Voraussetzungen

Zusätzlich zu Python 3.10+ müssen folgende Tools im System-Pfad erreichbar sein:
1. ExifTool (exiftool.exe)
2. Siegfried (sf.exe)
3. FFmpeg/FFprobe (ffprobe.exe)
4. Hachoir (hachoir-metadata.exe)
5. YARA (mit gültiger rules.yar)

---

## Erwartete Ordnerstruktur

Das Skript verknüpft die gesamte Prozesskette:

    Documents/data/[AC-Nummer]/[Datenträger-ID]/
    ├── 1_[ID]_image-LZA/logfiles/         <-- QUELLE (Imaging-Log CSV)
    ├── 2_[ID]_extracted-files/            <-- QUELLE (Brunnhilde JSON)
    ├── 4_[ID]_VL/files/                   <-- EINGABE (Zu scannende Dateien)
    └── 5_[ID]_LZA/logfiles/               <-- ZIEL (Index & Integrity-Log)

---

## Ausführung

Das Skript wird über die Kommandozeile mit AC-Nummer und Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python metadata_integrity_check.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Initialisierung: Das Skript validiert alle Pfade und lädt die Referenz-Hashes aus den Stufen 1 und 2 in den Speicher.
2. Dateiscan: Jede Datei im VL-Ordner (Stufe 4) wird indexiert.
3. Fixity-Check: Unmittelbar nach der SHA-256-Berechnung erfolgt der Abgleich mit der Referenzliste. Abweichungen werden sofort im Terminal rot markiert.
4. Metadaten-Erfassung: Parallel dazu werden alle technischen Metadaten extrahiert und harmonisiert.
5. Berichterstellung:
   - Der technische Master-Index (.index) wird geschrieben.
   - Das Integritäts-Protokoll (.log) wird mit einer Zusammenfassung aller Prüf-Ergebnisse erstellt.
6. Finalisierung: Die Berichte werden in den LZA-Ordner (Stufe 5) verschoben und als Arbeitskopie zurück nach Stufe 4 kopiert.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT