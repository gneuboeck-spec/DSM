# Universeller Grafik-Konverter (Raster & Vektor)

Dieses Verzeichnis enthält Skripte zur Batch-Konvertierung einer Vielzahl von Raster- und Vektorgrafikformaten in standardisierte, archivsichere Zielformate.

## Zweck des Skripts

Das Skript durchsucht einen Quellordner und alle seine Unterordner nach unterstützten Grafikdateien. Es wendet dann intelligent das jeweils beste Konvertierungswerkzeug an, um archivwürdige Derivate zu erstellen:

1.  **Rastergrafiken** (`.jpg`, `.png`, `.heic`, etc.) werden in das verlustfreie **TIFF-Format (`.tiff`)** konvertiert.
2.  **Vektorgrafiken** (`.svg`, `.eps`, `.ai`, etc.) werden in ein visuell stabiles **PDF-Format** umgewandelt.

Alle erstellten Dateien folgen der Namenskonvention `Originalname.originalendung.zielendung`, um die Herkunft nachvollziehbar zu machen. Bei wiederholter Ausführung des Skripts werden bereits existierende Zieldateien **überschrieben**, um sicherzustellen, dass sie immer auf dem neuesten Stand sind.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen mehrere externe Programme installiert und korrekt konfiguriert sein.

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Es werden nur Standardmodule (`os`, `subprocess`, etc.) verwendet.

### 2. ImageMagick (für Rastergrafiken)
*   **Zweck:** Konvertiert Formate wie JPEG, PNG, HEIC und GIF nach TIFF.
*   **Installation:** Muss installiert sein, sodass der Befehl `magick` (`magick.exe` unter Windows) systemweit verfügbar ist (im `PATH`).
    *   **macOS:** `brew install imagemagick`
    *   **Windows:** Installer von [imagemagick.org](https://imagemagick.org/script/download.php) herunterladen und bei der Installation die Option "Add application directory to your system path" aktivieren.

### 3. Inkscape (für SVG und andere Vektorformate)
*   **Zweck:** Konvertiert Vektorformate wie SVG oder WMF in PDF.
*   **Installation:** Muss installiert sein, sodass der Befehl `inkscape` (`inkscape.exe`) systemweit verfügbar ist.
    *   **macOS:** `brew install --cask inkscape`
    *   **Windows:** Installer von [inkscape.org](https://inkscape.org/release/inkscape-1.3.2/windows/64-bit/) herunterladen und bei der Installation die Option "Add Inkscape to system PATH" aktivieren.

### 4. Ghostscript (Wichtiger Helfer für EPS, PDF, AI)
*   **Zweck:** Wird von Inkscape und ImageMagick im Hintergrund benötigt, um PostScript-basierte Dateien (`.eps`, `.ai`, `.pdf`) korrekt zu lesen.
*   **Installation:** Muss installiert und systemweit verfügbar sein.
    *   **macOS:** `brew install ghostscript`
    *   **Windows:** Installer von [ghostscript.com](https://www.ghostscript.com/releases/gsdnld.html) herunterladen. Es wird dringend empfohlen, den Installationspfad (insb. das `bin`-Verzeichnis) zur Systemumgebungsvariable `PATH` hinzuzufügen.

---

## Konfiguration im Skript

Vor der Ausführung müssen die Pfade am Anfang des Skripts für das jeweilige Betriebssystem angepasst werden.

*   **`input_folder`**: Der absolute Pfad zum Hauptordner, der die zu konvertierenden Grafikdateien enthält.
*   **Pfade zu den Tools** (`imagemagick_path`, `inkscape_path`, `ghostscript_path`):
    *   Wenn die Programme wie oben beschrieben zum System-`PATH` hinzugefügt wurden, reichen die Standardnamen (`magick.exe`, `inkscape.exe`, `gswin64c.exe`).
    *   Andernfalls muss hier der vollständige, absolute Pfad zur jeweiligen `.exe`-Datei (Windows) oder zur Binärdatei (macOS) eingetragen werden.

**Beispiel für macOS:**
```python
input_folder = "/Users/IhrBenutzername/Desktop/Bildformate_konvertieren"
imagemagick_path = "magick"
inkscape_path = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
ghostscript_path = "gs"
```

**Beispiel für Windows:**```python
input_folder = "C:/Users/IhrBenutzername/Desktop/Bildformate_konvertieren"
imagemagick_path = "magick.exe"
inkscape_path = "inkscape.exe"
ghostscript_path = "gswin64c.exe"
```

---

## Ausführung

Die Skripte für die verschiedenen Betriebssysteme befinden sich in den jeweiligen Unterordnern (`mac/`, `win/`).

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Stellen Sie sicher, dass alle oben genannten Voraussetzungen erfüllt und die Pfade im Skript korrekt konfiguriert sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel für macOS:**
```bash
python3 /pfad/zum/skript/mac/convert_graphics.py
```

**Beispiel für Windows:**
```cmd
python C:\pfad\zum\skript\win\convert_graphics.py
```

Das Skript gibt den Fortschritt live auf der Konsole aus und erstellt eine detaillierte Log-Datei (`konvertierungs_log.txt`) im `input_folder`.