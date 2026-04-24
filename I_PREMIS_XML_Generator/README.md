# Skript I: PREMIS v3 XML-Generator (Digital Preservation)

Dieses Skript ist das zentrale Dokumentationswerkzeug im Archivierungsworkflow. Es generiert eine valide PREMIS v3 (Preservation Metadata: Implementation Strategies) XML-Datei, die den gesamten Lebenszyklus eines digitalen Objekts – von der physischen Quelle bis zum fertigen Archivpaket – normgerecht und maschinenlesbar dokumentiert. 

Das Skript verfügt über eine intelligente "Medien-Weiche" (Version 22.3), die automatisch erkennt, ob es sich um USB-Sticks (FTK), Disketten (Greaseweazle), Festplatten (ddrescue) oder optische Datenträger (Redumper) handelt, und extrahiert die entsprechenden forensischen Metadaten direkt aus den jeweiligen Logs.

---

## Hauptfunktionen

*   **Automatisierte Medien-Erkennung (Forensic Context):**
    *   **FTK-Parser:** Extrahiert Hardware-Informationen (z.B. Tableau Write-Blocker), Seriennummern und Verifikations-Hashes aus forensischen USB-Images.
    *   **Redumper-Parser:** NEU – Liest Metadaten aus Audio-CD/DVD-Rips (Redumper) und übernimmt die Hardware-Kennung des optischen Laufwerks.
    *   **Greaseweazle-Parser:** Dokumentiert Flux-Stream-Parameter, Heads/Cylinders und Host-Tools für Disketten-Images.
    *   **ddrescue-Support:** Erkennt HDD-Clones anhand von Mapfiles.
*   **Normdaten-Integration (GND & LOBID):**
    *   Interaktive Suche nach Urhebern in der Deutschen Nationalbibliothek (DNB) via SRU-Schnittstelle.
    *   **LOBID-Fallback:** Nutzt bei Erreichbarkeitsproblemen der DNB automatisch die lobid-gnd API (hbz), um Namen, Lebensdaten und Berufe zur Identifikation zu verknüpfen.
*   **Hierarchische PREMIS-Struktur:**
    *   **Objects:** Dokumentiert Träger-Fotos (Stage 0), Disk-Images (Stage 1), extrahierte Originaldateien (Stage 2) und den technischen Index (Stage 3).
    *   **Events:** Protokolliert Imaging, Extraktion, Metadaten-Erfassung, Konvertierung und Packaging.
    *   **Agents:** Verknüpft Software-Tools (Siegfried, Brunnhilde, Python-Scripts), Hardware und Personen (Urheber).
    *   **Rights:** Erstellt Copyright-Statements basierend auf den Urheberdaten.
*   **Schema-Validierung & XSD-Compliance:**
    *   Erzwingt die strikte Einhaltung der Element-Reihenfolge (Objects -> Events -> Agents -> Rights).
    *   Integrierte Live-Validierung gegen das offizielle PREMIS-Schema der Library of Congress (LOC).

---

## TREE-Struktur & Dateipfade (Zustand während Phase 4)

Das Skript aggregiert Daten aus allen bisherigen Projektstufen, um die lückenlose Provenienz zu beweisen:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/          <-- QUELLE (Hardware-Fotos .tif)
├── 1_[ID]_image-LZA/                <-- QUELLE (Disk-Images .img / .001 / .bin / .dd)
│   └── logfiles/                    <-- QUELLE (Imaging-Logs .txt / .csv)
├── 2_[ID]_extracted-files/          <-- QUELLE (Siegfried.csv & Brunnhilde-Berichte)
├── 3_[ID]_for-transfer/             <-- QUELLE (Technischer Index .index)
└── 5_[ID]_LZA/                      <-- ARBEITSBEREICH & ZIEL (Archiv-Staging)
    └── logfiles/                    <-- ZIEL (Hier wird die Dokumentation erstellt)
        └── 5_[ID]_LZA_premis.xml    <-- Das finale PREMIS-Hauptdokument

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt `lxml` (für XML-Sortierung/Validierung) und `requests` (für GND-Abfragen).
    pip install lxml requests urllib3

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf:
    python generate_premis.py AC_0001 ID_001

### Ablauf der Ausführung

1.  **Urheber-Wahl:** Das Skript bittet um die Eingabe eines Namens und sucht diesen in der GND. Ein passender Eintrag kann interaktiv ausgewählt werden.
2.  **Referenz-Analyse:** Imaging-Logs in Stufe 1 werden gescannt, um den Medientyp (USB, CD, Floppy, HDD) zu bestimmen.
3.  **Objekt-Erstellung:** Hashes und Metadaten aller Objekte (aus 0, 1, 2 und 3) werden als PREMIS-Objekte angelegt.
4.  **Event-Verknüpfung:** Die gesamte Kette (Imaging -> Extraktion -> Metadaten -> Konvertierung) wird dokumentiert.
5.  **Reihenfolge-Fix:** Das Skript sortiert alle XML-Elemente XSD-konform um (Objects -> Events -> Agents -> Rights).
6.  **Validierung:** Die finale Datei wird live gegen den LOC-Standard geprüft und in Stufe 5 gespeichert.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT