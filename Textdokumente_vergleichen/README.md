# Textdokumente_vergleichen - Dokumenten-Analyse

Eine automatisierte Python-Pipeline zur systematischen Bewertung elektronischer Vor- und Nachlässe (z. B. von Autor:innen). Das Tool hilft Archivar:innen und Bewerter:innen dabei, den tatsächlichen Umfang, die Einzigartigkeit und den Wert eines Dokumentenbestands objektiv und effizient zu ermitteln.

## Zielsetzung

Bei der monetären und archivischen Bewertung eines Nachlasses ist es entscheidend zu wissen, ob eine Sammlung aus hunderten einzigartigen Textdokumenten oder aus zahlreichen Kopien und Dubletten besteht. Diese Skriptsammlung automatisiert den Bereinigungs-, Analyse- und Visualisierungsprozess, um den *echten* textuellen Wert eines Bestands schnell sichtbar zu machen.

## Struktur

    Textdokumente_vergleichen/
    |-- Start.bat                          <-- Starter für diesen Bereich
    |-- Menu.py                            <-- Menü für Textdokumente_vergleichen
    |-- requirements.txt                   <-- Python-Abhängigkeiten
    |-- README.md                          <-- Diese Datei
    |
    |-- 01_Dateiendungen_reparieren/
    |   |-- README.md
    |   `-- win/
    |       `-- 01_Dateiendungen_reparieren.py
    |-- 02_Duplikatenfinder/
    |   |-- README.md
    |   `-- win/
    |       `-- 02_Duplikatenfinder.py
    |-- 03_Analyse_Skript_Brunnhilde_Fixity/
    |   |-- README.md
    |   `-- win/
    |       `-- 03_Analyse_Skript_Brunnhilde_Fixity.py
    |-- 04_Bereinigungsskript/
    |   |-- README.md
    |   `-- win/
    |       `-- 04_Bereinigungsskript.py
    |-- 05_Dokumente_vergleichen/
    |   |-- README.md
    |   `-- win/
    |       `-- 05_Dokumente_vergleichen.py
    |-- 06_KI_Analyse/
    |   |-- README.md
    |   `-- win/
    |       `-- 06_KI_Analyse.py
    `-- 07_Visualisierung/
        |-- README.md
        `-- win/
            `-- 07_Visualisierung.py

## Workflow (Empfohlene Reihenfolge)

Die Skripte sind nummeriert und sollten idealerweise in dieser Reihenfolge über die zentrale `Menu.py` ausgeführt werden:

1. **`01_Dateiendungen_reparieren.py`**: Repariert fehlende oder falsche Dateiendungen durch mehrstufige Analyse:
   - **PRONOM-basierte Erkennung** via Siegfried (Magic Bytes und binäre Signaturen)
   - **Flat XML**: Erkennung von FODT, FODS, FODP durch `office:mimetype`-Attribute
   - **Office Open XML**: ZIP-Struktur-Analyse (word/, xl/, ppt/ Ordner)
   - **Markdown-Syntax**: Erkennung mit 13 Indikatoren (Überschriften, Links, Listen, Code-Blöcke, etc.)
   - **Strenge CSV-Erkennung**: Nur für Textdateien, mind. 5 Zeilen mit ≥2 konsistenten Trennzeichen
   - **MIME-Typ-Korrekturen**: Verhindert Falscherkennung von XML als XSL, RTF-Erkennung, etc.
   - Automatische Löschung von Windows-Systemdateien ohne archivischen Wert

2. **`02_Duplikatenfinder.py`**: Entfernt Dubletten auf zwei Ebenen:
   - **Binäre Dubletten**: 100% identische Dateien (gleiche Größe + SHA-256 Hash)
   - **Inhaltliche Dubletten**: Dokumente in verschiedenen Formaten (.doc, .docx, .pdf, .odt, .rtf, UOF) mit identischem Textinhalt
   - Intelligente Text-Normalisierung (Unicode NFKC, Trennstriche, Seitenkennungen)
   - **Prioritätsliste** für das Behalten des Originals: PDF > DOCX > ODT > RTF > TXT > MD
   - Umfangreiche Textextraktion mit direkten Python-Bibliotheken (pypdf, docx, odf, striprtf) und LibreOffice als Fallback
   - Generiert Vorschau-CSV mit Bestätigungsdialog vor der Löschung

3. **`03_Analyse_Skript_Brunnhilde_Fixity.py`**: Erstellt einen tiefgehenden Überblick über alle vorhandenen Dateitypen und prüft auf Integrität und Schadsoftware:
   - Vollständige Brunnhilde-Analyse mit Siegfried und ClamAV
   - SHA-256 Prüfsummen-Generierung für alle Dateien
   - **Automatische ClamAV-Updates**: Erkennt veraltete Virendefinitionen (>7 Tage) und öffnet automatisch ein Admin-Fenster für `freshclam.exe`, während die Analyse weiterläuft
   - Manuelle Erstellung der `tree.txt` als Workaround

4. **`04_Bereinigungsskript.py`**: Entfernt systembedingten Dateimüll:
   - Rund 180 bekannte Müll-Dateiendungen (.tmp, .log, .bak, .dll, .exe, etc.)
   - Windows-Systemdateien (Thumbs.db, desktop.ini)
   - Versteckte Dateien (._*, ~*)
   - Konvertierungslogs und andere Artefakte
   - Rekursives Löschen leerer Ordner
   - Schreibschutz-Handling für geschützte Dateien

5. **`05_Dokumente_vergleichen.py`**: Führt hochperformante, mathematische Textvergleiche durch:
   - **Dreistufige Filter-Logik**: Jaccard-Index (Wort-Overlap) → Längenverhältnis → Zeichen-für-Zeichen-Vergleich
   - **C++-Beschleunigung** via RapidFuzz (mit difflib Fallback)
   - **Intelligentes Bucketing**: Logarithmische Längen-Kategorien reduzieren die Vergleiche um 95%
   - **Union-Find-Algorithmus** zur effizienten Gruppenbildung
   - **Multiprocessing** über alle CPU-Kerne
   - Smart Sampling (Anfang + Ende) für lange Dokumente
   - LibreOffice-Konvertierung mit Cache-System für alte Formate
   - Umfangreicher GUI-Einstellungsdialog mit Parameter-Erklärungen

6. **`06_KI_Analyse.py`**: Nutzt semantische KI-Modelle für inhaltliche Ähnlichkeit:
   - **Sentence-Transformers** (`paraphrase-multilingual-mpnet-base-v2`)
   - **Kosinus-Ähnlichkeit** zwischen semantischen Vektoren
   - **Trigger-Wort-Erkennung**: abstract, zusammenfassung, summary, review, rezension, einleitung, etc.
   - **Intelligente Filterung**: Nur Kurztexte (100-5000 Zeichen) oder Dateien mit Trigger-Wörtern werden analysiert
   - **Zentraler Modell-Cache** in `~/.ki_model_cache` für schnelle Wiederverwendung
   - Zuordnung von Abstracts und Zusammenfassungen zu bestehenden Dokumentengruppen

7. **`07_Visualisierung.py`**: Stellt die Ergebnisse in interaktiven Matplotlib-Diagrammen dar:
   - **Gesamtübersicht** (4 Diagramme): Dokumente pro Gruppe, Dokumententypen-Verteilung, durchschnittliche Dateigröße, KI-Ähnlichkeit
   - **Einzelgruppen-Analyse**: Zeitstrahl mit dynamischer Zeitachse, Dateigrößen-Vergleich, Text-Änderungen gegen Basis, KI-Ähnlichkeit
   - Dynamische Formatierung basierend auf Datenmenge
   - Pastellfarben pro Gruppe, gelbe Hervorhebung für Kurztexte

## Ausgabeformate

Alle Analyse-Ergebnisse werden in zwei Formaten exportiert:

- **CSV-Datei** (`versionen_analyse_mit_ki.csv`): Universelle Tabellenstruktur mit UTF-8 BOM
- **Excel-Datei** (`versionen_analyse_mit_ki_farbig.xlsx`):
  - Farbige Hintergrundfarben pro Gruppe (20 Pastellfarben)
  - Gelbe Hervorhebung für KI-zugeordnete Kurztexte
  - Graue Markierung für nicht gruppierte Dokumente
  - Auto-Filter und eingefrorene Kopfzeile
  - Automatisch angepasste Spaltenbreiten

## Nutzung

1. Doppelklick auf `Start.bat` im Ordner `Textdokumente_vergleichen`
2. Das Menü (`Menu.py`) öffnet sich und listet alle 7 Skripte auf
3. Wählen Sie über den Datei-Explorer den Quell- und Zielordner aus
4. Passen Sie bei Bedarf die Schwellenwerte im GUI-Dialog an oder nutzen Sie die Standardwerte
5. Die Skripte arbeiten sequentiell - jedes baut auf den Ergebnissen des vorherigen auf

## Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Git** (für Versionskontrolle)
- **Python-Pakete:** siehe `Textdokumente_vergleichen/requirements.txt` bzw. das zentrale `requirements.txt` im Repo-Root. Installation:

      pip install -r requirements.txt

- **Externe Programme:** siehe `EXTERNE_TOOLS.md` im Repo-Root. Für diesen Bereich relevant sind insbesondere:
  - **Siegfried** (`sf`) – für Dateiidentifizierung (Skripte 01, 03)
  - **ClamAV** (`clamscan`, `freshclam`) – für Virenscan (Skript 03)
  - **LibreOffice** (`soffice`) – für Dokumentenkonvertierung (Skripte 02, 05)
  - **FFprobe** (`ffprobe`) – für MPEG-4-Audio/Video-Unterscheidung (Skript 01)

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

## Python-Interpreter

Dieser Bereich verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der verwendete Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an die Subskripte weitergegeben. Damit ist es egal, ob Python systemweit oder als User-Installation vorliegt.

## Performance-Tipps

- **RapidFuzz installieren**: `pip install rapidfuzz` für drastisch schnellere Textvergleiche (C++-Engine)
- **tqdm installieren**: `pip install tqdm` für Fortschrittsbalken bei langen Analysen
- **LibreOffice**: Sollte installiert sein, damit alte Formate (.doc, .wpd, .pages) korrekt konvertiert werden können
- **Cache-Systeme**: Sowohl der Dokumentenvergleich als auch die KI-Analyse nutzen Cache-Ordner (`.conversion_cache`, `.ki_conversion_cache`, `~/.ki_model_cache`), um wiederholte Konvertierungen und Modell-Ladungen zu vermeiden

## Detaillierte Parameter-Erklärungen

Jedes Skript mit GUI-Dialog verfügt über integrierte Hilfe-Buttons:
- **Ablauf**: Erklärt den Algorithmus Schritt für Schritt
- **Hilfe**: Detaillierte Erklärungen aller Parameter und Schwellenwerte

## Dokumentation der einzelnen Skripte

Jedes Skript verfügt über eine eigene `README.md` im entsprechenden Unterordner. Dort finden sich detaillierte Informationen zu:
- Funktionsweise des Skripts
- Verwendete externe Tools
- Eingabe-/Ausgabe-Parameter
- Beispiele und Troubleshooting

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT