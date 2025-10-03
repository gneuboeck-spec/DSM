# FileTrove: Umfassende Metadaten-Extraktion und Archiv-Analyse

Dieses Verzeichnis enthält ein Python-Skript zur Extraktion von Metadaten aus einer Vielzahl von Dateiformaten sowie zur Durchführung einer detaillierten Analyse von Archiven. Der Hauptzweck ist die Gewinnung umfassender Informationen über Dateien und deren Eigenschaften.

## Zweck des Skripts

Das Skript durchsucht rekursiv einen angegebenen Quellordner und führt für jede gefundene Datei einen mehrstufigen Analyseprozess durch:

1.  **Metadaten-Extraktion:** Verwendet verschiedene Tools und Bibliotheken (ExifTool, FFprobe, Mutagen, PyPDF2, etc.), um Metadaten aus Dateien zu extrahieren.
2.  **YARA-Regel-Anwendung:** Wendet YARA-Regeln an, um Dateien auf spezifische Muster zu untersuchen.
3.  **Brunhilde-Integration:** Führt Brunhilde aus, um umfassende Analysen und Berichte über Archive zu erstellen, einschließlich Formatzusammenfassungen, MIME-Typ-Zusammenfassungen und Virenscan-Ergebnisse.
4.  **XML-Ausgabe:** Speichert die extrahierten Metadaten und Analyseergebnisse in einer strukturierten XML-Datei.

Alle erstellten XML-Dateien folgen der Namenskonvention `FileTrove_output.xml`, um die Ergebnisse der Analyse zu speichern.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme und Bibliotheken installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.9 oder neuer
*   **Grund:** Das Skript verwendet moderne Python-Funktionen.

### 2. Python-Pakete
*   **Abhängigkeiten:** Die erforderlichen Python-Pakete sind in `requirements.txt` aufgelistet und können mit `pip` installiert werden.

### 3. Externe Tools
*   **ExifTool:** Für die Extraktion von Metadaten aus einer Vielzahl von Dateiformaten.
*   **FFmpeg (für FFprobe):** Für die Extraktion von Metadaten aus Mediendateien.
*   **hachoir-metadata:** Für zusätzliche Metadaten-Extraktion.
*   **yara:** Für die Anwendung von YARA-Regeln zur Mustererkennung.
*   **Brunhilde:** Für eine umfassende Analyse von Archiven.

### Betriebssystem-spezifische Konfiguration

*   Stellen Sie sicher, dass die oben genannten externen Tools installiert und im System-Pfad (PATH) verfügbar sind.

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts überprüft und angepasst werden:

*   `BASE_DIR`: Der absolute Pfad zum Hauptordner, der die zu analysierenden Dateien enthält.
*   `OUTPUT_XML`: Der Pfad, an dem die Ausgabe-XML-Datei gespeichert werden soll.
*   `YARA_RULES_FILE`: Der Pfad zur YARA-Regeldatei.
*   `BRUNHILDE_OUTPUT_DIR`: (Optional) Der Pfad, in dem Brunhilde seine Berichte speichern soll. Wenn leer, wird ein temporäres Verzeichnis verwendet.

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS/Linux) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Stellen Sie sicher, dass alle oben genannten Voraussetzungen erfüllt sind und die erforderlichen Python-Pakete installiert sind.
3.  Navigieren Sie zum Verzeichnis des Skripts.
4.  Aktivieren Sie die virtuelle Umgebung (falls verwendet):
    ```bash
    source filetrove-venv/bin/activate  # oder filetrove-venv\Scripts\activate unter Windows
    ```
5.  Führen Sie das Skript mit dem Python-Interpreter aus und übergeben Sie den Eingabeordner als Argument:

    **Beispiel:**
    ```bash
    python3 filetrove_scan_und_brunhilde.py /Pfad/zum/Eingabeordner
    ```

Das Skript gibt den Fortschritt live auf der Konsole aus und speichert die extrahierten Metadaten in der konfigurierten XML-Datei.

---

## Anpassung

*   **YARA-Regeln:** Bearbeiten Sie die YARA-Regeldatei, um spezifische Dateitypen oder Muster zu erkennen.
*   **Metadaten-Extraktion:** Ändern Sie die Metadaten-Extraktionsfunktionen, um zusätzliche Metadaten oder Dateitypen zu unterstützen.
*   **`unify_metadata_keys`-Funktion:** Passen Sie diese Funktion an, um die Standardisierung und Vereinheitlichung von Metadatenschlüsseln zu verbessern.
*   **Externe Tools:** Das Skript kann erweitert werden, um zusätzliche externe Tools für die Dateianalyse zu integrieren.

## Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.


## Danksagung

Dieses Projekt verwendet Open-Source-Tools und -Bibliotheken. Wir danken den Entwicklern dieser Tools für ihre wertvollen Beiträge.