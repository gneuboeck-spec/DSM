# Aufräum-Skript für Zwischendateien (ODF & WAV)

Dieses Skript dient der gezielten Bereinigung von technischen Zwischendateien in der VL-Stufe (Stufe 4). Es entfernt Derivate, die während des Konvertierungsprozesses lediglich als Brückentechnologie erstellt wurden (z. B. ODF-Dateien als Zwischenschritt zum PDF/A-Export), um den Archivbestand schlank und übersichtlich zu halten.

Das Skript ist interaktiv gestaltet und erlaubt es dem Benutzer, gezielt verschiedene Kategorien von Zwischendateien zu löschen.

---

## Hauptfunktionen

*   Interaktives Menü: Wahlweise Löschung von ODF-Zwischendateien oder konvertierten WAV-Dateien.
*   Intelligente ODF-Bereinigung: Identifiziert .odt, .ods oder .odp Dateien, die aus alten Office-Formaten (z. B. .doc, .docx, .rtf) erzeugt wurden. Eine Löschung erfolgt nur, wenn die ursprüngliche Quelldatei im selben Verzeichnis noch existiert.
*   WAV-Bereinigung: Identifiziert .wav-Dateien, die aus anderen Audioformaten (z. B. .mp3, .flac, .m4a) generiert wurden, und entfernt diese, sofern das Original vorhanden ist.
*   Sicherheitsmodus (Dry-Run): Für die ODF-Bereinigung kann ein Testlauf aktiviert werden, der lediglich protokolliert, was gelöscht würde.
*   Protokollierung in Stufe 5: Alle Löschvorgänge (oder Testläufe) werden detailliert in Log-Dateien im LZA-Verzeichnis (Stufe 5 / logfiles) dokumentiert.
*   Validierung: Das Skript prüft vorab die Existenz aller Pfade und stellt sicher, dass der Log-Ordner in Stufe 5 vorhanden ist.

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Standard-Bibliotheken: Nutzt pathlib, os und subprocess (keine externen Installationen erforderlich).

---

## Konfiguration im Skript

Im Header des Skripts kann der Testlauf-Modus global gesteuert werden:

    DELETE_ODF_DRY_RUN = False  # Auf True setzen für eine Simulation

### Erwartete Ordnerstruktur

Das Skript arbeitet auf der VL-Stufe (4) und schreibt Logs in die LZA-Stufe (5):

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                ├── 4_[ID]_VL/
                │   └── files/                      <-- ARBEITSVERZEICHNIS (Löschung)
                └── 5_[ID]_LZA/
                    └── logfiles/                   <-- LOG-ZIEL (Protokolle)

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python cleanup_intermediate.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Das Skript prüft die Pfade und erstellt ggf. den Log-Ordner in Stufe 5.
2. Menü-Auswahl: Der Benutzer wählt zwischen ODF-Bereinigung (Option 1) oder WAV-Bereinigung (Option 2).
3. Analyse: Das System sucht rekursiv nach Dateien, die dem Muster "Originalname.originalendung.zwischenendung" entsprechen.
4. Bestätigung: Vor dem tatsächlichen Löschen wird eine Liste der gefundenen Dateien angezeigt und eine explizite Bestätigung (j/n) angefordert.
5. Löschung & Logging: Die Dateien werden entfernt und der Vorgang wird mit Zeitstempel in den LZA-Logordner geschrieben.
6. Abschluss: Das Skript kehrt zum Menü zurück oder öffnet auf Wunsch den Zielordner im Explorer.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT