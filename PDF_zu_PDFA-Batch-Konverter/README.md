# PDF zu PDF/A Batch-Konverter

Dieses Verzeichnis enthält ein Python-Skript zur automatisierten Konvertierung von Standard-PDF-Dateien in das langzeitarchivierbare PDF/A-2b-Format.

## Zweck des Skripts

Das Hauptziel dieses Skripts ist es, eine Sammlung von PDF-Dateien, die möglicherweise nicht den Archivierungsstandards entsprechen, in konforme PDF/A-Versionen umzuwandeln. Es ist speziell dafür ausgelegt, als zweiter Schritt in einem größeren Workflow zu fungieren, bei dem die Zieldateien eine doppelte Endung wie `.sam.pdf` haben.

Der Konvertierungsprozess ist robust gestaltet, um eine hohe Kompatibilität und Standardkonformität zu gewährleisten:

1.  **Dateisuche:** Das Skript durchsucht rekursiv einen angegebenen Ordner nach allen PDF-Dateien, die auf `.sam.pdf` enden.
2.  **Zwischenkonvertierung (Der Trick):** Jede gefundene PDF wird mithilfe von LibreOffice im Hintergrund geöffnet und als OpenDocument Graphics (`.odg`) Datei zwischengespeichert. Dieser Schritt "normalisiert" den Inhalt der PDF in einem nativen LibreOffice-Format.
3.  **PDF/A-Export:** Aus der temporären `.odg`-Datei wird anschließend eine neue, saubere **PDF/A-2b**-Version exportiert. Der Export aus einem nativen Format ist oft zuverlässiger als eine direkte PDF-zu-PDF/A-Konvertierung.
4.  **Ersetzen:** Die neu erstellte PDF/A-Datei ersetzt die ursprüngliche `.sam.pdf`-Datei.
5.  **Protokollierung:** Alle Schritte, Erfolge und Fehler werden in einer Log-Datei (`konvertierungslog.txt`) im Quellverzeichnis sowie auf der Konsole protokolliert.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Das Skript verwendet nur die Standardbibliotheken `os`, `subprocess`, `datetime`, `shutil` und `sys`.

### 2. LibreOffice
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript ist auf eine funktionierende Installation von LibreOffice angewiesen, um die Konvertierungen durchzuführen.
*   **Installation:** Eine aktuelle, stabile Version von LibreOffice muss auf dem System installiert sein.
*   **Konfiguration:** Der Pfad zur ausführbaren `soffice`-Datei muss im Skript korrekt angegeben werden (siehe unten).

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts **unbedingt** angepasst werden:

*   `libreoffice_path`: Der exakte Pfad zur ausführbaren `soffice`-Datei von LibreOffice.
*   `input_folder`: Der absolute Pfad zum Hauptordner, in dem die Suche nach `.sam.pdf`-Dateien beginnen soll.
*   `log_path`: (Optional) Der Pfad zur Log-Datei. Standardmäßig wird sie im `input_folder` erstellt.

**Beispiel für macOS:**
```python
libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
input_folder = "/Users/IhrName/Desktop/Mein_Archiv/Unterordner"