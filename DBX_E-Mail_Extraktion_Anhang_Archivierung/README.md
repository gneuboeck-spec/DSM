# DBX E-Mail-Extraktion und Anhang-Archivierung ("Super-Skript")

Dieses Verzeichnis enthält ein hochspezialisiertes Python-Skript, das einen vollständigen Archivierungs-Workflow automatisiert: Es rettet E-Mails aus dem veralteten Microsoft Outlook Express (`.dbx`)-Format und konvertiert anschließend alle extrahierten Anhänge in moderne, archivsichere Formate.

## Zweck des Skripts

Das Skript ist eine "All-in-One"-Lösung, die einen komplexen, mehrstufigen Prozess durchführt:

1.  **E-Mail-Rettung:** Es durchsucht einen Quellordner nach `.dbx`-Datenbanken, konvertiert diese in das offene MBOX-Format und extrahiert jede einzelne E-Mail als separate, standardkonforme `.eml`-Datei.
2.  **Intelligente Benennung:** Jede `.eml`-Datei wird nach dem Schema `JJJJ-MM-TT-HH-MM-SS_Betreff.eml` benannt, um eine einfache chronologische Sortierung zu ermöglichen.
3.  **Anhang-Extraktion:** Alle Anhänge werden aus den E-Mails extrahiert und mit einer klaren Namenskonvention gespeichert, die die Zuordnung zur ursprünglichen E-Mail sicherstellt (`EML-Name.Anhang-Name.ext`).
4.  **Intelligente Anhang-Konvertierung:** Für jeden extrahierten Anhang wird automatisch der passende Konvertierungsprozess für die Langzeitarchivierung angestoßen:
    *   **Office-Dokumente** → nach **PDF/A** (über ODF-Zwischenschritt).
    *   **Rasterbilder** → nach **TIFF**.
    *   **Vektorgrafiken** → nach **PDF**.
    *   **Audiodateien** → nach **MP3** und **WAV**.
    *   **Videodateien** → nach **MP4**.

Das Endergebnis ist ein sauber strukturiertes, durchsuchbares und zukunftssicheres Archiv Ihrer alten E-Mail-Kommunikation inklusive aller Anhänge.

---

## Technische Voraussetzungen

Dieses Skript ist ein Orchestrierungs-Tool, das eine Vielzahl von externen Programmen benötigt. **Alle** der folgenden Komponenten müssen installiert und korrekt konfiguriert sein.

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich.

### 2. Externe Programme

Alle Kommandozeilen-Tools müssen systemweit verfügbar sein (d.h. ihre Verzeichnisse müssen zur **Systemumgebungsvariable `PATH`** hinzugefügt werden).

| Werkzeug | Zweck | Installationshinweis |
| :--- | :--- | :--- |
| **Wine** | (Nur macOS/Linux) Führt Windows-Programme aus. | **macOS:** `brew install wine-stable` |
| **DbxConv.exe**| (Nur Windows) Extrahiert E-Mails aus `.dbx`-Dateien. | Manuell herunterladen und in einen Ordner im `PATH` legen. |
| **LibreOffice** | Konvertiert Office-Dokumente. | Standard-Installer verwenden. **Windows:** Pfad im Skript anpassen. |
| **ImageMagick** | Konvertiert Rasterbilder. | **macOS:** `brew install imagemagick` / **Windows:** Installer mit "Add to PATH". |
| **Inkscape** | Konvertiert Vektorgrafiken. | **macOS:** `brew install --cask inkscape` / **Windows:** Installer mit "Add to PATH". |
| **Ghostscript** | Helfer für PDF/EPS/AI-Import. | **macOS:** `brew install ghostscript` / **Windows:** Installer, Pfad zum `bin`-Ordner zum `PATH` hinzufügen. |
| **FFmpeg** | Konvertiert Audio- & Videodateien. | **macOS:** `brew install ffmpeg` / **Windows:** Von [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) laden und zum `PATH` hinzufügen. |

---

## Konfiguration im Skript

Vor der Ausführung müssen die Pfade zu den externen Tools und zum Eingabeordner am Anfang des Skripts für das jeweilige Betriebssystem angepasst werden.

*   **`main_input_dir` (ganz am Ende des Skripts):** Der absolute Pfad zum Hauptordner, der die `.dbx`-Dateien enthält.
*   **Pfade zu den externen Tools (am Anfang):** Überprüfen Sie, ob die Pfade (`dbxconv_path`, `libreoffice_path`, etc.) für Ihr System korrekt sind. Wenn die Tools im `PATH` sind, reichen die einfachen Namen.

**Beispiel für macOS:**
```python
dbxconv_path = "/Users/IhrName/Desktop/dbxconv/DbxConv.exe"
libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
inkscape_path = "/Applications/Inkscape.app/Contents/MacOS/inkscape"
# ... etc.
main_input_dir = "/Users/IhrName/Desktop/Email_Archiv"
```

**Beispiel für Windows:**
```python
dbxconv_path = "DbxConv.exe" # Wenn im PATH
libreoffice_path = "C:/Program Files/LibreOffice/program/soffice.exe"
inkscape_path = "inkscape.exe" # Wenn im PATH
# ... etc.
main_input_dir = "C:/Users/IhrName/Desktop/Email_Archiv"
```

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/Git Bash (Windows).
2.  Stellen Sie sicher, dass **alle** oben genannten Voraussetzungen erfüllt und die Pfade im Skript korrekt konfiguriert sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**```bash
python3 /pfad/zum/skript/email_archivierer.py

Das Skript gibt seinen Fortschritt live auf der Konsole aus. Es gibt **keine** separate Log-Datei, daher wird empfohlen, die Konsolenausgabe bei Bedarf in eine Datei umzuleiten.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT
