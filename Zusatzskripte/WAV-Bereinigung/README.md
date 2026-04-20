# WAV-Bereinigungs-Skript (Cleanup)

Dieses Skript dient der gezielten Entfernung von WAV-Dateien, die während des Archivierungsworkflows lediglich als technische Derivate (Normalisierungskopien) erstellt wurden. Es erkennt automatisch, ob eine WAV-Datei das ursprüngliche Original oder ein generiertes Derivat ist, und löscht letzteres, um Speicherplatz zu sparen und die Datenstruktur vor der Langzeitarchivierung zu bereinigen.

Das Skript ist als Sicherheitsmaßnahme so programmiert, dass es Derivate nur dann löscht, wenn die ursprüngliche Quelldatei im selben Verzeichnis zweifelsfrei vorhanden ist.

---

## Hauptfunktionen

*   **Intelligente Derivat-Erkennung:** Identifiziert Dateien nach dem Namensschema "Originalname.Originalendung.wav" (z.B. "interview.mp3.wav").
*   **Existenz-Validierung:** Eine generierte WAV-Datei wird nur dann zur Löschung vorgemerkt, wenn die im Dateinamen referenzierte Originaldatei (z.B. die .mp3 oder .flac) tatsächlich im selben Ordner existiert.
*   **Vollständige Rekursion:** Durchsucht den gesamten Projektordner inklusive aller Unterverzeichnisse.
*   **Sicherheitsabfrage:** Vor dem eigentlichen Löschvorgang wird dem Benutzer eine Liste aller gefundenen Derivate angezeigt. Der Vorgang startet erst nach einer expliziten Bestätigung (j/n).
*   **Detaillierte Protokollierung:** Erstellt ein umfassendes Log-File (..._delete-converted-wavs.log), das alle erfolgreichen Löschungen sowie eventuelle Dateisystemfehler dokumentiert.

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Standard-Bibliotheken: Nutzt pathlib, os und datetime (keine externen Pakete erforderlich).

---

## Konfiguration

Das Skript gleicht Dateien mit einer internen Liste unterstützter Audio-Originalformate ab. Diese Liste umfasst standardmäßig:
`.aiff`, `.flac`, `.ogg`, `.wav` (als Original), `.m4a`, `.wma`, `.aac`, `.mp3`

---

## Erwartete Ordnerstruktur

Das Skript operiert innerhalb der Transfer-Stufe (Stufe 3) des Workflows:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- ARBEITSVERZEICHNIS
                    └── 3_[ID]_delete-converted-wavs.log

---

## Ausführung

Das Skript wird über die Kommandozeile unter Angabe der AC-Nummer und der Datenträger-ID gestartet (ideal über eine start.bat).

Beispielhafter Aufruf:

    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python cleanup_wav.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1.  **Validierung:** Prüfung der Pfade und der Ordnerstruktur.
2.  **Scan:** Rekursive Suche nach .wav-Dateien, deren Dateiname auf ein Derivat hindeutet.
3.  **Abgleich:** Prüfung, ob das Original (Stamm-Dateiname) physisch im selben Verzeichnis liegt.
4.  **Bestätigung:** Auflistung der Kandidaten im Terminal und Warteschleife für die Benutzereingabe.
5.  **Löschvorgang:** Entfernung der Derivate bei Bestätigung.
6.  **Abschluss:** Erstellung des Lösch-Protokolls im übergeordneten Verzeichnis und Option zum Öffnen des Zielordners im Explorer.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT