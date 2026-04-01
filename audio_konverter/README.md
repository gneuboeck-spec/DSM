# Intelligenter Audio-Konverter (MP3 & WAV)

Dieses Verzeichnis enthält ein Skript zur automatisierten Batch-Konvertierung einer Vielzahl von Audioformaten. Das Hauptziel ist die Erstellung eines standardisierten Archivs, das für jede Quelldatei sowohl eine hochkompatible, komprimierte Version (MP3) als auch eine verlustfreie Archivkopie (WAV) enthält.

Das Skript ist für die Integration in eine vordefinierte Ordnerstruktur konzipiert und wird über Kommandozeilenargumente gesteuert, typischerweise durch eine Start-Datei wie `start.bat`.

---

## Zweck des Skripts

Das Skript durchsucht einen spezifischen `Files`-Ordner innerhalb einer Projektstruktur und wendet eine intelligente "Digital Twin"-Logik an. Es stellt sicher, dass für jede Originaldatei ein Paar aus MP3- und WAV-Version existiert.

1.  **Erstellung von Derivaten:**
    *   Für jedes Audioformat, das nicht bereits MP3 oder WAV ist (z. B. `.flac`, `.aiff`, `.m4a`), werden **zwei** neue Dateien erstellt:
        *   Eine **MP3-Datei** in hoher Qualität (VBR `q:a 2`) für maximale Kompatibilität.
        *   Eine **WAV-Datei** (unkomprimiertes PCM 16-bit) für verlustfreie Archivqualität.
    *   Die Zieldateien folgen der Namenskonvention `Originalname.originalendung.mp3` und `Originalname.originalendung.wav`, um die Herkunft lückenlos zu dokumentieren.

2.  **Intelligente Ergänzung:**
    *   Wenn die Quelldatei bereits eine `.mp3` ist, wird nur die fehlende `.wav`-Version erstellt.
    *   Wenn die Quelldatei bereits eine `.wav` ist, wird nur die fehlende `.mp3`-Version erstellt.

3.  **Überschreiben:** Bei wiederholter Ausführung werden bereits existierende Zieldateien automatisch überschrieben (`-y` Flag), um sicherzustellen, dass sie immer auf dem neuesten Stand der Konvertierungseinstellungen sind.

---

## Technische Voraussetzungen

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich (nur Standardmodule).

### 2. FFmpeg
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript benötigt `ffmpeg` und `ffprobe` für die Audio-Analyse und -Konvertierung.
*   **Installation:** FFmpeg muss so installiert sein, dass die Befehle `ffmpeg.exe` und `ffprobe.exe` systemweit verfügbar sind (Pfad-Variable). Das Skript prüft beim Start automatisch die Verfügbarkeit.

---

## Konfiguration und Ordnerstruktur

Das Skript erfordert **keine manuelle Bearbeitung** der Pfade im Quellcode. Es arbeitet dynamisch basierend auf der `AC-Nummer` und der `Datenträger-ID`.

### Erwartete Ordnerstruktur

Das Skript erwartet die folgende Verzeichnisstruktur im Benutzer-Dokumentenordner:

```text
Documents/
└── Datentraeger_sichern/
    └── [AC-Nummer]/
        └── [Datenträger-ID]/
            └── 3_[Datenträger-ID]_for-transfer/
                ├── Files/                      <-- HIER MÜSSEN DIE AUDIODATEIEN LIEGEN
                └── 3_[Datenträger-ID]_audio_conversion.log
```

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts (z. B. `AC_0001`).
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers (z. B. `CD_01`).

---

## Ausführung

Nutzen Sie eine Start-Datei (`start.bat`), um das Skript mit den korrekten Argumenten aufzurufen.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python audio_converter_skript.py %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft Argumente, Ordnerstruktur und die FFmpeg-Verfügbarkeit.
2.  **Suche:** Der `Files`-Ordner wird nach unterstützten Audiodateien durchsucht.
3.  **Konvertierung:** Für jede Datei wird die Konvertierung gestartet (inkl. Live-Fortschrittsbalken).
4.  **Protokollierung:** Alle Aktionen werden in der Log-Datei `3_[Datenträger-ID]_audio_conversion.log` gespeichert (alte Logs werden überschrieben).
5.  **Abschluss:** Das Skript bietet an, den Zielordner im Datei-Explorer zu öffnen.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT