# Aufräum-Skript für konvertierte WAV-Dateien

Dieses Python-Skript dient als intelligentes Bereinigungswerkzeug, das speziell als Ergänzung zum Audio-Konverter (`convert_audio.py`) entwickelt wurde.

## Zweck des Skripts

Nachdem der Audio-Konverter für jede Quelldatei eine MP3- und eine WAV-Version erstellt hat, kann dieses Skript verwendet werden, um Speicherplatz freizugeben, indem die unkomprimierten, großen WAV-Dateien wieder entfernt werden.

Die Logik ist dabei "intelligent" und sicher:
*   Es löscht **nur** jene WAV-Dateien, die eindeutig als Nebenprodukt einer Konvertierung identifiziert werden können (z.B. `song.flac.wav`).
*   WAV-Dateien, die bereits **ursprünglich** vorhanden waren (z.B. `aufnahme.wav`), werden **nicht gelöscht**, da für sie keine dazugehörige Quelldatei gefunden wird.

Das Ziel ist es, nach dem Aufräumprozess nur noch die Originaldateien und die komprimierten MP3-Derivate im Ordner zu haben.

---

## Technische Voraussetzungen

Das Skript ist sehr schlank und hat minimale Anforderungen.

*   **Python:** Version 3.6 oder neuer.
*   **Externe Bibliotheken:** Keine. Das Skript verwendet ausschließlich Python-Standardbibliotheken (`os`, `sys`).
*   **Betriebssystem:** Plattformunabhängig. Funktioniert auf macOS, Windows und Linux.

---

## Konfiguration im Skript

Vor der Ausführung müssen die Variablen am Anfang des Skripts für das jeweilige Betriebssystem angepasst werden:

*   **`target_folder`**: Dies muss der **absolute Pfad** zum Hauptverzeichnis sein, das aufgeräumt werden soll. Dieser Pfad sollte mit dem `input_folder` des Konvertierungs-Skripts übereinstimmen.
*   **`source_audio_extensions`**: Diese Liste muss mit der im Konvertierungs-Skript verwendeten Liste übereinstimmen. Sie ist entscheidend für die Logik, um Original- von Zwischendateien zu unterscheiden.

**Beispiel für macOS:**
```python
target_folder = "/Users/IhrBenutzername/Desktop/Audiodateien_konvertieren"
```
**Beispiel für Windows:**
```python
target_folder = "C:/Users/IhrBenutzername/Desktop/Audiodateien_konvertieren"
```

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/Git Bash (Windows).
2.  Stellen Sie sicher, dass die Pfade im Skript korrekt konfiguriert sind.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**
```bash
python3 /pfad/zum/skript/cleanup_wav_files.py
```

### Sicherheitsabfrage

Das Skript ist sicher in der Anwendung. Bevor Dateien endgültig gelöscht werden, listet es alle identifizierten Zwischendateien auf und stellt eine explizite Ja/Nein-Sicherheitsabfrage (`Möchten Sie diese Dateien wirklich löschen? (j/n):`). Der Löschvorgang wird nur nach einer Bestätigung mit `j` gestartet.