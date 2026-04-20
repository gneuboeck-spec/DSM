# PREMIS v3 XML-Generator (Digital Preservation)

Dieses Skript ist das finale Dokumentationswerkzeug im Archivierungsworkflow. Es generiert eine valide PREMIS v3 (Preservation Metadata: Implementation Strategies) XML-Datei, die den gesamten Lebenszyklus eines digitalen Objekts – von der physischen Quelle bis zum fertigen Archivpaket – lizenskonform und maschinenlesbar dokumentiert.

Das Skript integriert eine intelligente "Medien-Weiche", die automatisch erkennt, ob es sich um USB-Sticks, Disketten oder optische Datenträger handelt, und extrahiert die entsprechenden forensischen Metadaten.

---

## Hauptfunktionen

*   **Automatisierte Medien-Erkennung:**
    *   **FTK-Parser:** Extrahiert Hardware-Informationen (z.B. Tableau Write-Blocker), Seriennummern und Verifikations-Hashes aus forensischen USB-Images.
    *   **Redumper-Parser:** Liest Metadaten aus Audio-CD/DVD-Rips und übernimmt die Hardware-Kennung des optischen Laufwerks.
    *   **Greaseweazle-Parser:** Dokumentiert Flux-Stream-Parameter und Host-Tools für Disketten-Images.
    *   **ddrescue-Support:** Erkennt HDD-Clones anhand von Mapfiles.
*   **GND- & LOBID-Integration:**
    *   Ermöglicht die interaktive Suche nach Urhebern in der Deutschen Nationalbibliothek (DNB).
    *   Nutzt die lobid-gnd API als robusten Fallback, um Namen, Lebensdaten und Berufe zur eindeutigen Identifikation zu verknüpfen.
*   **Hierarchische PREMIS-Struktur:**
    *   **Objects:** Dokumentiert Träger-Fotos (Stage 0), Disk-Images (Stage 1), extrahierte Dateien (Stage 3) und Derivate.
    *   **Events:** Protokolliert Imaging, Extraktion, Metadaten-Erfassung, Konvertierung und Packaging.
    *   **Agents:** Verknüpft Software-Tools, Hardware und Personen (Urheber).
    *   **Rights:** Erstellt Copyright-Statements basierend auf den Urheberdaten.
*   **Schema-Validierung:** Enthält eine integrierte Validierung gegen das offizielle XSD-Schema der Library of Congress (LOC), um die Standardkonformität der Ausgabe sicherzustellen.
*   **XSD-Compliance:** Erzwingt die strikte Einhaltung der Element-Reihenfolge (Objects -> Events -> Agents -> Rights), die für valide PREMIS-Dateien zwingend erforderlich ist.

---

## Technische Voraussetzungen

*   **Python:** Version 3.10 oder neuer empfohlen.
*   **Bibliotheken:**
    *   `lxml`: Für die performante XML-Generierung und XSD-Validierung.
    *   `requests`: Für die API-Abfragen (GND/LOBID).
    ```bash
    pip install lxml requests urllib3
    ```

---

## Erwartete Ordnerstruktur

Das Skript aggregiert Daten aus fast allen Projektstufen:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                ├── 0_[ID]_picture-carrier/        <-- Träger-Fotos
                ├── 1_[ID]_image-LZA/
                │   └── logfiles/                   <-- Imaging-Logs (FTK, Redumper etc.)
                ├── 3_[ID]_for-transfer/
                │   └── 5_[ID]_LZA.index           <-- Metadaten-Quelle (filetrove)
                └── 5_[ID]_LZA/
                    ├── *.img                       <-- Das finale Archiv-Image
                    └── logfiles/                   <-- ZIELORDNER (premis.xml)

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

1. **Urheber-Identifikation:** Das Skript bittet um die Eingabe eines Namens und sucht diesen in der GND. Ein passender Eintrag kann interaktiv ausgewählt werden.
2. **Log-Analyse:** Die forensischen Logs in Stufe 1 werden analysiert, um Hardware, Software und Erstellungsdatum zu ermitteln.
3. **Objekt-Generierung:** Träger, Images und Dateien werden als PREMIS-Objekte angelegt. Dabei werden Metadaten aus der .index-Datei (filetrove) direkt in die Extension-Felder eingebettet.
4. **Event-Mapping:** Alle Prozessschritte des Workflows werden mit den beteiligten Agenten verknüpft.
5. **XML-Finishing:** Die Elemente werden gemäß XSD-Schema sortiert und als UTF-8 XML gespeichert.
6. **Validierung:** Das Skript lädt das offizielle Schema herunter und validiert die Datei live.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT