# Universelles Bereinigungsskript für Dateisammlungen

Dieses Verzeichnis enthält ein Python-Skript zur aggressiven und permanenten Bereinigung von Dateiverzeichnissen.

## ⚠️ Wichtige Warnung

Dieses Skript ist ein **destruktives Werkzeug**. Es löscht Dateien und Ordner **permanent und ohne Sicherheitsabfrage**. Es wurde für den speziellen Zweck entwickelt, digitale Nachlässe oder komplexe Dateisammlungen von System-Ballast, temporären Dateien und als irrelevant eingestuften Formaten zu bereinigen.

**Führen Sie dieses Skript niemals auf wichtigen Originaldaten aus! Arbeiten Sie immer mit einer Kopie Ihrer Daten.** Die Autoren übernehmen keine Haftung für Datenverlust.

---

## Zweck des Skripts

Das Skript durchsucht einen Quellordner und alle seine Unterordner rekursiv und wendet eine Reihe von vordefinierten Regeln an, um unerwünschte Dateien zu löschen. Anschließend entfernt es alle Verzeichnisse, die durch den Prozess leer geworden sind.

**Die Bereinigung erfolgt auf Basis von vier Hauptkriterien:**

1.  **Löschung nach Dateiendung:**
    Eine sehr umfangreiche, kuratierte Liste von über 200 Dateiendungen (`.exe`, `.dll`, `.tmp`, `.bak`, `.log` etc.) wird verwendet, um System-, Cache-, temporäre und veraltete Dateien zu entfernen.

2.  **Löschung nach Schlüsselwort im Namen:**
    Eine spezifische Liste von Schlüsselwörtern (z.B. `konvertierungslog`) wird verwendet, um Log-Dateien von vorherigen Konvertierungsprozessen zu löschen.

3.  **Löschung von versteckten Systemdateien:**
    Das Skript zielt auf plattformübergreifende versteckte Dateien ab:
    *   **macOS:** `.DS_Store`, `._*`-Dateien (AppleDouble) und andere.
    *   **Allgemein (Unix-artig):** Alle Dateien, deren Name mit einem Punkt (`.`) beginnt.
    *   **Temporäre Office-Dateien:** Alle Dateien, deren Name mit einer Tilde (`~`) beginnt.

4.  **Löschung leerer Ordner:**
    Nachdem die Dateien entfernt wurden, durchsucht das Skript den Verzeichnisbaum von unten nach oben und löscht alle Ordner, die nun leer sind.

---

## Technische Voraussetzungen

Das Skript ist extrem schlank und hat minimale Anforderungen.

*   **Python:** Version 3.6 oder neuer.
*   **Externe Bibliotheken:** Keine. Das Skript verwendet ausschließlich die Python-Standardbibliothek `os`.
*   **Betriebssystem:** Plattformunabhängig. Funktioniert auf macOS, Windows und Linux.

---

## Konfiguration im Skript

Vor der Ausführung müssen die Konfigurationslisten am Anfang des Skripts überprüft und der Hauptpfad angepasst werden.

*   **`base_directory`**: Dies muss der **absolute Pfad** zum Hauptverzeichnis sein, das bereinigt werden soll.
*   **`delete_keywords`**: Kann bei Bedarf um weitere Schlüsselwörter ergänzt werden.
*   **`mac_hidden_files`**: Liste spezifischer macOS-Systemdateien.
*   **`delete_extensions`**: Die Hauptliste der zu löschenden Dateiendungen. **Änderungen an dieser Liste haben die größten Auswirkungen und sollten mit äußerster Vorsicht vorgenommen werden.**

**Beispiel für macOS:**
```python
base_directory = "/Users/IhrBenutzername/Desktop/Kopie_des_Projekts"
```
**Beispiel für Windows:**
```python
base_directory = "C:/Users/IhrBenutzername/Desktop/Kopie_des_Projekts"
```

---

## Ausführung

1.  **DATEN SICHERN!** Erstellen Sie eine vollständige Kopie des Verzeichnisses, das Sie bereinigen möchten.
2.  Passen Sie die `base_directory`-Variable im Skript an den Pfad Ihrer **Kopie** an.
3.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung (Windows).
4.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**
```bash
python3 /pfad/zum/skript/cleanup.py
```

Das Skript beginnt sofort mit dem Löschvorgang und gibt jeden Schritt (erfolgreich gelöschte Datei/Ordner oder Fehler) auf der Konsole aus. Es gibt **keine "Sind Sie sicher?"-Abfrage**.