# PostScript zu PDF Batch-Konverter

Dieses Verzeichnis enthält ein Python-Skript zur automatisierten Konvertierung von PostScript (`.ps`) Dateien in das Portable Document Format (`.pdf`).

---

## Zweck des Skripts

Das Skript durchsucht rekursiv einen angegebenen Quellordner nach allen Dateien mit der Endung `.ps`. Für jede gefundene Datei wird mithilfe des Kommandozeilen-Tools **Ghostscript** eine PDF-Version erstellt. Die resultierende PDF-Datei wird **im selben Ordner wie die Originaldatei** gespeichert.

Dieser Prozess ist ideal, um eine große Sammlung von PostScript-Dateien, die in einer bestehenden Verzeichnisstruktur verteilt sind, für eine bessere Zugänglichkeit und Kompatibilität in das PDF-Format zu überführen, ohne die Ordnerstruktur manuell verändern zu müssen.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Das Skript verwendet ausschließlich Standardbibliotheken (`os` und `subprocess`).

### 2. Ghostscript
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript fungiert als Wrapper, der Ghostscript für jede gefundene Datei aufruft.
*   **Installation:** Ghostscript muss auf Ihrem System installiert sein.
    *   **macOS:** Am einfachsten via [Homebrew](https://brew.sh/): `brew install ghostscript`
    *   **Windows:** Laden Sie den Installer von der [offiziellen Ghostscript-Webseite](https://ghostscript.com/releases/gsdnld.html) herunter.
*   **Konfiguration:** Der Pfad zur ausführbaren Ghostscript-Datei muss im Skript korrekt angegeben werden (siehe unten).

---

## Konfiguration im Skript

Vor der Ausführung müssen die Variablen am Anfang des Skripts an Ihre Systemumgebung angepasst werden:

*   **`ps_dir`**: Der absolute Pfad zum Hauptordner, in dem die Suche nach `.ps`-Dateien beginnen soll.
*   **`gs_path`**: Der exakte Pfad zur ausführbaren Ghostscript-Datei. Der Name unterscheidet sich je nach Betriebssystem (z. B. `gs` unter macOS/Linux vs. `gswin64c.exe` unter Windows).

### Beispiel für macOS (Apple Silicon/Homebrew):
```python
# Pfad zum Ordner mit den PS-Dateien
ps_dir = "/Users/Name/Desktop/Meine_Dokumente"

# Pfad zu Ghostscript
gs_path = "/opt/homebrew/bin/gs" 
```

### Beispiel für Windows:
```python
# Pfad zum Ordner mit den PS-Dateien
ps_dir = r"C:\Users\IhrName\Documents\PostScript_Files"

# Pfad zu Ghostscript (Die Versionsnummer im Pfad kann variieren!)
gs_path = r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe"
```

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT