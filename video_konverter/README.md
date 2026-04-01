# Video-Konverter nach MP4 (FFmpeg)

Dieses Skript dient zur automatisierten Batch-Konvertierung einer Vielzahl von Videoformaten in das hochkompatible MP4-Containerformat. Es wurde entwickelt, um eine heterogene Sammlung von Videodateien für eine bessere Wiedergabekompatibilität und Langzeitarchivierung zu normalisieren.

Das Skript ist als Teil eines standardisierten Archivierungsworkflows konzipiert. Es wird über eine Start-Datei (`start.bat`) gesteuert, die dynamische Pfade basierend auf einer Projekt- und Datenträger-ID generiert.

---

## Kernfunktionalität

Das Skript durchsucht einen Zielordner rekursiv und wendet die folgenden Konvertierungsregeln an:

*   **Zielformat:** Alle unterstützten Quellvideos werden in einen **MP4-Container** konvertiert.
*   **Codecs:**
    *   **Video:** H.264 (`libx264`), ein weit verbreiteter und qualitativ hochwertiger Codec.
    *   **Audio:** AAC (`aac`) mit einer Bitrate von 192k für gute Audioqualität.
*   **Namenskonvention:** Die Zieldatei wird nach dem Muster `Originalname.originalendung.mp4` benannt. Dies stellt sicher, dass die Herkunft der Datei immer nachvollziehbar bleibt (z. B. wird `urlaub_2005.mov` zu `urlaub_2005.mov.mp4`).
*   **Intelligente Dateisuche:** Das Skript identifiziert und überspringt automatisch Dateien, die bereits nach diesem Muster konvertiert wurden, um doppelte Arbeit bei wiederholter Ausführung zu vermeiden.
*   **Protokollierung:** Alle durchgeführten Aktionen, Erfolge und detaillierte FFmpeg-Fehlermeldungen werden in einer Log-Datei festgehalten.

---

## Technische Voraussetzungen

1.  **Python:** Version 3.6 oder neuer.
2.  **FFmpeg:** Eine aktuelle Version von FFmpeg muss installiert sein. Die ausführbare Datei (`ffmpeg.exe` unter Windows) muss systemweit verfügbar sein (Eintrag im System-`PATH`).

---

## Konfiguration

Die Konfiguration erfolgt direkt am Anfang des Skripts:

```python
# Name des FFmpeg-Programms. Wenn FFmpeg im System-PATH ist, reicht dies.
FFMPEG_PATH = "ffmpeg.exe"

# Liste der zu verarbeitenden Quellformate (Beispiel).
SOURCE_VIDEO_EXTENSIONS = {".avi", ".mov", ".mkv", ".wmv", ".mpg", ".mp4", ".m4v"}
```

*   **`FFMPEG_PATH`**: Muss nur angepasst werden, wenn FFmpeg nicht im System-`PATH` hinterlegt ist.
*   **`SOURCE_VIDEO_EXTENSIONS`**: Definiert, welche Dateiendungen als Quellvideos für die Konvertierung berücksichtigt werden.

---

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:

```text
Documents/
└── Datentraeger_sichern/
    └── [AC-Nummer]/
        └── [Datenträger-ID]/
            └── 3_[Datenträger-ID]_for-transfer/
                ├── Files/                      <-- IN DIESEM ORDNER WIRD GESUCHT
                └── 3_[Datenträger-ID]_video_conversion.log
```

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

---

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z. B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python video_conversion_skript.py %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die Argumente, die Ordnerstruktur und die Verfügbarkeit von FFmpeg.
2.  **Suche:** Das `Files`-Verzeichnis wird rekursiv nach unterstützten Videodateien durchsucht, die noch nicht konvertiert wurden.
3.  **Konvertierung:** Jede gefundene Datei wird mit FFmpeg in das MP4-Format konvertiert.
4.  **Protokollierung:** Alle Aktionen, Erfolge und Fehler werden detailliert in die Log-Datei geschrieben.
5.  **Zusammenfassung:** Am Ende wird eine Übersicht über die Anzahl der erfolgreich konvertierten Dateien ausgegeben.
6.  **Abschluss:** Das Skript bietet an, den Zielordner im Datei-Explorer zu öffnen.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT