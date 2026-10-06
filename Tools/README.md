# Tools - Hilfs-Skripte und Utilities

Dieser Bereich enthält eigenständige Hilfs-Skripte und Utilities, die den Haupt-Workflow unterstützen oder separate Aufgaben erfüllen.

## Struktur

```text
Tools/
├── start.bat                          <-- Starter für diesen Bereich
├── menu.py                            <-- Menü für Tools
├── requirements.txt                   <-- Python-Abhängigkeiten
├── README.md                          <-- Diese Datei
│
└── PREMIS_Validierung/
    ├── README.md
    ├── premis-v3-0.xsd                <-- Offizielles PREMIS v3 XML-Schema (Library of Congress)
    └── win/
        └── PREMIS_Validierung.py
```

## Schnellstart

1. **Start über das Hauptmenü:** `Start.bat` im Root → Eingabe von `O`
2. **Skript auswählen:** Nummer des gewünschten Tools eingeben
3. **Ausführung:** Das Tool startet

## Verfügbare Tools

### PREMIS_Validierung

Validiert PREMIS XML-Dateien gegen das offizielle PREMIS v3 Schema der Library of Congress.

**Funktionsweise:**
- Lädt eine PREMIS XML-Datei
- Validiert gegen die beiliegende `premis-v3-0.xsd` (direkt im Skript-Ordner)
- Gibt detaillierte Fehlermeldungen bei Validierungsfehlern aus
- Bestätigt die Konformität bei erfolgreicher Validierung

**Nutzung:**
- Das Tool fragt interaktiv nach dem Pfad zur zu prüfenden PREMIS XML-Datei
- Die Validierung erfolgt automatisch
- Ergebnisse werden übersichtlich im Terminal angezeigt

**Parameter:**
- Keine festen Parameter (interaktive Eingabe des Dateipfads beim Start)

## Workflow-Integration

Die Tools sind unabhängig vom Haupt-Workflow einsetzbar, können aber in verschiedenen Phasen nützlich sein:

- **PREMIS_Validierung:** Kann nach der Erstellung von PREMIS-Dateien (z. B. durch Skript I im Bereich *Datenaufbereitung*) verwendet werden, um die Konformität der generierten Metadaten unabhängig zu überprüfen.

## Dokumentation der einzelnen Tools

Jedes Tool verfügt über eine eigene `README.md` im entsprechenden Unterordner. Dort finden sich detaillierte Informationen zu:
- Funktionsweise des Tools
- Eingabe-/Ausgabe-Parameter
- Beispiele und Troubleshooting

## Systemvoraussetzungen

- **Python 3.13** oder höher
- **Windows 10/11**
- **Externe Bibliotheken:** `lxml` (für XML-Validierung, siehe `requirements.txt`)

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck  
SPDX-License-Identifier: MIT