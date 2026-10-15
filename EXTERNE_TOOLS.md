# Externe Tools & Abhängigkeiten

Diese Datei dokumentiert alle **externen Programme**, die von den Skripten dieser Sammlung aufgerufen werden und **nicht** über `pip` installierbar sind.

Sie ist **kein Ersatz** für die `requirements.txt`. Die Aufteilung ist bewusst:

| Datei | Inhalt | Installation |
|-------|--------|--------------|
| `requirements.txt` | Python-Pakete (pip) | `pip install -r requirements.txt` |
| `EXTERNE_TOOLS.md` | Externe Programme und Interpreter | manuell, siehe unten |

## Referenz-Rechner

Alle Pfad- und Versionsangaben in dieser Datei beziehen sich auf **Rechner A** (Entwicklungs- und Referenzrechner). Neue Rechner sollen bei den externen Tools **denselben Pfaden folgen**, damit die Skripte ohne Anpassung laufen.

---

## Python-Interpreter

| Eigenschaft | Wert |
|-------------|------|
| Version | **3.13.7** |
| Installationspfad (A) | `C:\Users\digit\AppData\Local\Programs\Python\Python313\` |
| Fallback-Pfad (B) | `C:\Program Files\Python313\` |
| Launcher | `py -3.13` |
| Im PATH (A) | nein – `where python` liefert andere Pythons zuerst |

**Wichtig:** Der Interpreter wird **nicht** über einen PATH-Eintrag gefunden, sondern über die Fallback-Kette in den `Start.bat`-Dateien:

1. `C:\Program Files\Python313\python.exe` (systemweite Installation)
2. `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (User-Installation, auf A aktiv)
3. `py -3.13` (Launcher)

Die `Menu.py`-Dateien geben den laufenden Interpreter per `sys.executable` an die Subskripte weiter. Details siehe Root-`README.md`.

---

## Python-Pakete

Alle Python-Pakete (z. B. `lxml`, `requests`, `openpyxl`, `pypdf`, `python-docx`, `PyMuPDF`, `pdfplumber`, `sentence-transformers`, `rapidfuzz`, `tqdm`, `yara-python`, `chardet`, `mutagen`, `bagit`, `colorama`, `brunnhilde`, `hachoir`) sind in der zentralen **`requirements.txt`** gelistet.

Installation:

    pip install -r requirements.txt

Der Befehl verwendet den Interpreter, der im aktuellen Menü läuft. Details siehe Root-`README.md`.

---

## Externe Programme

Alle Programme sind auf **Rechner A im Windows-PATH** eingetragen. Der Aufruf-Name (siehe Tabelle) genügt daher. Auf einem neuen Rechner müssen die Programme ebenfalls im PATH eingetragen sein – oder, wo angegeben, am Fallback-Pfad liegen, den die Skripte automatisch prüfen.

| # | Programm | Aufruf | Pfad auf A | Version | Quelle |
|---|----------|--------|------------|---------|--------|
| 1 | Siegfried | `sf` | `C:\Program Files\siegfried\` | 1.11.9 | <https://github.com/richardlehane/siegfried/releases> |
| 2 | ClamAV | `clamscan` / `freshclam` | `C:\Program Files\ClamAV\` | 1.5.4 | <https://www.clamav.net/downloads> |
| 3 | FFmpeg | `ffmpeg` / `ffprobe` | `C:\Program Files\ffmpeg\` | git-c1dc2e2b7c (2025-09-10, Gyan Build) | <https://ffmpeg.org/download.html> |
| 4 | ImageMagick | `magick` | `C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\` | 7.1.2-3 | <https://imagemagick.org/download/> |
| 5 | Ghostscript | `gswin64c` | `C:\Program Files\gs\gs10.06.0\bin\` | 10.06.0 | <https://ghostscript.com/releases/gsdnld.html> |
| 6 | Inkscape | `inkscape` | `C:\Program Files\Inkscape\bin\` | 1.3.2 | <https://inkscape.org/release/> |
| 7 | LibreOffice | `soffice` | `C:\Program Files\LibreOffice\program\` | 26.2.6.3 | <https://de.libreoffice.org/download/download/> |
| 8 | ExifTool | `exiftool` | `C:\Program Files\ExifTool\` | 13.38 | <https://exiftool.org/> |
| 9 | DbxConv | `DbxConv` | `C:\Program Files\dbxconv\` | 1.3.4 | <https://www.ukrebs-software.de/english/dbxconv/dbxconv.html> |
| 10 | Hachoir | `hachoir-metadata` | `%LOCALAPPDATA%\Programs\Python\Python313\Scripts\` | siehe `requirements.txt` | <https://pypi.org/project/hachoir/> |

### Hinweise zu einzelnen Programmen

**Siegfried** wird von den Skripten A, C, G und K verwendet. Die Skripte suchen ihn erst per `shutil.which("sf")` und fallen dann auf `C:\Program Files\Siegfried\` zurück.

**ClamAV** wird von den Skripten A und D verwendet. Die Skripte suchen `clamscan` erst per `shutil.which()` und fallen dann auf `C:\Program Files\ClamAV\` zurück. `freshclam.exe` liegt im selben Ordner und wird bei veralteten Signaturen aufgerufen.

**FFmpeg/FFprobe** wird von den Skripten C, D, G und K verwendet. Pflicht: **im PATH**.

**ImageMagick, Ghostscript** werden von Skript D verwendet. Pflicht: **im PATH**.

**Inkscape** wird von Skript D verwendet. Fallback-Pfad im Skript: `C:\Program Files\Inkscape\bin\inkscape.exe`. Es liegt außerdem eine eigene `gswin64c.exe` unter `C:\Program Files\Inkscape\bin\` – diese wird **nicht** verwendet; die Skripte nutzen die systemweite Ghostscript-Installation.

**LibreOffice** wird von Skript D sowie den Skripten 01, 02 und 05 des Bereichs `Textdokumente_vergleichen` verwendet. Fallback-Pfad im Skript: `C:\Program Files\LibreOffice\program\soffice.exe`. Es liegt außerdem ein eigenes `python.exe` unter `C:\Program Files\LibreOffice\program\` – dieses wird **nicht** verwendet.

**ExifTool** wird von den Skripten G und K verwendet. Fallback-Pfad: `C:\Program Files\ExifTool\`.

**DbxConv** wird von Skript D verwendet. Pflicht: **im PATH** – kein Fallback-Pfad im Skript. Beim Aufruf über `"C:\Program Files\dbxconv\DbxConv.exe"` ist der Ordner in den PATH einzutragen.

**Hachoir** ist ein Grenzfall: Es ist als Python-Paket (`hachoir`) in `requirements.txt` gelistet, stellt aber gleichzeitig das Kommando `hachoir-metadata` bereit, das die Skripte G und K direkt aufrufen. Nach `pip install -r requirements.txt` liegt `hachoir-metadata.exe` im `Scripts\`-Ordner des verwendeten Python-Interpreters. Dieses Verzeichnis muss im PATH sein.

---

## Nicht in dieser Datei: YARA

**YARA** wird von den Skripten G und K als **Python-Paket** (`yara-python`) verwendet – also über `import yara`. Die offiziellen YARA-Binaries (`yara.exe`, `yarac64.exe`, z. B. unter `C:\Program Files\YARA\`) werden von den Skripten **nicht** aufgerufen. Falls YARA-Binaries auf einem Rechner installiert sind, ist das kein Fehler – sie sind für die Skripte aber nicht erforderlich.

Die Regeldatei `rules.yar` liegt im Skript-Ordner selbst und wird dynamisch über `SCRIPT_DIR` gefunden.

---

## Aufsetzen auf einem neuen Rechner

Empfohlene Reihenfolge:

1. **Python 3.13 installieren** – systemweit unter `C:\Program Files\Python313\` **oder** user-spezifisch unter `%LOCALAPPDATA%\Programs\Python\Python313\`. Die `Start.bat`-Fallback-Kette findet beides.
2. **`pip install -r requirements.txt`** mit dem installierten Interpreter.
3. **Git installieren** – für die Repo-Verwaltung.
4. **Externe Programme installieren** – gemäß der Tabelle oben. Wenn möglich, dieselben Versionen und Pfade wie auf Rechner A. Alle Programme, deren Aufruf in der Spalte „Aufruf" steht, müssen im **PATH** liegen.
5. **Neue Konsole öffnen** – PATH-Änderungen werden erst in neuen Sitzungen wirksam.
6. **`git-sync.bat` ausführen** – um den aktuellen Stand vom Server zu holen.
7. **Optional: `setup-check.bat` ausführen** – prüft, welche der externen Tools auf diesem Rechner fehlen.
8. **`Start.bat` doppelklicken** – und die Bereiche testen.

---

## Prüfen, ob ein Programm gefunden wird

In der Eingabeaufforderung:

    where sf
    where clamscan
    where ffmpeg
    where ffprobe
    where magick
    where gswin64c
    where inkscape
    where soffice
    where exiftool
    where hachoir-metadata
    where DbxConv

Jedes Programm, das gefunden wird, gibt seinen vollständigen Pfad aus. Fehlt eines, wird es nicht aufgelistet.

---

## Was passiert, wenn ein Programm fehlt

Die Skripte prüfen ihre externen Abhängigkeiten beim Start. Fehlt ein Programm, wird es mit einer klaren Fehlermeldung quittiert – z. B.

    Fehler: Die folgenden benötigten Programme wurden nicht gefunden:
    - DbxConv.exe

    Bitte installieren Sie die Programme und/oder fügen Sie deren Ordner zum Windows PATH hinzu.

Die Installation ist dann wie in der Tabelle oben beschrieben nachzuholen. Nach einer PATH-Änderung muss die Konsole neu geöffnet werden.

---

## Änderungshistorie

Wenn ein neues externes Tool in einem Skript hinzukommt, wird es **hier** nachgetragen – nicht in der `requirements.txt`.