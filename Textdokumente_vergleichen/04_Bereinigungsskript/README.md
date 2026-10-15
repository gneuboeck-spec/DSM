# 04 - Bereinigungsskript

Entfernt automatisch bekannten, inhaltsleeren Dateimüll, der für die literarische Bewertung irrelevant ist und die nachfolgenden Analysen nur verlangsamen würde.

Das Skript arbeitet rein lokal und verwendet ausschließlich die Python-Standardbibliothek (keine externen Tools wie Siegfried oder LibreOffice nötig).

## Struktur

    04_Bereinigungsskript/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- 04_Bereinigungsskript.py       <-- Ausführbare Python-Datei

## Funktionsweise

Das Skript durchsucht das Quellverzeichnis rekursiv und markiert Dateien zur Löschung, wenn sie:

- Bestimmte Dateiendungen haben (z. B. `.tmp`, `.bak`, `.lnk`, `.log`, `.exe`, `.dll`).
- Systemdateien sind (z. B. `Thumbs.db`, `desktop.ini`).
- Bestimmte Schlüsselwörter im Namen enthalten (z. B. `konvertierungslog`, `bereinigungslog`).
- Versteckte Dateien sind (beginnen mit `.` oder `~`, außer `.git` und `.gitignore`).
- macOS-Ressourcen-Dateien sind (beginnen mit `._`).

Zusätzlich werden **leere Ordner** rekursiv entfernt.

Vor der endgültigen Löschung wird eine **Vorschau-Log-Datei** erstellt, und ein GUI-Dialog fordert eine Bestätigung an.

## Konfiguration

Passe die Listen im Konfigurationsbereich an deine spezifischen Bedürfnisse an:

    DRY_RUN = False  # Simulation ohne Löschung
    DELETE_KEYWORDS = ["video_konvertierung", "konvertierungslog", ...]
    SYSTEM_HIDDEN_FILES = ["Thumbs.db", "desktop.ini"]
    DELETE_EXTENSIONS = [".tmp", ".bak", ".lnk", ...]   # Umfangreiche Liste vordefinierter Endungen

## Löschkriterien

### Dateiendungen (`DELETE_EXTENSIONS`)

Das Skript löscht Dateien mit rund 180 Endungen – darunter typische System- und Hilfsdateien wie `.tmp`, `.bak`, `.log`, `.lnk`, `.exe`, `.dll`, `.ini`, `.old`, `.bak`, `.cache`, `.db`, `.msi`, `.msg`, `.mbox` und viele weitere.

### Schlüsselwörter (`DELETE_KEYWORDS`)

Dateien werden gelöscht, wenn ihr Name (in Kleinbuchstaben) eines der folgenden Schlüsselwörter enthält:

`video_konvertierung`, `konvertierungslog`, `konvertierungslog_praesentation_tabelle`, `konvertierungslog_html_mht`, `bereinigungslog`

### System-Dateien (`SYSTEM_HIDDEN_FILES`)

Folgende Dateien werden immer gelöscht (exakter Name, Groß-/Kleinschreibung egal):

`Thumbs.db`, `desktop.ini`

### Zusätzliche Löschkriterien (hart codiert)

Dateien werden gelöscht, wenn sie:

- mit `._` beginnen (macOS-Ressourcen-Dateien)
- mit `~` beginnen (temporäre Dateien)
- mit `.` beginnen – **ABER nicht**, wenn der genaue Name `.git` oder `.gitignore` ist (diese bleiben erhalten).

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Standardbibliothek:** `os`, `sys`, `shutil`, `subprocess`, `stat`, `collections`, `pathlib`, `datetime`, `tkinter`
- **Keine externen Tools oder Python-Pakete erforderlich.**

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

### Über das Menü (empfohlen)

1. `Start.bat` im Root doppelklicken
2. Im Hauptmenü `T` (Textdokumente_vergleichen) eingeben
3. Im Dialog Eingabeverzeichnis (Quelle) und Ausgabeverzeichnis (Logs) wählen
4. Im Menü das Skript `04_Bereinigungsskript.py` auswählen

### Direkt über die Kommandozeile

    python 04_Bereinigungsskript.py <quellverzeichnis> <log_verzeichnis>

**Beispiel:**

    python 04_Bereinigungsskript.py "C:\Daten\MeineSammlung" "C:\Daten\Logs"

### Ablauf

1. Das Skript scannt das Quellverzeichnis rekursiv.
2. Es werden Dateien und leere Ordner identifiziert, die den Löschkriterien entsprechen.
3. Eine **Vorschau-Log-Datei** (`bereinigung_VORSCHAU_*.log`) wird im Log-Verzeichnis erstellt.
4. Ein GUI-Dialog fordert eine Bestätigung an.
5. Nach Bestätigung werden die Dateien gelöscht und ein **finales Log** (`geloeschte_*.log`) wird geschrieben.
6. Auf Wunsch wird das bereinigte Quellverzeichnis geöffnet.

## Log-Dateien

Für Vorschau und Final-Log werden **Text-Log-Dateien** (`.log`) erstellt. Beide enthalten:

- **Kopfzeile:** Datum und Status (Vorschau / Final)
- **Zusammenfassung der Dateitypen:** Liste der Dateiendungen mit Anzahl, absteigend sortiert
- **Detaillierte Liste der Dateien:** Alle betroffenen Dateipfade, alphabetisch sortiert
- **Detaillierte Liste der leeren Ordner:** Alle betroffenen Ordnerpfade, alphabetisch sortiert

**Dateinamen:**

- Vorschau: `bereinigung_VORSCHAU_<Ordnername>_<YYYYMMDD_HHMMSS>.log`
- Final: `geloeschte_<Ordnername>_<YYYYMMDD_HHMMSS>.log`

## Hinweise & Sicherheit

- **Erst Vorschau prüfen!** Vor dem endgültigen Löschen wird immer eine Vorschau-Log-Datei erstellt.
- **`DRY_RUN = True`** führt einen kompletten Testlauf durch, ohne irgendetwas zu löschen. Die Vorschau wird trotzdem erstellt, und das finale Log wird mit den simulierten Löschungen geschrieben.
- **Schreibgeschützte Dateien:** Werden erkannt und ihr Schreibschutz-Attribut wird automatisch entfernt, bevor sie gelöscht werden.
- **Backup empfohlen:** Bei produktiven Läufen vorab ein Backup des Quellverzeichnisses anlegen.
- **Fehlerhafte Dateien:** Einzelne Fehler beim Löschen brechen den Vorgang nicht ab – das Skript fährt mit den nächsten Dateien fort.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT