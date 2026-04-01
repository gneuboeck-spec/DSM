# Automatisches Analyse-Skript (Brunnhilde)

Dieses Skript automatisiert die Analyse von Dateisammlungen mithilfe des digitalen Archivierungs-Tools [Brunnhilde](https://github.com/timothyryanwalsh/brunnhilde). Es integriert Siegfried zur Dateiformat-Identifikation und optional ClamAV für Virenscans, um umfassende Berichte zu erstellen.

Das Skript ist für die wiederholte Anwendung in einer vordefinierten Ordnerstruktur konzipiert und wird über Kommandozeilenargumente gesteuert, typischerweise durch eine Start-Datei (`start.bat`).

---

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
    *   **Bibliotheken:** `brunnhilde` muss über `pip` installiert sein:
        ```bash
        pip install brunnhilde
        ```

2.  **Siegfried:**
    *   **Zweck:** Identifizierung von Dateiformaten via PRONOM.
    *   **Installation:** Laden Sie Siegfried herunter und entpacken Sie es (z. B. nach `C:\Program Files\Siegfried`). Der Pfad muss im Skript konfiguriert werden.

3.  **ClamAV (Optional):**
    *   **Zweck:** Virenscans. Wenn gewünscht, ClamAV installieren und den Pfad im Skript hinterlegen.

---

## Konfiguration im Skript

Vor der ersten Ausführung müssen die Pfade zu den externen Werkzeugen am Anfang des Skripts angepasst werden:

```python
SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
CLAMAV_DIR = ""  # Leer lassen, wenn nicht verwendet, z. B.: r"C:\Program Files\ClamAV"
```

*   **`SIEGFRIED_DIR`**: Pfad zum Verzeichnis, das die `sf.exe` enthält.
*   **`CLAMAV_DIR`**: Pfad zum Verzeichnis von ClamAV (optional).

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:

```text
Documents/
└── Datentraeger_sichern/
    └── [AC-Nummer]/
        └── [Datenträger-ID]/
            └── 2_[Datenträger-ID]_extracted-files/
                ├── Files/                      <-- DIESER ORDNER WIRD ANALYSIERT
                └── (Hier werden die Analyseberichte erstellt)
```

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

---

## Ausführung

Nutzen Sie eine Start-Datei (`start.bat`), um die Argumente korrekt zu übergeben.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python analyse_skript.py %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1.  **Validierung:** Das Skript überprüft Argumente, Ordnerstruktur und die Pfade zu Siegfried/ClamAV.
2.  **Brunnhilde-Ausführung:** Brunnhilde analysiert das `Files`-Verzeichnis. Die Ausgabe erfolgt in einen `Brunnhilde_[Datenträger-ID]`-Ordner.
3.  **Tree-Workaround:** Das Skript erzeugt manuell eine `tree.txt`, falls Brunnhilde dies unter Windows überspringt.
4.  **Parsing:** Die CSV-Berichte von Brunnhilde werden eingelesen.
5.  **JSON-Erstellung:** Zusammenfassung der Ergebnisse (Formate, MIME-Typen, Warnungen, Virenfunde) in einer JSON-Datei.
6.  **Finalisierung:** Die JSON-Datei und die `tree.txt` werden mit standardisierten Namen in das Zielverzeichnis verschoben.
7.  **Abschluss:** Das Skript bietet an, den Zielordner im Datei-Explorer zu öffnen.

### Generierte Berichte

Nach Abschluss befinden sich im Ordner `2_[Datenträger-ID]_extracted-files` folgende Berichte:

*   **`Brunnhilde_[Datenträger-ID]`**: Der vollständige Detail-Berichtsordner.
*   **`2_[Datenträger-ID]_Brunnhilde_output.json`**: Die strukturierte JSON-Zusammenfassung.
*   **`2_[Datenträger-ID]_extracted-Files-Tree.txt`**: Die vollständige Verzeichnisstruktur als Textdatei.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT