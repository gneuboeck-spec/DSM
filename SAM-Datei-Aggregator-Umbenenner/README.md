# SAM-Datei-Aggregator und -Umbenenner

Dieses Verzeichnis enthält ein Python-Skript, das rekursiv `.sam`-Dateien aus einem Quellverzeichnis und seinen Unterordnern sammelt, sie in einen zentralen Zielordner kopiert und dabei eindeutige Namen vergibt, um Dateikonflikte zu vermeiden.

## Zweck des Skripts

In komplexen Verzeichnisstrukturen kommt es häufig vor, dass Dateien mit identischen Namen in verschiedenen Unterordnern existieren. Das manuelle Zusammenführen solcher Dateien ist fehleranfällig und zeitaufwendig. Dieses Skript automatisiert den Prozess für `.sam`-Dateien und löst dabei folgende Aufgaben:

1.  **Zentralisierung:** Es durchsucht einen Quellordner (`source_root`) rekursiv nach allen Dateien mit der Endung `.sam`.
2.  **Kopieren:** Jede gefundene `.sam`-Datei wird in einen zentralen Zielordner (`target_dir`, standardmäßig ein Unterordner namens `SAM`) kopiert. Die Originaldateien bleiben unberührt.
3.  **Intelligente Umbenennung:** Um Namenskonflikte zu vermeiden, prüft das Skript, ob eine Datei mit dem gleichen Namen bereits im Zielordner existiert.
    *   Wenn der Name bereits vergeben ist, wird die neue Datei systematisch umbenannt, indem ein numerischer Suffix angehängt wird (z.B. `Datei001.sam`, `Datei002.sam`, etc.).
4.  **Detaillierte Protokollierung:** Nach Abschluss des Kopiervorgangs wird eine Log-Datei (`sam_file_mapping.txt`) erstellt. Diese Datei dokumentiert für jede kopierte Datei:
    *   Den neuen Dateinamen im Zielordner.
    *   Den ursprünglichen Dateinamen.
    *   Den vollständigen Pfad zum ursprünglichen Speicherort.
5.  **Dubletten-Erkennung:** Das Protokoll hebt außerdem "Dubletten-Gruppen" hervor. Dies sind Fälle, in denen Dateien mit demselben ursprünglichen Namen, aber aus unterschiedlichen Unterordnern stammend, gefunden wurden. So lässt sich leicht nachvollziehen, welche neuen Dateinamen zu einer Gruppe von Originaldateien gehören.

---

## Technische Voraussetzungen

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Das Skript verwendet nur Standardbibliotheken (`os`, `shutil`, `collections`), es sind keine zusätzlichen Installationen per `pip` erforderlich.

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts angepasst werden:

*   `source_root`: Der absolute Pfad zum Hauptordner, der die zu sammelnden `.sam`-Dateien enthält.
*   `target_dir`: (Optional) Der Pfad zum Zielordner. Standardmäßig wird ein Ordner namens `SAM` innerhalb des `source_root`-Verzeichnisses erstellt.
*   `log_file_path`: (Optional) Der Pfad, an dem die `sam_file_mapping.txt`-Datei erstellt werden soll. Standardmäßig wird sie im `source_root`-Verzeichnis angelegt.

**Beispiel für macOS:**
```python
source_root = "/Users/IhrName/Desktop/Mein_Archiv/Sicherung_ZPH1082_011_Eisendle"
---

## Anpassung für andere Dateitypen

Obwohl dieses Skript standardmäßig für `.sam`-Dateien konfiguriert ist, kann es mit minimalen Änderungen für jeden beliebigen Dateityp verwendet werden. Um beispielsweise `.jpg`-Dateien zu sammeln, müssen Sie nur die Dateiendung an den folgenden Stellen im Skript anpassen:

1.  Ändern Sie in beiden `for`-Schleifen die Bedingung `if file.lower().endswith(".sam"):` zu `if file.lower().endswith(".jpg"):`.
2.  Passen Sie die Zeile für die Umbenennung von `new_name = f"{base_name}{counter:03d}.sam"` zu `new_name = f"{base_name}{counter:03d}.jpg"` an.
3.  (Optional) Benennen Sie die Variablen `target_dir` und `log_file_path` um, um die Übersichtlichkeit zu wahren.