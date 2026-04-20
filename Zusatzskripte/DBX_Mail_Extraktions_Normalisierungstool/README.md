# DBX Mail-Archiv Extraktions- & Normalisierungstool

Dieses Skript ist ein spezialisiertes Werkzeug zur forensischen Aufbereitung und Langzeitarchivierung von Outlook Express Mail-Archiven (.dbx). Es automatisiert den gesamten Prozess von der Konvertierung proprietärer Datenbanken bis hin zur Normalisierung aller enthaltenen E-Mails und deren Anhänge in archivsichere Formate.

Das Skript kombiniert die Funktionen von DbxConv mit einer leistungsstarken Normalisierungs-Engine für Office-Dokumente, Bilder, Audio- und Videodateien.

---

## Hauptfunktionen

*   **Mehrstufiger Extraktions-Workflow:**
    1.  **DBX zu MBOX:** Konvertiert Outlook Express Datenbanken (.dbx) in das standardisierte MBOX-Format via DbxConv.
    2.  **MBOX zu EML:** Extrahiert einzelne E-Mails als .eml-Dateien inklusive korrekter Datums- und Betreff-Benennung.
    3.  **Anhang-Extraktion:** Löst alle Dateianhänge aus den E-Mails heraus und speichert sie separat ab.
*   **Vollautomatische Normalisierung der Anhänge:**
    *   **Office-Dokumente:** Konvertierung nach ODF und PDF/A (via LibreOffice).
    *   **Rastergrafiken:** Konvertierung nach TIFF (via ImageMagick).
    *   **Vektorgrafiken:** Konvertierung nach PDF (via Inkscape oder Ghostscript bei EPS/AI).
    *   **Audio:** Erstellung von WAV- und MP3-Derivaten (via FFmpeg).
    *   **Video:** Normalisierung nach MP4/H.264 (via FFmpeg).
*   **Intelligente Benennung:** Erzeugt Dateinamen basierend auf dem Sendedatum und dem Betreff der E-Mail (YYYY-MM-DD-HH-MM-SS_Betreff.eml), um die chronologische Ordnung zu wahren.
*   **Bereinigung:** Entfernt temporäre Zwischendateien (wie ODF-Hilfsdateien) nach dem erfolgreichen PDF/A-Export.

---

## Technische Voraussetzungen

Für die volle Funktionalität müssen folgende Programme auf dem Windows-System installiert und im Pfad erreichbar sein:

1.  **Python 3.10+**
2.  **DbxConv.exe:** Muss im Skriptordner oder System-PATH liegen.
3.  **LibreOffice:** (C:/Program Files/LibreOffice/program/soffice.exe).
4.  **ImageMagick:** (magick.exe).
5.  **Inkscape:** (inkscape.exe).
6.  **Ghostscript:** (gswin64c.exe).
7.  **FFmpeg & FFprobe:** (ffmpeg.exe).

---

## Konfiguration

Das Skript ist in fünf logische Teile unterteilt. Anpassungen an den Systempfaden können direkt in **Teil 1** vorgenommen werden:

    dbxconv_path = "DbxConv.exe"
    libreoffice_path = "C:/Program Files/LibreOffice/program/soffice.exe"

Der zu scannende Hauptordner wird am Ende des Skripts in **Teil 5** definiert:

    main_input_dir = "C:/Pfad/zu/deinen/DBX_Daten"

---

## Ausführung

Starten Sie das Skript über die Konsole oder eine entsprechende Batch-Datei:

    python dbx_processor.py

### Ablauf der Verarbeitung

1.  Das Skript scannt den Zielordner rekursiv nach `.dbx`-Dateien.
2.  Jede gefundene Datenbank wird einzeln konvertiert.
3.  Im selben Verzeichnis wie die DBX-Datei entsteht ein neuer Ordner `[Name].dbx.eml`, der alle extrahierten Inhalte enthält.
4.  Anhänge werden innerhalb dieses Ordners abgelegt und sofort in ihre jeweiligen Archivformate (TIFF, PDF/A, MP4 etc.) umgewandelt.

---

## Lizenz & Urheberrecht

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT