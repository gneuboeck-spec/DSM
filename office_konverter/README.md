# Office-Dokumenten-Konverter (ODF & PDF/A)

Dieses Verzeichnis enthält Skripte zur Batch-Konvertierung einer Vielzahl von Office- und textbasierten Dateiformaten. Der Hauptzweck ist die Standardisierung von Dokumenten in offene Formate und die Erstellung von langzeitarchivierbaren PDF/A-Derivaten.

## Zweck des Skripts

Das Skript durchsucht rekursiv einen angegebenen Quellordner und führt für jede gefundene Datei einen zweistufigen Konvertierungsprozess durch:

1.  **Konvertierung nach OpenDocument Format (ODF):** Jedes proprietäre Format (z.B. `.doc`, `.xls`, `.ppt`) wird in sein modernes, offenes Gegenstück (`.odt`, `.ods`, `.odp`) umgewandelt. Diese ODF-Datei wird als bearbeitbares Archivformat **behalten**.
2.  **Export nach PDF/A:** Aus der (originalen oder neu erstellten) ODF-Datei wird eine **PDF/A-2b**-Datei exportiert. Dies ist ein ISO-standardisiertes Format für die Langzeitarchivierung, das sicherstellt, dass die visuelle Darstellung des Dokuments über Jahrzehnte erhalten bleibt.
3.  **Spezialfall PDF:** Bereits existierende PDF-Dateien, die nicht dem PDF/A-Standard entsprechen, werden ebenfalls erkannt und in eine neue PDF/A-Version konvertiert.

Alle erstellten Dateien folgen der Namenskonvention `Originalname.originalendung.zielendung`, um die Herkunft nachvollziehbar zu machen.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme installiert und konfiguriert sein:

### 1. Python
*   **Version:** 3.6 oder neuer
*   **Grund:** Das Skript verwendet f-Strings für die Formatierung.

### 2. LibreOffice
*   **Version:** Eine aktuelle, stabile Version (z.B. 7.x oder neuer) wird dringend empfohlen.
*   **Zweck:** Dies ist das **zentrale Konvertierungswerkzeug**. Das Skript ruft LibreOffice im Hintergrund (`headless`) auf, um alle Dokumenten-Transformationen durchzuführen.
*   **Konfiguration:** Der Pfad zur ausführbaren `soffice`-Datei muss im Skript in der Variable `libreoffice_path` korrekt angegeben werden.
    *   **macOS (Standard):** `/Applications/LibreOffice.app/Contents/MacOS/soffice`
    *   **Windows (Standard):** `C:/Program Files/LibreOffice/program/soffice.exe`

### 3. Betriebssystem-spezifische Befehle
*   **macOS / Linux:** Das Skript verwendet den Befehl `pkill`, um eventuell hängengebliebene LibreOffice-Prozesse zu beenden. Dieser ist standardmäßig verfügbar.

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts überprüft und angepasst werden:

*   `libreoffice_path`: Der exakte Pfad zur ausführbaren `soffice`-Datei (siehe oben).
*   `input_folder`: Der absolute Pfad zum Hauptordner, der die zu konvertierenden Dateien enthält.
*   `log_path`: (Optional) Der Pfad, an dem die `konvertierungslog.txt`-Datei erstellt werden soll. Standardmäßig wird sie im `input_folder` angelegt.
*   `conversion_map`: Dieses Dictionary definiert, welche Dateiendungen erkannt und wie sie verarbeitet werden sollen. Es kann bei Bedarf um weitere Formate erweitert werden.

---

## Ausführung

Die Skripte für die verschiedenen Betriebssysteme befinden sich in den jeweiligen Unterordnern (`mac/`, `win/`).

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Stellen Sie sicher, dass alle oben genannten Voraussetzungen erfüllt sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel für macOS:**
```bash
python3 /pfad/zum/skript/mac/office_konverter.py
```

**Beispiel für Windows:**
```cmd
python C:\pfad\zum\skript\win\office_konverter.py
```

Das Skript gibt den Fortschritt live auf der Konsole aus und erstellt eine detaillierte Log-Datei im `input_folder`. Bei wiederholter Ausführung werden bereits erstellte Derivat-Dateien überschrieben, um sicherzustellen, dass sie immer auf dem neuesten Stand sind.