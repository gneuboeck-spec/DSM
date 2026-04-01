# Aufräumskript für konvertierte OpenDocument-Dateien

Dieses Skript ist ein spezialisiertes Werkzeug zur Bereinigung nach einem Dokumenten-Konvertierungsprozess. Seine einzige Aufgabe ist es, OpenDocument-Dateien (`.odt`, `.ods`, `.odp`) zu identifizieren und zu löschen, die zuvor von einem Konvertierungsskript als Archivkopien (`Originalname.originalendung.odf_endung`) erstellt wurden.

Der Zweck ist es, die Dateisammlung zu bereinigen, indem diese temporären oder redundanten Zwischenformate entfernt werden, während die ursprünglichen Quelldateien erhalten bleiben.

## Kernfunktionen

*   **Präzise Identifikationslogik:** Löscht eine Datei nur, wenn sie eindeutig als Konvertierungsergebnis identifiziert werden kann (z.B. `bericht.doc.odt`). Dabei wird sichergestellt, dass die Originaldatei (`bericht.doc`) noch existiert, um Datenverlust zu vermeiden.
*   **Sicherheitsmechanismen:**
    *   **Testlauf (`Dry Run`):** Das Skript kann in einem reinen Simulationsmodus ausgeführt werden. In diesem Modus werden keine Dateien gelöscht, sondern es wird lediglich eine Log-Datei mit den zur Löschung identifizierten Dateien erstellt.
    *   **Bestätigungsabfrage:** Im Echt-Modus listet das Skript alle zu löschenden Dateien auf und fordert eine explizite Bestätigung vom Benutzer (`j/n`), bevor der Löschvorgang gestartet wird.
*   **Detaillierte Protokollierung:** Alle Aktionen – ob im Testlauf oder im Echt-Modus – werden in einer Log-Datei festgehalten. Im Echt-Modus werden erfolgreiche und fehlgeschlagene Löschungen getrennt protokolliert.
*   **Dynamische Pfad-Konfiguration:** Alle Arbeitsverzeichnisse werden automatisch basierend auf einer `AC-Nummer` und einer `Datenträger-ID` abgeleitet, die über die Kommandozeile übergeben werden.

---

## Konfiguration im Skript

Die primäre Konfiguration erfolgt über einen einzigen Schalter am Anfang des Skripts:

```python
# True:  Nur simulieren und eine Liste der zu löschenden Dateien im Log erstellen. Es wird nichts gelöscht.
# False: Dateien nach Bestätigung tatsächlich löschen und den Vorgang protokollieren.
DRY_RUN = False
*   **`DRY_RUN = True`**: Sicherer Modus zur Überprüfung.
*   **`DRY_RUN = False`**: Produktiver Modus zum tatsächlichen Löschen.

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

@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python cleanup_odf_skript.py %AC_NUMBER% %DISK_ID%
pause

**Beispielhafter Aufruf in einer `start.bat`:**

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die übergebenen Argumente und die Ordnerstruktur.
2.  **Modus-Erkennung:** Das Skript stellt fest, ob es im `DRY_RUN` (Testlauf) oder im Echt-Modus läuft.
3.  **Suche:** Das `Files`-Verzeichnis wird rekursiv nach OpenDocument-Dateien durchsucht, die den Kriterien für konvertierte Dateien entsprechen.
4.  **Aktion (je nach Modus):**
    *   **Im Testlauf:** Es wird eine Log-Datei mit allen Dateien erstellt, die gelöscht *würden*.
    *   **Im Echt-Modus:** Die gefundenen Dateien werden aufgelistet, und eine Bestätigung vom Benutzer wird eingeholt.
5.  **Löschvorgang (nur im Echt-Modus):** Nach der Bestätigung werden die Dateien gelöscht.
6.  **Protokollierung:** Die Ergebnisse (simuliert oder echt) werden in die Log-Datei `3_[Datenträger-ID]_delete_converted_odfs.log` geschrieben.
7.  **Zusammenfassung:** Am Ende wird eine Übersicht über die durchgeführten Aktionen ausgegeben.
8.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT