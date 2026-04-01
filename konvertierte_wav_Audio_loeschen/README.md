# Aufräumskript für konvertierte WAV-Dateien

Dieses Skript ist ein spezialisiertes Werkzeug zur Bereinigung nach einem Audio-Konvertierungsprozess. Seine einzige Aufgabe ist es, `.wav`-Dateien zu identifizieren und zu löschen, die zuvor von einem Konvertierungsskript als verlustfreie Archivkopien (`Originalname.originalendung.wav`) erstellt wurden.

Der Zweck ist es, Speicherplatz zu sparen, indem diese unkomprimierten Zwischenformate entfernt werden, nachdem ihre Nützlichkeit für den aktuellen Arbeitsschritt erfüllt ist. Das Skript stellt sicher, dass nur die *generierten* WAV-Dateien gelöscht werden, während Originaldateien (einschließlich originaler `.wav`-Dateien) unberührt bleiben.

## Wie es funktioniert (Identifikationslogik)

Das Skript durchsucht den Zielordner und löscht eine Datei nur dann, wenn **alle** folgenden Kriterien erfüllt sind:

1.  Die Datei hat die Endung `.wav`.
2.  Der Dateiname folgt dem Muster `Originalname.originalendung.wav`.
3.  Die `originalendung` (z.B. `.mp3`, `.flac`) ist in der Liste der bekannten Quell-Audioformate enthalten.
4.  Die ursprüngliche Quelldatei (`Originalname.originalendung`) existiert noch im selben Verzeichnis.

Diese präzise Logik verhindert das versehentliche Löschen von wichtigen Originaldateien.

---

## Technische Voraussetzungen

*   **Python:** Version 3.6 oder neuer. Es sind keine externen Bibliotheken erforderlich.

---

## Konfiguration

Die einzige wichtige Konfiguration befindet sich direkt im Skript:

```python
# Diese Liste muss mit der `source_audio_extensions`-Liste aus Ihrem Konverter übereinstimmen.
source_audio_extensions = {".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"}
*   **`source_audio_extensions`**: Diese Liste **muss exakt** mit der Liste der Quellformate aus dem zugehörigen Audio-Konvertierungsskript übereinstimmen, damit die Erkennung der generierten WAV-Dateien zuverlässig funktioniert.

Alle Pfade zum Arbeitsverzeichnis und zur Log-Datei werden dynamisch basierend auf den übergebenen Kommandozeilenargumenten erstellt.

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:
Documents
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 3_[Datenträger-ID]_for-transfer
                ├── Files  <-- IN DIESEM ORDNER WIRD AUFGERÄUMT
                └── (Hier wird die Log-Datei erstellt)
*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python cleanup_wav_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die übergebenen Argumente und die Ordnerstruktur.
2.  **Suche:** Das `Files`-Verzeichnis wird rekursiv nach `.wav`-Dateien durchsucht, die den oben genannten Kriterien entsprechen.
3.  **Bestätigung:** Alle zur Löschung identifizierten Dateien werden aufgelistet. Das Skript fordert eine explizite Bestätigung vom Benutzer an (`j/n`), bevor es fortfährt.
4.  **Löschvorgang:** Nach der Bestätigung werden die Dateien gelöscht.
5.  **Protokollierung:** Alle erfolgreichen und fehlgeschlagenen Löschaktionen werden detailliert in die Log-Datei `3_[Datenträger-ID]_delete_converted_wavs.log` geschrieben.
6.  **Zusammenfassung:** Am Ende wird eine Übersicht über die Anzahl der gelöschten Dateien ausgegeben.
7.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT