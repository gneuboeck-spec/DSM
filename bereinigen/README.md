# Universelles Bereinigungsskript für Dateisammlungen

Dieses Verzeichnis enthält ein Python-Skript zur aggressiven und permanenten Bereinigung von Dateiverzeichnissen. Es wurde um wichtige Sicherheitsfunktionen erweitert, um eine kontrollierte Ausführung zu ermöglichen.

## ⚠️ Wichtige Warnung

Dieses Skript ist ein **destruktives Werkzeug**. Es löscht Dateien und Ordner **permanent**. Obwohl es einen Testlauf-Modus gibt, sollten Sie es niemals auf wichtigen Originaldaten ausführen.

**Arbeiten Sie immer mit einer Kopie Ihrer Daten!** Die Autoren übernehmen keine Haftung für Datenverlust.

---

## Zweck des Skripts

Das Skript durchsucht einen Quellordner und alle seine Unterordner rekursiv und wendet eine Reihe von vordefinierten Regeln an, um unerwünschte Dateien zu löschen. Anschließend entfernt es alle Verzeichnisse, die durch den Prozess leer geworden sind.

**Die Bereinigung erfolgt auf Basis von vier Hauptkriterien:**

1.  **Löschung nach Dateiendung:**
    Eine sehr umfangreiche, kuratierte Liste von über 200 Dateiendungen (`.exe`, `.dll`, `.tmp`, `.bak`, `.log` etc.) wird verwendet, um System-, Cache-, temporäre und veraltete Dateien zu entfernen.

2.  **Löschung nach Schlüsselwort im Namen:**
    Eine spezifische Liste von Schlüsselwörtern (z.B. `konvertierungslog`) wird verwendet, um Log-Dateien von vorherigen Konvertierungsprozessen zu löschen.

3.  **Löschung von versteckten Systemdateien:**
    Das Skript zielt auf plattformspezifische und allgemeine versteckte Dateien ab:
    *   **macOS:** `.DS_Store`, `._*`-Dateien (AppleDouble) etc.
    *   **Windows:** `Thumbs.db`, `desktop.ini`.
    *   **Allgemein:** Dateien, deren Name mit einem Punkt (`.`) oder einer Tilde (`~`) beginnt.

4.  **Löschung leerer Ordner:**
    Nachdem die Dateien entfernt wurden, durchsucht das Skript den Verzeichnisbaum von unten nach oben und löscht alle Ordner, die nun leer sind.

---

## Neue Funktionen: Testlauf und Report-Erstellung

Um die destruktive Natur des Skripts kontrollierbar zu machen, wurden zwei Schlüsselfunktionen hinzugefügt:

### 1. Testlauf-Modus (`dry_run`)

Dies ist der wichtigste Sicherheitsschalter. Wenn `dry_run` auf `True` gesetzt ist, führt das Skript eine **vollständige Simulation** durch:
*   Es werden **keine Dateien oder Ordner gelöscht**.
*   Das Skript gibt in der Konsole genau aus, welche Aktionen es durchführen *würde*.
*   Dies ermöglicht eine gefahrlose Überprüfung der Regeln und der zu löschenden Dateien.

### 2. Report-Datei (`create_log_file`)

Wenn diese Option auf `True` gesetzt ist, erstellt das Skript im Zielverzeichnis eine Textdatei (z.B. `bereinigungs_report.txt`). Diese Datei enthält eine übersichtliche, nach Häufigkeit sortierte Liste aller Dateitypen (Endungen), die gelöscht wurden oder im Testlauf gelöscht würden. Dies ist ideal für eine schnelle Analyse.

**Beispielinhalt einer Report-Datei:**
```Anzahl und Typ der zu löschenden Dateien
========================================
210     .fot
15      .drv
4       .tmp
...