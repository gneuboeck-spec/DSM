# VL-Export Kopiertool

Ein Python-Skript zum automatisierten Kopieren von Dateien für den VL-Export (Verzeichnislieferung) im Rahmen digitaler Archivierungsprojekte.

## Funktionsumfang

- Kopiert TIF-Dateien aus dem Picture-Carrier-Ordner
- Kopiert content-, tree- und index-Dateien aus den entsprechenden Ordnern
- Kopiert den kompletten Files-Ordner
- Prüft auf bereits existierende Dateien im Zielordner
- Farbige Konsolenausgabe für bessere Lesbarkeit
- Optionales Öffnen des Zielordners nach Abschluss
- Keine Überschreibung vorhandener Dateien

## Voraussetzungen

- Python 3.6 oder höher
- Benötigte Python-Bibliothek: colorama (für farbige Konsolenausgabe)
- Betriebssystem: Windows, macOS oder Linux

## Installation

1. Skript herunterladen und in einer Datei speichern, z.B. copy_for_vl_export.py

2. Benötigte Bibliothek installieren:
   pip install colorama

## Verwendung

### Aufruf des Skripts

Das Skript benötigt zwei Parameter:
- AC-Nummer (Archivierungsprojekt-Kennung)
- Datenträger-ID (eindeutige Kennung des Datenträgers)

python copy_for_vl_export.py <AC_NUMMER> <DATENTRÄGER_ID>

Beispiel:
python copy_for_vl_export.py AC-2024-001 DISK-12345

Das Skript erwartet folgende Verzeichnisstruktur:

~/Documents/data/<AC_NUMMER>/<DATENTRÄGER_ID>/
```text
├── 0_<ID>_picture-carrier/
│   └── *.tif
├── 2_<ID>_extracted-files/
│   ├── 2_<ID>_extracted-files.content
│   └── 2_<ID>_extracted-files_tree.txt
├── 3_<ID>_for-transfer/
│   ├── 3_<ID>_for-transfer.index
│   └── files/
│       └── [beliebige Dateien]
└── 4_<ID>_VL/ (Zielordner, muss bereits existieren)
```

## Ablauf im Detail

Das Skript führt folgende Schritte aus:

### 1. Pfadvalidierung
- Überprüft, ob alle erforderlichen Quell- und Zielordner existieren
- Bei fehlenden Ordnern wird das Skript mit einer Fehlermeldung beendet

### 2. TIF-Dateien kopieren
- Durchsucht den 0_<ID>_picture-carrier-Ordner nach .tif-Dateien
- Kopiert jede gefundene TIF-Datei in den VL-Zielordner
- Bestehende Dateien werden nicht überschrieben

### 3. content-Datei kopieren
- Kopiert die .content-Datei aus dem extracted-files-Ordner
- Enthält Metadaten über die extrahierten Dateien

### 4. tree-Datei kopieren
- Kopiert die _tree.txt-Datei aus dem extracted-files-Ordner
- Enthält die Verzeichnisstruktur der extrahierten Daten

### 5. index-Datei kopieren
- Kopiert die .index-Datei aus dem for-transfer-Ordner
- Enthält Index-Informationen für den Transfer

### 6. Files-Ordner kopieren
- Kopiert den gesamten files-Ordner rekursiv in den VL-Zielordner
- Bei bereits existierendem Zielordner wird der Vorgang übersprungen

### 7. Zielordner öffnen (optional)
- Nach Abschluss kann der Zielordner interaktiv geöffnet werden
- Unterstützt Windows (explorer), macOS (finder) und Linux (xdg-open)

## Ausgabe

Das Skript gibt während der Ausführung farbige Statusmeldungen aus:

- Grün: Erfolgreich kopierte Dateien
- Gelb: Warnungen (fehlende Dateien/Ordner, bereits existierende Dateien)
- Rot: Fehlermeldungen
- Cyan/Magenta: Überschriften und Strukturinformationen

## Sicherheitshinweise

1. Keine Überschreibung: Bereits im Zielordner existierende Dateien werden nicht überschrieben
2. Prüfung vorher: Alle Quellordner werden vor dem Kopieren auf Existenz geprüft
3. Zielordner muss existieren: Der VL-Zielordner (4_<ID>_VL) muss vorab manuell erstellt werden
4. Nur Kopieren: Das Skript löscht keine Dateien, es werden nur Kopien erstellt

## Fehlerbehandlung

Das Skript behandelt verschiedene Fehlersituationen:

- Fehlende Parameter: Ausgabe einer Fehlermeldung mit Hinweis zur korrekten Verwendung
- Fehlende Ordner: Ausgabe einer Fehlermeldung und Abbruch des Skripts
- Fehlende Dateien: Ausgabe einer Warnung, Vorgang wird fortgesetzt
- Bereits existierende Dateien: Ausgabe einer Warnung, Datei wird nicht überschrieben

## Beispiel für die Ausgabe

Werte aus der Kommandozeile erhalten: AC=AC-2024-001, ID=DISK-12345

----------------------------------------
  DATEIEN FUER VL-EXPORT KOPIEREN
----------------------------------------

Pfade definieren
  BasePath: C:\Users\user\Documents\data\AC-2024-001
  MainFolder: C:\Users\user\Documents\data\AC-2024-001\DISK-12345
  DestinationFolder: C:\Users\user\Documents\data\AC-2024-001\DISK-12345\4_DISK-12345_VL

Pfade validieren
Alle Pfade vorhanden

Kopiervorgang starten

1. TIF-Dateien kopieren
  Kopiert: image001.tif
  Kopiert: image002.tif

2. content-Datei kopieren
  Kopiert: 2_DISK-12345_extracted-files.content

3. tree-Datei kopieren
  Kopiert: 2_DISK-12345_extracted-files_tree.txt

4. index-Datei kopieren
  Kopiert: 3_DISK-12345_for-transfer.index

5. Files-Ordner kopieren
  Files-Ordner komplett kopiert

Zielordner oeffnen? (j/n): j
Zielordner geoeffnet

----------------------------------------
  KOPIERVORGANG ABGESCHLOSSEN
----------------------------------------

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT

---

**Hinweis**: Dieses Skript ist speziell für die Anforderungen digitaler Archivierungsprojekte entwickelt worden. Stellen Sie sicher, dass der VL-Zielordner (4_<ID>_VL) vor der Ausführung manuell erstellt wurde.