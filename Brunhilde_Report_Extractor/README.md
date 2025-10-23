# Brunnhilde Report Extractor

Dieses Verzeichnis enthält ein spezialisiertes Python-Skript (`brunnhilde_macOS.py`) zur automatisierten Ausführung von **Brunnhilde**, einem mächtigen Werkzeug zur Analyse von Dateisammlungen. Das Skript orchestriert den Scan eines Verzeichnisses, parst die resultierenden Berichte und aggregiert die wichtigsten Informationen in einer einzigen, maschinenlesbaren JSON-Datei.

## Zweck des Skripts

Das Hauptziel dieses Skripts ist es, einen schnellen, aber umfassenden Überblick über eine digitale Sammlung zu erhalten. Anstatt die detaillierten Einzelberichte von Brunnhilde manuell zu sichten, extrahiert dieses Skript die Kernaussagen und fasst sie zusammen. Dies ist ideal für die Erstbewertung von digitalen Archiven, die Qualitätskontrolle oder die Vorbereitung weiterführender Analysen.

### Der Prozess im Überblick:

1.  **Automatisierte Ausführung:** Das Skript ruft Brunnhilde für ein spezifiziertes Quellverzeichnis auf. Dies beinhaltet standardmäßig die Ausführung von Werkzeugen wie Siegfried (Format-Identifikation) und ClamAV (Virenscan).
2.  **Berichts-Parsing:** Nach Abschluss des Scans lokalisiert das Skript die von Brunnhilde erstellten CSV-Berichte (`formats.csv`, `mimetypes.csv`, `unidentified.csv` etc.) sowie die Log-Datei des Virenscanners.
3.  **Datenextraktion & Aggregation:** Die relevanten Informationen aus diesen Berichten – wie Format- und MIME-Typ-Statistiken, Warnungen, nicht identifizierte Dateien und Virenfunde – werden extrahiert und in einer strukturierten Form zusammengefasst.
4.  **JSON-Ausgabe:** Alle gesammelten und aufbereiteten Informationen werden in einer einzigen, sauberen JSON-Datei (`brunnhilde_summary.json`) gespeichert, die sich ideal für die weitere maschinelle Verarbeitung oder schnelle manuelle Durchsicht eignet.

## Technische Voraussetzungen

Dieses Skript ist ein "Power-User"-Werkzeug und hat eine Reihe von Abhängigkeiten. Alle der folgenden Komponenten müssen installiert und korrekt konfiguriert sein.

### 1. Python

*   **Version:** 3.9 oder neuer.
*   **Bibliotheken:** Das Skript benötigt das `brunnhilde`-Paket. Es wird dringend empfohlen, eine virtuelle Umgebung (venv) zu verwenden.
    1.  Erstellen Sie eine venv: `python3 -m venv brunnhilde-venv`
    2.  Aktivieren Sie sie: `source brunnhilde-venv/bin/activate`
    3.  Installieren Sie Brunnhilde: `pip install brunnhilde`

### 2. Externe Kommandozeilen-Tools

Brunnhilde selbst ist ein Wrapper-Skript, das andere Werkzeuge aufruft. Die folgenden Programme müssen installiert und systemweit verfügbar sein (d.h. ihre Verzeichnisse müssen zur Systemumgebungsvariable `PATH` hinzugefügt werden).

*   **Siegfried**
    *   **Zweck:** Format-Identifikation
    *   **Installationshinweis (macOS):** `brew install siegfried`

*   **ClamAV**
    *   **Zweck:** Virenscan
    *   **Installationshinweis (macOS):** `brew install clamav`

## Konfiguration im Skript

Vor der Ausführung müssen die Pfade am Anfang des Skripts an Ihre Umgebung angepasst werden.

*   **`BASE_DIR`**: Der absolute Pfad zum Hauptordner, der analysiert werden soll. Kann auch als Kommandozeilen-Argument übergeben werden.
*   **`BRUNHILDE_OUTPUT_DIR`**: Ein permanenter Ordner für die detaillierten HTML-, CSV- und `tree`-Berichte, die Brunnhilde erstellt.
*   **`OUTPUT_JSON`**: Der Pfad, an dem die finale JSON-Zusammenfassung gespeichert werden soll.

#### Beispiel für:

```python
macOS:
BASE_DIR = "/Users/IhrName/Desktop/Mein_Archiv"
BRUNHILDE_OUTPUT_DIR = "/Users/IhrName/Desktop/Brunnhilde_Reports"
OUTPUT_JSON = "/Users/IhrName/Desktop/brunnhilde_summary.json"

Windows:
BASE_DIR = r"C:\Users\IhrName\Desktop\Mein_Archiv"
BRUNHILDE_OUTPUT_DIR = r"C:\Users\IhrName\Desktop\Brunnhilde_Reports"
OUTPUT_JSON = r"C:\Users\IhrName\Desktop\brunnhilde_summary.json"
