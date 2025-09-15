# Aufräum-Skript für ODF-Zwischendateien

Dieses Python-Skript dient als intelligentes Bereinigungswerkzeug, das speziell als Ergänzung zum universellen Office-Konverter (`office_konverter.py`) entwickelt wurde.

## Zweck des Skripts

Nachdem der Office-Konverter aus verschiedenen Quellformaten (`.doc`, `.xls` etc.) sowohl ein OpenDocument-Format (`.odt`, `.ods`, etc.) als auch ein PDF/A erstellt hat, verbleiben die ODF-Dateien als Zwischendateien im Verzeichnis.

Dieses Skript durchsucht einen Ordner und **löscht gezielt nur jene ODF-Dateien, die als Nebenprodukt einer Konvertierung erstellt wurden**. Ursprüngliche ODF-Dateien, die bereits vor der Konvertierung existierten, werden **nicht** gelöscht.

**Die Kernlogik:**
Eine Datei wie `Bericht.doc.odt` wird gelöscht, weil die Originaldatei `Bericht.doc` ebenfalls existiert. Eine Datei wie `MeinDokument.odt` wird hingegen ignoriert, da keine dazugehörige "Originaldatei" (`MeinDokument`) gefunden wird.

Das Ziel ist es, nach dem Aufräumprozess nur noch die Originaldateien und die finalen PDF/A-Derivate im Ordner zu haben.

---

## Technische Voraussetzungen

Das Skript ist sehr schlank und hat minimale Anforderungen.

*   **Python:** Version 3.6 oder neuer (wegen der Verwendung von f-Strings).
*   **Externe Bibliotheken:** Keine. Das Skript verwendet ausschließlich Python-Standardbibliotheken (`os`, `sys`).
*   **Betriebssystem:** Plattformunabhängig. Funktioniert auf macOS, Windows und Linux.

---

## Konfiguration im Skript

Vor der Ausführung muss eine Variable am Anfang des Skripts angepasst werden:

*   **`target_folder`**: Dies muss der **absolute Pfad** zum Hauptverzeichnis sein, das aufgeräumt werden soll. Dieser Pfad sollte mit dem `input_folder` des Konvertierungs-Skripts übereinstimmen.

**Beispiel für macOS:**
```python
target_folder = "/Users/gregorneuboeck/Desktop/Texdateien_konvertieren"
```
**Beispiel für Windows:**
```python
target_folder = "C:/Users/DeinBenutzer/Desktop/Texdateien_konvertieren"
```

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/Git Bash (Windows).
2.  Stellen Sie sicher, dass der `target_folder` im Skript korrekt konfiguriert ist.
3.  Führen Sie das Skript mit dem Python-Interpreter aus.

**Beispiel:**
```bash
python3 /pfad/zum/skript/cleanup_odf_files.py
```

### Sicherheitsabfrage

Das Skript ist sicher in der Anwendung. Bevor Dateien endgültig gelöscht werden, listet es alle identifizierten Zwischendateien auf und stellt eine explizite Ja/Nein-Sicherheitsabfrage (`Möchten Sie diese Dateien wirklich löschen? (j/n):`). Der Löschvorgang wird nur nach einer Bestätigung mit `j` gestartet.