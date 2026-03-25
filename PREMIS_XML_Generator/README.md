# PREMIS XML Generator (Universal LZA Version)

Dieses Python-Skript (`J_generate_premis_win.py`) automatisiert die Erstellung von **PREMIS v3.0** Metadaten-Dateien für die Langzeitarchivierung (LZA). Es fungiert als zentrale Metadaten-Schnittstelle, die Informationen aus Imaging-Logs (FTK, Redumper, Greaseweazle), Dateianalysen (Siegfried/Brunnhilde) und Normdaten-Datenbanken (GND) zu einem validen Archiv-Paket zusammenführt.

## Inhaltsverzeichnis
1. [Features](#features)
2. [Voraussetzungen](#voraussetzungen)
3. [Die LZA-Pipeline (Ordnerstruktur)](#die-lza-pipeline-ordnerstruktur)
4. [Verwendung](#verwendung)
5. [Funktionsweise & Modi](#funktionsweise--modi)
6. [GND-Integration](#gnd-integration)
7. [Lizenz](#lizenz)

## Features
- **Multi-Format Support**: Automatische Erkennung des Medientyps anhand der Log-Dateien:
  - **USB-Sticks/Festplatten**: Extrahiert Metadaten (Tableau Bridge, Seriennummern) aus FTK Imager Logs.
  - **Disketten**: Verarbeitet Greaseweazle Flux-Logs und Metadaten (Zylinder/Heads).
  - **Optische Medien**: Parst Redumper-Logs für Audio-CDs und DVDs.
- **GND-Anbindung**: Live-Suche über die SRU-Schnittstelle der Deutschen Nationalbibliothek (DNB) zur eindeutigen Identifizierung von Urhebern.
- **Validität**: Erzwingt die korrekte XSD-Reihenfolge der XML-Elemente gemäß PREMIS v3 Schema.
- **Beziehungsmanagement**: Bildet komplexe Abhängigkeiten ab (`is derived from`, `is part of`, `is included in`) – vom physischen Träger bis zum konvertierten Derivat.
- **Integrität**: Berechnet SHA-512 Hashes oder übernimmt vorhandene Prüfsummen (MD5, SHA1) aus Imaging-Logs.

## Voraussetzungen
Das Skript benötigt **Python 3.x** und folgende Bibliotheken:

- **lxml**: Für die performante XML-Generierung und Namespace-Verwaltung.
- **requests**: Für die Kommunikation mit der DNB/GND-Schnittstelle.

Installation der Abhängigkeiten:
`pip install lxml requests`

## Die LZA-Pipeline (Ordnerstruktur)
Das Skript erwartet eine fest definierte Struktur im Home-Verzeichnis unter `Documents/data/`. Jede Disk-ID durchläuft folgende Schritte:

- **0_[ID]_picture-carrier/**: Fotos des physischen Objekts (.tif).
- **1_[ID]_image-LZA/**: Disk-Images (.img, .bin, .001) + Imaging-Logs.
- **2_[ID]_extracted-files/**: Brunnhilde-Berichte & extrahierte Daten.
- **3_[ID]_for-transfer/**: Finalisierte Dateien + `.index` Metadaten-Datei.
- **5_[ID]_LZA/**: **ZIELORDNER**. Hier wird die `5_[ID]_LZA_premis.xml` erstellt.

## Verwendung

Führe das Skript über die Kommandozeile aus und übergib die AC-Nummer sowie die Datenträger-ID:

`python J_generate_premis_win.py AC12345678 ID001`

### Ablauf im Skript:
1. **Urheber-Auswahl**: Das Skript bittet um die Eingabe eines Namens.
2. **GND-Suche**: Es erfolgt eine Abfrage bei der Nationalbibliothek. Wähle einen Treffer (1-N), suche neu (s) oder fahre ohne GND (x) fort.
3. **Automatisierte Analyse**: Das Skript scannt die Pipeline-Ordner und verknüpft alle gefundenen Dateien.
4. **XML-Erstellung**: Die PREMIS-Datei wird generiert und im Zielordner gespeichert.

## Funktionsweise & Modi
Das Skript nutzt eine „Auto-Weiche“ (`analyze_source_media`), um den Kontext des Imaging-Prozesses zu verstehen:
- **FTK-Modus**: Wird aktiviert, wenn ein `Exterro FTK Imager` Log gefunden wird.
- **Redumper-Modus**: Wird aktiviert, wenn ein Log mit XML-ähnlichen `<rom>` Tags gefunden wird (typisch für Optical Media).
- **Greaseweazle-Modus**: Wird aktiviert, wenn Floppy-spezifische Parameter (Host Tools) in den Logs auftauchen.

## GND-Integration
Die Anbindung an die DNB ermöglicht es, Personen eindeutig zu identifizieren. Das Skript zeigt Lebensdaten und Berufe an, um Verwechslungen zu vermeiden. Die gewählte **GND-ID** wird direkt als `agentIdentifier` (Typ: `gnd`) in das PREMIS-XML eingebettet.

## Lizenz
**Copyright (c) 2025 Gregor Neuboeck**

Lizenziert unter der **MIT-Lizenz**.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck <g.neuboeck@gmail.com>  
**SPDX-License-Identifier:** MIT