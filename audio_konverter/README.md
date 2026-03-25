# Intelligenter Audio-Konverter (MP3 & WAV)

Dieses Verzeichnis enthält ein Skript zur automatisierten Batch-Konvertierung einer Vielzahl von Audioformaten. Das Hauptziel ist die Erstellung eines standardisierten Archivs, das für jede Quelldatei sowohl eine hochkompatible, komprimierte Version (MP3) als auch eine verlustfreie Archivkopie (WAV) enthält.

Das Skript ist für die Integration in eine vordefinierte Ordnerstruktur konzipiert und wird über Kommandozeilenargumente gesteuert, typischerweise durch eine Start-Datei wie `start.bat`.

## Zweck des Skripts

Das Skript durchsucht einen spezifischen `Files`-Ordner innerhalb einer Projektstruktur und wendet eine intelligente "Digital Twin"-Logik an. Es stellt sicher, dass für jede Originaldatei ein Paar aus MP3- und WAV-Version existiert.

1.  **Erstellung von Derivaten:**
    *   Für jedes Audioformat, das nicht bereits MP3 oder WAV ist (z.B. `.flac`, `.aiff`, `.m4a`), werden **zwei** neue Dateien erstellt:
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
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Es werden nur Standardmodule verwendet.

### 2. FFmpeg
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript benötigt `ffmpeg` und `ffprobe` für die Audio-Analyse und -Konvertierung.
*   **Installation:** FFmpeg muss so installiert sein, dass die Befehle `ffmpeg.exe` und `ffprobe.exe` systemweit verfügbar sind (d.h. zum System-`PATH` hinzugefügt wurden). Das Skript prüft beim Start automatisch, ob die Programme gefunden werden können.

---

## Konfiguration und Ordnerstruktur

Das Skript erfordert **keine manuelle Bearbeitung** der Pfade im Quellcode mehr. Stattdessen arbeitet es mit einer dynamischen Ordnerstruktur, die durch zwei Parameter (`AC-Nummer` und `Datenträger-ID`) definiert wird.

### Erwartete Ordnerstruktur

Das Skript erwartet die folgende Verzeichnisstruktur in Ihrem Benutzer-Dokumentenordner:
Documents
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 3_[Datenträger-ID]_for-transfer
                ├── Files <-- HIER MÜSSEN DIE AUDIODATEIEN LIEGEN
                └── (Hier wird die Log-Datei erstellt)
*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts (z.B. `AC_0001`).
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers (z.B. `CD_01`).

Das Skript leitet aus diesen beiden Werten automatisch alle benötigten Pfade ab:
*   **Eingabe-Ordner:** `.../Files`
*   **Log-Datei:** `.../3_[Datenträger-ID]_audio_conversion.log`

---

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine Batch-Datei unter Windows) vorgesehen, die die `AC-Nummer` und die `Datenträger-ID` als Argumente übergibt.

**Direkter Aufruf wird nicht empfohlen!** Nutzen Sie stattdessen eine Start-Datei (`start.bat` o.ä.), die den Aufruf für Sie übernimmt.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python script.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  Das Skript validiert die übergebenen Argumente und prüft, ob die erwartete Ordnerstruktur und die FFmpeg-Programme existieren.
2.  Es durchsucht den `Files`-Ordner nach unterstützten Audiodateien.
3.  Für jede gefundene Datei wird die Konvertierung gestartet und ein **Live-Fortschrittsbalken** in der Konsole angezeigt.
4.  Alle Aktionen, Erfolge und Fehler werden in der Log-Datei `3_[Datenträger-ID]_audio_conversion.log` protokolliert. Die alte Log-Datei wird bei jedem neuen Start gelöscht.
5.  Nach Abschluss aller Konvertierungen fragt das Skript, ob der Zielordner (`for-transfer`) im Datei-Explorer geöffnet werden soll.