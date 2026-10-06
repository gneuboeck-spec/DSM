# Skriptsammlung WIENBIBLIOTHEK

Zentrale Arbeitsumgebung für die digitale Datenrettung und Langzeitarchivierung. Die Skriptsammlung ist modular aufgebaut und in drei Hauptbereiche unterteilt, die über ein zentrales Startmenü erreichbar sind.

## Gesamtstruktur

```text
Skriptsammlung/
├── Start.bat                          <-- Haupt-Startpunkt (Doppelklick hier)
├── Menu.py                            <-- Zentrales Auswahlmenü
├── requirements.txt                   <-- Python-Abhängigkeiten
├── git-update.bat                     <-- Git-Update-Skript
├── README.md                          <-- Diese Datei
│
├── Datenaufbereitung/                 <-- Haupt-Workflow (Skripte A-L)
│   ├── start.bat
│   ├── menu.py
│   ├── requirements.txt
│   ├── README.md
│   ├── A_Analyse_Skript_Brunnhilde_Fixity/
│   ├── B_XML_Zusammenfassungs_Generator_content/
│   ├── C_Reparatur_von_Dateiendungen/
│   ├── D_Master_Konvertierungsskript/
│   ├── E_VL_Bereinigung_Vorbereitung_Archivierung/
│   ├── F_Zwischendateien_ODF_WAV_löschen/
│   ├── G_Metadata_Extraction_Indexing_filetrove/
│   ├── H_VL_Export/
│   ├── I_PREMIS_XML_Generator/
│   ├── J_Staging-Workflow/
│   ├── K_Master_Index_Metadaten_Generator_LZA/
│   └── L_BagIt_METS_TAR_Archivierung/
│
├── Textdokumente_vergleichen/         <-- Vergleichs-Modul
│   ├── start.bat
│   ├── menu.py
│   ├── requirements.txt
│   ├── README.md
│   ├── 01_Dateiendungen_reparieren/
│   ├── 02_Dublikatenfinder/
│   ├── 03_Analyse_Skript_Brunnhilde_Fixity/
│   ├── 04_Bereinigungsskript/
│   ├── 05_Dokumente_vergleichen/
│   ├── 06_KI_Analyse/
│   └── 07_Visualisierung/
│
└── Tools/                             <-- Hilfs-Skripte
    ├── start.bat
    ├── menu.py
    ├── requirements.txt
    ├── README.md
    └── PREMIS_Validierung/
```

## Aufbau eines Skript-Ordners

Jedes einzelne Skript ist in einem eigenen Unterordner gekapselt. Dieser enthält immer eine `README.md` mit der Dokumentation des Skripts sowie einen Unterordner `win/`, in dem sich die eigentliche Python-Datei befindet. Der Name der Python-Datei entspricht dabei dem Namen des übergeordneten Skript-Ordners.

Beispiel am Skript `A_Analyse_Skript_Brunnhilde_Fixity`:

```text
A_Analyse_Skript_Brunnhilde_Fixity/
├── README.md                          <-- Dokumentation des Skripts
└── win/
    └── A_Analyse_Skript_Brunnhilde_Fixity.py   <-- Ausführbare Python-Datei
```

Dieses Muster gilt einheitlich für alle Skripte in allen drei Hauptbereichen.

## Die drei Hauptbereiche

### 1. Datenaufbereitung

Enthält die komplette Pipeline für die digitale Datenrettung und Langzeitarchivierung. Die Skripte A bis L bilden den Master-Workflow.

```text
Datenaufbereitung/
├── start.bat
├── menu.py
├── requirements.txt
├── README.md
├── A_Analyse_Skript_Brunnhilde_Fixity/
│   ├── README.md
│   └── win/
│       └── A_Analyse_Skript_Brunnhilde_Fixity.py
├── B_XML_Zusammenfassungs_Generator_content/
│   ├── README.md
│   └── win/
│       └── B_XML_Zusammenfassungs_Generator_content.py
├── C_Reparatur_von_Dateiendungen/
│   ├── README.md
│   └── win/
│       └── C_Reparatur_von_Dateiendungen.py
├── D_Master_Konvertierungsskript/
│   ├── README.md
│   └── win/
│       └── D_Master_Konvertierungsskript.py
├── E_VL_Bereinigung_Vorbereitung_Archivierung/
│   ├── README.md
│   └── win/
│       └── E_VL_Bereinigung_Vorbereitung_Archivierung.py
├── F_Zwischendateien_ODF_WAV_löschen/
│   ├── README.md
│   └── win/
│       └── F_Zwischendateien_ODF_WAV_löschen.py
├── G_Metadata_Extraction_Indexing_filetrove/
│   ├── README.md
│   └── win/
│       └── G_Metadata_Extraction_Indexing_filetrove.py
├── H_VL_Export/
│   ├── README.md
│   └── win/
│       └── H_VL_Export.py
├── I_PREMIS_XML_Generator/
│   ├── README.md
│   └── win/
│       └── I_PREMIS_XML_Generator.py
├── J_Staging-Workflow/
│   ├── README.md
│   └── win/
│       └── J_Staging-Workflow.py
├── K_Master_Index_Metadaten_Generator_LZA/
│   ├── README.md
│   └── win/
│       └── K_Master_Index_Metadaten_Generator_LZA.py
└── L_BagIt_METS_TAR_Archivierung/
    ├── README.md
    └── win/
        └── L_BagIt_METS_TAR_Archivierung.py
```

**Start:** Hauptmenü → `D`  
**Parameter:** AC-Nummer und Datenträger-ID

### 2. Textdokumente_vergleichen

Eigenständiges Modul zur syntaktischen und semantischen Analyse von Textdokumenten.

```text
Textdokumente_vergleichen/
├── start.bat
├── menu.py
├── requirements.txt
├── README.md
├── 01_Dateiendungen_reparieren/
│   ├── README.md
│   └── win/
│       └── 01_Dateiendungen_reparieren.py
├── 02_Dublikatenfinder/
│   ├── README.md
│   └── win/
│       └── 02_Dublikatenfinder.py
├── 03_Analyse_Skript_Brunnhilde_Fixity/
│   ├── README.md
│   └── win/
│       └── 03_Analyse_Skript_Brunnhilde_Fixity.py
├── 04_Bereinigungsskript/
│   ├── README.md
│   └── win/
│       └── 04_Bereinigungsskript.py
├── 05_Dokumente_vergleichen/
│   ├── README.md
│   └── win/
│       └── 05_Dokumente_vergleichen.py
├── 06_KI_Analyse/
│   ├── README.md
│   └── win/
│       └── 06_KI_Analyse.py
└── 07_Visualisierung/
    ├── README.md
    └── win/
        └── 07_Visualisierung.py
```

**Start:** Hauptmenü → `T`  
**Parameter:** Eingabe- und Ausgabe-Verzeichnis (über GUI-Dialog)

### 3. Tools

Sammlung von Hilfs-Skripten und Utilities.

```text
Tools/
├── start.bat
├── menu.py
├── requirements.txt
├── README.md
└── PREMIS_Validierung/
    ├── README.md
    └── win/
        └── PREMIS_Validierung.py
```

**Start:** Hauptmenü → `O`

## Schnellstart

1. **Doppelklick auf `Start.bat`** im Hauptverzeichnis
2. Das Hauptmenü öffnet sich mit drei Bereichen:
   - **D** - Datenaufbereitung (Haupt-Workflow)
   - **T** - Textdokumente_vergleichen
   - **O** - Tools
3. Buchstaben eingeben, um den gewünschten Bereich zu starten
4. Im gewählten Bereich werden alle verfügbaren Skripte aufgelistet
5. Nach Beenden des Unterbereichs kehrt man automatisch zum Hauptmenü zurück

## Zentrale Dateien im Root

### Start.bat
Der Einstiegspunkt der Arbeitsumgebung. Wechselt in das eigene Verzeichnis, prüft ob `Menu.py` vorhanden ist, und startet das Hauptmenü.

### Menu.py
Das zentrale Auswahlmenü. Zeigt die drei Hauptbereiche an und startet beim Auswählen die jeweilige `start.bat` des gewählten Unterordners als separaten Prozess. Nach Beenden des Unterbereichs kehrt man automatisch zum Hauptmenü zurück.

### requirements.txt
Enthält alle Python-Abhängigkeiten für das Projekt. Installation:

```bash
pip install -r requirements.txt
```

### git-update.bat
Automatisiertes Git-Update-Skript. Führt folgende Schritte aus:

1. **Pull**: Holt aktuelle Änderungen vom Server
2. **Add**: Fügt alle lokalen Änderungen hinzu (`git add -A`)
3. **Commit**: Erstellt Commit mit Zeitstempel
4. **Push**: Lädt Änderungen hoch

Bei Fehlern wird eine entsprechende Meldung angezeigt und das Skript pausiert.

## Systemvoraussetzungen

- **Python 3.13** oder höher
- **Windows 10/11**
- **Git** (für Versionskontrolle)
- Externe Tools je nach Bereich (ExifTool, FFprobe, Siegfried, YARA, etc.)

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck  
SPDX-License-Identifier: MIT