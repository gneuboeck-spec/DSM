# Data Cleanup Tool für Archivierungsprozesse

Ein Python-Skript zur automatisierten Bereinigung von Zwischendateien im Rahmen von digitalen Archivierungsprojekten. Das Tool identifiziert und löscht sicher konvertierte ODF-Dateien sowie temporäre WAV-Dateien.

## Inhaltsverzeichnis

- [Funktionsumfang](#funktionsumfang)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Funktionsweise im Detail](#funktionsweise-im-detail)
- [Konfiguration](#konfiguration)
- [Logging](#logging)
- [Sicherheitshinweise](#sicherheitshinweise)
- [Fehlerbehandlung](#fehlerbehandlung)
- [Lizenz](#lizenz)

## Funktionsumfang

- Automatische Pfadvalidierung basierend auf AC-Nummer und Datenträger-ID
- Intelligente Erkennung von ODF-Zwischendateien (Dateien mit `.odt`-Endung, die aus Originaldokumenten konvertiert wurden)
- Sicheres Löschen von konvertierten WAV-Dateien unter Beibehaltung der Original-Audiodateien
- Testlauf-Modus für ODF-Löschungen (konfigurierbar)
- Detaillierte Protokollierung aller Löschvorgänge
- Interaktives Menü für benutzerfreundliche Bedienung
- Optionaler Ordner-Öffner nach Abschluss der Aktionen

## Voraussetzungen

- Python 3.6 oder höher
- Betriebssystem: Windows, macOS oder Linux
- Keine externen Python-Bibliotheken erforderlich (nur Standardbibliothek)

## Installation

1. Skript herunterladen:
   
   git clone [repository-url]
   oder
   curl -O [skript-url]


2. Ausführungsberechtigungen setzen (Linux/macOS):
   
   chmod +x data_cleanup.py


## Verwendung

### Aufruf des Skripts

Das Skript benötigt zwei Parameter:
- **AC-Nummer** (Archivierungsprojekt-Kennung)
- **Datenträger-ID** (eindeutige Kennung des Datenträgers)


python data_cleanup.py <AC_NUMMER> <DATENTRÄGER_ID>


Beispiel:

python data_cleanup.py AC-2024-001 DISK-12345


Das Skript erwartet folgende Verzeichnisstruktur:

~/Documents/data/<AC_NUMMER>/<DATENTRÄGER_ID>/
└── 3_<DATENTRÄGER_ID>_for-transfer/
    └── files/
        └── [zu bereinigende Dateien]


### Menüoptionen

Nach erfolgreicher Pfadvalidierung erscheint ein interaktives Menü:


  Wählen Sie eine Aufräum-Aktion:

  1 - Zwischendateien (ODF) löschen
  2 - Konvertierte WAV-Dateien löschen
  Q - Beenden


**Option 1: ODF-Zwischendateien löschen**
- Identifiziert `.odt`-Dateien, die aus Originaldokumenten konvertiert wurden
- Prüft, ob die Originaldatei noch existiert
- Löscht nur dann die ODF-Datei

**Option 2: Konvertierte WAV-Dateien löschen**
- Identifiziert WAV-Dateien, die aus anderen Audioformaten konvertiert wurden
- Unterstützte Originalformate: `.aiff`, `.flac`, `.ogg`, `.wav`, `.m4a`, `.wma`, `.aac`, `.mp3`
- Löscht die WAV-Datei, wenn das Original noch vorhanden ist

## Funktionsweise im Detail

### ODF-Zwischendateien löschen

Das Skript durchsucht rekursiv den `files`-Ordner nach `.odt`-Dateien. Für jede gefundene Datei wird geprüft, ob:

1. Der Dateiname (ohne `.odt`) auf eine der folgenden Endungen endet: `.doc`, `.docx`, `.rtf`, `.wpd`, `.wps`, `.dot`, `.dotx`, `.wbk`
2. Die ursprüngliche Quelldatei im selben Verzeichnis existiert

Beispiel:
- Gefunden: `dokument.doc.odt`
- Original: `dokument.doc`
- Wenn Original existiert → ODF-Datei wird zur Löschung vorgemerkt

### Konvertierte WAV-Dateien löschen

Das Skript identifiziert WAV-Dateien, die durch Konvertierung aus anderen Audioformaten entstanden sind:

1. Sucht nach allen `.wav`-Dateien
2. Analysiert den Dateinamen auf Muster wie `original.flac.wav`
3. Prüft, ob die Original-Audiodatei noch vorhanden ist
4. Löscht die WAV-Datei bei vorhandenem Original

## Konfiguration

Am Anfang des Skripts können folgende Parameter angepasst werden:

DELETE_ODF_DRY_RUN = False  # True = nur Testlauf (keine tatsächlichen Löschungen)

original_extensions = {
    ".doc", ".docx", ".rtf", ".wpd", ".wps", ".dot", ".dotx", ".wbk"
}

SOURCE_AUDIO_EXTENSIONS_FOR_WAV_CLEANUP = {
    ".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"
}


## Logging

Das Skript erstellt für jede Aktion eine separate Log-Datei im `for-transfer`-Ordner:

- **ODF-Löschung**: `3_<ID>_for-transfer_delete-converted-odfs.log`
- **WAV-Löschung**: `3_<ID>_for-transfer_delete-converted-wavs.log`

Jede Log-Datei enthält:
- Zeitstempel der Ausführung
- Liste der erfolgreich gelöschten Dateien
- Fehler beim Löschen (falls aufgetreten)
- Im Testlauf: Liste der Dateien, die gelöscht worden wären

## Sicherheitshinweise

1. **Bestätigung erforderlich**: Vor jedem Löschvorgang müssen Sie die Aktion mit `j` bestätigen
2. **Testlauf-Modus**: Für ODF-Löschungen kann der Testlauf aktiviert werden (`DELETE_ODF_DRY_RUN = True`)
3. **Keine automatischen Löschungen**: Alle Aktionen erfordern manuelle Bestätigung
4. **Prüfung auf Originaldateien**: Es werden nur Dateien gelöscht, deren Originale noch existieren
5. **Ausführliche Protokollierung**: Alle Aktionen werden detailliert protokolliert

## Fehlerbehandlung

Das Skript behandelt verschiedene Fehlersituationen:

- **Fehlende Pfade**: Detaillierte Fehlermeldung und Abbruch
- **Fehlende Parameter**: Hinweis auf korrekte Verwendung
- **Löschfehler**: Einzelfehler werden protokolliert, der Vorgang wird fortgesetzt
- **Schreibfehler bei Logs**: Fehlermeldung wird ausgegeben, Skript läuft weiter

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT

---

**Hinweis**: Dieses Tool ist speziell für die Anforderungen digitaler Archivierungsprojekte entwickelt worden. Stellen Sie sicher, dass Sie vor der Verwendung eine Sicherungskopie Ihrer Daten haben.
```
