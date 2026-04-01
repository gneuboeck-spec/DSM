# Batch-Löscher für PostScript-Dateien

Dieses Verzeichnis enthält ein einfaches Python-Skript, um rekursiv alle PostScript (`.ps`) Dateien in einem angegebenen Verzeichnis und all seinen Unterordnern zu löschen.

## Zweck des Skripts

Dieses Skript dient als Aufräum-Werkzeug, typischerweise nachdem `.ps`-Dateien in ein anderes Format (wie z.B. PDF) konvertiert wurden und die Originaldateien nicht mehr benötigt werden. Es automatisiert den Prozess des Auffindens und Entfernens dieser Dateien, um Speicherplatz freizugeben und die Verzeichnisstruktur zu bereinigen.

**Der Prozess im Überblick:**

1.  **Durchsuchen:** Das Skript durchsucht den angegebenen `base_path` rekursiv.
2.  **Identifizieren:** Es findet alle Dateien, deren Name auf `.ps` endet (unabhängig von Groß- oder Kleinschreibung).
3.  **Löschen:** Jede gefundene `.ps`-Datei wird dauerhaft vom System entfernt.
4.  **Protokollieren:** Jeder Löschvorgang wird auf der Konsole ausgegeben. Am Ende wird eine Zusammenfassung der Gesamtzahl der gelöschten Dateien angezeigt.

**⚠️ Wichtiger Warnhinweis:** Dieses Skript löscht Dateien **dauerhaft**. Die gelöschten Dateien werden **nicht** in den Papierkorb verschoben und können nicht einfach wiederhergestellt werden. Führen Sie dieses Skript nur aus, wenn Sie sicher sind, dass Sie die `.ps`-Dateien nicht mehr benötigen. Es wird empfohlen, vor der Ausführung ein Backup des Verzeichnisses zu erstellen.

---

## Technische Voraussetzungen

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Das Skript verwendet nur die Standardbibliotheken `os` und `shutil`.

---

## Konfiguration im Skript

Vor der Ausführung muss die folgende Variable am Anfang des Skripts **unbedingt** angepasst werden:

*   `base_path`: Der absolute Pfad zum Hauptordner, in dem die Suche nach `.ps`-Dateien beginnen soll.

**Beispiel für macOS:**
```python
# Pfad zum Ordner, der aufgeräumt werden soll
base_path = "/Users/gregorneuboeck/Desktop/Sicherung_ZPH1082_011_Eisendle/ZPH1082_011_Eisendle Kopie"

**Beispiel für Windows:**
```python
# Pfad zum Ordner, der aufgeräumt werden soll
base_path = "C:\\Users\\IhrName\\Documents\\Archiv"

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT