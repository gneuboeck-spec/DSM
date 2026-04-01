# Automatisches Analyse-Skript (Brunnhilde)

Dieses Skript automatisiert die Analyse von Dateisammlungen mithilfe des digitalen Archivierungs-Tools [Brunnhilde](https://github.com/timothyryanwalsh/brunnhilde). Es integriert Siegfried zur Dateiformat-Identifikation und optional ClamAV für Virenscans, um umfassende Berichte zu erstellen.

Das Skript ist für die wiederholte Anwendung in einer standardisierten Ordnerstruktur konzipiert und wird über Kommandozeilenargumente gesteuert, typischerweise durch eine Start-Datei (`start.bat`).

## Hauptfunktionen

*   **Vollständige Automatisierung:** Führt den gesamten Analyseprozess von Brunnhilde mit einem einzigen Befehl aus.
*   **Dynamische Pfad-Konfiguration:** Alle Pfade werden zur Laufzeit basierend auf einer `AC-Nummer` und einer `Datenträger-ID` generiert.
*   **Integration externer Tools:** Nutzt die Stärken von Siegfried (Format-Erkennung) und ClamAV (Virenscan) innerhalb des Brunnhilde-Workflows.
*   **Zusammenfassender Bericht:** Parsed die verschiedenen CSV-Berichte von Brunnhilde und fasst die wichtigsten Ergebnisse in einer einzigen, strukturierten JSON-Datei zusammen.
*   **Robuste Ausführung:** Enthält Workarounds, um bekannte Probleme bei der Ausführung von Brunnhilde unter Windows (insbesondere bei der Erstellung der `tree.txt`-Datei) zu umgehen.
*   **Finalisierung:** Benennt die finalen Berichte (`tree.txt` und die JSON-Zusammenfassung) automatisch um und legt sie im Zielverzeichnis ab.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen die folgenden Programme auf Ihrem **Windows-System** installiert und konfiguriert sein:

1.  **Python:**
    *   Version: 3.6 oder neuer.
    *   **Bibliotheken:** `brunnhilde` muss über `pip` installiert sein (`pip install brunnhilde`).

2.  **Siegfried:**
    *   **Zweck:** Wird von Brunnhilde zur Identifizierung von Dateiformaten benötigt.
    *   **Installation:** Laden Sie Siegfried herunter und entpacken Sie es in ein Verzeichnis, z.B. `C:\Program Files\Siegfried`. Der Pfad zu diesem Verzeichnis muss im Skript konfiguriert werden.

3.  **ClamAV (Optional):**
    *   **Zweck:** Wird von Brunnhilde für Virenscans verwendet.
    *   **Installation:** Wenn Sie Virenscans durchführen möchten, installieren Sie ClamAV und konfigurieren Sie den Pfad im Skript.

---

## Konfiguration im Skript

Vor der ersten Ausführung müssen die Pfade zu den externen Werkzeugen am Anfang des Skripts angepasst werden.


SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
CLAMAV_DIR = ""  # Leer lassen, wenn nicht verwendet, z.B.: r"C:\Program Files\ClamAV"

*   **`SIEGFRIED_DIR`**: Tragen Sie hier den vollständigen Pfad zum Installationsverzeichnis von Siegfried ein. Das Skript erwartet, in diesem Ordner eine `sf.exe` zu finden.
*   **`CLAMAV_DIR`**: Tragen Sie hier den Pfad zum Installationsverzeichnis von ClamAV ein, falls es verwendet werden soll. Andernfalls lassen Sie den String leer (`""`).

### Erwartete Ordnerstruktur

Das Skript ist für eine spezifische Ordnerstruktur ausgelegt, die sich im `Documents`-Ordner des Benutzers befinden muss:
Documents
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 2_[Datenträger-ID]_extracted-files
                ├── Files  <-- DIESER ORDNER WIRD ANALYSIERT
                └── (Hier werden die Analyseberichte erstellt)

*   **[AC-Nummer]**: Die Haupt-Archivierungsnummer des Projekts.
*   **[Datenträger-ID]**: Die eindeutige ID des zu verarbeitenden Datenträgers.

## Ausführung

Das Skript sollte über eine Wrapper-Datei (z.B. eine `start.bat` unter Windows) gestartet werden, die die `AC-Nummer` und die `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python analyse_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript überprüft die übergebenen Argumente, die Ordnerstruktur und die Pfade zu den konfigurierten Tools (Siegfried, ClamAV).
2.  **Brunnhilde-Ausführung:** Das Skript startet Brunnhilde und zielt auf das `Files`-Verzeichnis. Die Ausgabe wird in einen `Brunnhilde_[Datenträger-ID]`-Ordner geschrieben.
3.  **Tree-Workaround:** Da Brunnhilde unter Windows manchmal keine `tree.txt` erstellt, führt das Skript den `tree`-Befehl manuell aus, um diese wichtige Datei zu erzeugen.
4.  **Parsing:** Die von Brunnhilde erstellten CSV-Berichte und Log-Dateien werden eingelesen.
5.  **JSON-Erstellung:** Die extrahierten Informationen (Format-Zusammenfassung, MIME-Typen, Warnungen, Virenfunde etc.) werden in einer einzigen JSON-Datei zusammengefasst.
6.  **Finalisierung:** Die erstellte JSON-Datei und die `tree.txt` werden in das Zielverzeichnis verschoben und erhalten ihre finalen, standardisierten Namen.
7.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.

### Generierte Berichte

Nach erfolgreicher Ausführung befinden sich im Ordner `2_[Datenträger-ID]_extracted-files` folgende primäre Berichte:

*   **`Brunnhilde_[Datenträger-ID]`**: Der vollständige Brunnhilde-Berichtsordner mit allen Details.
*   **`2_[Datenträger-ID]_Brunnhilde_output.json`**: Die strukturierte JSON-Zusammenfassung der Analyse.
*   **`2_[Datenträger-ID]_extracted-Files-Tree.txt`**: Eine Textdatei mit der vollständigen Verzeichnisstruktur der analysierten Dateien.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT
