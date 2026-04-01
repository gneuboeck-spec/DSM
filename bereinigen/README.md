# Automatisches Bereinigungsskript

Dieses Skript dient zur automatisierten und tiefgehenden Bereinigung von Verzeichnissen. Es wurde entwickelt, um Dateistrukturen (z. B. von alten Datenträgern) für die Archivierung vorzubereiten, indem es eine Vielzahl von Systemdateien, temporären Dateien, ausführbaren Programmen und sonstigem "Datenmüll" entfernt.

Das Skript ist für die Integration in eine vordefinierte Ordnerstruktur konzipiert und wird über Kommandozeilenargumente gesteuert, typischerweise durch eine Start-Datei wie `start.bat`.

---

## Hauptfunktionen

*   **Dynamische Pfad-Konfiguration:** Das Skript erfordert keine manuelle Bearbeitung von Pfaden im Quellcode. Alle Pfade werden dynamisch basierend auf einer `AC-Nummer` und einer `Datenträger-ID` generiert.
*   **Umfassende Löschkriterien:** Dateien werden anhand einer umfangreichen Liste von Dateiendungen, Schlüsselwörtern im Namen sowie typischen Mustern für versteckte oder temporäre Dateien identifiziert.
*   **Sicherheitsmechanismen:**
    *   **Testlauf (`Dry Run`):** Kann in einem reinen Simulationsmodus ausgeführt werden, der anzeigt, was gelöscht *würde*, ohne tatsächlich Änderungen vorzunehmen.
    *   **Vorschau-Protokoll:** Erstellt vor dem Löschen eine detaillierte Log-Datei aller zur Löschung identifizierten Elemente.
    *   **Bestätigungsabfrage:** Fordert vor dem Start des eigentlichen Löschvorgangs eine explizite Bestätigung vom Benutzer an.
*   **Detaillierte Protokollierung:** Erstellt nach Abschluss ein finales Protokoll, das alle tatsächlich durchgeführten Löschaktionen dokumentiert.
*   **Interaktive Bedienung:** Bietet am Ende an, den Zielordner direkt im Datei-Explorer zu öffnen.

---

## Was wird gelöscht?

Das Skript durchsucht den Zielordner rekursiv und identifiziert Elemente anhand der folgenden Kriterien zur Löschung:

#### 1. Nach Dateiendung
Eine fest definierte Liste von über 200 Dateiendungen (`.exe`, `.dll`, `.tmp`, `.bak`, `.sys` etc.), die typischerweise Systemdateien, temporäre Dateien oder ausführbare Programme darstellen.

#### 2. Nach Schlüsselwörtern im Dateinamen
Dateien und Ordner, deren Name bestimmte Schlüsselwörter enthält (z. B. `video_konvertierung`, `konvertierungslog`), die auf prozessinterne Protokolle hinweisen.

#### 3. Nach Dateinamen-Mustern und Systemdateien
*   Versteckte Systemdateien wie `Thumbs.db` oder `desktop.ini`.
*   macOS-spezifische Metadaten-Dateien (beginnend mit `._`).
*   Versteckte Unix-Dateien (beginnend mit `.`, ausgenommen `.git` und `.gitignore`).
*   Temporäre Office-Dateien (beginnend mit `~`).

#### 4. Leere Ordner
Alle Ordner, die nach dem Löschen der Dateien leer sind, werden ebenfalls entfernt.

---

## Technische Voraussetzungen

*   **Python:** Version 3.6 oder neuer. Es sind keine externen Bibliotheken erforderlich (nur Standardmodule).

---

## Konfiguration und Ordnerstruktur

Das Skript wird **nicht** im Code selbst konfiguriert. Stattdessen erwartet es eine bestimmte Ordnerstruktur und erhält die notwendigen Informationen über Kommandozeilenargumente.

### Erwartete Ordnerstruktur

Das Skript muss innerhalb dieser Verzeichnisstruktur ausgeführt werden, die sich im `Documents`-Ordner des Benutzers befinden sollte:

```text
Documents/
└── Datentraeger_sichern/
    └── [AC-Nummer]/
        └── [Datenträger-ID]/
            └── 3_[Datenträger-ID]_for-transfer/
                ├── Files/                      <-- DIESER ORDNER WIRD BEREINIGT
                └── (Hier werden die Log-Dateien erstellt)
```

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

---

## Ausführung

Das Skript sollte über eine Wrapper-Datei (z. B. `start.bat` unter Windows) gestartet werden, die die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python bereinigungsskript.py %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft, ob die Ordnerstruktur korrekt ist.
2.  **Analyse:** Das Verzeichnis `Files` wird durchsucht und eine Liste der zu löschenden Elemente erstellt.
3.  **Vorschau-Protokoll:** Eine Log-Datei (`..._delete_preview_all.log`) wird mit allen gefundenen Elementen erstellt. Sie werden aufgefordert, diese Datei zu prüfen.
4.  **Bestätigung:** Das Skript fragt, ob der Löschvorgang gestartet werden soll (`j/n`).
5.  **Löschvorgang:** Nach Bestätigung werden die identifizierten Dateien und leeren Ordner entfernt.
6.  **Finales Protokoll:** Eine zweite Log-Datei (`..._delete_all.log`) wird mit einer Liste der tatsächlich gelöschten Elemente erstellt.
7.  **Abschluss:** Das Skript fragt, ob der bereinigte Ordner geöffnet werden soll.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT