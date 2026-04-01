# Data Cleanup Tool für Archivierungsprozesse

Ein Python-Skript zur automatisierten Bereinigung von Zwischendateien im Rahmen von digitalen Archivierungsprojekten. Das Tool identifiziert und löscht sicher konvertierte ODF-Dateien sowie temporäre WAV-Dateien.

---

## Inhaltsverzeichnis

- [Funktionsumfang](#funktionsumfang)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Funktionsweise im Detail](#funktionsweise-im-detail)
- [Konfiguration](#konfiguration)
- [Logging](#logging)
- [Sicherheitshinweise](#sicherheitshinweise)
- [Fehlerbehandlung](#fehlerbehandlung)
- [Lizenz](#lizenz)

---

## Funktionsumfang

- **Automatische Pfadvalidierung:** Basierend auf AC-Nummer und Datenträger-ID.
- **Intelligente ODF-Erkennung:** Identifiziert `.odt`-Dateien, die lediglich als Zwischenschritt aus Originaldokumenten konvertiert wurden.
- **Sicherer WAV-Cleanup:** Löscht konvertierte WAV-Dateien nur dann, wenn die Original-Audiodateien noch vorhanden sind.
- **Testlauf-Modus:** Optionaler Simulation-Modus für ODF-Löschungen zur Risikominimierung.
- **Detaillierte Protokollierung:** Erstellt separate Log-Dateien für alle durchgeführten Aktionen.
- **Interaktives Menü:** Benutzerfreundliche Auswahl der Bereinigungsaktionen über die Konsole.

---

## Voraussetzungen

- **Python:** Version 3.6 oder höher.
- **Betriebssystem:** Windows, macOS oder Linux.
- **Bibliotheken:** Keine externen Abhängigkeiten erforderlich (nur Standardbibliothek).

---

## Installation

1. **Skript herunterladen:**
   ```bash
   git clone [repository-url]
   # oder direkt via curl
   curl -O [skript-url]
   ```

2. **Ausführungsberechtigungen setzen (Linux/macOS):**
   ```bash
   chmod +x data_cleanup.py
   ```

---

## Verwendung

### Aufruf des Skripts

Das Skript benötigt zwei Parameter beim Start:
1. **AC-Nummer** (Archivierungsprojekt-Kennung)
2. **Datenträger-ID** (Eindeutige Kennung des Datenträgers)

```bash
python data_cleanup.py <AC_NUMMER> <DATENTRÄGER_ID>
```

**Beispiel:**
```bash
python data_cleanup.py AC-2024-001 DISK-12345
```

### Erwartete Verzeichnisstruktur

Das Skript erwartet folgende Struktur in Ihrem Dokumenten-Ordner:

```text
~/Documents/data/<AC_NUMMER>/<DATENTRÄGER_ID>/
└── 3_<DATENTRÄGER_ID>_for-transfer/
    └── files/
        └── [zu bereinigende Dateien]
```

### Menüoptionen

Nach der Pfadvalidierung erscheint ein interaktives Menü:

```text
Wählen Sie eine Aufräum-Aktion:

1 - Zwischendateien (ODF) löschen
2 - Konvertierte WAV-Dateien löschen
Q - Beenden
```

---

## Funktionsweise im Detail

### ODF-Zwischendateien löschen
Das Skript durchsucht rekursiv den `files`-Ordner. Eine `.odt`-Datei wird nur gelöscht, wenn:
1. Der Dateiname (ohne `.odt`) auf eine bekannte Dokumenten-Endung endet (z. B. `.doc`, `.docx`, `.rtf`).
2. Die ursprüngliche Quelldatei im selben Verzeichnis existiert.

### Konvertierte WAV-Dateien löschen
Das Skript identifiziert WAV-Dateien, die durch Konvertierung entstanden sind:
1. Analysiert den Dateinamen auf Muster wie `original.flac.wav`.
2. Prüft, ob das Original (z. B. `.flac`, `.mp3`, `.m4a`) noch vorhanden ist.
3. Löscht die WAV-Datei nur bei positivem Befund.

---

## Konfiguration

Im Kopfbereich des Skripts können Parameter angepasst werden:

```python
DELETE_ODF_DRY_RUN = False  # True = nur Simulation

# Unterstützte Original-Endungen für Dokumente
original_extensions = {
    ".doc", ".docx", ".rtf", ".wpd", ".wps", ".dot", ".dotx", ".wbk"
}

# Unterstützte Originalformate für Audio-Cleanup
SOURCE_AUDIO_EXTENSIONS_FOR_WAV_CLEANUP = {
    ".aiff", ".flac", ".ogg", ".wav", ".m4a", ".wma", ".aac", ".mp3"
}
```

---

## Logging

Das Skript erstellt für jede Aktion eine separate Log-Datei im `for-transfer`-Ordner:
- **ODF-Löschung:** `3_<ID>_for-transfer_delete-converted-odfs.log`
- **WAV-Löschung:** `3_<ID>_for-transfer_delete-converted-wavs.log`

---

## Sicherheitshinweise

1. **Bestätigung:** Vor jedem Löschvorgang ist eine explizite Bestätigung mit `j` erforderlich.
2. **Originalprüfung:** Es werden niemals Dateien gelöscht, deren Originale nicht mehr auffindbar sind.
3. **Testlauf:** Nutzen Sie `DELETE_ODF_DRY_RUN = True` für eine erste Analyse ohne Risiko.

---

## Fehlerbehandlung

- **Pfadfehler:** Das Skript bricht mit einer klaren Fehlermeldung ab, wenn die AC- oder ID-Struktur nicht gefunden wird.
- **Berechtigungen:** Fehlgeschlagene Löschversuche werden im Log vermerkt, ohne den Gesamtablauf zu stoppen.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT

**Hinweis:** Dieses Tool wurde speziell für die Anforderungen digitaler Archivierungsprojekte entwickelt. Stellen Sie sicher, dass Sie vor der Verwendung eine Sicherungskopie Ihrer Daten erstellt haben.