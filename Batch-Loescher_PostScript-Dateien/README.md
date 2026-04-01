# PS-Dateien Löschtool

Ein einfaches Python-Skript zum rekursiven Löschen aller `.ps`-Dateien (PostScript) in einem angegebenen Verzeichnis und allen seinen Unterordnern.

## Funktionsumfang

- Rekursive Suche nach allen `.ps`-Dateien im angegebenen Startverzeichnis
- Löschen aller gefundenen `.ps`-Dateien
- Detaillierte Ausgabe aller gelöschten Dateien
- Fehlerbehandlung bei Löschvorgängen
- Prüfung, ob der angegebene Pfad existiert

## Voraussetzungen

- Python 3.4 oder höher (wegen `pathlib`)
- Betriebssystem: Windows, macOS oder Linux
- Keine externen Python-Bibliotheken erforderlich (nur Standardbibliothek)

## Installation

1. Skript herunterladen und in einer Datei speichern, z.B. `delete_ps_files.py`

2. Ausführungsberechtigungen setzen (Linux/macOS):
   ```bash
   chmod +x delete_ps_files.py
   ```

## Verwendung

### Vorbereitung

Bevor Sie das Skript ausführen, müssen Sie den Pfad zu Ihrem Arbeitsordner anpassen.

Öffnen Sie die Skript-Datei und ändern Sie die Variable `base_path`:

```python
base_path = Path(r"C:\Users\digit\Desktop\ZPH1082_011_Eisendle") # <-- HIER IHREN PFAD EINFÜGEN
```

**Wichtig:** 
- Verwenden Sie einen **absoluten Pfad** für die `base_path`-Variable
- Unter Windows: Nutzen Sie den Raw-String mit `r"..."` oder doppelte Backslashes `\\`
- Unter macOS/Linux: Verwenden Sie Pfade wie `/home/benutzer/ordner`

### Ausführen des Skripts

```bash
python delete_ps_files.py
```

### Beispiel

Angenommen, Sie haben folgende Verzeichnisstruktur:

```
ZPH1082_011_Eisendle/
├── dokument.ps
├── unterordner/
│   ├── bild.ps
│   └── datei.txt
└── backup/
    └── alt.ps
```

Nach der Ausführung werden alle `.ps`-Dateien gelöscht:
- `dokument.ps`
- `unterordner/bild.ps`
- `backup/alt.ps`

Die `.txt`-Datei bleibt unberührt.

## Funktionsweise im Detail

Das Skript führt folgende Schritte aus:

1. **Pfadprüfung**: Überprüft, ob der angegebene `base_path` existiert
2. **Rekursive Suche**: Durchsucht mit `rglob("*.ps")` den gesamten Verzeichnisbaum nach `.ps`-Dateien
3. **Löschvorgang**: Löscht jede gefundene Datei mit `file_path.unlink()`
4. **Ausgabe**: Gibt jede gelöschte Datei auf der Konsole aus
5. **Fehlerbehandlung**: Fängt und meldet Fehler beim Löschen einzelner Dateien
6. **Zusammenfassung**: Zeigt die Gesamtzahl der gelöschten Dateien an

## Ausgabe

Das Skript gibt während der Ausführung folgende Informationen aus:

- Erfolgreiche Löschungen: `🗑️ Gelöscht: [Dateipfad]`
- Fehler beim Löschen: `❌ Fehler beim Löschen von [Dateipfad]: [Fehlermeldung]`
- Fehler bei Pfadprüfung: `❌ FEHLER: Der angegebene Ordner '[Pfad]' existiert nicht.`
- Abschließende Zusammenfassung: `✅ Insgesamt X .ps-Dateien gelöscht.`

## Konfiguration

Am Anfang des Skripts muss nur ein Parameter angepasst werden:

```python
# Geben Sie hier den Pfad zu Ihrem Arbeitsordner an
base_path = Path(r"C:\Ihr\Pfad\hier")  # <-- HIER IHREN PFAD EINFÜGEN
```

## Sicherheitshinweise

1. **Keine Bestätigung**: Dieses Skript löscht Dateien **ohne Rückfrage**! Stellen Sie sicher, dass der angegebene Pfad korrekt ist.
2. **Keine Wiederherstellung**: Gelöschte Dateien können nicht wiederhergestellt werden (es sei denn, Sie haben ein Backup).
3. **Empfohlene Vorsichtsmaßnahmen**:
   - Testen Sie das Skript zuerst in einem Testverzeichnis
   - Erstellen Sie vor der Ausführung ein Backup wichtiger Daten
   - Überprüfen Sie den `base_path` sorgfältig
4. **Nur `.ps`-Dateien**: Das Skript löscht ausschließlich Dateien mit der Endung `.ps`. Andere Dateitypen bleiben unberührt.

## Fehlerbehandlung

Das Skript behandelt verschiedene Fehlersituationen:

- **Pfad existiert nicht**: Ausgabe einer Fehlermeldung mit Hinweis zur Korrektur
- **Berechtigungsfehler**: Fehlermeldung für die betroffene Datei, andere Dateien werden weiterverarbeitet
- **Datei wird verwendet**: Fehlermeldung, das Skript fährt fort

## Beispiel für die Ausgabe

```
Suche nach .ps-Dateien im Ordner: C:\Users\digit\Desktop\ZPH1082_011_Eisendle

🗑️ Gelöscht: C:\Users\digit\Desktop\ZPH1082_011_Eisendle\dokument.ps
🗑️ Gelöscht: C:\Users\digit\Desktop\ZPH1082_011_Eisendle\unterordner\bild.ps
🗑️ Gelöscht: C:\Users\digit\Desktop\ZPH1082_011_Eisendle\backup\alt.ps

✅ Insgesamt 3 .ps-Dateien gelöscht.
```

## Anpassungsmöglichkeiten

Möchten Sie andere Dateitypen löschen, ändern Sie die Zeile:

```python
ps_files = list(base_path.rglob("*.ps"))  # .ps durch .pdf, .tmp usw. ersetzen
```

## Lizenz

```
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT
```

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---


**Hinweis**: Dieses Skript löscht Dateien unwiderruflich. Verwenden Sie es mit Vorsicht und nur, wenn Sie sicher sind, dass die `.ps`-Dateien nicht mehr benötigt werden.
```
