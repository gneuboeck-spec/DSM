# Video-Konvertierungsskript (MP4-Normalisierung)

Dieses Skript automatisiert die Konvertierung und Normalisierung einer Vielzahl von Videoformaten in ein hochkompatibles Standardformat (MP4). Es ist als Modul innerhalb eines digitalen Archivierungsworkflows konzipiert, um sicherzustellen, dass proprietäre oder obsolete Videoformate in eine moderne, archivsichere Nutzungskopie überführt werden.

Das Skript nutzt FFmpeg für die technische Umsetzung und bietet eine robuste Stapelverarbeitung für Windows-Systeme.

---

## Hauptfunktionen

*   **Standardisierte Normalisierung:** Konvertiert Videos in das MP4-Format unter Verwendung des H.264-Video-Codecs und des AAC-Audio-Codecs.
*   **Web-Optimierung:** Aktiviert das "Faststart"-Flag, damit die erzeugten MP4-Dateien auch in Browsern oder Streaming-Umgebungen sofort startfähig sind.
*   **Intelligente Dubletten-Vermeidung:** Erkennt anhand der Dateinamen-Struktur (z.B. `film.avi.mp4`), ob für eine Quelldatei bereits ein Derivat erstellt wurde, und überspringt diese automatisch.
*   **Vollständige Rekursion:** Durchsucht den Quellordner und alle Unterverzeichnisse nach konvertierbaren Videodateien.
*   **Detaillierte Protokollierung:** Alle Konvertierungsvorgänge sowie eventuelle Fehlermeldungen von FFmpeg werden in einer Log-Datei (`..._video-conversion.log`) dokumentiert.
*   **Automatisierter Workflow:** Berechnet Pfade dynamisch basierend auf der übergebenen AC-Nummer und Datenträger-ID.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen folgende Programme installiert sein:

1.  **Python 3.10+**
2.  **FFmpeg:** Das Programm `ffmpeg.exe` muss installiert und im System-PATH registriert sein (oder der Pfad muss im Skript-Header manuell hinterlegt werden).

---

## Unterstützte Quellformate

Das Skript identifiziert und verarbeitet unter anderem folgende Endungen:
`.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.mpg`, `.mpeg`, `.m4v`, `.vob`, `.m2ts`, `.mts`, `.mxf`, `.ogm`, `.ts`

*Hinweis: Bereits vorhandene `.mp4`-Dateien werden ignoriert, um unnötige Qualitätsverluste durch Rekodierung zu vermeiden.*

---

## Erwartete Ordnerstruktur

Das Skript arbeitet innerhalb der Transfer-Stufe (Stufe 3) der Datenverarbeitung:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- QUELLORDNER
                    └── 3_[ID]_video-conversion.log <-- ZIEL DES LOGS

---

## Ausführung

Das Skript wird über die Kommandozeile gestartet und benötigt zwei Argumente: die AC-Nummer und die Datenträger-ID.

**Beispielhafter Aufruf in einer start.bat:**

    @echo off
    set AC_NUMBER=AC_556677
    set DISK_ID=DISK_01
    python video_converter.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1.  **Systemcheck:** Das Skript validiert die Ordnerstruktur und prüft, ob FFmpeg erreichbar ist.
2.  **Dateisuche:** Erstellung einer Liste aller Quelldateien, die den unterstützten Formaten entsprechen.
3.  **Normalisierung:** FFmpeg kodiert jedes Video nach MP4 um. Die Zieldatei wird nach dem Muster `Originalname.Originalendung.mp4` benannt (z.B. `aufnahme.mov.mp4`).
4.  **Logging:** Jeder Schritt wird mit Zeitstempel im Log vermerkt. Bei Fehlern wird die Original-Fehlermeldung von FFmpeg mitprotokolliert.
5.  **Abschluss:** Das Skript meldet die Anzahl der erfolgreichen Konvertierungen und bietet an, den Ordner im Explorer zu öffnen.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT