# ODF-Bereinigungs-Skript (Cleanup)

Dieses Skript dient der automatisierten Bereinigung von technischen Zwischendateien innerhalb eines digitalen Archivierungsworkflows. Es identifiziert und entfernt gezielt ODF-Dateien (.odt), die während des Normalisierungsprozesses lediglich als Brückentechnologie für den PDF/A-Export erstellt wurden, sofern die ursprüngliche Quelldatei noch vorhanden ist.

Das Skript stellt sicher, dass der Archivbestand übersichtlich bleibt und keine redundanten Zwischenschritte in die Langzeitarchivierung übernommen werden.

---

## Hauptfunktionen

*   **Intelligente Identifizierung:** Nutzt eine Namenslogik (Pattern Matching), um Derivate zu finden, die nach dem Muster "Originaldatei.originalendung.odt" benannt sind.
*   **Sicherheitsabgleich:** Eine .odt-Datei wird nur dann zur Löschung vorgeschlagen, wenn die dazugehörige Quelldatei (z.B. .doc, .rtf) im selben Verzeichnis zweifelsfrei existiert.
*   **Sicherheitsmodus (DRY_RUN):** Das Skript verfügt über einen Testlauf-Modus, in dem lediglich protokolliert wird, welche Dateien gelöscht würden, ohne tatsächliche Änderungen am Dateisystem vorzunehmen.
*   **Detaillierte Protokollierung:** Erzeugt ein umfassendes Log-File (..._delete-converted-odfs.log), das alle erfolgreichen Löschungen sowie eventuelle Fehler dokumentiert.
*   **Interaktive Bestätigung:** Im Echt-Modus fordert das Skript vor dem eigentlichen Löschvorgang eine explizite Bestätigung durch den Benutzer an.

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Standard-Bibliotheken: Nutzt pathlib, os und datetime (keine externen Pakete erforderlich).

---

## Konfiguration

Im Kopfbereich des Skripts kann das Verhalten über die Variable `DRY_RUN` gesteuert werden:

    DRY_RUN = False  # Auf True setzen für eine Simulation ohne Löschvorgang

Das Skript erkennt Zwischendateien basierend auf folgenden Original-Endungen:
`.doc`, `.docx`, `.rtf`, `.wpd`, `.wps`, `.dot`, `.dotx`, `.wbk`

---

## Erwartete Ordnerstruktur

Das Skript operiert innerhalb der Transfer-Stufe (Stufe 3) des Workflows:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- ARBEITSVERZEICHNIS
                    └── 3_[ID]_delete-converted-odfs.log

---

## Ausführung

Das Skript wird über die Kommandozeile unter Angabe der AC-Nummer und der Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:

    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python cleanup_odf.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1.  **Pfadvalidierung:** Prüfung der Projektverzeichnisse.
2.  **Dateiscan:** Rekursive Suche im Ordner `files/` nach .odt-Dateien.
3.  **Pattern-Check:** Extraktion des Dateistamms und Abgleich mit der Liste der Originalformate.
4.  **Listen-Generierung:** Anzeige aller zur Löschung identifizierten Dateien im Terminal.
5.  **Löschvorgang:** Nach Benutzerbestätigung werden die Dateien entfernt.
6.  **Logging:** Erstellung des Abschlussberichts im übergeordneten Verzeichnis.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT