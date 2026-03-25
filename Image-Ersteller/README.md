# LZA Derivation Image Creator

Dieses Python-Skript automatisiert die Erstellung von Archiv-Images (TAR) für die Langzeitarchivierung (LZA). Es validiert vordefinierte Pfadstrukturen, packt Quelldateien verlustfrei in ein Archiv, berechnet SHA-512 Checksummen und generiert einen Metadaten-Block im PREMIS-Format für die Dokumentation.

## Inhaltsverzeichnis
1. [Features](#features)
2. [Voraussetzungen](#voraussetzungen)
3. [Strukturvorgaben](#strukturvorgaben)
4. [Verwendung](#verwendung)
5. [Ausgabe & Metadaten](#ausgabe--metadaten)
6. [Lizenz](#lizenz)

## Features
- **Automatisierte Pfadgenerierung**: Erstellt Zielordner basierend auf AC-Nummer und Datenträger-ID.
- **TAR-Archivierung**: Packt den Inhalt des Transfer-Ordners (`files/`) in ein `.img` (Tape Archive).
- **Integritätsprüfung**: Berechnet automatisch einen SHA-512 Hash der erstellten Image-Datei.
- **LZA-Logging**: Erstellt ein detailliertes Logfile inklusive eines maschinenlesbaren **PREMIS DATA BLOCK** für die Metadaten-Übernahme.
- **Sicherheitsabfrage**: Verhindert das versehentliche Überschreiben bestehender Images.
- **Komfort-Funktion**: Bietet an, den Zielordner nach Abschluss direkt im Dateimanager zu öffnen.

## Voraussetzungen
- **Python 3.x**
- Es werden keine externen Bibliotheken benötigt (Standardmodule: `pathlib`, `tarfile`, `hashlib`, `logging`, `subprocess`).

## Strukturvorgaben
Das Skript arbeitet mit einer Pfadlogik im Home-Verzeichnis des Nutzers:

### Eingabestruktur (Quelle)
Die Dateien müssen zwingend hier liegen:  
`~/Documents/data/[AC-Nummer]/[ID]/3_[ID]_for-transfer/files/`

### Ausgabestruktur (Ziel)
Das Skript erstellt diesen Ordner:  
`~/Documents/data/[AC-Nummer]/[ID]/5_[ID]_LZA/`  
Darin enthalten: Image (`.img`) und Protokoll (`.log`).

## Verwendung

### Option 1: Kommandozeile
Übergib die AC-Nummer und die ID direkt beim Aufruf:  
`python skriptname.py AC12345678 ID001`

### Option 2: Interaktiver Modus
Starte das Skript ohne Parameter, um die Daten nacheinander einzugeben:  
- AC-Nummer eingeben: AC12345678  
- Datenträger-ID eingeben: ID001

## Ausgabe & Metadaten
Nach der Erstellung schreibt das Skript technische Metadaten in das Log. Beispiel des PREMIS-Blocks:

--- PREMIS DATA BLOCK START ---  
executingAgent: image_creator.py v1.0  
objectIdentifier: 5_ID001_LZA_derivation-image.img  
size: [DATEIGRÖSSE IN BYTES]  
formatName: TAR (Tape Archive)  
pronomId: x-fmt/265  
fixity-sha512: [DER_BERECHNETE_HASHWERT]  
--- PREMIS DATA BLOCK END ---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT