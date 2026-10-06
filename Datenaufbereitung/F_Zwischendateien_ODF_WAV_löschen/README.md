# F - Bereinigung von Zwischendateien (ODF & WAV)

Dieses Skript dient der gezielten Bereinigung von technischen Zwischendateien in der VL-Stufe (Stufe 4). Es entfernt Derivate, die während des Konvertierungsprozesses lediglich als Brückentechnologie erstellt wurden (z. B. ODF-Dateien als Zwischenschritt zum PDF/A-Export oder WAV-Dateien als Zwischenschritt für MP3), um den Archivbestand schlank und übersichtlich zu halten.

Das Skript ist interaktiv gestaltet und erlaubt es dem Benutzer, gezielt verschiedene Kategorien von Zwischendateien zu löschen.

---

## Hauptfunktionen

* **Interaktives Menü:** Wahlweise Löschung von ODF-Zwischendateien oder konvertierten WAV-Dateien.
* **Intelligente ODF-Bereinigung:** Identifiziert `.odt`, `.ods` oder `.odp` Dateien, die aus alten Office-Formaten (z. B. `.doc`, `.docx`, `.rtf`) erzeugt wurden. Eine Löschung erfolgt nur, wenn die ursprüngliche Quelldatei im selben Verzeichnis noch existiert.
* **WAV-Bereinigung:** Identifiziert `.wav`-Dateien, die aus anderen Audioformaten (z. B. `.mp3`, `.flac`, `.m4a`) generiert wurden, und entfernt diese, sofern das Original vorhanden ist.
* **Sicherheitsmodus (Dry-Run):** Für die ODF-Bereinigung kann ein Testlauf aktiviert werden, der lediglich protokolliert, was gelöscht würde.
* **Zentrales LZA-Logging:** Alle Löschvorgänge werden in Log-Dateien innerhalb des LZA-Verzeichnisses (Stufe 5 / `logfiles`) dokumentiert, um die Revisionssicherheit zu gewährleisten.

---

## TREE-Struktur & Dateipfade

Das Skript scannt die kuratierten Daten in Stufe 4 und dokumentiert den Vorgang in Stufe 5:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 4_[ID]_VL/
│   └── files/                              <-- ARBEITSBEREICH (Eingabe & Löschung)
│       ├── Dokument.doc                    <-- Original (bleibt)
│       ├── Dokument.doc.odt                <-- ARTEFAKT (wird gelöscht)
│       └── Dokument.doc.pdf                <-- Derivat (bleibt)
└── 5_[ID]_LZA/logfiles/                    <-- LOG-ZIEL (Protokolle)
    ├── 4_[ID]_VL_delete-converted-odfs.log <-- Protokoll der ODF-Bereinigung
    └── 4_[ID]_VL_delete-converted-wavs.log <-- Protokoll der WAV-Bereinigung
```

---

## Technische Voraussetzungen

* **Python:** Version 3.10 oder neuer empfohlen.
* **Standard-Bibliotheken:** Nutzt `pathlib`, `os` und `subprocess` (keine externen Pakete erforderlich).

---

## Konfiguration im Skript

Im Header des Skripts kann der Testlauf-Modus global gesteuert werden:

```python
DELETE_ODF_DRY_RUN = False  # Auf True setzen für eine Simulation
```

---

## Ausführung

Das Skript wird im normalen Arbeitsablauf über den zentralen **Workflow Launcher** (`Workflow_Launcher_start.bat`) und das darauf folgende **Auswahlmenü** gestartet. Die benötigten Parameter (AC-Nummer und Datenträger-ID) werden dabei automatisch vom Menü an das Skript übergeben.

Nach dem Start öffnet das Skript ein eigenes interaktives Untermenü, in dem die spezifische Bereinigungsaktion gewählt werden kann.

Für manuelle Tests oder Debugging kann das Skript auch direkt über die Kommandozeile aufgerufen werden. Es erwartet zwei Argumente: die AC-Nummer und die Datenträger-ID.

**Beispiel für einen manuellen Aufruf:**

```bat
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python "F_Zwischendateien_ODF_WAV_löschen.py" %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1. **Validierung:** Das Skript prüft die Pfade in Stufe 4 und stellt sicher, dass der Log-Ordner in Stufe 5 existiert (wird ggf. erstellt).
2. **Menü-Auswahl:** Der Benutzer wählt die gewünschte Aufräum-Aktion (ODF oder WAV).
3. **Analyse:** Das System sucht rekursiv nach Dateien, die dem Muster `Originalname.originalendung.zwischenendung` entsprechen, und prüft die Existenz des Originals.
4. **Bestätigung:** Vor dem tatsächlichen Löschen wird eine Liste der gefundenen Dateien angezeigt.
5. **Löschung & Logging:** Die Dateien werden entfernt und der Vorgang wird mit Zeitstempel in den LZA-Logordner (Stufe 5) geschrieben.

---

## Detaillierte Hinweise zum Skriptverhalten

### Original-Endungen für ODF-Bereinigung

Das Skript löscht `.odt`-Dateien, deren Stammname (ohne `.odt`) auf eine der folgenden Endungen endet (Groß-/Kleinschreibung egal):

`.doc`, `.docx`, `.rtf`, `.wpd`, `.wps`, `.dot`, `.dotx`, `.wbk`

**Erkennungslogik für ODF:**
1. Rekursive Suche nach allen `.odt`-Dateien.
2. `file.stem` ergibt z. B. `dokument.doc` (bei Datei `dokument.doc.odt`).
3. Prüfung, ob dieser Stammname mit einer der Original-Endungen endet.
4. Prüfung, ob die Quelldatei (`file.parent / file.stem`) tatsächlich existiert.
5. Nur wenn beides zutrifft, wird die `.odt`-Datei zur Löschung vorgemerkt.

### Quell-Audio-Endungen für WAV-Bereinigung

Das Skript löscht `.wav`-Dateien, die aus folgenden Audioformaten konvertiert wurden (erkennbar am Dateinamenmuster `name.originalendung.wav`):

`.aiff`, `.flac`, `.ogg`, `.wav`, `.m4a`, `.wma`, `.aac`, `.mp3`

**Erkennungslogik für WAV:**
1. Alle Dateien im Zielordner werden in einen Set `all_found_files` geladen.
2. Für jede `.wav`-Datei wird der Name an `.` gesplittet.
3. Wenn mindestens 3 Teile vorhanden sind (z. B. `song.flac.wav` → `['song', 'flac', 'wav']`).
4. Wird die vorletzte Endung (`.flac`) als `original_ext` interpretiert.
5. Prüfung, ob diese Endung in `SOURCE_AUDIO_EXTENSIONS_FOR_WAV_CLEANUP` enthalten ist.
6. Prüfung, ob die Originaldatei (`".".join(parts[:-1])`, also `song.flac`) im Set `all_found_files` existiert.
7. Nur wenn beides zutrifft, wird die `.wav`-Datei zur Löschung vorgemerkt.

### Interaktives Menü

Das Skript zeigt folgendes Menü an:
```text
========================================
  Wählen Sie eine Aufräum-Aktion:
========================================
  1 - Zwischendateien (ODF) löschen
  2 - Konvertierte WAV-Dateien löschen
  Q - Beenden
========================================
```
Nach jeder abgeschlossenen Aktion muss der Benutzer **Enter drücken**, um zum Menü zurückzukehren.

### Simulationsmodus (nur für ODF)

Die globale Variable `DELETE_ODF_DRY_RUN = False` steuert den Testlauf:
- `True` → Simulation: Keine Löschung, nur Log mit potenziellen Löschkandidaten.
- `False` → Echter Löschvorgang mit Bestätigungsabfrage.

Die WAV-Bereinigung hat **keinen Dry-Run-Modus** (löscht immer nach Bestätigung).

### Bestätigungsabfragen

**ODF-Bereinigung** (bei `DELETE_ODF_DRY_RUN = False`):
```text
Die folgenden ODF-Zwischendateien wurden zur Löschung identifiziert:
  - Pfad/zu/datei.odt

Möchten Sie diese Dateien wirklich löschen? (j/n):
```

**WAV-Bereinigung**:
```text
Die folgenden, durch Konvertierung erstellten WAV-Dateien werden gelöscht:
  - datei.wav

Möchten Sie diese Dateien wirklich löschen? (j/n):
```
Bei `n` oder anderer Eingabe wird der Löschvorgang abgebrochen.

### Log-Dateien

Beide Logs werden im Ordner `5_[ID]_LZA/logfiles/` abgelegt.

**ODF-Log** (`*_delete-converted-odfs.log`):
- Enthält bei Dry-Run: `# Protokoll des TESTLAUFS (keine ODF-Dateien wurden gelöscht)`
- Enthält bei echtem Lauf: `# Protokoll des Aufräumvorgangs (ODF)`
- Aufteilung in: `--- ERFOLGREICH GELÖSCHT ---` und `--- FEHLER BEIM LÖSCHEN ---`

**WAV-Log** (`*_delete-converted-wavs.log`):
- Enthält: `# Protokoll des Aufräumvorgangs (WAV)`
- Aufteilung in: `--- ERFOLGREICH GELÖSCHT ---` und `--- FEHLER BEIM LÖSCHEN ---`

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| VL-Zielordner (Stufe 4) existiert nicht | rote Fehlermeldung + `return None` → Skriptabbruch |
| Log-Ordner in Stufe 5 kann nicht erstellt werden | wird automatisch mit `mkdir(parents=True, exist_ok=True)` erstellt |
| Log-Datei kann nicht geschrieben werden | Fehlermeldung im Terminal, Skript fährt fort |
| Einzelne Datei kann nicht gelöscht werden | Fehlermeldung im Terminal, Datei wird übersprungen, Zähler für Fehler erhöht |

### Plattformabhängiges Öffnen des Zielordners

Nach Verlassen des Menüs (Auswahl `Q`) fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(str(destination_folder))`
- **macOS** → `subprocess.run(["open", str(destination_folder)])`
- **Linux/andere** → `subprocess.run(["xdg-open", str(destination_folder)])`

### Wichtiger Hinweis zum Skript-Ende

Nach dem Verlassen des Menüs und optionalem Öffnen des Zielordners erscheint:
`Drücken Sie Enter, um das Fenster zu schließen.`
Dies verhindert das sofortige Schließen des Konsolenfensters bei Ausführung per Doppelklick.

### Abhängigkeiten

Das Skript verwendet nur Module der Python-Standardbibliothek: `os`, `sys`, `subprocess`, `datetime`, `pathlib`. Keine externen Python-Pakete erforderlich.

---

## Lizenz

Copyright (c) 2025 Florian Lüftner <florian.lueftner@posteo.com>
Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Florian Lüftner
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT