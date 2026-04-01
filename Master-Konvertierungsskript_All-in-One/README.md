# Master-Konvertierungsskript (All-in-One)



Dieses Skript ist das zentrale Werkzeug zur Konvertierung und Normalisierung von Dateien für die Langzeitarchivierung. Es vereint die Funktionalitäten der spezialisierten Einzel-Skripte (Audio, Bild, Text/Office, Video) in einem einzigen, umfassenden Workflow. Das Ziel ist es, für jede unterstützte Quelldatei standardisierte, archivsichere Derivate zu erstellen.



Das Skript ist als integraler Bestandteil eines automatisierten Archivierungsworkflows konzipiert und wird über eine Start-Datei (`start.bat`) mit dynamischen Pfaden gesteuert.



## Kernfunktionalität: Der "Digital Twin"-Ansatz



Das Skript durchsucht einen Quellordner und wendet je nach Dateityp eine spezifische Konvertierungslogik an, um "digitale Zwillingspaare" oder standardisierte Derivate zu erzeugen:



\*   \*\*Audio-Dateien:\*\*

&nbsp;   \*   \*\*Quelle:\*\* `.mp3`, `.wav`, `.flac`, etc.

&nbsp;   \*   \*\*Derivate:\*\* Eine `.mp3`-Datei (für Kompatibilität) und eine `.wav`-Datei (für Archivqualität).

&nbsp;   \*   \*\*Werkzeug:\*\* FFmpeg



\*   \*\*Bild-Dateien:\*\*

&nbsp;   \*   \*\*Rastergrafiken (`.jpg`, `.png`, etc.):\*\* Werden in eine verlustfreie `.tiff`-Datei konvertiert. (Werkzeug: ImageMagick)

&nbsp;   \*   \*\*Vektorgrafiken (`.svg`, `.ai`, etc.):\*\* Werden in eine archivsichere `.pdf`-Datei konvertiert. (Werkzeuge: Inkscape, Ghostscript)



\*   \*\*Office-Dokumente:\*\*

&nbsp;   \*   \*\*Quelle:\*\* `.doc`, `.xls`, `.ppt`, etc.

&nbsp;   \*   \*\*Derivate:\*\* Eine OpenDocument-Version (`.odt`, `.ods`, `.odp`) und eine `.pdf`/A-Version.

&nbsp;   \*   \*\*Werkzeug:\*\* LibreOffice



\*   \*\*Video-Dateien:\*\*

&nbsp;   \*   \*\*Quelle:\*\* `.mov`, `.avi`, `.mkv`, etc.

&nbsp;   \*   \*\*Derivat:\*\* Eine hochkompatible `.mp4`-Datei (H.264/AAC).

&nbsp;   \*   \*\*Werkzeug:\*\* FFmpeg



Alle erstellten Dateien folgen der konsistenten Namenskonvention `Originalname.originalendung.zielendung`, um die Herkunft nachvollziehbar zu machen. Eine intelligente Logik verhindert die erneute Konvertierung bereits verarbeiteter Dateien.



---



## Technische Voraussetzungen



Damit dieses Skript funktioniert, müssen \*\*alle\*\* folgenden Programme installiert und korrekt konfiguriert sein:



1\.  \*\*Python:\*\* Version 3.6 oder neuer.

2\.  \*\*FFmpeg:\*\* `ffmpeg.exe` und `ffprobe.exe` müssen im System-`PATH` sein.

3\.  \*\*ImageMagick:\*\* `magick.exe` muss im System-`PATH` sein.

4\.  \*\*Inkscape:\*\* Der vollständige Pfad zur `inkscape.exe` muss im Skript konfiguriert werden.

5\.  \*\*Ghostscript:\*\* `gswin64c.exe` (oder `gswin32c.exe`) muss im System-`PATH` sein.

6\.  \*\*LibreOffice:\*\* Der vollständige Pfad zur `soffice.exe` muss im Skript konfiguriert werden.



---



## Konfiguration im Skript


Alle wichtigen Einstellungen sind zentral am Anfang des Skripts gebündelt. Insbesondere die Pfade zu Programmen, die sich nicht im System-`PATH` befinden, müssen hier angepasst werden:


# Beispiele für Pfad-Konfigurationen

INKSCAPE\_PATH = r"C:\\Program Files\\Inkscape\\bin\\inkscape.exe"

LIBREOFFICE\_PATH = "C:/Program Files/LibreOffice/program/soffice.exe"

Zusätzlich sind hier die Listen der unterstützten Dateiendungen für jede Kategorie definiert.

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:

Documents

└── Datentraeger\_sichern

&nbsp;   └── \[AC-Nummer]

&nbsp;       └── \[Datenträger-ID]

&nbsp;           └── 3\_\[Datenträger-ID]\_for-transfer

&nbsp;               ├── Files  <-- IN DIESEM ORDNER WIRD GESUCHT

&nbsp;               └── (Hier wird die Log-Datei erstellt)



\*   \*\*`\[AC-Nummer]`\*\*: Die Haupt-Archivierungsnummer des Projekts.

\*   \*\*`\[Datenträger-ID]`\*\*: Die eindeutige ID des zu verarbeitenden Datenträgers.


## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.


\*\*Beispielhafter Aufruf in einer `start.bat`:\*\*

@echo off

set AC\_NUMBER=AC\_0001

set DISK\_ID=CD\_01

python master\_conversion\_skript.py %AC\_NUMBER% %DISK\_ID%

pause


### Ablauf der Ausführung


1\.  \*\*Validierung:\*\* Das Skript prüft die übergebenen Argumente, die Ordnerstruktur und die Verfügbarkeit \*\*aller\*\* benötigten externen Tools.

2\.  \*\*Suche:\*\* Das `Files`-Verzeichnis wird rekursiv nach allen unterstützten Dateitypen durchsucht, wobei bereits konvertierte Dateien übersprungen werden.

3\.  \*\*Kategorisierung \& Konvertierung:\*\* Für jede gefundene Datei wird der Typ (Audio, Bild, etc.) bestimmt und die entsprechende Konvertierungslogik mit dem zuständigen Werkzeug aufgerufen.

4\.  \*\*Protokollierung:\*\* Alle Aktionen, Erfolge und Fehler über alle Dateitypen hinweg werden in einer einzigen, umfassenden Log-Datei (`3\_\[Datenträger-ID]\_all\_conversions.log`) zusammengefasst.

5\.  \*\*Zusammenfassung:\*\* Am Ende wird eine finale Statusmeldung ausgegeben.

6\.  \*\*Abschluss:\*\* Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT

