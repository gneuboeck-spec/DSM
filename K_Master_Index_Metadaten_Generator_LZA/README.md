# Master-Index & Metadaten-Generator (LZA-Stufe)

Dieses Skript ist das finale Indexierungswerkzeug für das Langzeitarchivierungspaket (LZA). Es führt eine tiefgehende Metadaten-Extraktion über den gesamten Inhalt der Stufe 5 durch und erstellt eine zentrale XML-Indexdatei (.index). Diese Datei dient als maschinenlesbares Inventar und technische Dokumentation des gesamten Archivpakets.

Im Gegensatz zur VL-Version ist dieses Skript speziell auf die finale Struktur in Stufe 5 optimiert und enthält Sonderlogiken für forensische Dateiformate.

---

## Hauptfunktionen

*   Zentrales Archiv-Inventar: Erstellt die finale .index-Datei direkt im LZA-Verzeichnis (Stufe 5), die alle Dateien, Prüfsummen und technischen Metadaten bündelt.
*   Multi-Tool-Metadaten-Extraktion: Kombiniert die Analyseergebnisse von Siegfried, ExifTool, FFprobe, Hachoir und YARA.
*   Erweiterte Forensik-Logik (Greaseweazle/KryoFlux):
    *   Automatischer Header-Scan für .raw-Dateien.
    *   Erzwingt die korrekte PRONOM-ID (fmt/2015) und MIME-Typen für KryoFlux-Stream-Dateien.
    *   Unterdrückt fehlerhafte Bild-Metadaten-Interpretationen bei binären Rohdaten.
*   SHA-256 Fixity: Berechnet den finalen digitalen Fingerabdruck für jedes Objekt im Archivpaket.
*   Metadaten-Harmonisierung & Bereinigung:
    *   Überführt hunderte unterschiedliche Tool-Tags in ein kontrolliertes, einheitliches Schema.
    *   Entfernt über 100 redundante oder nicht archivwürdige Tags (Blockliste).
    *   Validierung der XML-Konformität (Entfernung ungültiger Steuerzeichen).
*   Integrierte Integritätsprüfung: Validiert die Funktionalität von PDFs, Bildern, Audio/Video-Streams und Office-Dokumenten (<validity>-Tag).

---

## Technische Voraussetzungen

Die folgenden Programme müssen installiert und die Pfade im Skript-Header konfiguriert sein:

1.  Python: Version 3.10 oder neuer empfohlen (Module: mutagen, PyPDF2, Pillow, yara-python, chardet).
2.  ExifTool: exiftool.exe.
3.  Siegfried: sf.exe (PRONOM-Identifikation).
4.  FFmpeg/FFprobe: ffprobe.exe für die Medienanalyse.
5.  Hachoir: hachoir-metadata.exe.
6.  YARA: rules.yar (Signaturdatei).

---

## Konfiguration im Skript

Passen Sie die Systempfade zu den Tools im Abschnitt KONFIGURATION an:

    YARA_RULES_FILE = r"C:\Pfad\zu\rules.yar"
    EXIFTOOL_PATH = r"C:\Program Files\ExifTool\exiftool.exe"
    SIEGFRIED_PATH = r"C:\Program Files\Siegfried\sf.exe"

### Erwartete Ordnerstruktur

Das Skript scannt den gesamten Inhalt des LZA-Ordners (Stufe 5) inklusive aller Unterordner (z.B. logfiles, 3_files):

    Documents/data/
    └── [AC-Nummer]/
        └── [Datenträger-ID]/
            └── 5_[ID]_LZA/                 <-- EINGABE-ORDNER (Base Dir)
                ├── logfiles/
                ├── 3_files/
                └── 5_[ID]_LZA.index        <-- ZIELDATEI (Master-Index)

---

## Ausführung

Das Skript wird über die Kommandozeile mit der AC-Nummer und der Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python master_index_generator.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Das Skript prüft die Projektpfade und die Verfügbarkeit der fünf Analyse-Werkzeuge.
2. Vollständiger Scan: Rekursive Erfassung aller Dateien innerhalb der LZA-Stufe 5.
3. Metadaten-Processing: Jede Datei durchläuft die Kette der Extraktoren. Besonders .raw-Dateien werden hierbei als KryoFlux-Archive fixiert.
4. Konsistenz-Checks: Harmonisierung der Tags und Prüfung der Dateivalidität.
5. XML-Generierung: Erstellung der .index-Datei mit sauber eingerückter Struktur.
6. Abschluss: Das Skript zeigt die Anzahl der verarbeiteten Dateien an und bietet an, den LZA-Ordner im Explorer zu öffnen.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT