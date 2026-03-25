# Universeller Office-Dokumenten-Konverter (ODF & PDF/A)

Dieses Skript ist ein leistungsstarkes Werkzeug zur automatisierten Batch-Konvertierung einer breiten Palette von Office-Dokumenten (Text, Tabellen, Präsentationen) in standardisierte Archivformate. Es nutzt die Kommandozeilen-Schnittstelle von LibreOffice, um für jede Quelldatei sowohl eine offene, bearbeitbare Version als auch ein stabiles, archivsicheres PDF/A zu erstellen.

Das Skript ist als integraler Bestandteil eines automatisierten Archivierungsworkflows konzipiert und wird über eine Start-Datei (`start.bat`) mit dynamischen Pfaden gesteuert.

## Das "Digital Twin"-Konvertierungsprinzip

Für jede unterstützte Quelldatei (z.B. `.doc`, `.xls`, `.ppt`) führt das Skript einen zweistufigen Prozess durch, um ein "digitales Zwillingspaar" zu erzeugen:

1.  **Konvertierung zu OpenDocument Format (ODF):**
    *   Die Originaldatei wird zuerst in ihr modernes, offenes Gegenstück konvertiert (`.odt`, `.ods` oder `.odp`). Dies stellt die zukünftige Bearbeitbarkeit und Interoperabilität sicher.
    *   *Beispiel: `bericht.doc` → `bericht.doc.odt`*

2.  **Konvertierung zu PDF/A:**
    *   Die neu erstellte ODF-Datei wird anschließend in ein PDF/A-2 konvertiert. Dieses Format ist für die Langzeitarchivierung optimiert und garantiert eine konsistente Darstellung über die Zeit.
    *   *Beispiel: `bericht.doc.odt` → `bericht.doc.pdf`*

**Sonderfall:** Bereits existierende `.pdf`-Dateien werden direkt in das PDF/A-Format überführt, um ihre Archivtauglichkeit zu verbessern.

Die Namenskonvention `Originalname.originalendung.zielendung` stellt sicher, dass die Herkunft jeder konvertierten Datei lückenlos nachvollziehbar bleibt.

---

## Technische Voraussetzungen

1.  **Python:** Version 3.6 oder neuer.
2.  **LibreOffice:** Eine vollständige Installation von LibreOffice ist erforderlich. Das Skript benötigt Zugriff auf die ausführbare Datei `soffice.exe`.

---

## Konfiguration im Skript

Vor der ersten Ausführung muss der Pfad zur LibreOffice-Installation am Anfang des Skripts überprüft und bei Bedarf angepasst werden.

```python
# --- 1. System-Pfade (manuell anpassen, falls nötig) ---
LIBREOFFICE_PATH = "C:/Program Files/LibreOffice/program/soffice.exe"
*   **`LIBREOFFICE_PATH`**: Dieser Pfad muss exakt auf die `soffice.exe` (oder `soffice.bin` auf anderen Systemen) in Ihrem LibreOffice-Installationsverzeichnis zeigen. Der Standardpfad im Skript ist ein häufiges Beispiel für Windows.

Die `CONVERSION_MAP` im Skript definiert alle unterstützten Quellformate und die entsprechenden LibreOffice-Exportfilter.

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 3_[Datenträger-ID]_for-transfer
                ├── Files  <-- IN DIESEM ORDNER WIRD GESUCHT
                └── (Hier wird die Log-Datei erstellt)```

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

---

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python office_conversion_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die übergebenen Argumente, die Ordnerstruktur und ob die `soffice.exe` am konfigurierten Pfad gefunden wird.
2.  **Suche:** Das `Files`-Verzeichnis wird rekursiv nach allen unterstützten Office-Dateien durchsucht. Eine intelligente Logik stellt sicher, dass bereits konvertierte Dateien übersprungen werden.
3.  **Konvertierung (pro Datei):** Für jede neue Datei wird der zweistufige Konvertierungsprozess (ODF, dann PDF/A) gestartet. Der Fortschritt wird mit einem Balken in der Konsole angezeigt.
4.  **Protokollierung:** Alle Aktionen, Erfolge und insbesondere Fehler werden detailliert in die Log-Datei `3_[Datenträger-ID]_text_conversion.log` geschrieben.
5.  **Zusammenfassung:** Nach Abschluss aller Vorgänge wird eine finale Statusmeldung in der Konsole und im Log ausgegeben.
6.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.