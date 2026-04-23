# Skript I: PREMIS v3 XML-Generator (Digital Preservation)

Dieses Skript ist das zentrale Dokumentationswerkzeug im Archivierungsworkflow. Es generiert eine valide PREMIS v3 (Preservation Metadata: Implementation Strategies) XML-Datei, die den gesamten Lebenszyklus eines digitalen Objekts – von der physischen Quelle bis zum fertigen Archivpaket – normgerecht und maschinenlesbar dokumentiert. 

Das Skript verfügt über eine intelligente "Medien-Weiche", die automatisch erkennt, ob es sich um USB-Sticks, Disketten oder optische Datenträger handelt, und extrahiert die entsprechenden forensischen Metadaten direkt aus den jeweiligen Logs.

---

## Hauptfunktionen

*   **Automatisierte Medien-Erkennung (Forensic Context):**
    *   **FTK-Parser:** Extrahiert Hardware-Informationen (z.B. Tableau Write-Blocker), Seriennummern und Verifikations-Hashes aus forensischen USB-Images.
    *   **Redumper-Parser:** Liest Metadaten aus Audio-CD/DVD-Rips (Redumper) und übernimmt die Hardware-Kennung des optischen Laufwerks.
    *   **Greaseweazle-Parser:** Dokumentiert Flux-Stream-Parameter, Heads/Cylinders und Host-Tools für Disketten-Images.
    *   **ddrescue-Support:** Erkennt HDD-Clones anhand von Mapfiles.
*   **Normdaten-Integration (GND & LOBID):**
    *   Interaktive Suche nach Urhebern in der Deutschen Nationalbibliothek (DNB) via SRU-Schnittstelle.
    *   **LOBID-Fallback:** Nutzt bei Erreichbarkeitsproblemen der DNB automatisch die lobid-gnd API (hbz), um Namen, Lebensdaten und Berufe zur Identifikation zu verknüpfen.
*   **Hierarchische PREMIS-Struktur:**
    *   **Objects:** Dokumentiert Träger-Fotos (Stage 0), Disk-Images (Stage 1), extrahierte Dateien (Stage 3/5) und Derivate inklusive technischer Metadaten aus dem filetrove-Index.
    *   **Events:** Protokolliert Imaging, Extraktion, Metadaten-Erfassung, Konvertierung und Packaging.
    *   **Agents:** Verknüpft Software-Tools (Siegfried, Brunnhilde, Python-Scripts), Hardware und Personen (Urheber).
    *   **Rights:** Erstellt Copyright-Statements basierend auf den Urheberdaten.
*   **Schema-Validierung & XSD-Compliance:**
    *   Erzwingt die strikte Einhaltung der Element-Reihenfolge (Objects -> Events -> Agents -> Rights).
    *   Integrierte Live-Validierung gegen das offizielle PREMIS-Schema der Library of Congress (LOC).

---

## TREE-Struktur & Dateipfade (Phase 4)

Das Skript aggregiert Daten aus fast allen Projektstufen, um die lückenlose Provenienz zu beweisen:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/          <-- QUELLE (Hardware-Fotos .tif)
├── 1_[ID]_image-LZA/logfiles/       <-- QUELLE (Imaging-Logs .txt / .csv)
├── 3_[ID]_for-transfer/             <-- QUELLE (Technischer Index .index)
└── 5_[ID]_LZA/                      <-- ARBEITSBEREICH (Archiv-Staging)
    ├── *.img / *.001 / *.bin        <-- Die zu dokumentierenden Images
    └── logfiles/                    <-- ZIEL (Archiv-Dokumentation)
        └── 5_[ID]_LZA_premis.xml    <-- Das finale PREMIS-Hauptdokument

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt `lxml` (für XML-Sortierung/Validierung) und `requests` (für GND-Abfragen).
    pip install lxml requests urllib3

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python generate_premis.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1.  **Urheber-Wahl:** Das Skript fordert zur Eingabe des Urhebernamens auf und führt eine Live-Suche in der GND durch.
2.  **Referenz-Analyse:** Imaging-Logs in Stufe 1 werden gescannt, um den Medientyp und die Hardware-Agenten zu identifizieren.
3.  **Objekt-Erstellung:** Hashes und Metadaten der Hardware-Fotos, Disk-Images und Nutzdaten werden als PREMIS-Objekte angelegt.
4.  **Event-Verknüpfung:** Die gesamte Prozesskette (Imaging -> Extraktion -> Indexierung) wird chronologisch als Events dokumentiert.
5.  **Reihenfolge-Fix:** Das Skript sortiert alle XML-Elemente XSD-konform um.
6.  **Validierung:** Die finale Datei wird live gegen den LOC-Standard geprüft und in Stufe 5 gespeichert.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT