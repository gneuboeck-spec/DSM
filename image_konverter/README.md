# Universeller Grafik-Konverter (TIFF & PDF)

Dieses Skript ist ein leistungsstarkes Werkzeug zur automatisierten Batch-Konvertierung von diversen Raster- und Vektorgrafikformaten in standardisierte Archivformate. Es dient dazu, eine heterogene Sammlung von Bilddateien für die Langzeitarchivierung zu normalisieren.

Das Skript ist für die Integration in einen vordefinierten Archivierungsworkflow konzipiert. Es wird über Kommandozeilenargumente gesteuert, die typischerweise von einer Start-Datei (`start.bat`) übergeben werden, und erwartet eine spezifische Ordnerstruktur.

## Kernfunktionalität

Das Skript verfolgt zwei Hauptziele, indem es die Stärken spezialisierter Kommandozeilen-Tools nutzt:

1.  **Rastergrafiken nach TIFF:**
    *   **Quelle:** Gängige Rasterformate wie `.jpg`, `.png`, `.bmp`, `.webp`, `.heic` etc.
    *   **Ziel:** Verlustfreies `.tiff`-Format.
    *   **Werkzeug:** [ImageMagick](https://imagemagick.org/)

2.  **Vektorgrafiken nach PDF:**
    *   **Quelle:** Gängige Vektorformate wie `.svg`, `.wmf`, `.eps`, `.ai`.
    *   **Ziel:** Archivierungsfähiges `.pdf`-Format.
    *   **Werkzeuge:** [Inkscape](https://inkscape.org/) (für SVG, WMF) und [Ghostscript](https://www.ghostscript.com/) (für EPS, AI).

Die Zieldateien folgen der Namenskonvention `Originalname.originalendung.zielendung` (z.B. `logo.svg.pdf`), um die Herkunft der Datei nachvollziehbar zu machen. Bereits konvertierte Dateien werden bei erneuter Ausführung übersprungen.

---

## Technische Voraussetzungen

Die folgenden Programme müssen auf dem System installiert und korrekt konfiguriert sein:

1.  **Python:** Version 3.6 oder neuer.
2.  **ImageMagick:** Muss installiert sein. Die `magick.exe` sollte entweder im System-`PATH` sein oder der Pfad muss im Skript direkt angegeben werden.
3.  **Inkscape:** Muss installiert sein. Da Inkscape sich selten zum `PATH` hinzufügt, muss der vollständige Pfad zur `inkscape.exe` im Skript wahrscheinlich manuell eingetragen werden.
4.  **Ghostscript:** Muss installiert sein. Die `gswin64c.exe` (oder `gswin32c.exe`) sollte entweder im System-`PATH` sein oder der Pfad muss im Skript angegeben werden.

---

## Konfiguration im Skript

Vor der ersten Ausführung müssen die Pfade zu den externen Werkzeugen am Anfang des Skripts überprüft und bei Bedarf angepasst werden.

```python
# Pfade zu den Kommandozeilen-Tools
IMAGEMAGICK_PATH = "magick.exe"
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe" # Beispielpfad, ggf. anpassen
GHOSTSCRIPT_PATH = "gswin64c.exe"

*   Wenn ein Werkzeug im System-`PATH` ist, reicht der Name der `.exe`-Datei.
*   Andernfalls muss der vollständige, absolute Pfad zur jeweiligen `.exe`-Datei eingetragen werden (siehe `INKSCAPE_PATH`-Beispiel).

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:
Documents
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 3_[Datenträger-ID]_for-transfer
                ├── Files  <-- IN DIESEM ORDNER WIRD GESUCHT
                └── (Hier wird die Log-Datei erstellt)

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python image_conversion_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die übergebenen Argumente, die Ordnerstruktur und die Verfügbarkeit der konfigurierten Tools.
2.  **Suche:** Das `Files`-Verzeichnis wird rekursiv nach allen unterstützten Bilddateien durchsucht.
3.  **Konvertierung:** Jede gefundene Datei wird mit dem passenden Werkzeug (ImageMagick, Inkscape oder Ghostscript) in das jeweilige Zielformat konvertiert. Der Fortschritt wird in der Konsole angezeigt.
4.  **Protokollierung:** Alle Aktionen, Erfolge und Fehler werden detailliert in die Log-Datei `3_[Datenträger-ID]_image_conversion.log` geschrieben.
5.  **Zusammenfassung:** Am Ende wird eine Übersicht über die Anzahl der erfolgreich konvertierten Dateien und aufgetretenen Fehler ausgegeben.
6.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT