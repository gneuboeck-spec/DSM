# 01_Dateiendungen_reparieren.py

## 📋 Beschreibung

Dieses Python-Skript repariert verlorene oder fehlende Dateiendungen in einem Verzeichnis. Es analysiert die Magic Bytes (binäre Signatur) jeder Datei mithilfe von Siegfried (PRONOM-Register) und weist ihr die korrekte Dateiendung zu. Falls Siegfried keine eindeutige Zuordnung liefern kann, greifen verschiedene Fallback-Methoden (ZIP-Struktur-Analyse, MIME-Typ-Erkennung, Markdown-Syntax-Erkennung, CSV-Strukturprüfung).

Das Skript ist in eine menu.py-Arbeitsumgebung integriert und wird über eine Batch-Datei (start.bat) gestartet. Es erwartet zwei Verzeichnisse als Eingabe:
- Eingabeverzeichnis: Wird rekursiv nach Dateien ohne Endung durchsucht und direkt bearbeitet.
- Ausgabeverzeichnis: Dient ausschließlich zur Ablage der Log-Datei.

---

## ✨ Funktionen

- 🔍 Rekursive Suche nach Dateien ohne Dateiendung im Eingabeverzeichnis
- 🧬 Magic-Bytes-Analyse via Siegfried (PRONOM-Register)
- 📦 ZIP-Struktur-Analyse zur Unterscheidung von ODT/ODS/ODP und DOCX/XLSX/PPTX
- 📄 Flat-XML-Erkennung (FODT, FODS, FODP)
- 📝 Markdown-Erkennung durch Analyse typischer Syntax-Elemente
- 📊 Strenge CSV-Erkennung (verhindert Falscherkennung von Textdateien)
- 🎬 Video/Audio-Unterscheidung bei MPEG-4-Dateien via ffprobe
- 🗑️ Automatische Löschung von Windows-Systemdateien ohne archivischen Wert (z. B. IndexerVolumeGuid)
- 🎨 Farbige Konsolenausgabe mit gleichzeitig sauberer Log-Datei
- 🧪 Dry-Run-Modus zum gefahrlosen Testen

---

## 🛠️ Voraussetzungen

### Software
- Python 3.10+ (getestet mit Python 3.13)
- Siegfried (sf.exe) – installiert unter C:\Program Files\Siegfried\sf.exe
  Download: https://github.com/richardlehane/siegfried
- FFmpeg / ffprobe – muss im System-PATH verfügbar sein
  Download: https://ffmpeg.org/download.html

### Python-Module
Das Skript verwendet ausschließlich Standardbibliotheken – es sind keine zusätzlichen pip install-Befehle erforderlich:
os, subprocess, json, sys, mimetypes, shutil, logging, argparse, zipfile, re, pathlib, datetime

---

## 📦 Installation

1. Siegfried installieren
   sf.exe nach C:\Program Files\Siegfried\sf.exe kopieren

2. FFmpeg installieren
   ffprobe.exe in einen Ordner legen, der im System-PATH liegt (z. B. C:\Program Files\FFmpeg\bin)

3. Skript ablegen
   01_Dateiendungen_reparieren.py in denselben Ordner wie menu.py und start.bat legen

4. Arbeitsumgebung starten
   start.bat ausführen → menu.py startet automatisch

---

## 🚀 Verwendung

### Über die menu.py (empfohlen)
1. start.bat ausführen
2. Im Dialog Eingabeverzeichnis wählen (Ordner mit Dateien ohne Endung)
3. Im Dialog Ausgabeverzeichnis wählen (Ordner für Log-Dateien)
4. Im Menü das Skript 01_Dateiendungen_reparieren.py auswählen (Nummer eingeben)
5. Das Skript arbeitet direkt im Eingabeverzeichnis und schreibt die Log-Datei ins Ausgabeverzeichnis

### Direkt über die Kommandozeile

    python 01_Dateiendungen_reparieren.py <eingabe_verzeichnis> <ausgabe_verzeichnis> [--dryrun]

Beispiel:

    python 01_Dateiendungen_reparieren.py "C:\Users\digit\Desktop\Testdaten" "C:\Users\digit\Desktop\Logfiles"

### Dry-Run-Modus
Mit dem Flag --dryrun werden alle Änderungen nur simuliert – es werden keine Dateien umbenannt oder gelöscht:

    python 01_Dateiendungen_reparieren.py "C:\Eingabe" "C:\Ausgabe" --dryrun

---

## 🔬 Wie es funktioniert

Das Skript durchläuft für jede Datei ohne Endung folgende Entscheidungshierarchie:

### 1. Siegfried-Analyse (PRONOM)
- Aufruf von sf.exe -json <datei>
- Auswertung der PRONOM-ID, des MIME-Typs und des Formatnamens
- Anwendung der manuellen pronom_to_ext_map-Zuordnung

### 2. Spezielle Korrekturen
- ODT vs. ODS vs. ODP: Bei PRONOM-IDs fmt/290, fmt/291, fmt/292 wird die ZIP-Struktur geprüft (Inhalt der mimetype-Datei im ZIP-Archiv)
- MPEG-4: Bei fmt/199 wird mit ffprobe geprüft, ob ein Video-Stream vorhanden ist → .mp4 oder .m4a
- XML-Dateien: Bei MIME-Typ application/xml wird zuerst auf Flat-OpenDocument-Struktur (FODT/FODS/FODP) geprüft
- Text-Dateien: Bei MIME-Typ text/plain wird zuerst auf Markdown-Syntax geprüft

### 3. Fallback-Methoden (falls Siegfried keine Zuordnung liefert)
1. ZIP-Struktur: Prüfung auf mimetype-Datei (OpenDocument) oder Ordner wie word/, xl/, ppt/ (Office Open XML)
2. Flat XML: Analyse des XML-Headers auf office:mimetype-Attribut
3. CSV-Struktur: Mindestens 5 Zeilen mit jeweils ≥2 konsistenten Trennzeichen (;, ,, \t, |)
4. Markdown-Syntax: Erkennung von Überschriften, Links, Listen, Code-Blöcken etc. (mind. 2 Indikatoren)
5. Plain Text: Fallback auf .txt, wenn die Datei überwiegend druckbare Zeichen enthält

---

## ⚙️ Konfiguration

Alle wichtigen Zuordnungen sind am Anfang des Skripts als Konstanten definiert und können leicht angepasst werden:

### pronom_to_ext_map
Manuelle Zuordnung von PRONOM-IDs zu Dateiendungen. Beispiele:
    "fmt/612": ".docx",   # Office Open XML Document
    "fmt/291": ".odt",    # OpenDocument Text
    "fmt/279": ".flac",   # FLAC Audio

### mime_to_ext_map
Korrigierte MIME-Typ-Zuordnungen für problematische Fälle (z. B. application/xml → .xml statt .xsl).

### SYSTEM_JUNK_FILES
Liste von Dateinamen, die als Windows-Systemdateien ohne archivischen Wert erkannt und gelöscht werden:
    SYSTEM_JUNK_FILES = ["IndexerVolumeGuid"]

---

## 📄 Log-Datei

Das Skript erstellt im Ausgabeverzeichnis eine Log-Datei:
    <ausgabe_verzeichnis>/repair-file-extension.log

Inhalt:
- Zeitstempel aller Aktionen
- Umbenannte Dateien mit Quelle der Erkennung (z. B. PRONOM ID (Manuell), MIME-Typ (korrigiert durch Flat XML))
- Gelöschte Systemdateien
- Nicht zuordenbare Dateien mit Siegfried-Info
- Zusammenfassung am Ende (Anzahl umbenannt/gelöscht/nicht zugeordnet)

Die Konsolenausgabe ist farbig formatiert (grün = INFO, gelb = WARNING, rot = ERROR), die Log-Datei enthält keine ANSI-Codes und ist sauber lesbar.

---

## 📊 Unterstützte Formate (Auszug)

| Kategorie         | Formate                                                              |
|-------------------|----------------------------------------------------------------------|
| Dokumente         | PDF, DOC, DOCX, ODT, RTF, FODT, TXT, MD                              |
| Tabellen          | XLS, XLSX, ODS, FODS, CSV, SLK                                       |
| Präsentationen    | ODP, FODP, PPTX                                                      |
| Bilder            | JPG, PNG, TIF, BMP                                                   |
| Audio             | FLAC, M4A, OGG                                                       |
| Video             | MP4, MKV, MXF, FLV                                                   |
| Spezialformate    | AppleWorks (.cwk), Apple Pages (.pages), Finale (.mus), Ami Pro (.sam), Outlook Express (.dbx), TeX (.tex) |

---

## ⚠️ Wichtige Hinweise

- Das Skript verändert Dateien direkt im Eingabeverzeichnis! Vor der ersten Ausführung sollte ein Backup erstellt werden.
- Dry-Run-Modus (--dryrun) wird für den ersten Test dringend empfohlen.
- Das Ausgabeverzeichnis wird nicht für die bearbeiteten Dateien verwendet – es dient ausschließlich als Speicherort für die Log-Datei.
- Dateien, die nicht zugeordnet werden können, werden nicht umbenannt und im Log als ❓ Nicht zugeordnet markiert.
- Bei mehreren Dateien gleichen Namens nach der Umbenennung wird automatisch ein Zähler angehängt (z. B. datei_1.pdf, datei_2.pdf).

---

## 🐛 Fehlerbehebung

| Problem                              | Lösung                                                              |
|--------------------------------------|---------------------------------------------------------------------|
| Siegfried nicht gefunden             | Prüfen, ob C:\Program Files\Siegfried\sf.exe existiert              |
| ffprobe nicht im PATH                | FFmpeg installieren und bin-Ordner zum System-PATH hinzufügen       |
| Eingabeverzeichnis existiert nicht   | Pfad in der menu.py prüfen                                          |
| Markdown-Datei wird als .txt erkannt | Markdown-Syntax prüfen – es müssen mind. 2 Indikatoren vorhanden sein |

---

## 📝 Autor & Lizenz

- Autor: Gregor Neuboeck (g.neuboeck@gmail.com)
- Jahr: 2025
- Lizenz: MIT License

SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT

---

## 🔄 Versionshistorie

- v1.0 – Erste Version mit PRONOM- und Fallback-Erkennung
- v1.1 – Integration in menu.py-Arbeitsumgebung (Eingabe-/Ausgabeverzeichnis)
- v1.2 – Korrektur der MIME-Typ-Zuordnungen (XML/XSL, Flat XML)
- v1.3 – Strengere CSV-Erkennung, ZIP-Struktur-Analyse für ODT/ODS
- v1.4 – Markdown-Erkennung, Flat-XML-Erkennung (FODT/FODS/FODP)