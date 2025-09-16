# Video-Konverter nach MP4

Dieses Verzeichnis enthält Skripte zur Batch-Konvertierung einer Vielzahl von Videoformaten in das hochkompatible MP4-Format.

## Zweck des Skripts

Das Skript durchsucht einen Quellordner und alle seine Unterordner nach unterstützten Videodateien. Jede gefundene Datei (außer bereits existierende `.mp4`-Dateien) wird in eine **hochkompatible und web-optimierte MP4-Datei** konvertiert.

**Hauptmerkmale:**

1.  **Standardisierung:** Wandelt diverse Formate wie `.mov`, `.avi`, `.mkv` etc. in den universellen MP4-Standard um.
2.  **Qualität und Kompatibilität:** Verwendet den H.264-Videocodec und den AAC-Audiocodec, um eine breite Abspielbarkeit auf fast allen Geräten und im Web zu gewährleisten.
3.  **Web-Optimierung:** Die erstellten MP4-Dateien sind für Streaming optimiert (`+faststart`), was bedeutet, dass sie abgespielt werden können, bevor der Download vollständig abgeschlossen ist.
4.  **Überschreiben:** Bei wiederholter Ausführung des Skripts werden bereits existierende Zieldateien automatisch überschrieben, um sicherzustellen, dass sie immer auf dem neuesten Stand sind.
5.  **Namenskonvention:** Die Zieldateien folgen dem Muster `Originalname.originalendung.mp4`, um die Herkunft der Datei nachvollziehbar zu machen.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und korrekt konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich.

### 2. FFmpeg
*   **Version:** Eine aktuelle, stabile Version (z.B. 4.x oder neuer) wird dringend empfohlen.
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript ruft FFmpeg im Hintergrund auf, um die gesamte Videoverarbeitung durchzuführen.
*   **Installation:** FFmpeg muss so installiert sein, dass der Befehl `ffmpeg` systemweit verfügbar ist (im System-`PATH`).

#### Installationsanleitung für FFmpeg:

*   **macOS (empfohlen):**
    *   Öffnen Sie das Terminal und installieren Sie FFmpeg mit Homebrew:
        ```bash
        brew install ffmpeg
        ```

*   **Windows 11:**
    1.  Laden Sie einen "release build" von [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) herunter.
    2.  Entpacken Sie die Datei.
    3.  Kopieren Sie den Inhalt des `bin`-Ordners (insb. `ffmpeg.exe` und `ffprobe.exe`) in ein einfaches Verzeichnis, z.B. `C:\ffmpeg`.
    4.  Fügen Sie dieses Verzeichnis (`C:\ffmpeg`) zur **Systemumgebungsvariable `PATH`** hinzu.

---

## Konfiguration im Skript

Vor der Ausführung muss die Variable `input_folder` am Anfang des Skripts für das jeweilige Betriebssystem angepasst werden.

*   **`input_folder`**: Der absolute Pfad zum Hauptordner, der die zu konvertierenden Videodateien enthält.

**Beispiel für macOS:**
```python
input_folder = "/Users/IhrBenutzername/Desktop/Videodateien_konvertieren"
```

**Beispiel für Windows:**
```python
input_folder = "C:/Users/IhrBenutzername/Desktop/Videodateien_konvertieren"
```

---

## Ausführung

Die Skripte für die verschiedenen Betriebssysteme befinden sich in den jeweiligen Unterordnern (`mac/`, `win/`).

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Stellen Sie sicher, dass alle oben genannten Voraussetzungen erfüllt und die Pfade im Skript korrekt konfiguriert sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**
```bash
python3 /pfad/zum/skript/mac/convert_video.py
```

Das Skript gibt den Fortschritt live auf der Konsole aus und erstellt eine detaillierte Log-Datei (`video_konvertierung.log`) im `input_folder`.