# Intelligenter Audio-Konverter (MP3 & WAV)

Dieses Verzeichnis enthält Skripte zur Batch-Konvertierung einer Vielzahl von Audioformaten. Das Hauptziel ist die Erstellung eines standardisierten Archivs, das für jede Quelldatei sowohl eine hochkompatible, komprimierte Version als auch eine verlustfreie Archivkopie enthält.

## Zweck des Skripts

Das Skript durchsucht einen Quellordner und alle seine Unterordner nach unterstützten Audiodateien. Es wendet dann eine intelligente "Digital Twin"-Logik an, um sicherzustellen, dass für jede Originaldatei ein Paar aus MP3- und WAV-Version existiert:

1.  **Erstellung von Derivaten:**
    *   Für jedes Audioformat (z.B. `.flac`, `.aiff`, `.m4a`) werden **zwei** neue Dateien erstellt:
        *   Eine **MP3-Datei** in hoher Qualität (VBR) für maximale Kompatibilität und Portabilität.
        *   Eine **WAV-Datei** (unkomprimiertes PCM 16-bit) für verlustfreie Archivqualität.
    *   Die Zieldateien folgen der Namenskonvention `Originalname.originalendung.mp3` und `Originalname.originalendung.wav`, um die Herkunft lückenlos zu dokumentieren.

2.  **Intelligente Ergänzung:**
    *   Wenn die Quelldatei bereits eine `.mp3` ist, wird nur die fehlende `.wav`-Version erstellt.
    *   Wenn die Quelldatei bereits eine `.wav` ist, wird nur die fehlende `.mp3`-Version erstellt.

3.  **Überschreiben:** Bei wiederholter Ausführung des Skripts werden bereits existierende Zieldateien automatisch überschrieben, um sicherzustellen, dass sie immer auf dem neuesten Stand sind.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Es werden nur Standardmodule (`os`, `subprocess`, etc.) verwendet.

### 2. FFmpeg
*   **Version:** Eine aktuelle, stabile Version (z.B. 4.x oder neuer) wird dringend empfohlen.
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript ruft FFmpeg im Hintergrund auf für:
    *   **Analyse (`ffprobe`):** Ermittlung der exakten Dauer einer Audiodatei für die Fortschrittsanzeige.
    *   **Konvertierung (`ffmpeg`):** Umwandlung der Quelldateien in MP3 und WAV.
*   **Installation:** FFmpeg muss so installiert sein, dass die Befehle `ffmpeg` und `ffprobe` systemweit verfügbar sind (im System-`PATH`).

---

## Konfiguration im Skript

Vor der Ausführung müssen die Pfade am Anfang des Skripts für das jeweilige Betriebssystem angepasst werden.

*   **`input_folder`**: Der absolute Pfad zum Hauptordner, der die zu konvertierenden Audiodateien enthält.
*   **`log_file_path`**: (Optional) Der Pfad, an dem die `audio_conversion_log.txt`-Datei erstellt werden soll.
*   **`ffmpeg_path` / `ffprobe_path` (Für Windows):**
    *   Wenn FFmpeg zum System-`PATH` hinzugefügt wurde, reichen die Standardnamen (`ffmpeg.exe`, `ffprobe.exe`).
    *   Andernfalls muss hier der vollständige, absolute Pfad zur jeweiligen `.exe`-Datei eingetragen werden.

**Beispiel für macOS:**
```python
input_folder = "/Users/IhrBenutzername/Desktop/Audiodateien_konvertieren"
```

**Beispiel für Windows:**
```python
input_folder = "C:/Users/IhrBenutzername/Desktop/Audiodateien_konvertieren"
```

---

## Ausführung

Die Skripte für die verschiedenen Betriebssysteme befinden sich in den jeweiligen Unterordnern (`mac/`, `win/`).

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/Git Bash (Windows).
2.  Stellen Sie sicher, dass alle oben genannten Voraussetzungen erfüllt und die Pfade im Skript korrekt konfiguriert sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**
```bash
python3 /pfad/zum/skript/mac/convert_audio.py
```

Das Skript gibt den Fortschritt jeder Konvertierung live in der Konsole aus und erstellt eine detaillierte Log-Datei, die alle Aktionen, Erfolge und eventuelle Fehler von FFmpeg protokolliert.