# A - Analyse-Skript (Brunnhilde & Fixity)

Dieses Skript automatisiert die Analyse von Dateisammlungen mithilfe des digitalen Archivierungs-Tools Brunnhilde. Es berechnet kryptografische Prüfsummen (SHA-256), integriert Siegfried zur Dateiformat-Identifikation und nutzt optional ClamAV für Virenscans.

Eine Besonderheit ist die Live-Überwachung des Virenscanners: Sollten die Virendefinitionen älter als 7 Tage sein, öffnet das Skript automatisch ein Administrator-Fenster für das ClamAV-Update (`freshclam.exe`) und lässt die laufende Analyse parallel weiterlaufen.

## Struktur

    A_Analyse_Skript_Brunnhilde_Fixity/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- A_Analyse_Skript_Brunnhilde_Fixity.py   <-- Ausführbare Python-Datei

## Hauptfunktionen

* **Vollständige Automatisierung:** Führt den gesamten Analyseprozess von Brunnhilde mit einem einzigen Befehl aus.
* **SHA-256 Fixity-Check:** Berechnet automatisch SHA-256 Prüfsummen für alle Dateien im Quellverzeichnis und bettet diese direkt in den JSON-Bericht ein.
* **Live-Virenschutz-Check:** Überwacht den Status von ClamAV während der Ausführung. Bei veralteten Signaturen (> 7 Tage) öffnet sich automatisch ein Administrator-Fenster für `freshclam.exe`; die laufende Analyse wird nicht unterbrochen.
* **Dynamische Tool-Suche:** Siegfried und ClamAV werden zur Laufzeit im System-PATH gesucht (`shutil.which`). Falls nicht gefunden, greift ein Fallback-Pfad.
* **Dynamische Pfad-Konfiguration:** Alle Projektpfade werden zur Laufzeit basierend auf AC-Nummer, Datenträger-ID und dem vom Menü übergebenen Datenpfad generiert.
* **Zusammenfassender Bericht:** Erstellt eine strukturierte JSON-Datei, die alle wichtigen Ergebnisse (Hashes, Formate, Warnungen, Virenfunde) bündelt.
* **Windows-Optimierung:** Enthält Workarounds für die manuelle Erstellung der `tree.txt`-Datei unter Windows (CMD-basiert).

## TREE-Struktur & Dateipfade

Das Skript erwartet die Datenstruktur unterhalb des vom Menü übergebenen Datenpfads. Die Ergebnisse werden im Extraktions-Ordner (Stufe 2) abgelegt:

    [AC-Nummer]/[Datenträger-ID]/
    `-- 2_[Datenträger-ID]_extracted-files/
        |-- files/                                  <-- QUELLE (Eingabe: Zu analysierende Dateien)
        |   `-- ... (Ihre Nutzdaten)
        |-- 2_[ID]_extracted-files_brunnhilde/      <-- DETAIL-BERICHTE (Brunnhilde Output-Ordner)
        |-- 2_[ID]_extracted-files_brunnhilde-summary.json <-- ZIEL (Zentrale Hash- & Formatliste)
        `-- 2_[ID]_extracted-files_tree.txt         <-- ZIEL (Verzeichnisstruktur)

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Python-Paket:** `brunnhilde` (`pip install brunnhilde`) im benutzten Python-Interpreter
- **Siegfried** (identifiziert Dateiformate via PRONOM) – Ordner im System-PATH oder unter dem Fallback-Pfad `C:\Program Files\Siegfried`
- **ClamAV** (Virenscan) – Ordner im System-PATH oder unter dem Fallback-Pfad `C:\Program Files\ClamAV`

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

## Konfiguration im Skript

Die Pfade zu Siegfried und ClamAV werden zur Laufzeit automatisch ermittelt:

1. **Zuerst** wird das Tool über `shutil.which()` im System-PATH gesucht.
2. **Falls nicht gefunden**, greift der Fallback-Pfad (`C:\Program Files\Siegfried` bzw. `C:\Program Files\ClamAV`).

Eine Anpassung im Skript ist damit nur dann nötig, wenn Sie die Tools an einem anderen Ort installiert haben und sie *nicht* im PATH eingetragen sind. In diesem Fall können die Fallback-Pfade in den Zeilen

    SIEGFRIED_DIR = find_tool_dir("sf", r"C:\Program Files\Siegfried")
    CLAMAV_DIR = find_tool_dir("clamscan", r"C:\Program Files\ClamAV")

angepasst werden.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

Zusätzlich prüft das Skript beim Aufruf von Brunnhilde selbst, ob das verwendete Python das Paket `brunnhilde` importieren kann. Falls nicht, werden die bekannten Installationspfade (`C:\Program Files\Python313\python.exe` und `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`) durchprobiert.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `1` (A_Analyse_Skript_Brunnhilde_Fixity) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript auch direkt über die Kommandozeile aufgerufen werden:

    python "A_Analyse_Skript_Brunnhilde_Fixity.py" AC_12345 ID_001 "C:\Pfad\zum\Datenordner"

### Ablauf der Ausführung

1. **Validierung:** Prüfung von Argumenten, Ordnern sowie der Existenz von `sf.exe` und `clamscan.exe`.
2. **SHA-256 Hashing:** Erstellt Prüfsummen für alle Dateien im Ordner `files/`.
3. **Brunnhilde-Ausführung:** Analyse der Dateiformate und Echtzeit-Überwachung des ClamAV-Status. Bei veralteten Signaturen wird automatisch ein Administrator-Fenster für `freshclam.exe` geöffnet.
4. **Tree-Workaround:** Manuelle Erstellung der `tree.txt` innerhalb des Berichtsordners über `cmd /c tree`.
5. **Parsing & JSON:** Zusammenfassung der CSV-Ergebnisse (Formate, Warnungen, Viren) in der zentralen JSON-Datei.
6. **Finalisierung:** Verschieben der `tree.txt` in die übergeordnete Ebene (`2_[ID]_extracted-files`).
7. **Abschluss:** Optionale Abfrage, ob der Zielordner im Windows Explorer geöffnet werden soll.

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Eingabestruktur (streng erforderlich)

Das Skript setzt zwingend folgende Ordnerstruktur voraus. Die zu analysierenden Dateien MÜSSEN bereits in `files/` liegen:

    [Datenpfad]/2_[Datenträger-ID]_extracted-files/files/
      `-- (Ihre zu analysierenden Dateien und Unterordner)

Fehlt dieses `files/`-Verzeichnis oder ist es leer, bricht das Skript mit einer Fehlermeldung ab.

### Fehlerfälle und Abbruchbedingungen

Das Skript prüft beim Start:
- Existenz von `files/` und dem übergeordneten `…_extracted-files/`
- `sf.exe` im ermittelten Siegfried-Verzeichnis
- `clamscan.exe` im ermittelten ClamAV-Verzeichnis

Bei Fehlern erscheint eine rote Fehlermeldung, das Skript wird beendet.

### Temporäres Verzeichnis für Brunnhilde

Wenn in der Funktion `extract_brunnhilde_info` der Parameter `brunnhilde_output_dir` leer ist oder `None`, erzeugt das Skript ein temporäres Verzeichnis (mit `tempfile.mkdtemp`). Dieses wird nach der Analyse **automatisch gelöscht**. Der Regelfall (aus `setup_and_validate_analysis_paths`) verwendet jedoch ein festes Verzeichnis.

### Pfad-Erweiterung für Brunnhilde

Brunnhilde wird mit erweiterter Umgebungsvariable `PATH` aufgerufen: Die Ordner von Siegfried und ClamAV werden vorne an `PATH` angehängt. Dadurch findet Brunnhilde die Kommandozeilenwerkzeuge, auch wenn sie nicht systemweit installiert sind.

### Exakter ClamAV-Live-Check

Das Skript überwacht die Ausgabe von Brunnhilde **zeilenweise** auf die Zeichenkette `"older than 7 days"` (Groß-/Kleinschreibung wird ignoriert). Sobald diese Zeile erscheint, wird über `ShellExecuteW` mit dem Verb `runas` ein separates Administrator-Fenster geöffnet, das `freshclam.exe` ausführt. Der laufende Scan wird dabei **nicht** unterbrochen.

### SHA-256-Fehlerbehandlung

`calculate_sha256()` fängt alle Ausnahmen ab und schreibt dann `f"Error: {str(e)}"` in das SHA-256-Feld. Im JSON erscheint also kein korrekter Hash, sondern ein Fehlertext.

### Aufbau der erzeugten JSON-Datei

Die finale `*-summary.json` enthält folgende Felder:

| Feld | Inhalt |
|------|--------|
| `file_fixity_sha256` | Liste von `{"file": "relativer Pfad", "sha256": "Hash oder Fehlertext"}` |
| `brunhilde_format_summary` | JSON-String des `formats.csv` von Brunnhilde |
| `brunhilde_mime_type_summary` | JSON-String des `mimetypes.csv` |
| `structured_siegfried_warnings` | Dictionary: Dateipfad → Liste der Warnungszeilen aus `siegfried_warnings.csv` |
| `structured_unidentified_files` | Liste der Dateipfade aus `unidentified.csv` |
| `brunhilde_clamav_infected_files` | Anzahl infizierter Dateien (als String) aus `virus_scan_log.txt` |
| `brunhilde_clamav_virus_details` | JSON-String der Liste `[Datei, Virusname]` (nur wenn Infizierte > 0) |
| `brunhilde_clamav_status` | Nur wenn kein Log gefunden: `"Kein virus_scan_log.txt gefunden."` |

### Manuelle `tree.txt`-Erstellung (Windows)

Das Skript verwendet nicht `tree.exe` direkt, sondern `cmd /c tree "…" /A /F > "tree.txt"`. Dies wird unabhängig vom Erfolg von Brunnhilde ausgeführt. Falls der Befehl fehlschlägt, erscheint eine Warnung, das Skript wird aber **fortgesetzt**.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n)`. Bei `j`:
- **Windows** → `os.startfile(destination_folder)`
- **macOS** → `open`
- **Linux/andere** → `xdg-open`

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT