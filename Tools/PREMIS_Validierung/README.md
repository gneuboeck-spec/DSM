# PREMIS XML Validator

Ein eigenständiges Validierungstool für PREMIS-XML-Dateien gegen XSD-Schemas. Das Tool wurde speziell für den Einsatz in der digitalen Langzeitarchivierung entwickelt und kombiniert einfache Bedienung mit robuster Validierungslogik.

## Zweck

Das Tool validiert PREMIS-XML-Dateien (Preservation Metadata: Implementation Strategies) gegen das offizielle XSD-Schema der Library of Congress. Es wurde entwickelt, um die Konformität von PREMIS-Dateien zu prüfen, die im Rahmen des Master-Workflows zur digitalen Datenrettung und Langzeitarchivierung (LZA) erstellt werden.

## Features

### Benutzerfreundliche GUI-Dialoge
- Interaktive Dateiauswahl über native System-Dialoge (tkinter)
- Keine Kommandozeilen-Parameter erforderlich
- Schrittweise Führung durch den Validierungsprozess

### 3-stufiger Schema-Fallback
Das Tool versucht, das PREMIS-Schema auf drei Wegen zu laden:
1. Direkter Abruf von der offiziellen Library of Congress URL
2. Browser-User-Agent Fallback gegen Bot-Schutz-Mechanismen
3. Lokale Datei als letzte Option (die vom Benutzer ausgewählte XSD-Datei)

Diese mehrstufige Strategie stellt sicher, dass die Validierung auch bei Netzwerkproblemen oder API-Beschränkungen zuverlässig funktioniert.

### Automatische Versionserkennung
- Erkennt automatisch PREMIS v3.0 (Namespace: http://www.loc.gov/premis/v3)
- Warnt bei nicht-standardkonformen oder benutzerdefinierten Schemas
- Zeigt den erkannten Namespace und die Version an

### Intelligente Fehlerfilterung
Das PREMIS-Schema erlaubt explizit Erweiterungen über das Element objectCharacteristicsExtension. Im Rahmen des FileTrove-Workflows werden zusätzliche Namespaces eingebettet:
- info:onb.ac.at/filetrove-schema/v1 (FileTrove-Metadaten)
- info:onb.ac.at/greaseweazle-format-schema/v1 (Greaseweazle Flux-Stream-Daten)

Das Tool filtert Warnungen zu diesen erwarteten Erweiterungs-Namespaces automatisch heraus und zeigt nur echte PREMIS-Validierungsfehler an. So bleibt die Ausgabe übersichtlich und fokussiert auf tatsächliche Probleme.

### Optionaler Report-Export
- Validierungsergebnisse können als Textdatei gespeichert werden
- Zeitgestempelter Dateiname (z.B. premis_validation_20260929_143022.txt)
- Vollständiger Bericht mit allen Fehlern und Statistiken
- Speicherung im gleichen Ordner wie die validierte PREMIS-Datei

## Nutzung

### Start über das Tools-Menü
1. Im Hauptmenü "O" drücken (Shortcut für Tools-Ordner)
2. Im Tools-Menü die Nummer für PREMIS_Validierung.py auswählen
3. Das Tool startet und zeigt einen Dateiauswahl-Dialog

### Ablauf der Validierung

Schritt 1: PREMIS-XML-Datei auswählen
- Dateiauswahl-Dialog öffnet sich
- Die zu validierende PREMIS-Datei auswählen (z.B. 5_ZPH350-110_3-5-12_LZA_premis.xml)

Schritt 2: XSD-Schema auswählen
- Zweiter Dateiauswahl-Dialog öffnet sich
- Das PREMIS-XSD-Schema auswählen (z.B. premis-v3-0.xsd)
- Tipp: Die offizielle Schema-Datei kann von https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd heruntergeladen werden

Schritt 3-5: Automatische Validierung
- Das Tool prüft die Dateien
- Erkennt die Schema-Version
- Führt die Validierung durch
- Zeigt das Ergebnis an

Schritt 6: Ergebnis
- VALIDATION SUCCESSFUL: Die Datei ist PREMIS-konform
- VALIDATION FAILED: Es wurden Fehler gefunden
- Option zum Speichern eines detaillierten Berichts

### Beispiel-Ausgabe (Erfolg)

==================================================
  VALIDATION RESULT
==================================================
  File:    5_ZPH350-110_3-5-12_LZA_premis.xml
  Schema:  premis-v3-0.xsd
  Version: PREMIS v3.0 (2015 - Current Standard)

  ==============================================
  [OK] VALIDATION SUCCESSFUL!
  The PREMIS file is fully conformant.
  ==============================================

  INFO: 1406 warning(s) from custom extensions
        (FileTrove/Greaseweazle namespace) were ignored.

### Beispiel-Ausgabe (Fehler)

==================================================
  VALIDATION RESULT
==================================================
  File:    invalid_premis.xml
  Schema:  premis-v3-0.xsd
  Version: PREMIS v3.0 (2015 - Current Standard)

  ==============================================
  [FAIL] VALIDATION FAILED!
  3 error(s) found.
  ==============================================

  ERRORS:
  -------------------------------------------
  ERROR (Line 42): Element '{http://www.loc.gov/premis/v3}objectIdentifier': Missing child element(s).
  ERROR (Line 156): Element '{http://www.loc.gov/premis/v3}eventDateTime': '2026-13-45' is not a valid value of the atomic type 'xs:dateTime'.
  ERROR (Line 289): Element '{http://www.loc.gov/premis/v3}relationship': The element has incomplete content.

## Voraussetzungen

### Python-Pakete
pip install lxml requests

Beide Pakete sind bereits in der zentralen requirements.txt des Projekts enthalten.

### Systemvoraussetzungen
- Python: 3.10 oder höher
- tkinter: Für die GUI-Dialoge (standardmäßig in Python enthalten)
- Internetverbindung: Optional (für Online-Schema-Abruf)

## Technische Details

### Validierungs-Engine
- lxml: Hochperformante XML-Verarbeitung mit vollständiger XSD-Validierung
- XMLSchema: lxml's native XSD-Validierungsklasse
- Fehlerprotokollierung: Detaillierte Fehlermeldungen mit Zeilennummern

### Schema-Quellen
- Offizielle URL: https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd
- Browser-User-Agent: Chrome 115.0 (Windows 10) für den Fallback-Versuch
- Timeout: 10 Sekunden pro Versuch

### Ignorierte Namespaces
Die folgenden Namespaces werden als gültige PREMIS-Erweiterungen erkannt und ihre Warnungen werden herausgefiltert:
- info:onb.ac.at/filetrove-schema/v1 - FileTrove-spezifische Metadaten
- info:onb.ac.at/greaseweazle-format-schema/v1 - Greaseweazle Flux-Stream-Daten

## Ordnerstruktur

Das Tool folgt dem standardisierten Schema des Tools-Ordners:

Tools/
├── start.bat
├── menu.py
└── PREMIS_Validierung/
    ├── README.md              ← Diese Datei
    └── win/
        └── PREMIS_Validierung.py

## Integration in den Workflow

Das Tool ist Teil des DSM-Workflows (Digitale Datenrettung & Langzeitarchivierung) und wird typischerweise nach der Erstellung der PREMIS-Datei durch das Skript J_generate_premis_win.py (Stufe 5) ausgeführt, um die Konformität der generierten Metadaten zu verifizieren.

### Typischer Einsatzort
- Phase 4: Archiv-Versiegelung (Stufe 5 / LZA)
- Validierung der Datei 5_[ID]_LZA_premis.xml im logfiles/-Unterordner

## Fehlerbehebung

### Problem: "lxml nicht installiert"
pip install lxml

### Problem: "requests nicht installiert"
pip install requests
Hinweis: Das Tool funktioniert auch ohne requests, nutzt dann aber nur die lokale XSD-Datei.

### Problem: Schema kann nicht geladen werden
- Prüfen Sie die Internetverbindung
- Stellen Sie sicher, dass die lokale XSD-Datei korrekt und vollständig ist
- Das offizielle Schema kann von https://www.loc.gov/standards/premis/v3/ heruntergeladen werden

### Problem: GUI-Dialoge öffnen sich nicht
- Stellen Sie sicher, dass tkinter installiert ist (standardmäßig in Python enthalten)
- Unter Linux ggf. nachinstallieren: sudo apt-get install python3-tk

## Validierungsstatistiken

Das Tool erstellt folgende Statistiken:
- Anzahl der echten PREMIS-Fehler
- Anzahl der ignorierten FileTrove/Greaseweazle-Erweiterungs-Warnungen
- Dateigrößen von PREMIS-XML und XSD-Schema
- Erkannte Schema-Version

## Changelog

### Version 1.0 (Final Combined Version)
- GUI-Dialoge für einfache Bedienung
- 3-stufiger Schema-Fallback (Online → User-Agent → Lokal)
- Automatische PREMIS v3.0 Versionserkennung
- Intelligente Filterung von FileTrove/Greaseweazle-Erweiterungen
- Ausgabe nur echter PREMIS-Fehler
- Optionaler Report-Export als Textdatei
- Keine Abhängigkeit von Administratorrechten

## Lizenz

SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT

---

Hinweis: Dieses Tool ist Teil der DSM-Skriptsammlung zur digitalen Datenrettung und Langzeitarchivierung. Für den vollständigen Workflow siehe die Haupt-README.md im Root-Verzeichnis des Projekts.