# PostScript zu PDF Batch-Konverter

Dieses Verzeichnis enthält ein Python-Skript zur automatisierten Konvertierung von PostScript (`.ps`) Dateien in das Portable Document Format (`.pdf`).

## Zweck des Skripts

Das Skript durchsucht rekursiv einen angegebenen Quellordner nach allen Dateien mit der Endung `.ps`. Für jede gefundene Datei wird mithilfe des Kommandozeilen-Tools **Ghostscript** eine PDF-Version erstellt. Die resultierende PDF-Datei wird **im selben Ordner wie die Originaldatei** gespeichert.

Dieser Prozess ist ideal, um eine große Sammlung von PostScript-Dateien, die in einer bestehenden Verzeichnisstruktur verteilt sind, für eine bessere Zugänglichkeit und Kompatibilität in das PDF-Format zu überführen, ohne die Ordnerstruktur zu verändern.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Das Skript verwendet nur die Standardbibliotheken `os` und `subprocess`.

### 2. Ghostscript
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript ist im Wesentlichen ein Wrapper, der Ghostscript für jede gefundene Datei aufruft.
*   **Installation:** Ghostscript muss auf Ihrem System installiert sein.
    *   **macOS:** Am einfachsten via [Homebrew](https://brew.sh/): `brew install ghostscript`
    *   **Windows:** Laden Sie den Installer von der [offiziellen Ghostscript-Webseite](https://ghostscript.com/releases/gsdnld.html) herunter.
*   **Konfiguration:** Der Pfad zur ausführbaren Ghostscript-Datei muss im Skript korrekt angegeben werden (siehe unten).

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts **unbedingt** angepasst werden:

*   `ps_dir`: Der absolute Pfad zum Hauptordner, in dem die Suche nach `.ps`-Dateien beginnen soll.
*   `gs_path`: Der exakte Pfad zur ausführbaren Ghostscript-Datei. Der Name der Datei unterscheidet sich je nach Betriebssystem.

**Beispiel für macOS:**
```python
# Pfad zum Ordner mit den PS-Dateien
ps_dir = "/Users/gregorneuboeck/Desktop/Meine_Dokumente"

# Pfad zu Ghostscript (Standard nach Homebrew-Installation auf Apple Silicon)
gs_path = "/opt/homebrew/bin/gs" 
# Alternativ auf älteren Macs: gs_path = "/usr/local/bin/gs"

**Beispiel für Windows:**
```python
# Pfad zum Ordner mit den PS-Dateien
ps_dir = "C:\\Users\\IhrName\\Documents\\PostScript_Files"

# Pfad zu Ghostscript (Die Versionsnummer im Pfad kann variieren!)
gs_path = "C:\\Program Files\\gs\\gs10.03.1\\bin\\gswin64c.exe"