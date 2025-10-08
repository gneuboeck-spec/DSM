# Datei-Rückverteilungs-Skript

Dieses Verzeichnis enthält ein Python-Skript, das als Gegenstück zum "SAM-Datei-Aggregator-Umbenenner" dient. Seine Hauptaufgabe ist es, neu erstellte oder bearbeitete Dateien (standardmäßig `.ps`-Dateien) aus einem zentralen Sammelordner zurück in ihre ursprünglichen Verzeichnisse zu verteilen, basierend auf einer zuvor erstellten Mapping-Datei.

## Zweck des Skripts

Dieses Skript ist der zweite Schritt in einem zweistufigen Workflow zur Bearbeitung von verteilten Dateien:

1.  **Schritt 1 (Sammeln):** Ein erstes Skript (wie der "SAM-Datei-Aggregator-Umbenenner") sammelt alle Dateien eines bestimmten Typs (z.B. `.sam`) aus einer komplexen Verzeichnisstruktur in einem zentralen Ordner und erstellt dabei eine Log-Datei (`..._file_mapping.txt`), die die ursprünglichen Speicherorte festhält.
2.  **Schritt 2 (Rückverteilen):** Dieses Skript liest die Log-Datei aus Schritt 1, um zugehörige Derivat-Dateien (z.B. neu erstellte `.ps`-Dateien) vom zentralen Ordner zurück an die ursprünglichen Speicherorte der Quelldateien zu kopieren.

**Der Prozess im Überblick:**

1.  **Lesen der Mapping-Datei:** Das Skript parst die Log-Datei (`sam_file_mapping.txt`), um die Verknüpfung zwischen den neuen (ggf. umbenannten) Dateinamen im Sammelordner und den ursprünglichen Pfaden der Quelldateien zu verstehen.
2.  **Pfad-Rekonstruktion:** Für jeden Eintrag in der Log-Datei ermittelt das Skript:
    *   Den **Quellpfad** der zu kopierenden Derivat-Datei (z.B. `.../SAM/Datei001.ps`).
    *   Den **Zielpfad** im ursprünglichen Unterverzeichnis (z.B. `.../Projekt_A/Unterordner_B/Datei.ps`).
3.  **Kopieren:** Das Skript prüft, ob die Derivat-Datei im Sammelordner existiert. Wenn ja, wird sie an ihren ursprünglichen Zielort kopiert.
4.  **Status-Ausgabe:** Jeder Kopiervorgang oder jede nicht gefundene Datei wird auf der Konsole protokolliert, um den Prozess nachvollziehbar zu machen.

---

## Technische Voraussetzungen

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Das Skript verwendet nur Standardbibliotheken (`os`, `shutil`), es sind keine zusätzlichen Installationen per `pip` erforderlich.

### 2. Log-Datei
*   Es muss eine **Mapping-Datei** (`sam_file_mapping.txt`) existieren, die von einem vorherigen Sammel-Skript erstellt wurde. Das Format dieser Datei ist entscheidend und muss dem Muster `NeuerName <-- OriginalName | /original/pfad/zur/datei` folgen.

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts angepasst werden:

*   `sam_dir`: Der absolute Pfad zum zentralen Sammelordner, der die Quelldateien für den Kopiervorgang enthält (z.B. die `.ps`-Dateien).
*   `log_file_path`: Der absolute Pfad zur Mapping-Datei, die als "Landkarte" für die Rückverteilung dient.

**Beispiel für macOS:**
```python
sam_dir = "/Users/IhrName/Desktop/Sicherung/SAM"
log_file_path = "/Users/IhrName/Desktop/Sicherung/sam_file_mapping.txt"```

**Beispiel für Windows:**
```python
sam_dir = "C:\\Users\\IhrName\\Desktop\\Sicherung\\SAM"
log_file_path = "C:\\Users\\IhrName\\Desktop\\Sicherung\\sam_file_mapping.txt"
---

## Anpassung für andere Dateitypen

Obwohl dieses Skript für das Zurückkopieren von `.ps`-Dateien konfiguriert ist, kann es mit minimalen Änderungen für jeden beliebigen Dateityp angepasst werden. Angenommen, Sie möchten `.xml`-Dateien zurückverteilen:

1.  **Dateiendung im Ziel anpassen:** Ändern Sie in der `for`-Schleife die Zeile, die den Zieldateinamen erstellt:
    *   **Alt:** `ps_target_name = base_name + ".ps"`
    *   **Neu:** `ps_target_name = base_name + ".xml"`

2.  **Dateiendung in der Quelle anpassen:** Ändern Sie die Zeile, die den Quelldateinamen erstellt:
    *   **Alt:** `ps_source_name = os.path.splitext(new_name)[0] + ".ps"`
    *   **Neu:** `ps_source_name = os.path.splitext(new_name)[0] + ".xml"`

3.  **(Optional)** Benennen Sie die Variablen um (z.B. von `ps_target_path` zu `xml_target_path`), um die Lesbarkeit des Codes zu erhalten.

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS/Linux) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Stellen Sie sicher, dass die Pfade in den Variablen `sam_dir` und `log_file_path` im Skript korrekt gesetzt sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**
```bash
python3 /pfad/zum/skript/rueckverteilung.py