# Audio-Konvertierungsskript (Normalisierung)

Dieses Skript automatisiert die Konvertierung und Normalisierung von Audio-Dateien innerhalb eines digitalen Archivierungsworkflows. Es stellt sicher, dass für jedes Quell-Audioformat sowohl eine verlustfreie Archivkopie (WAV) als auch eine hochkompatible Nutzungskopie (MP3) vorhanden ist.

Das Skript nutzt die Leistungsfähigkeit von FFmpeg und ist speziell für die Stapelverarbeitung in einer vordefinierten Ordnerstruktur unter Windows optimiert.

---

## Hauptfunktionen

*   **Duale Normalisierungs-Strategie:** 
    *   Erzeugt aus jedem unterstützten Format (z.B. AIFF, FLAC, WMA) ein "Zwillingspaar": eine `.wav`-Datei (PCM 16-Bit) und eine `.mp3`-Datei (LAME, hohe Qualität).
    *   Erkennt Originale: Liegt bereits ein MP3 vor, wird nur das WAV ergänzt. Liegt ein WAV vor, wird nur das MP3 ergänzt.
*   **Intelligente Fortschrittsanzeige:** Zeigt während der Konvertierung einen grafischen Fortschrittsbalken (`[####    ] 50%`) direkt in der Konsole an.
*   **Vermeidung von Redundanz:** Das Skript erkennt bereits konvertierte Dateien anhand der Namensstruktur (z.B. `datei.flac.wav`) und überspringt diese automatisch, um doppelte Arbeit zu verhindern.
*   **Detaillierte Protokollierung:** Alle Aktionen, Erfolge und Fehler werden zeitgenau in einer Log-Datei im Projektordner festgehalten.
*   **Dynamische Pfadverwaltung:** Berechnet alle Verzeichnisse automatisch basierend auf der AC-Nummer und der Datenträger-ID.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen folgende Programme installiert sein:

1.  **Python 3.10+**
2.  **FFmpeg:** Die Programme `ffmpeg.exe` und `ffprobe.exe` müssen installiert und im System-PATH registriert sein (oder der Pfad muss im Skript-Header manuell angepasst werden).

---

## Unterstützte Formate (Quelle)

Das Skript verarbeitet Dateien mit folgenden Endungen:
`.aiff`, `.flac`, `.ogg`, `.wav`, `.m4a`, `.wma`, `.aac`, `.mp3`

---

## Erwartete Ordnerstruktur

Das Skript arbeitet innerhalb der Transfer-Stufe (Stufe 3) des Archivierungsworkflows:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- QUELLORDNER (wird rekursiv durchsucht)
                    └── 3_[ID]_audio-conversion.log <-- ZIEL DES LOGS

---

## Ausführung

Das Skript wird über die Kommandozeile unter Angabe der AC-Nummer und der Datenträger-ID gestartet.

**Beispielhafter Aufruf in einer start.bat:**

    @echo off
    set AC_NUMBER=AC_12345
    set DISK_ID=ID_001
    python audio_converter.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft, ob die Ordnerstruktur existiert und FFmpeg/FFprobe auf dem System verfügbar sind.
2.  **Dateisuche:** Der Ordner `files/` wird rekursiv nach unterstützten Audioformaten durchsucht. Bereits konvertierte Derivate werden ignoriert.
3.  **Metadaten-Analyse:** FFprobe ermittelt die Dauer der Quelldatei für die Fortschrittsberechnung.
4.  **Konvertierung:** FFmpeg führt die eigentliche Umwandlung durch. Die Zieldateien werden nach dem Muster `Originalname.Originalendung.Zielendung` benannt (z.B. `lied.wma.wav`).
5.  **Abschluss:** Nach der Verarbeitung aller Dateien bietet das Skript an, den Zielordner direkt im Explorer zu öffnen.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT