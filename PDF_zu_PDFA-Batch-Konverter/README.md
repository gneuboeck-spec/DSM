# PDF zu PDF/A Batch-Konverter

Dieses Verzeichnis enthält ein Python-Skript zur automatisierten Konvertierung von Standard-PDF-Dateien in das langzeitarchivierbare **PDF/A-2b-Format**. 

Es ist darauf hinzuweisen, dass im Skript `convert_textbasierte_to_pdfa` bereits eine standardmäßige Konvertierung inkludiert ist. Das hier vorliegende Skript widmet sich jedoch einer **spezifischen Anforderung**: Es verarbeitet PDF-Dateien, die ursprünglich mit Hilfe von Ghostscript aus PostScript-Dateien (`.ps`) erzeugt wurden, welche wiederum aus AmiPro-Dateien (`.sam`) stammen. Dieser Workflow ermöglicht es, das ursprüngliche Layout der SAM-Dateien exakt beizubehalten und dennoch ein valides Archivierungsformat zu erhalten.

---

## Zweck des Skripts

Das Hauptziel dieses Skripts ist es, eine Sammlung von PDF-Dateien, die möglicherweise nicht den Archivierungsstandards entsprechen, in konforme PDF/A-Versionen umzuwandeln. Es fungiert als spezialisierter Schritt in einem größeren Workflow, bei dem die Zieldateien oft eine doppelte Endung wie `.sam.pdf` besitzen.

Der Konvertierungsprozess ist robust gestaltet:

1.  **Dateisuche:** Das Skript durchsucht rekursiv einen angegebenen Ordner nach allen PDF-Dateien, die auf `.sam.pdf` enden.
2.  **Zwischenkonvertierung (Normalisierung):** Jede gefundene PDF wird mithilfe von LibreOffice im Hintergrund geöffnet und als OpenDocument Graphics (`.odg`) Datei zwischengespeichert. Dieser Schritt "normalisiert" den Inhalt der PDF in einem nativen LibreOffice-Format.
3.  **PDF/A-Export:** Aus der temporären `.odg`-Datei wird anschließend eine neue, saubere **PDF/A-2b**-Version exportiert. Der Export aus einem nativen Format ist oft zuverlässiger als eine direkte PDF-zu-PDF/A-Manipulation.
4.  **Ersetzen:** Die neu erstellte PDF/A-Datei ersetzt die ursprüngliche `.sam.pdf`-Datei.
5.  **Protokollierung:** Alle Schritte, Erfolge und Fehler werden in einer Log-Datei (`konvertierungslog.txt`) im Quellverzeichnis sowie auf der Konsole protokolliert.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Das Skript verwendet ausschließlich Standardbibliotheken (`os`, `subprocess`, `datetime`, `shutil`, `sys`).

### 2. LibreOffice
*   **Zweck:** Dies ist das zentrale Konvertierungswerkzeug. Das Skript ist auf eine funktionierende Installation von LibreOffice angewiesen.
*   **Installation:** Eine aktuelle, stabile Version von LibreOffice muss auf dem System installiert sein.
*   **Konfiguration:** Der Pfad zur ausführbaren `soffice`-Datei muss im Skript korrekt angegeben werden.

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts angepasst werden:

*   `libreoffice_path`: Der exakte Pfad zur ausführbaren `soffice`-Datei (abhängig vom Betriebssystem).
*   `input_folder`: Der absolute Pfad zum Hauptordner, in dem die Suche nach `.sam.pdf`-Dateien beginnen soll.
*   `log_path`: (Optional) Der Pfad zur Log-Datei. Standardmäßig wird sie im `input_folder` erstellt.

**Beispiel für die Konfiguration (macOS):**

```python
libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
input_folder = "/Users/IhrName/Desktop/Mein_Archiv/Unterordner"
```

**Beispiel für die Konfiguration (Windows):**

```python
libreoffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
input_folder = r"C:\Users\IhrName\Documents\Archiv"
```

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT