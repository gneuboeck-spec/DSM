# Skript F: Aufräum-Skript für Zwischendateien (ODF & WAV)

Dieses Skript dient der gezielten Bereinigung von technischen Zwischendateien in der VL-Stufe (Stufe 4). Es entfernt Derivate, die während des Konvertierungsprozesses lediglich als Brückentechnologie erstellt wurden (z. B. ODF-Dateien als Zwischenschritt zum PDF/A-Export oder WAV-Dateien als Zwischenschritt für MP3), um den Archivbestand schlank und übersichtlich zu halten.

Das Skript ist interaktiv gestaltet und erlaubt es dem Benutzer, gezielt verschiedene Kategorien von Zwischendateien zu löschen.

---

## Hauptfunktionen

*   Interaktives Menü: Wahlweise Löschung von ODF-Zwischendateien oder konvertierten WAV-Dateien.
*   Intelligente ODF-Bereinigung: Identifiziert .odt, .ods oder .odp Dateien, die aus alten Office-Formaten (z. B. .doc, .docx, .rtf) erzeugt wurden. Eine Löschung erfolgt nur, wenn die ursprüngliche Quelldatei im selben Verzeichnis noch existiert.
*   WAV-Bereinigung: Identifiziert .wav-Dateien, die aus anderen Audioformaten (z. B. .mp3, .flac, .m4a) generiert wurden, und entfernt diese, sofern das Original vorhanden ist.
*   Sicherheitsmodus (Dry-Run): Für die ODF-Bereinigung kann ein Testlauf aktiviert werden, der lediglich protokolliert, was gelöscht würde.
*   Zentrales LZA-Logging: Alle Löschvorgänge werden in Log-Dateien innerhalb des LZA-Verzeichnisses (Stufe 5 / logfiles) dokumentiert, um die Revisionssicherheit zu gewährleisten.

---

## TREE-Struktur & Dateipfade

Das Skript scannt die kuratierten Daten in Stufe 4 und dokumentiert den Vorgang in Stufe 5:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 4_[ID]_VL/
│   └── files/                              <-- ARBEITSBEREICH (Eingabe & Löschung)
│       ├── Dokument.doc                    <-- Original (bleibt)
│       ├── Dokument.doc.odt                <-- ARTEFAKT (wird gelöscht)
│       └── Dokument.doc.pdf                <-- Derivat (bleibt)
└── 5_[ID]_LZA/logfiles/                    <-- LOG-ZIEL (Protokolle)
    ├── 4_[ID]_VL_delete-converted-odfs.log <-- Protokoll der ODF-Bereinigung
    └── 4_[ID]_VL_delete-converted-wavs.log <-- Protokoll der WAV-Bereinigung

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Standard-Bibliotheken: Nutzt pathlib, os und subprocess (keine externen Pakete erforderlich).

---

## Konfiguration im Skript

Im Header des Skripts kann der Testlauf-Modus global gesteuert werden:

    DELETE_ODF_DRY_RUN = False  # Auf True setzen für eine Simulation

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

1. Validierung: Das Skript prüft die Pfade in Stufe 4 und stellt sicher, dass der Log-Ordner in Stufe 5 existiert.
2. Menü-Auswahl: Der Benutzer wählt die gewünschte Aufräum-Aktion (ODF oder WAV).
3. Analyse: Das System sucht rekursiv nach Dateien, die dem Muster "Originalname.originalendung.zwischenendung" entsprechen und prüft die Existenz des Originals.
4. Bestätigung: Vor dem tatsächlichen Löschen wird eine Liste der gefundenen Dateien angezeigt.
5. Löschung & Logging: Die Dateien werden entfernt und der Vorgang wird mit Zeitstempel in den LZA-Logordner (Stufe 5) geschrieben.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT