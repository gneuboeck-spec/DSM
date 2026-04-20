# Master-Konvertierungsskript (All-in-One)

Dieses Skript ist das zentrale Werkzeug zur Konvertierung und Normalisierung von Dateien für die Langzeitarchivierung. Es vereint die Funktionalitäten spezialisierter Einzel-Skripte für Audio, Bild, Text/Office und Video in einem einzigen, umfassenden Workflow. Das Ziel ist es, für jede unterstützte Quelldatei standardisierte, archivsichere Derivate zu erstellen.

Das Skript ist als integraler Bestandteil eines automatisierten Archivierungsworkflows konzipiert und wird über eine Start-Datei (start.bat) mit dynamischen Pfaden gesteuert.

---

## Kernfunktionalität: Der "Digital Twin"-Ansatz

Das Skript durchsucht einen Quellordner und wendet je nach Dateityp eine spezifische Konvertierungslogik an. Alle erstellten Dateien folgen der Namenskonvention "Originalname.originalendung.zielendung" (z.B. dokument.doc.pdf), um die Herkunft eindeutig zu dokumentieren.

*   Audio-Dateien:
    *   Erzeugt aus Quellformaten (.wav, .flac, .mp3, .aiff, etc.) jeweils ein hochqualitatives .wav-Derivat (PCM 16-Bit) und ein kompatibles .mp3-Derivat. (Werkzeug: FFmpeg)
*   Bild-Dateien:
    *   Rastergrafiken (.jpg, .png, .bmp, etc.) werden in verlustfreie .tiff-Dateien konvertiert. (Werkzeug: ImageMagick)
    *   Vektorgrafiken und Ghostscript-Formate (.svg, .wmf, .eps, .ai) werden in archivsichere .pdf-Dateien überführt. (Werkzeuge: Inkscape, Ghostscript)
*   Office-Dokumente:
    *   Dokumente (.doc, .xls, .ppt, etc.) werden in das entsprechende OpenDocument-Format (.odt, .ods, .odp) und zusätzlich in ein PDF/A-Format konvertiert.
    *   Besonderheit: Enthält einen Fix für das Windows-Pfadlängenlimit (260 Zeichen) durch Nutzung eines temporären Arbeitsverzeichnisses. (Werkzeug: LibreOffice)
*   Video-Dateien:
    *   Videocontainer (.mov, .avi, .mkv, .mpg, etc.) werden in hochkompatible .mp4-Dateien (H.264/AAC) normalisiert. (Werkzeug: FFmpeg)

---

## Technische Voraussetzungen

Damit dieses Skript funktioniert, müssen die folgenden Programme installiert sein:

1.  Python: Version 3.10 oder neuer empfohlen.
2.  FFmpeg: ffmpeg.exe und ffprobe.exe müssen im System-PATH verfügbar sein.
3.  ImageMagick: magick.exe muss im System-PATH verfügbar sein.
4.  Ghostscript: gswin64c.exe muss im System-PATH verfügbar sein.
5.  Inkscape: Muss unter C:\Program Files\Inkscape\bin\inkscape.exe installiert sein.
6.  LibreOffice: Muss unter C:/Program Files/LibreOffice/program/soffice.exe installiert sein.

---

## Konfiguration im Skript

Die Pfade zu den ausführbaren Dateien von Inkscape und LibreOffice sind fest im Skript-Header hinterlegt und müssen bei Abweichungen angepasst werden:

    INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe"
    LIBREOFFICE_PATH = "C:/Program Files/LibreOffice/program/soffice.exe"

### Erwartete Ordnerstruktur

Das Skript arbeitet innerhalb der "data"-Struktur im Documents-Ordner:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- QUELLORDNER
                    └── 3_[Datenträger-ID]_for-transfer_all-conversions.log

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Kommandozeilenargumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python master_converter.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Das Skript prüft die Existenz der Quellpfade und die Erreichbarkeit aller externen Tools.
2. Indexierung: Alle relevanten Dateien werden identifiziert. Bereits existierende Derivate werden erkannt und übersprungen (Vermeidung von Doppelkonvertierung).
3. Verarbeitung: Die Dateien werden nacheinander je nach Kategorie (Audio, Bild, Text, Video) verarbeitet.
4. Fehlerbehandlung: Bei Fehlern (z.B. defekte Quelldatei) wird der Fehler im Log dokumentiert und das Skript fährt mit der nächsten Datei fort.
5. Protokollierung: Alle Vorgänge werden mit Zeitstempel in der Log-Datei "3_[ID]_for-transfer_all-conversions.log" gespeichert.
6. Abschluss: Das Skript bietet an, den "for-transfer"-Ordner direkt im Explorer zu öffnen.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT