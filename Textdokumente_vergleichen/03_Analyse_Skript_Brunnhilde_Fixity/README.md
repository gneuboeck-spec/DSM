# 03 - Analyse-Skript (Brunnhilde & Fixity)

Dieses Skript nutzt das Tool **Brunnhilde** (in Kombination mit Siegfried und ClamAV), um eine tiefgehende Analyse des Dateibestands durchzuführen. Es ist entscheidend, um festzustellen, wie viele *echte* Textdokumente in einem Nachlass vorhanden sind, im Gegensatz zu reinen Metadaten- oder Systemdateien.

Eine Besonderheit ist die Live-Überwachung des Virenscanners: Sollten die Virendefinitionen älter als 7 Tage sein, öffnet das Skript automatisch ein Administrator-Fenster für das ClamAV-Update (`freshclam.exe`) und lässt die laufende Analyse parallel weiterlaufen.

## Struktur

    03_Analyse_Skript_Brunnhilde_Fixity/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- 03_Analyse_Skript_Brunnhilde_Fixity.py   <-- Ausführbare Python-Datei

## Funktionsweise

1. **Fixity-Check**: Berechnet SHA-256-Prüfsummen für alle Dateien zur Sicherstellung der Integrität.
2. **Virenscan**: Führt einen ClamAV-Scan durch (mit automatischer Warnung bei veralteten Virendefinitionen).
3. **Format-Identifikation**: Nutzt Siegfried, um den wahren Dateityp (unabhängig von der Dateiendung) zu ermitteln.
4. **Berichterstellung**: Generiert einen `tree.txt` (Verzeichnisstruktur) und eine zusammenfassende JSON-Datei direkt im Berichtsordner.
5. **Konsolidierung**: Verschiebt den kompletten Brunnhilde-Berichtsordner in das gewählte Ausgabeverzeichnis.

## TREE-Struktur & Dateipfade

Das Skript arbeitet mit zwei vom Menü übergebenen Verzeichnissen: dem Quellverzeichnis (zu analysierende Dateien) und dem Ausgabeverzeichnis (Ablage der Berichte).

    [Quellverzeichnis]/
    `-- ... (zu analysierende Dateien)

    [Ausgabeverzeichnis]/
    |-- <Quellordnername>_collection_report/        <-- Finaler Brunnhilde-Bericht
    |   |-- tree.txt                                <-- Verzeichnisstruktur
    |   |-- <Quellordnername>_brunnhilde-summary.json  <-- Zusammenfassung (SHA-256, Formate, Viren)
    |   |-- csv_reports/                            <-- CSV-Detailberichte
    |   `-- virus_scan_log.txt                      <-- ClamAV-Protokoll
    `-- ... (weitere Dateien)

**Hinweis:** Falls das Ausgabeverzeichnis innerhalb des Quellverzeichnisses liegt, leitet das Skript den temporären Brunnhilde-Arbeitsordner automatisch nach `<Quellordner>_Brunnhilde_Reports/` um – damit Brunnhilde nicht seine eigenen Ausgabedateien scannt.

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Python-Paket:** `brunnhilde` (im benutzten Interpreter; Installation: `pip install brunnhilde`)
- **Siegfried** (`sf.exe`) – wird zur Laufzeit über `shutil.which("sf")` im PATH gesucht. Falls nicht gefunden, greift der Fallback-Pfad `C:\Program Files\Siegfried`.
- **ClamAV** (`clamscan.exe`) – wird zur Laufzeit über `shutil.which("clamscan")` im PATH gesucht. Falls nicht gefunden, greift der Fallback-Pfad `C:\Program Files\ClamAV`.

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

Zusätzlich prüft das Skript beim Aufruf von Brunnhilde selbst, ob das verwendete Python das Paket `brunnhilde` importieren kann. Falls nicht, werden die bekannten Installationspfade (`C:\Program Files\Python313\python.exe` und `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`) durchprobiert.

## Konfiguration im Skript

Die Pfade zu Siegfried und ClamAV werden zur Laufzeit automatisch ermittelt:

1. **Zuerst** wird das Tool über `shutil.which()` im System-PATH gesucht.
2. **Falls nicht gefunden**, greift der Fallback-Pfad (`C:\Program Files\Siegfried` bzw. `C:\Program Files\ClamAV`).

Eine Anpassung im Skript ist nur dann nötig, wenn Sie die Tools an einem anderen Ort installiert haben und sie *nicht* im PATH eingetragen sind. In diesem Fall können die Fallback-Pfade in den Zeilen

    SIEGFRIED_DIR = find_executable_dir("sf", r"C:\Program Files\Siegfried")
    CLAMAV_DIR = find_executable_dir("clamscan", r"C:\Program Files\ClamAV")

angepasst werden.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `T` eingeben (Textdokumente_vergleichen)
3. Im Dialog Eingabeverzeichnis (Quelle) und Ausgabeverzeichnis (Berichte) wählen
4. Im Menü das Skript `03_Analyse_Skript_Brunnhilde_Fixity.py` auswählen

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "03_Analyse_Skript_Brunnhilde_Fixity.py" "<quellverzeichnis>" "<ausgabeverzeichnis>"

**Beispiel:**

    python "03_Analyse_Skript_Brunnhilde_Fixity.py" "C:\Daten\MeineSammlung" "C:\Daten\Reports"

## Ablauf der Ausführung

1. **Validierung:** Prüfung der Argumente, der Verzeichnisse sowie der Existenz von `sf.exe` und `clamscan.exe`.
2. **SHA-256 Hashing:** Erstellt Prüfsummen für alle Dateien im Quellverzeichnis.
3. **Brunnhilde-Ausführung:** Analyse der Dateiformate und Echtzeit-Überwachung des ClamAV-Status. Bei veralteten Signaturen wird automatisch ein Administrator-Fenster für `freshclam.exe` geöffnet.
4. **Tree-Workaround:** Manuelle Erstellung der `tree.txt` innerhalb des Berichtsordners über `cmd /c tree`.
5. **Parsing & JSON:** Zusammenfassung der CSV-Ergebnisse (Formate, Warnungen, Viren) in der zentralen JSON-Datei.
6. **Finalisierung:** Verschieben des kompletten Berichtsordners in das Ausgabeverzeichnis.
7. **Abschluss:** Optionale Abfrage, ob der Zielordner im Windows Explorer geöffnet werden soll.

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Eingabestruktur

Das Skript benötigt ein Quellverzeichnis mit zu analysierenden Dateien (rekursiv) und ein Ausgabeverzeichnis für die Berichte. Beide müssen existieren.

### Fehlerfälle und Abbruchbedingungen

Das Skript prüft beim Start:

- Existenz von Quell- und Ausgabeverzeichnis
- `sf.exe` im ermittelten Siegfried-Verzeichnis
- `clamscan.exe` im ermittelten ClamAV-Verzeichnis
- Fehlende Argumente führen zu einer Fehlermeldung und Beenden.

Bei Fehlern erscheint eine Meldung, das Skript wird beendet.

### Live-Überwachung des ClamAV-Status

Das Skript überwacht die Ausgabe von Brunnhilde **zeilenweise** auf die Zeichenkette `"older than 7 days"` (Groß-/Kleinschreibung wird ignoriert). Sobald diese Zeile erscheint, wird über `ShellExecuteW` mit dem Verb `runas` ein separates Administrator-Fenster geöffnet, das `freshclam.exe` ausführt. Der laufende Scan wird dabei **nicht** unterbrochen.

### SHA-256-Fehlerbehandlung

`calculate_sha256()` fängt alle Ausnahmen ab und schreibt dann `f"Error: {str(e)}"` in das SHA-256-Feld. Im JSON erscheint also kein korrekter Hash, sondern ein Fehlertext.

### Aufbau der erzeugten JSON-Datei

Die finale `<Quellordnername>_brunnhilde-summary.json` enthält folgende Felder:

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

Nach Abschluss fragt das Skript per GUI-Dialog: `Möchten Sie den Zielordner öffnen?`. Bei Bestätigung wird `os.startfile(output_dir)` ausgeführt (Windows).

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT