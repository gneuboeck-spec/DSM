# SAM File Collector & Mapping Tool

Dieses Skript dient der zentralisierten Erfassung und Verwaltung von Lotus AmiPro Dokumenten (.sam), die über eine komplexe Ordnerstruktur verteilt sind. Es kopiert alle gefundenen Dateien in einen zentralen Sammelordner ("SAM"), löst Namenskollisionen durch eine intelligente Nummerierung auf und erstellt ein detailliertes Mapping-Protokoll.

Das Tool ist der erste Schritt in einem mehrstufigen Archivierungs-Workflow und stellt die notwendige Datenbasis für alle nachfolgenden Prozesse bereit.

---

## Workflow-Integration (WICHTIG)

Dieses Skript fungiert als **Vorbereitungswerkzeug**. Das hierbei automatisch erstellte Protokoll (`sam_file_mapping.txt`) ist die **zwingende Grundvoraussetzung** für das Rückkopier-Skript (PostScript_Rückkopierskript_Mapping_basiert.py). Ohne diese Log-Datei können die bearbeiteten oder konvertierten Dateien später nicht mehr automatisch ihren ursprünglichen Verzeichnissen zugeordnet werden.

**Empfohlener Ablauf:**
1. Dieses Skript ausführen, um alle `.sam`-Dateien im Ordner `SAM` zu bündeln.
2. Dateien im Sammelordner bearbeiten (z.B. Konvertierung nach PDF/PostScript).
3. Das Rückkopier-Skript verwenden, um die Ergebnisse basierend auf der Mapping-Datei wieder an die Originalschauplätze zu verteilen.

---

## Hauptfunktionen

*   **Vollständige Rekursion:** Durchsucht das gesamte Quellverzeichnis inklusive aller Unterebenen nach .sam-Dateien.
*   **Intelligentes Kollisions-Management:** Falls verschiedene Dateien in unterschiedlichen Ordnern denselben Namen tragen, benennt das Skript diese beim Kopieren automatisch um (z.B. BRIEF.sam -> BRIEF001.sam), anstatt sie zu überschreiben.
*   **Detailliertes Mapping-Log:** Erzeugt die Datei `sam_file_mapping.txt`, die lückenlos dokumentiert, welcher neue Dateiname welcher Originaldatei in welchem Pfad entspricht.
*   **Dubletten-Erkennung:** Identifiziert Dateien mit identischem Namen in verschiedenen Pfaden und markiert diese im Logfile als "Dubletten-Gruppe" für eine leichtere manuelle Prüfung.
*   **Metadaten-Erhalt:** Verwendet shutil.copy2, um ursprüngliche Zeitstempel und Dateiattribute beim Kopieren zu bewahren.

---

## Technische Voraussetzungen

*   Python: Version 3.4 oder neuer empfohlen.
*   Berechtigungen: Schreibzugriff auf das Quellverzeichnis, um den Unterordner "SAM" und die Log-Datei anzulegen.

---

## Konfiguration

Vor dem Start muss der Pfad zum Quellverzeichnis im Skript-Header angepasst werden:

    source_root = Path(r"C:\Users\digit\Desktop\Ihr_Projektordner")

Das vorangestellte 'r' stellt sicher, dass Windows-Backslashes korrekt interpretiert werden.

---

## Ausführung

Starten Sie das Skript über die Konsole:

    python collect_sam_files.py

### Ablauf des Prozesses

1. Indizierung: Das Skript scannt den Ordnerbaum und zählt alle SAM-Dateien.
2. Transfer: Die Dateien werden in den neu erstellten Ordner /SAM kopiert. Bei Namensgleichheit wird ein dreistelliger Zähler an den Dateinamen angehängt.
3. Protokollierung: Das Mapping-File sam_file_mapping.txt wird erstellt. Jede Zeile folgt dem Schema:
   NeuerName.sam <-- OriginalName | Vollständiger_Ursprungspfad
4. Bericht: Am Ende wird die Gesamtzahl der verarbeiteten Dateien ausgegeben.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT