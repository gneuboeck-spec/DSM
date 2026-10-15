# Tools - Hilfs-Skripte und Utilities

Dieser Bereich enthält eigenständige Hilfs-Skripte und Utilities, die den Haupt-Workflow unterstützen oder separate Aufgaben erfüllen.

## Struktur

    Tools/
    |-- Start.bat                          <-- Starter für diesen Bereich
    |-- Menu.py                            <-- Menü für Tools
    |-- requirements.txt                   <-- Python-Abhängigkeiten
    |-- README.md                          <-- Diese Datei
    |
    `-- PREMIS_Validierung/
        |-- README.md
        |-- premis-v3-0.xsd                <-- Offizielles PREMIS v3 XML-Schema (Library of Congress)
        `-- win/
            `-- PREMIS_Validierung.py

## Schnellstart

1. **Start über das Hauptmenü:** `Start.bat` im Root → Eingabe von `O`
2. **Skript auswählen:** Nummer des gewünschten Tools eingeben
3. **Ausführung:** Das Tool startet

## Verfügbare Tools

### PREMIS_Validierung

Validiert PREMIS XML-Dateien gegen das offizielle PREMIS v3 Schema der Library of Congress.

**Funktionsweise:**
- Lädt eine PREMIS XML-Datei
- Validiert gegen die beiliegende `premis-v3-0.xsd` (direkt im Skript-Ordner) sowie – falls erreichbar – gegen das offizielle Schema unter `www.loc.gov` (3-stufiger Fallback)
- Filtert erwartete FileTrove-/Greaseweazle-Erweiterungswarnungen heraus
- Gibt detaillierte Fehlermeldungen bei Validierungsfehlern aus
- Bestätigt die Konformität bei erfolgreicher Validierung

**Nutzung:**
- Das Tool fragt interaktiv nach dem Pfad zur zu prüfenden PREMIS XML-Datei
- Die Validierung erfolgt automatisch
- Ergebnisse werden übersichtlich im Terminal angezeigt
- Auf Wunsch wird ein Validierungsbericht als Textdatei gespeichert

**Parameter:**
- Keine festen Parameter (interaktive Eingabe des Dateipfads beim Start)

## Workflow-Integration

Die Tools sind unabhängig vom Haupt-Workflow einsetzbar, können aber in verschiedenen Phasen nützlich sein:

- **PREMIS_Validierung:** Kann nach der Erstellung von PREMIS-Dateien (z. B. durch Skript I im Bereich *Datenaufbereitung*) verwendet werden, um die Konformität der generierten Metadaten unabhängig zu überprüfen.

## Python-Interpreter

Dieser Bereich verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der verwendete Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an die Subskripte weitergegeben. Damit ist es egal, ob Python systemweit oder als User-Installation vorliegt.

## Dokumentation der einzelnen Tools

Jedes Tool verfügt über eine eigene `README.md` im entsprechenden Unterordner. Dort finden sich detaillierte Informationen zu:
- Funktionsweise des Tools
- Eingabe-/Ausgabe-Parameter
- Beispiele und Troubleshooting

## Systemvoraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette oben)
- **Git** (für Versionskontrolle)
- **Python-Pakete:** siehe `Tools/requirements.txt` bzw. das zentrale `requirements.txt` im Repo-Root. Installation:

      pip install -r requirements.txt

- **Externe Programme:** Für diesen Bereich sind derzeit keine externen Programme erforderlich. Sollte sich das ändern, sind sie in `EXTERNE_TOOLS.md` im Repo-Root dokumentiert.

Nach einer PATH-Änderung muss die Konsole neu geöffnet werden, damit der Eintrag wirksam wird.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT