# PostScript-Rückkopierskript (Mapping-basiert)

Dieses Skript dient der automatisierten Rückführung von PostScript-Dateien (.ps) in ihre ursprünglichen Verzeichnisse. Es ist ein komplementäres Werkzeug zu Prozessen, bei denen Dateien zur zentralen Bearbeitung (z. B. Konvertierung von Lotus AmiPro Dokumenten) extrahiert und umbenannt wurden. Das Skript nutzt eine Mapping-Logdatei, um die ursprünglichen Pfade zu identifizieren und die Dateien exakt dort wieder abzulegen.

Das Werkzeug stellt sicher, dass die räumliche Integrität der Originaldatenstruktur nach der Bearbeitung wiederhergestellt wird.

---

## Hauptfunktionen

*   **Log-basiertes Dateimanagement:** Liest eine spezifische Mapping-Datei (`sam_file_mapping.txt`), um die Zuordnung zwischen den neuen Dateinamen und den ursprünglichen Speicherorten zu ermitteln.
*   **Präzise Rekonstruktion:** Kopiert .ps-Dateien aus einem Sammelordner zurück in die Originalpfade und übernimmt dabei automatisch den Stamm-Dateinamen der ursprünglichen .sam-Datei.
*   **Automatische Verzeichniserstellung:** Falls Zielordner in der Zwischenzeit gelöscht oder verschoben wurden, erstellt das Skript die notwendige Ordnerhierarchie (`mkdir -p`) selbstständig neu.
*   **Metadaten-Erhalt:** Nutzt `shutil.copy2`, um beim Kopieren der Dateien so viele Metadaten (wie Zeitstempel) wie möglich zu erhalten.
*   **Fehlertoleranz:** Überspringt fehlerhafte Einträge in der Log-Datei oder fehlende Quelldateien automatisch und gibt entsprechende Warnmeldungen im Terminal aus.

---

## Technische Voraussetzungen

*   **Python:** Version 3.4 oder neuer empfohlen (nutzt das `pathlib`-Modul für Windows-Pfadkompatibilität).
*   **Mapping-Datei:** Eine Textdatei, die dem Format `NeuerName.sam <-- OriginalName | C:\Pfad\Original` entspricht.

---

## Konfiguration

Vor der Ausführung müssen die Pfade im Abschnitt "BITTE ANPASSEN" im Skript-Header hinterlegt werden:

1.  **`sam_dir`**: Der Ordner, in dem sich die aktuell bearbeiteten .sam- und .ps-Dateien befinden.
2.  **`log_file_path`**: Der Pfad zur Mapping-Datei, die beim ursprünglichen Kopiervorgang erstellt wurde.

    sam_dir = Path(r"C:\Users\digit\Desktop\Sicherung\SAM")
    log_file_path = Path(r"C:\Users\digit\Desktop\Sicherung\sam_file_mapping.txt")

Das vorangestellte 'r' sorgt für die korrekte Interpretation der Windows-Backslashes.

---

## Ausführung

Starten Sie das Skript über die Konsole oder per Doppelklick:

    python copy_ps_back.py

### Ablauf der Wiederherstellung

1.  **Validierung:** Prüfung, ob der Quellordner und die Mapping-Logdatei existieren.
2.  **Parsing:** Zeilenweises Einlesen der Logdatei und Extraktion der Pfadinformationen.
3.  **Pfad-Mapping:** Umwandlung des neuen Namens (z.B. `DOC001.ps`) zurück in den ursprünglichen Zielnamen und Pfad.
4.  **Dateitransfer:** Durchführung des Kopiervorgangs.
5.  **Statusbericht:** Echtzeit-Rückmeldung im Terminal über jede erfolgreich kopierte oder fehlende Datei.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT