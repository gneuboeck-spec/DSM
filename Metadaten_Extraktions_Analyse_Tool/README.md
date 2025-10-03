# FileTrove: Umfassendes Metadaten-Extraktions- und Analyse-Tool

Dieses Verzeichnis enthält ein hochspezialisiertes Python-Skript (`filetrove.py`) zur tiefgehenden Analyse und Extraktion von Metadaten aus einer Vielzahl von Dateiformaten. Das Skript orchestriert eine Kette von professionellen Kommandozeilen-Tools, aggregiert deren Ergebnisse, vereinheitlicht die Daten und gibt sie als strukturierte XML-Datei aus.

## Zweck des Skripts

Das Hauptziel von "FileTrove" ist die Erstellung eines detaillierten, maschinenlesbaren "Steckbriefs" für jede Datei in einer Sammlung. Dies ist besonders nützlich für die digitale Archivierung, forensische Analysen und die Katalogisierung großer Datenmengen.

**Der Prozess im Überblick:**

1.  **Globale Analyse:** Das Skript startet mit einem Gesamtdurchlauf über den Quellordner mithilfe von **Brunhilde**, um eine Übersicht über Dateiformate, MIME-Typen und potenzielle Probleme (z.B. Viren, Format-Inkonsistenzen) zu erhalten.
2.  **Einzeldatei-Extraktion:** Jede Datei wird anschließend einzeln mit einer Reihe von spezialisierten Werkzeugen analysiert, um technische, beschreibende und strukturelle Metadaten zu extrahieren.
3.  **Intelligente Aggregation & Vereinheitlichung:** Die oft redundanten und unterschiedlich benannten Roh-Metadaten aus allen Quellen werden in einem zentralen Schritt zusammengeführt, bereinigt und auf ein einheitliches, standardisiertes Vokabular abgebildet.
4.  **Validitätsprüfung:** Das Skript führt eine "Best-Effort"-Validierung durch, um zu beurteilen, ob eine Datei wahrscheinlich intakt oder beschädigt ist.
5.  **XML-Ausgabe:** Alle gesammelten und aufbereiteten Informationen werden in einer einzigen, gut strukturierten XML-Datei (`FileTrove_output.xml`) gespeichert.

---

## Technische Voraussetzungen

Dieses Skript ist ein "Power-User"-Werkzeug und hat eine **umfangreiche Liste an Abhängigkeiten**. Alle der folgenden Komponenten müssen installiert und korrekt konfiguriert sein.

### 1. Python
*   **Version:** 3.9 oder neuer.
*   **Grund:** Das Skript verwendet Funktionen (`ET.indent`) und Typ-Hinweise, die in neueren Python-Versionen Standard sind.
*   **Bibliotheken:** Alle folgenden Pakete müssen in einer **virtuellen Umgebung (`venv`)** installiert werden. Erstellen Sie dazu eine `requirements.txt`-Datei mit dem folgenden Inhalt und führen Sie `pip install -r requirements.txt` aus.
    ```
    yara-python
    mutagen
    PyPDF2
    Pillow
    chardet
    brunnhilde
    ```

### 2. Externe Kommandozeilen-Tools

Alle der folgenden Programme müssen installiert und systemweit verfügbar sein (d.h. ihre Verzeichnisse müssen zur **Systemumgebungsvariable `PATH`** hinzugefügt werden).

| Werkzeug | Zweck | Installationshinweis |
| :--- | :--- | :--- |
| **Brunhilde** | Globale Verzeichnis-Analyse, Berichterstattung | `pip install brunnhilde` |
| **Siegfried** | Format-Identifikation (wird von Brunhilde genutzt) | **macOS:** `brew install siegfried` / **Windows:** `sf.exe` von der Webseite herunterladen |
| **ExifTool** | Umfassende Metadaten-Extraktion | Von der offiziellen Webseite herunterladen |
| **FFmpeg** | Analyse von Audio- & Videodateien (`ffprobe`) | **macOS:** `brew install ffmpeg` / **Windows:** Von [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) laden |
| **ClamAV** | Virenscan (wird von Brunhilde genutzt) | **macOS:** `brew install clamav` / **Windows:** Installer von der Webseite |
| **YARA** | Mustererkennung in Dateien | Die `yara-python`-Bibliothek benötigt die C-Bibliotheken von YARA. **macOS:** `brew install yara` |
| **Hachoir** | Zusätzliche Metadaten-Extraktion | `pip install hachoir`, stellt `hachoir-metadata` bereit. |

---

## Konfiguration im Skript

Vor der Ausführung müssen die Pfade am Anfang des Skripts für das jeweilige Betriebssystem angepasst werden.

*   **`BASE_DIR`**: Der absolute Pfad zum Hauptordner, der analysiert werden soll. Kann auch als Kommandozeilen-Argument übergeben werden.
*   **`OUTPUT_XML`**: Der Pfad, an dem die finale XML-Ausgabedatei gespeichert werden soll.
*   **`YARA_RULES_FILE`**: Der Pfad zu Ihrer `.yar`-Regeldatei für YARA.
*   **`BRUNHILDE_OUTPUT_DIR`**: (Optional) Ein permanenter Ordner für die detaillierten Berichte, die Brunhilde erstellt.

**Beispiel für macOS:**
```python
BASE_DIR = "/Users/IhrName/Desktop/Mein_Archiv"
OUTPUT_XML = "/Users/IhrName/Desktop/FileTrove_output.xml"
# ... etc.
```

**Beispiel für Windows:**
```python
# Verwenden Sie os.path.join für Kompatibilität
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_DIR = os.path.join(desktop, "Mein_Archiv")
OUTPUT_XML = os.path.join(desktop, "FileTrove_output.xml")
# ... etc.
```

---

## Ausführung

1.  **Vorbereitung:** Stellen Sie sicher, dass **alle** oben genannten Voraussetzungen (Python-Pakete in einer `venv`, externe Tools im `PATH`) erfüllt sind.
2.  **Virtuelle Umgebung aktivieren:** Öffnen Sie ein Terminal oder eine PowerShell und aktivieren Sie Ihre `venv`.
    *   **macOS:** `source /pfad/zur/venv/bin/activate`
    *   **Windows:** `C:\pfad\zur\venv\Scripts\activate`
3.  **Skript starten:** Führen Sie das Skript mit dem Python-Interpreter aus.
    *   **Standard-Ausführung (verwendet `BASE_DIR` aus dem Skript):**
        ```bash
        python3 filetrove_scan_und_brunhilde.py
        ```
    *   **Flexible Ausführung (analysiert einen anderen Ordner):**
        ```bash
        python3 filetrove_scan_und_brunhilde.py "/pfad/zu/einem/anderen/Ordner"
        ```

Das Skript ist sehr gibt seinen Fortschritt sowie eventuelle Fehler live auf der Konsole aus. Der Prozess kann je nach Größe des Quellordners sehr lange dauern.