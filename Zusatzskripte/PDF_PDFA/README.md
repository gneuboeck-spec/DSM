# PDF/A-Veredelungsskript für AmiPro-Dokumente (.sam.pdf)

Dieses Skript ist ein spezialisiertes Werkzeug zur Erzeugung von archivkonformen PDF/A-2b Dateien aus bereits vorhandenen PDFs, die ursprünglich aus Lotus AmiPro (.sam) Dateien erzeugt wurden. Da einfache PDF-Exporte oft nicht die strengen Anforderungen der Langzeitarchivierung erfüllen, nutzt dieses Skript LibreOffice, um die Dokumente über einen Umweg (ODG) technisch aufzuwerten und als valide PDF/A-Dateien neu zu schreiben.

Das Skript ist für den Einsatz als Folgeschritt nach einer ersten Formatwandlung konzipiert.

---

## Hauptfunktionen

*   **Zweistufiger Veredelungsprozess:**
    1. Wandelt die Quell-PDF (`.sam.pdf`) intern in das OpenDocument Graphics Format (`.odg`) um.
    2. Exportiert dieses ODG unter Verwendung eines speziellen Filters (`SelectPdfVersion=2`) als ISO-konformes PDF/A-2b.
*   **Automatisches Prozess-Management:** Beendet vor jeder Konvertierung laufende LibreOffice-Instanzen (`taskkill`), um Dateisperren und Abstürze im Headless-Modus zu verhindern.
*   **Intelligente Bereinigung:** Entfernt alle während des Prozesses erzeugten Zwischendateien (.odg) automatisch nach dem erfolgreichen Export.
*   **Fortschrittsanzeige & Logging:** Bietet eine visuelle Fortschrittsleiste in der Konsole und führt ein detailliertes Konvertierungslog (`konvertierungslog.txt`) im Zielordner.
*   **Vollständige Rekursion:** Durchsucht das angegebene Verzeichnis und alle Unterordner gezielt nach Dateien mit der Endung `.sam.pdf`.

---

## Technische Voraussetzungen

*   **Python:** Version 3.4 oder neuer empfohlen.
*   **LibreOffice:** Muss auf dem System installiert sein. Das Skript benötigt den Pfad zur `soffice.exe`.
*   **Betriebssystem:** Optimiert für Windows.

---

## Konfiguration

Vor dem Start müssen die Pfade im Abschnitt "BITTE ANPASSEN" im Skript-Header hinterlegt werden:

    libreoffice_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
    input_folder = Path(r"C:\Pfad\zu\Ihren\Dateien")

Das vorangestellte 'r' bei den Pfaden stellt sicher, dass Windows-Backslashes korrekt verarbeitet werden.

---

## Ausführung

Starten Sie das Skript über die Konsole:

    python refine_sam_pdf.py

### Ablauf der Verarbeitung

1. **Systemcheck:** Validierung der Pfade zu LibreOffice und dem Arbeitsordner.
2. **Dateisuche:** Erfassung aller relevanten `.sam.pdf`-Dateien.
3. **Konvertierungszyklus:**
   - Bestehende Instanzen von LibreOffice werden geschlossen.
   - Die PDF wird als Vektorgrafik (ODG) geöffnet.
   - Ein neuer PDF/A-Container wird mit den Metadaten der Grafikdatei geschrieben.
4. **Ergebnissicherung:** Die ursprüngliche `.sam.pdf` wird durch die veredelte Version ersetzt.
5. **Abschluss:** Zusammenfassende Meldung im Terminal und Eintrag im Logfile.

---

## Sicherheitshinweis

Das Skript überschreibt die vorhandenen `.sam.pdf`-Dateien mit der veredelten PDF/A-Version. Es wird empfohlen, diesen Schritt nur an Kopien der Daten oder in einer gesicherten Staging-Umgebung durchzuführen.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT