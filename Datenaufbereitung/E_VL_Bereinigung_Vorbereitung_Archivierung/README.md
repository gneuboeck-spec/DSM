# E - VL-Bereinigung (Vorbereitung & Archivierung)

Dieses Skript dient der automatischen Bereinigung von Dateibeständen vor der endgültigen Übergabe in die Langzeitarchivierung (LZA). Es filtert unerwünschte Systemdateien, temporäre Dateien sowie Hilfsdateien aus vorherigen Konvertierungsschritten heraus, um einen sauberen Archivbestand in der VL-Stufe (Stufe 4) zu gewährleisten.

Das Skript ist Teil eines mehrstufigen Workflows und wird über das Menü mit der AC-Nummer und Datenträger-ID gesteuert.

## Struktur

    E_VL_Bereinigung_Vorbereitung_Archivierung/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- E_VL_Bereinigung_Vorbereitung_Archivierung.py   <-- Ausführbare Python-Datei

## Hauptfunktionen

* **Automatischer Datentransfer (Stufe 3 nach Stufe 4):** Das Skript kopiert automatisch den gesamten `files`-Ordner von der Transfer-Stufe (3) in die Bereinigungs-Stufe (4), bevor die Löschvorgänge starten. Ein bestehender Zielordner wird dabei sicherheitshalber vorher entfernt.
* **System-Dateien entfernen:** Automatische Löschung von Windows-spezifischen Dateien wie `Thumbs.db` oder `desktop.ini` sowie versteckten Apple-Ressourcen-Dateien (`._`).
* **Gezielte Extension-Bereinigung:** Löscht rund 180 potenziell unerwünschte Dateitypen (z. B. `.exe`, `.dll`, `.tmp`, `.bak`, `.ini`, `.log`, `.lnk`).
* **Keyword-Filter:** Identifiziert und löscht Dateien, die bestimmte Schlagworte im Namen tragen (z. B. `konvertierungslog`, `bereinigungslog`), um Hilfsberichte aus der VL-Stufe zu entfernen.
* **Bereinigung leerer Ordner:** Entfernt rekursiv alle Verzeichnisse, die nach der Dateibereinigung keine Inhalte mehr enthalten.
* **Detailliertes LZA-Logging:**
  * **Vorschau-Log:** Erstellt vor dem Löschen eine Liste aller identifizierten Elemente.
  * **Final-Log:** Dokumentiert alle tatsächlich gelöschten Dateien und Ordner.
  * Die Logs werden direkt im Verzeichnis der Stufe 5 (LZA) abgelegt, um den Audit-Trail lückenlos zu wahren.

## TREE-Struktur & Dateipfade (Phase 3)

Das Skript synchronisiert Stufe 3 mit Stufe 4 und dokumentiert die Bereinigung in Stufe 5. Der Projektpfad wird vom Menü übergeben (`sys.argv[3]` oder Umgebungsvariable `DATA_PATH`):

    [Projektpfad]/
    |-- 3_[ID]_for-transfer/
    |   `-- files/                              <-- QUELLE (Inhalt wird nach 4 kopiert)
    |-- 4_[ID]_VL/                              <-- ARBEITSBEREICH
    |   `-- files/                              <-- ZIEL (Hier erfolgt die Löschung)
    `-- 5_[ID]_LZA/logfiles/                    <-- LOG-ZIEL (Protokolle)
        |-- 4_[ID]_VL_delete-preview-all.log    <-- Vorschau der Löschkandidaten
        `-- 4_[ID]_VL_delete-all.log            <-- Bestätigung der erfolgten Löschung

## Technische Voraussetzungen

* **Windows 10/11**
* **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
* **Standard-Bibliotheken:** Benötigt keine externen Pakete. Es werden ausschließlich Module der Python-Standardbibliothek genutzt (`os`, `sys`, `shutil`, `subprocess`, `stat`, `collections`, `pathlib`, `datetime`).

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `5` (E_VL_Bereinigung_Vorbereitung_Archivierung) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "E_VL_Bereinigung_Vorbereitung_Archivierung.py" AC_0001 CD_01 "C:\Pfad\zum\Datenordner"

### Ablauf der Ausführung

1. **Datensynchronisation:** Der Ordner `files` wird von Stufe 3 nach Stufe 4 kopiert. Ein bereits existierender Zielordner wird dabei zuvor sicherheitstechnisch entfernt.
2. **Analyse:** Das Skript scannt Stufe 4 nach unerwünschten Elementen.
3. **Vorschau-Logging:** Ein Bericht über die gefundenen Dateien wird im LZA-Logordner gespeichert.
4. **Benutzerabfrage:** Das Skript fordert eine Bestätigung an, bevor die Dateien in der VL-Stufe tatsächlich gelöscht werden (sofern `DRY_RUN` auf `False` steht).
5. **Löschvorgang:** Dateien und anschließend leere Ordner werden gelöscht (mit Fallback für schreibgeschützte Dateien).
6. **Abschluss-Bericht:** Ein finaler Bericht über die gelöschten Elemente wird in Stufe 5 erstellt.
7. **Abschluss:** Optionale Abfrage, ob der VL-Zielordner im Explorer geöffnet werden soll.

## Detaillierte Hinweise zum Skriptverhalten

### Vollständige `DELETE_EXTENSIONS` Liste

Das Skript löscht Dateien mit folgenden Endungen (Groß-/Kleinschreibung wird ignoriert):

`.001`, `.030`, `.2gr`, `.3gr`, `.abk`, `.acl`, `.acm`, `.acs`, `.agd`, `.alt`, `.ani`, `.ann`, `.ax`, `.bak`, `.bat`, `.bin`, `.bmt`, `.bof`, `.bpl`, `.cab`, `.cal`, `.cat`, `.cbd`, `.cb`, `.cbk`, `.cfg`, `.chk`, `.chl`, `.chm`, `.chw`, `.class`, `.clb`, `.clp`, `.cnt`, `.cnf`, `.cnv`, `.com`, `.cov`, `.cpe`, `.cpi`, `.cpl`, `.cpx`, `.crd`, `.crl`, `.cur`, `.ctx`, `.dat`, `.db`, `.dbs`, `.dls`, `.ds`, `.dsz`, `.dct`, `.desklink`, `.dfv`, `.dic`, `.dka`, `.dki`, `.dll`, `.dmp`, `.dsc`, `.dr_`, `.drv`, `.p01`, `.ecf`, `.ecw`, `.ess`, `.exc`, `.ass`, `.env`, `.evt`, `.exe`, `.fcs`, `.fi`, `.flg`, `.flt`, `.fnt`, `.fon`, `.for`, `.fot`, `.fsd`, `.fsi`, `.gid`, `.grd`, `.grt`, `.grp`, `.he4`, `.hic`, `.him`, `.hti`, `.hlp`, `.hpm`, `.htt`, `.htx`, `.htz`, `.hyp`, `.icm`, `.ico`, `.id`, `.idf`, `.idx`, `.inf`, `.ini`, `.ink`, `.ins`, `.in2`, `.isr`, `.isu`, `.iwa`, `.job`, `.jpg^`, `.ki`, `.krn`, `.ku4`, `.last`, `.lex`, `.lgo`, `.lib`, `.liveupdate`, `.ld`, `.lnk`, `.log`, `.lst`, `.lwa`, `.m2v`, `.mad`, `.MAPIMail`, `.mdb`, `.ml`, `.ms`, `.msi`, `.msc`, `.msg`, `.mbx`, `.mbox`, `.mod`, `.mtm`, `.mydocs`, `._mp`, `.nch`, `.net`, `.nls`, `.nt`, `.ns`, `.olb`, `.old`, `.ocx`, `.osd`, `.ovl`, `.pal`, `.par`, `.p02`, `.p03`, `.pbk`, `.pci`, `.pco`, `.pdr`, `.pgm`, `.pfm`, `.pfb`, `.pif`, `.pip`, `.pkg`, `.plx`, `.pnf`, `.pol`, `.pr4`, `.pro`, `.prx`, `.ps2`, `.ptm`, `.pwl`, `.qlc`, `.qdat`, `.qtp`, `.qtr`, `.qts`, `.qtx`, `.ra4`, `.rat`, `.rbk`, `.reg`, `.rle`, `.rsc`, `.sav`, `.sca`, `.scn`, `.scf`, `.scr`, `.sdw`, `.set`, `.sf0`, `.sfc`, `.shx`, `.sik`, `.skp`, `.sob`, `.spd`, `.swx`, `.sys`, `.sdb`, `.sig`, `.slt`, `.smm`, `.sol`, `.spc`, `.ss`, `.stb`, `.stt`, `.sts`, `.str`, `.sty`, `.syd`, `.tab`, `.t`, `.tbs`, `.temp`, `.tbl`, `.ths`, `.tlb`, `.tmp`, `.tsc`, `.tsk`, `.ttf`, `.ttx`, `.tsp`, `.tys`, `.tyq`, `.uce`, `.url`, `.umb`, `.utf`, `.vbx`, `.vid`, `.vue`, `.vxd`, `.wab`, `.wa~`, `.wbm`, `.wlx`, `.wof`, `.w31`, `.xml.pdf`, `.x32`, `.000`, `.386`

### Vollständige `DELETE_KEYWORDS` Liste

Dateien werden gelöscht, wenn ihr Name (in Kleinbuchstaben) eines der folgenden Schlüsselwörter enthält:

`video_konvertierung`, `konvertierungslog`, `konvertierungslog_praesentation_tabelle`, `konvertierungslog_html_mht`, `bereinigungslog`

### `SYSTEM_HIDDEN_FILES` Liste

Folgende Dateien werden immer gelöscht (exakter Name, Groß-/Kleinschreibung egal):

`Thumbs.db`, `desktop.ini`

### Zusätzliche Löschkriterien (hart codiert)

Dateien werden gelöscht, wenn sie:
- mit `._` beginnen (z. B. `._Dokument.docx`)
- mit `~` beginnen (z. B. `~tempfile.tmp`)
- mit `.` beginnen – **ABER nicht**, wenn der genaue Name `.git` oder `.gitignore` ist (diese bleiben erhalten).

### Leere Ordner

Nach der Dateilöschung werden **alle leeren Ordner** rekursiv gelöscht. Die Prüfung erfolgt mit `os.listdir()`. Fehler beim Auslesen werden ignoriert (`pass`).

### Simulationsmodus (`DRY_RUN`)

Im Skript existiert die globale Variable `DRY_RUN = False`. Bei `DRY_RUN = True`:
- Es erfolgt **keine** tatsächliche Löschung.
- Es erfolgt **keine** Bestätigungsabfrage.
- Das Vorschau-Log wird trotzdem erstellt.
- Das Final-Log enthält die simulierten Löschungen (nicht die tatsächlichen).

### Vorschau-Log vs. Final-Log

| Log | Inhalt | Wann erstellt |
|-----|--------|---------------|
| `*_delete-preview-all.log` | Alle identifizierten Löschkandidaten (vor der Bestätigung) | **Immer** (wenn `CREATE_LOG_FILE = True`) |
| `*_delete-all.log` | Tatsächlich gelöschte Elemente (nach Bestätigung) | Nur nach erfolgreicher Löschung |

Beide Logs enthalten:
- Zusammenfassung nach Dateiendungen (sortiert nach Häufigkeit)
- Detaillierte Liste aller betroffenen Dateien (sortiert)
- Detaillierte Liste aller gelöschten leeren Ordner (sortiert)

### Benutzerabfrage vor Löschung

Das Skript fragt vor dem Löschen: `Möchten Sie den Löschvorgang in der VL-Stufe wirklich starten? (j/n):`
- Nur bei `j` wird gelöscht.
- Bei `n` oder anderer Eingabe bricht das Skript ab.

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| Quell-Ordner Stufe 3 existiert nicht | rote Fehlermeldung + `sys.exit(1)` |
| Kopiervorgang schlägt fehl | rote Fehlermeldung + `sys.exit(1)` |
| Log-Ordner in Stufe 5 kann nicht erstellt werden | rote Fehlermeldung + `return None` → Skriptabbruch |
| Einzelne Datei kann nicht gelöscht werden | Fehlermeldung im Terminal, Datei wird übersprungen, Skript fährt fort |
| Einzelner leerer Ordner kann nicht gelöscht werden | Fehlermeldung im Terminal, Ordner wird übersprungen, Skript fährt fort |

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `VL-Zielordner oeffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(str(destination_folder))`
- **macOS** → `subprocess.run(["open", str(destination_folder)])`
- **Linux/andere** → `subprocess.run(["xdg-open", str(destination_folder)])`

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT