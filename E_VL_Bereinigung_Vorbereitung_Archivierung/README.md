# Skript E: VL-Bereinigung & Datentransfer (Stage 3 zu 4)

Dieses Skript dient der automatischen Bereinigung von Dateibeständen vor der endgültigen Übergabe in die Langzeitarchivierung (LZA). Es filtert unerwünschte Systemdateien, temporäre Dateien sowie Hilfsdateien aus vorherigen Konvertierungsschritten heraus, um einen sauberen Archivbestand in der VL-Stufe (Stufe 4) zu gewährleisten.

Das Skript ist Teil eines mehrstufigen Workflows und wird über eine Start-Datei (start.bat) mit der AC-Nummer und Datenträger-ID gesteuert.

---

## Hauptfunktionen

*   Automatischer Datentransfer (Stage 3 nach Stage 4): Das Skript kopiert automatisch den gesamten "files"-Ordner von der Transfer-Stufe (3) in die Bereinigungs-Stufe (4), bevor die Löschvorgänge starten.
*   System-Dateien entfernen: Automatische Löschung von Windows-spezifischen Dateien wie Thumbs.db oder desktop.ini sowie versteckten Apple-Ressourcen-Dateien (._).
*   Gezielte Extension-Bereinigung: Löscht über 150 potenziell unerwünschte Dateitypen (z.B. .exe, .dll, .tmp, .bak, .ini, .log, .lnk).
*   Keyword-Filter: Identifiziert und löscht Dateien, die bestimmte Schlagworte im Namen tragen (z.B. "konvertierungslog", "bereinigungslog"), um Hilfsberichte aus der VL-Stufe zu entfernen.
*   Bereinigung leerer Ordner: Entfernt rekursiv alle Verzeichnisse, die nach der Dateibereinigung keine Inhalte mehr enthalten.
*   Detailliertes LZA-Logging:
    *   Vorschau-Log: Erstellt vor dem Löschen eine Liste aller identifizierten Elemente.
    *   Final-Log: Dokumentiert alle tatsächlich gelöschten Dateien und Ordner.
    *   Die Logs werden direkt im Verzeichnis der Stufe 5 (LZA) abgelegt, um den Audit-Trail zu wahren.

---

## TREE-Struktur & Dateipfade (Phase 3)

Das Skript synchronisiert Stufe 3 mit Stufe 4 und dokumentiert die Bereinigung in Stufe 5:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 3_[ID]_for-transfer/
│   └── files/                              <-- QUELLE (Inhalt wird nach 4 kopiert)
├── 4_[ID]_VL/                              <-- ARBEITSBEREICH
│   └── files/                              <-- ZIEL (Hier erfolgt die Löschung)
└── 5_[ID]_LZA/logfiles/                    <-- LOG-ZIEL (Protokolle)
    ├── 4_[ID]_VL_delete-preview-all.log    <-- Vorschau der Löschkandidaten
    └── 4_[ID]_VL_delete-all.log            <-- Bestätigung der erfolgten Löschung
```
---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Standard-Bibliotheken: Benötigt keine externen Pakete (shutil, pathlib und os werden genutzt).

---

## Ausführung

Das Skript benötigt die AC-Nummer und die Datenträger-ID beim Aufruf.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python vl_cleaner.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Datensynchronisation: Der Ordner "files" wird von Stufe 3 nach Stufe 4 kopiert. Ein bereits existierender Zielordner wird dabei zuvor sicherheitstechnisch entfernt.
2. Analyse: Das Skript scannt Stufe 4 nach unerwünschten Elementen.
3. Vorschau-Logging: Ein Bericht über die gefundenen Dateien wird im LZA-Logordner gespeichert.
4. Benutzerabfrage: Das Skript fordert eine Bestätigung an, bevor die Dateien in der VL-Stufe tatsächlich gelöscht werden (sofern DRY_RUN auf False steht).
5. Löschvorgang: Dateien und anschließend leere Ordner werden gelöscht.
6. Abschluss-Bericht: Ein finaler Bericht über die gelöschten Elemente wird in Stufe 5 erstellt.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT