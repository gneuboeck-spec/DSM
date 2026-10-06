# C_Reparatur_von_Dateiendungen.py

## 📋 Beschreibung

Dieses Python-Skript repariert verlorene oder fehlende Dateiendungen in einem Verzeichnis. Es analysiert die Magic Bytes (binäre Signatur) jeder Datei mithilfe von Siegfried (PRONOM-Register) und weist ihr die korrekte Dateiendung zu. Falls Siegfried keine eindeutige Zuordnung liefern kann, greifen verschiedene Fallback-Methoden (Magic-Bytes-Erkennung, ZIP-Struktur-Analyse, MusicXML-Signatur, Flat-XML-Erkennung, CSV-Strukturprüfung, Markdown-Syntax-Erkennung).

Das Skript ist in eine Arbeitsumgebung integriert und wird über ein Menü gestartet. Es erwartet eine AC-Nummer und eine Datenträger-ID als Eingabe und arbeitet mit einer fest definierten Ordnerstruktur:
- Stufe 2: 2_{ID}_extracted-files/files (Quelldaten)
- Stufe 3: 3_{ID}_for-transfer/files (Zieldaten, die bearbeitet werden)

Das Skript kopiert automatisch die Dateien von Stufe 2 nach Stufe 3 und führt dort die Reparatur durch.

---

## ✨ Funktionen

- 🔍 Rekursive Suche nach Dateien ohne Dateiendung im Analyse-Ordner
- 🧬 Magic-Bytes-Analyse via Siegfried (PRONOM-Register)
- 🖼️ Magic-Bytes-Erkennung für PSD (Adobe Photoshop) und FLV (Flash Video)
- 🎼 MusicXML-Erkennung durch Signatur-Prüfung (score-partwise / score-timewise)
- 📦 ZIP-Struktur-Analyse zur Unterscheidung von ODT/ODS/ODP und DOCX/XLSX/PPTX
- 📄 Flat-XML-Erkennung (FODT, FODS, FODP)
- 📝 Markdown-Erkennung durch Analyse typischer Syntax-Elemente (nur für Textdateien)
- 📊 Strenge CSV-Erkennung (nur für Textdateien, verhindert Falscherkennung von Binärdateien)
- 🎬 Video/Audio-Unterscheidung bei MPEG-4-Dateien via ffprobe
- 🗑️ Automatische Löschung von Windows-Systemdateien ohne archivischen Wert (z. B. IndexerVolumeGuid)
- 🎨 Farbige Konsolenausgabe mit gleichzeitig sauberer Log-Datei
- 🧪 Dry-Run-Modus zum gefahrlosen Testen
- 📋 Automatischer Transfer von Stufe 2 nach Stufe 3
- 📊 Debug-Ausgaben zur Analyse der gefundenen Dateien

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

### Ordnerstruktur
Das Skript erwartet folgende Struktur im Benutzerverzeichnis:

    C:\Users\<Benutzer>\Documents\data\<AC-Nummer>\<Datenträger-ID>\
        2_<ID>_extracted-files\files\    (Quelldaten)
        3_<ID>_for-transfer\files\       (Zieldaten, wird automatisch erstellt)

---

## 📦 Installation

1. Siegfried installieren
   sf.exe nach C:\Program Files\Siegfried\sf.exe kopieren

2. FFmpeg installieren
   ffprobe.exe in einen Ordner legen, der im System-PATH liegt (z. B. C:\Program Files\FFmpeg\bin)

3. Skript ablegen
   C_Reparatur_von_Dateiendungen.py in den Arbeitsordner legen

4. Arbeitsumgebung starten
   start.bat ausführen → Menü startet automatisch

---

## 🚀 Verwendung

### Über das Menü (empfohlen)
1. start.bat ausführen
2. Im Menü das Skript C_Reparatur_von_Dateiendungen.py auswählen
3. AC-Nummer eingeben (z. B. AC12345678)
4. Datenträger-ID eingeben (z. B. ZPH350-110_3-5-12)
5. Das Skript kopiert automatisch Dateien von Stufe 2 nach Stufe 3 und führt die Reparatur durch

### Direkt über die Kommandozeile

    python C_Reparatur_von_Dateiendungen.py <AC-Nummer> <Datenträger-ID> [--dryrun]

Beispiel:

    python C_Reparatur_von_Dateiendungen.py AC12345678 ZPH350-110_3-5-12

### Dry-Run-Modus
Mit dem Flag --dryrun werden alle Änderungen nur simuliert – es werden keine Dateien umbenannt oder gelöscht:

    python C_Reparatur_von_Dateiendungen.py AC12345678 ZPH350-110_3-5-12 --dryrun

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
1. Magic Bytes: Prüfung auf PSD (8BPS), FLV (FLV) und andere binäre Signaturen
2. ZIP-Struktur: Prüfung auf mimetype-Datei (OpenDocument) oder Ordner wie word/, xl/, ppt/ (Office Open XML)
3. MusicXML: Prüfung auf score-partwise oder score-timewise Tags
4. Flat XML: Analyse des XML-Headers auf office:mimetype-Attribut
5. CSV-Struktur: Mindestens 5 Zeilen mit jeweils ≥2 konsistenten Trennzeichen (;, ,, \t, |) – nur für Textdateien
6. Markdown-Syntax: Erkennung von Überschriften, Links, Listen, Code-Blöcken etc. (mind. 2 Indikatoren) – nur für Textdateien
7. Plain Text: Fallback auf .txt, wenn die Datei überwiegend druckbare Zeichen enthält

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

Das Skript erstellt im Stufe-3-Ordner eine Log-Datei:
    3_<ID>_for-transfer/files/3_<ID>_for-transfer_repair-file-extension.log

Inhalt:
- Zeitstempel aller Aktionen
- Debug-Ausgaben zur Anzahl der gefundenen Dateien
- Umbenannte Dateien mit Quelle der Erkennung (z. B. PRONOM ID (Manuell), Magic Bytes (PSD), MusicXML (Signatur))
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
| Bilder            | JPG, PNG, TIF, BMP, PSD (Magic Bytes)                                 |
| Audio             | FLAC, M4A, OGG                                                       |
| Video             | MP4, MKV, MXF, FLV (Magic Bytes)                                     |
| Musik/Noten       | MUS, MusicXML (Signatur)                                              |
| Spezialformate    | AppleWorks (.cwk), Apple Pages (.pages), Finale (.mus), Ami Pro (.sam), Outlook Express (.dbx), TeX (.tex) |

---

## ⚠️ Wichtige Hinweise

- Das Skript kopiert automatisch Dateien von Stufe 2 nach Stufe 3! Falls Stufe 3 bereits existiert, wird dieser Ordner verwendet.
- Das Skript verändert Dateien direkt im Stufe-3-Ordner! Vor der ersten Ausführung sollte ein Backup erstellt werden.
- Dry-Run-Modus (--dryrun) wird für den ersten Test dringend empfohlen.
- Dateien, die nicht zugeordnet werden können, werden nicht umbenannt und im Log als ❓ Nicht zugeordnet markiert.
- Bei mehreren Dateien gleichen Namens nach der Umbenennung wird automatisch ein Zähler angehängt (z. B. datei_1.pdf, datei_2.pdf).
- Die CSV-Erkennung funktioniert nur für Textdateien – binäre Dateien (wie FLV, PSD) werden nicht als CSV erkannt.
- Die Markdown-Erkennung funktioniert nur für Textdateien – binäre Dateien werden nicht als Markdown erkannt.

---

## 🐛 Fehlerbehebung

| Problem                              | Lösung                                                              |
|--------------------------------------|---------------------------------------------------------------------|
| Siegfried nicht gefunden             | Prüfen, ob C:\Program Files\Siegfried\sf.exe existiert              |
| ffprobe nicht im PATH                | FFmpeg installieren und bin-Ordner zum System-PATH hinzufügen       |
| Analyse-Ordner nicht gefunden        | Prüfen, ob die Ordnerstruktur korrekt ist: Documents/data/AC/ID/    |
| Keine Dateien ohne Endung gefunden   | Debug-Ausgabe prüfen – zeigt Anzahl der Dateien mit/ohne Endung     |
| Markdown-Datei wird als .txt erkannt | Markdown-Syntax prüfen – es müssen mind. 2 Indikatoren vorhanden sein |
| PSD-Datei wird als .md erkannt       | Magic-Bytes-Erkennung prüft PSD-Signatur (8BPS) zuerst              |
| FLV-Datei wird als .csv erkannt      | CSV-Erkennung prüft zuerst, ob es sich um eine Textdatei handelt    |
| MusicXML wird als .txt erkannt       | MusicXML-Signatur prüft auf score-partwise / score-timewise Tags    |

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
- v1.1 – Integration in Menü-Arbeitsumgebung (AC-Nummer / Datenträger-ID)
- v1.2 – Korrektur der MIME-Typ-Zuordnungen (XML/XSL, Flat XML)
- v1.3 – Strengere CSV-Erkennung, ZIP-Struktur-Analyse für ODT/ODS
- v1.4 – Markdown-Erkennung, Flat-XML-Erkennung (FODT/FODS/FODP)
- v1.5 – Magic-Bytes-Erkennung für PSD und FLV, MusicXML-Signatur, Debug-Ausgaben
- v1.6 – CSV- und Markdown-Erkennung nur für Textdateien (verhindert Falscherkennung binärer Dateien)