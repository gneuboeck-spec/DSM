# Bild-Konvertierungsskript (Normalisierung)

Dieses Skript automatisiert die Normalisierung von Bild- und Grafikdateien innerhalb eines digitalen Archivierungsworkflows. Es dient dazu, eine Vielzahl von proprietären oder verlustbehafteten Grafikformaten in standardisierte, archivtaugliche Formate zu überführen: Rastergrafiken werden nach TIFF (verlustfrei) und Vektorgrafiken nach PDF (ISO-Standard) konvertiert.

Das Skript kombiniert drei leistungsstarke Open-Source-Werkzeuge (ImageMagick, Inkscape und Ghostscript), um für jeden Dateityp die bestmögliche Konvertierungsqualität zu gewährleisten.

---

## Hauptfunktionen

*   **Duale Normalisierungs-Strategie:**
    *   Rastergrafiken (z.B. JPG, PNG, BMP) werden in das verlustfreie TIFF-Format (.tiff) konvertiert. (Werkzeug: ImageMagick)
    *   Vektorgrafiken (z.B. SVG, WMF) werden in das PDF-Format (.pdf) überführt. (Werkzeug: Inkscape)
    *   Spezialformate (EPS, AI) werden direkt über Ghostscript in PDF-Dateien gewandelt.
*   **Intelligente Dubletten-Vermeidung:** Erkennt anhand der Namensstruktur (z.B. datei.jpg.tiff), ob für eine Quelldatei bereits ein Derivat erstellt wurde, und überspringt diese automatisch.
*   **Prozess-Sicherheit:** Vor jedem Lauf wird die Verfügbarkeit aller benötigten externen Programme sowie die korrekte Ordnerstruktur geprüft.
*   **Detaillierte Protokollierung:** Erzeugt ein umfassendes Log-File (..._image-conversion.log), das jede erfolgreiche Konvertierung, jeden Fehler und die verwendeten Befehle dokumentiert.
*   **Fortschrittsanzeige:** Zeigt während der Laufzeit den aktuellen Fortschritt in Prozent sowie den Pfad der gerade verarbeiteten Datei an.

---

## Technische Voraussetzungen

Damit dieses Skript funktioniert, müssen folgende Programme auf dem System installiert sein:

1.  Python 3.10+
2.  ImageMagick: magick.exe muss im System-PATH erreichbar sein.
3.  Inkscape: Der Pfad zur inkscape.exe muss im Skript hinterlegt sein (Standard: C:\Program Files\Inkscape\bin\inkscape.exe).
4.  Ghostscript: gswin64c.exe muss im System-PATH erreichbar sein.

---

## Unterstützte Quellformate

Das Skript erkennt und verarbeitet folgende Endungen:
*   Rasterformate: .jpg, .jpeg, .png, .bmp, .webp, .heic, .tga, .gif, .jfif
*   Vektorgformate: .svg, .wmf
*   PostScript-basierte Formate: .eps, .ai

---

## Erwartete Ordnerstruktur

Das Skript operiert innerhalb der Transfer-Stufe (Stufe 3) des Workflows:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- QUELLORDNER
                    └── 3_[ID]_image-conversion.log <-- ZIEL DES LOGS

---

## Ausführung

Das Skript wird über die Kommandozeile unter Angabe der AC-Nummer und der Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_998877
    set DISK_ID=FOTO_DISK_01
    python image_converter.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Prüfung der Projektpfade und der Verfügbarkeit von ImageMagick, Inkscape und Ghostscript.
2. Indexierung: Rekursiver Scan des files-Ordners nach allen unterstützten Grafikformaten.
3. Konvertierung:
   - Quelldateien werden identifiziert und dem entsprechenden Werkzeug zugewiesen.
   - Zieldateien werden nach dem Schema Originalname.Originalendung.Zielendung benannt.
   - Existierende alte Zieldateien werden vor der Konvertierung sicher entfernt, um Konflikte zu vermeiden.
4. Finalisierung: Erstellung einer Zusammenfassung (Erfolge vs. Fehler) und Option zum Öffnen des Zielordners im Explorer.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT