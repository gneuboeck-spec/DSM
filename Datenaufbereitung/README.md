# Datenaufbereitung - Master-Workflow

Dieser Bereich enthält die komplette Pipeline für die digitale Datenrettung und Langzeitarchivierung. Die Skripte A bis L bilden den Master-Workflow und führen die Daten durch alle Phasen von der Erfassung bis zur finalen Archiv-Versiegelung.

## Struktur

```text
Datenaufbereitung/
├── start.bat                          <-- Starter für diesen Bereich
├── menu.py                            <-- Menü für Datenaufbereitung
├── requirements.txt                   <-- Python-Abhängigkeiten
├── README.md                          <-- Diese Datei
│
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
│       ├── G_Metadata_Extraction_Indexing_filetrove.py
│       └── rules.yar                  <-- YARA-Regeln für Dateiformat-Identifizierung
├── H_VL_Export/
│   ├── README.md
│   └── win/
│       └── H_VL_Export.py
├── I_PREMIS_XML_Generator/
│   ├── README.md
│   ├── premis-v3-0.xsd               <-- Offizielles PREMIS v3 XML-Schema (Library of Congress)
│   └── win/
│       └── I_PREMIS_XML_Generator.py
├── J_Staging-Workflow/
│   ├── README.md
│   └── win/
│       └── J_Staging-Workflow.py
├── K_Master_Index_Metadaten_Generator_LZA/
│   ├── README.md
│   └── win/
│       ├── K_Master_Index_Metadaten_Generator_LZA.py
│       └── rules.yar                  <-- YARA-Regeln für Dateiformat-Identifizierung
└── L_BagIt_METS_TAR_Archivierung/
    ├── README.md
    └── win/
        └── L_BagIt_METS_TAR_Archivierung.py
```

## Schnellstart

1. **Start über das Hauptmenü:** `Start.bat` im Root → Eingabe von `D`
2. **Parameter eingeben:**
   - AC-Nummer (z.B. `AC01234567`)
   - Datenträger-ID (z.B. `ZPH350-110_3-5-12`)
3. **Skript auswählen:** Nummer des gewünschten Skripts eingeben
4. **Ausführung:** Das Skript startet mit den übergebenen Parametern

*Hinweis: Die Parameter können auch später über die Option `N` im Menü geändert werden.*

## Die Skripte des Master-Workflows

### Phase 1: Erfassung & Analyse

**A - Analyse_Skript_Brunnhilde_Fixity**  
Forensische Analyse der extrahierten Dateien mit Brunnhilde. Erstellt Fixity-Referenzen (SHA-256), Struktur-Berichte und führt Virus-Scans mit ClamAV durch.

**B - XML_Zusammenfassungs_Generator_content**  
Generiert eine zusammenfassende XML-Datei (`*_extracted-files.content`) mit allen Metadaten der extrahierten Dateien.

**G - Metadata_Extraction_Indexing_filetrove**  
Metadaten-Extraktion und Indexierung mit filetrove. Nutzt YARA-Regeln (`rules.yar` im `win/`-Ordner) für die Dateiformat-Identifizierung und extrahiert technische Metadaten.

### Phase 2: Reparatur & Normalisierung

**C - Reparatur_von_Dateiendungen**  
Mehrstufige Erkennung und Reparatur von Dateiendungen. Nutzt PRONOM-basierte Erkennung (Siegfried), Magic Bytes und spezialisierte Fallback-Erkennung für verschiedene Formate.

**D - Master_Konvertierungsskript**  
Konvertierung der Dateien zu Archiv-Derivaten (PDF/A, ODF-Zwischenschritte). Erstellt Digital Twins für die Langzeitarchivierung.

### Phase 3: Kuratierung & VL-Representation

**E - VL_Bereinigung_Vorbereitung_Archivierung**  
Bereinigung der Dateien für das aktive Repository. Löscht Systemmüll und technische Artefakte. Führt Integritäts-Checks durch.

**F - Zwischendateien_ODF_WAV_löschen**  
Löscht konvertierte ODF- und WAV-Zwischendateien, die nicht im finalen Archiv benötigt werden.

**H - VL_Export**  
Export der bereinigten Daten für den Katalog-Import. Erstellt den technischen Index für die VL-Representation.

### Phase 4: Archiv-Versiegelung

**I - PREMIS_XML_Generator**  
Generiert standardkonforme PREMIS v3 XML-Dateien mit Erhaltungs-Metadaten. Inklusive automatischer Quellmedium-Erkennung und GND-Integration für Urheber. Die Validierung erfolgt gegen das offizielle Schema `premis-v3-0.xsd`, das direkt im Skript-Ordner abgelegt ist.

**J - Staging-Workflow**  
Konsolidierung aller Daten und Logs für die finale Archiv-Versiegelung. Bereitet die Struktur für den BagIt-Container vor.

**K - Master_Index_Metadaten_Generator_LZA**  
Erstellt den finalen Master-Index und führt den letzten Integritäts-Check über alle Phasen hinweg durch (SHA-512, SHA-256, MD5). Nutzt YARA-Regeln (`rules.yar` im `win/`-Ordner) für die Dateiformat-Identifizierung.

**L - BagIt_METS_TAR_Archivierung**  
Verpackt die finale Stufe 5 in einen BagIt-konformen Container. Erstellt `bag-info.txt`, `manifest-sha256.txt` und versiegelt alles in einem TAR-Archiv.

## Workflow-Phasen

Der Master-Workflow folgt dem "Dualen Output"-Prinzip:

1. **Phase 1 (Stufe 0-2):** Erfassung, forensische Analyse, Fixity-Checks
2. **Phase 2 (Stufe 3):** Reparatur, Konvertierung, Normalisierung
3. **Phase 3 (Stufe 4):** Bereinigung, Integritäts-Checks, VL-Representation
4. **Phase 4 (Stufe 5):** Konsolidierung, PREMIS-Metadaten, BagIt-Versiegelung

**Ergebnis:**
- **Repository (VL):** Bereinigte Nutzdaten und Derivate für den Katalog-Import
- **Archiv-Tresor (LZA):** Forensische Bit-Kopien und lückenlose Beweiskette in BagIt-Container

## Parameter

Alle Skripte in diesem Bereich benötigen zwei Parameter:

- **AC-Nummer:** Die Archiv-Nummer des Bestands (z.B. `AC01234567`)
- **Datenträger-ID:** Die ID des spezifischen Datenträgers (z.B. `ZPH350-110_3-5-12`)

Diese Parameter werden beim Start des Bereichs abgefragt und an alle Skripte weitergegeben.

## Zusätzliche Dateien

| Datei | Ort | Zweck |
|---|---|---|
| `rules.yar` | `G_Metadata_Extraction_Indexing_filetrove/win/` | YARA-Regeln für Dateiformat-Identifizierung (filetrove) |
| `premis-v3-0.xsd` | `I_PREMIS_XML_Generator/` | Offizielles PREMIS v3 XML-Schema der Library of Congress zur Validierung |
| `rules.yar` | `K_Master_Index_Metadaten_Generator_LZA/win/` | YARA-Regeln für Dateiformat-Identifizierung (Master-Index) |

## Dokumentation der einzelnen Skripte

Jedes Skript verfügt über eine eigene `README.md` im entsprechenden Unterordner. Dort finden sich detaillierte Informationen zu:
- Funktionsweise des Skripts
- Verwendete externe Tools
- Eingabe-/Ausgabe-Parameter
- Beispiele und Troubleshooting

## Systemvoraussetzungen

- **Python 3.13** oder höher
- **Windows 10/11**
- **Externe Tools:**
  - ExifTool (Metadaten-Extraktion)
  - FFprobe (Audio/Video-Metadaten)
  - Siegfried (PRONOM-basierte Dateiformat-Erkennung)
  - YARA (Dateiformat-Identifizierung)
  - ClamAV (Virus-Scan)
  - Brunnhilde (Forensische Analyse)
  - BagIt-Python (BagIt-Container-Erstellung)

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck  
SPDX-License-Identifier: MIT