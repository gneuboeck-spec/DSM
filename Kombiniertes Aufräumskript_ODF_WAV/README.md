\# Kombiniertes Aufräumskript (ODF \& WAV)



Dieses Skript ist ein zentrales Werkzeug zur Bereinigung des Arbeitsverzeichnisses nach Abschluss der Konvertierungsprozesse. Es vereint zwei spezialisierte Aufräum-Funktionen in einem einzigen, menügesteuerten Skript: das Löschen von temporären OpenDocument-Dateien und das Löschen von unkomprimierten WAV-Archivdateien.



Der Zweck des Skripts ist es, Speicherplatz zu sparen und die endgültige Dateisammlung zu finalisieren, indem nur die Quelldateien und die finalen, archivsicheren Derivate (z.B. PDF, MP3) zurückbleiben.



\## Kernfunktionen und Sicherheitsmechanismen



Das Skript bietet dem Benutzer über ein Menü zwei voneinander unabhängige Aufräum-Aktionen an. Beide Aktionen basieren auf einer präzisen und sicheren Identifikationslogik:



1\.  \*\*Zwischendateien (ODF) löschen:\*\*

&nbsp;   \*   \*\*Ziel:\*\* Löscht `.odt`, `.ods` und `.odp` Dateien.

&nbsp;   \*   \*\*Logik:\*\* Eine Datei wie `bericht.doc.odt` wird nur gelöscht, wenn die Originaldatei `bericht.doc` noch im selben Ordner existiert.

&nbsp;   \*   \*\*Sicherheit:\*\* Verfügt über einen `DRY\_RUN`-Modus (Testlauf) und erfordert im Echt-Modus eine explizite Benutzerbestätigung.



2\.  \*\*Konvertierte WAV-Dateien löschen:\*\*

&nbsp;   \*   \*\*Ziel:\*\* Löscht `.wav` Dateien.

&nbsp;   \*   \*\*Logik:\*\* Eine Datei wie `lied.mp3.wav` wird nur gelöscht, wenn die Originaldatei `lied.mp3` noch im selben Ordner existiert.

&nbsp;   \*   \*\*Sicherheit:\*\* Fordert immer eine explizite Benutzerbestätigung vor dem Löschen an.



Beide Aktionen erstellen ihre eigenen, separaten Log-Dateien, um die durchgeführten Löschungen nachvollziehbar zu machen.



---



\## Technische Voraussetzungen



\*   \*\*Python:\*\* Version 3.6 oder neuer. Es sind keine externen Bibliotheken erforderlich.



---



\## Konfiguration im Skript



Die Konfiguration erfolgt über Schalter und Listen am Anfang des Skripts:



```python

\# --- Konfiguration für "Zwischendateien (ODF) löschen" ---

DELETE\_ODF\_DRY\_RUN = False



\# --- Konfiguration für "Konvertierte WAVs löschen" ---

SOURCE\_AUDIO\_EXTENSIONS\_FOR\_WAV\_CLEANUP = {".aiff", ".flac", ...}



\*   \*\*`DELETE\_ODF\_DRY\_RUN`\*\*: `True` für einen sicheren Testlauf (nur für ODF), `False` für den echten Löschvorgang.

\*   \*\*`SOURCE\_AUDIO\_EXTENSIONS\_FOR\_WAV\_CLEANUP`\*\*: Diese Liste muss exakt mit der Liste der Quellformate aus dem Audio-Konvertierungsskript übereinstimmen.



\### Erwartete Ordnerstruktur



Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:

Documents

└── Datentraeger\_sichern

&nbsp;   └── \[AC-Nummer]

&nbsp;       └── \[Datenträger-ID]

&nbsp;           └── 3\_\[Datenträger-ID]\_for-transfer

&nbsp;               ├── Files  <-- IN DIESEM ORDNER WIRD AUFGERÄUMT

&nbsp;               └── (Hier werden die Log-Dateien erstellt)



\*   \*\*`\[AC-Nummer]`\*\*: Die Haupt-Archivierungsnummer des Projekts.

\*   \*\*`\[Datenträger-ID]`\*\*: Die eindeutige ID des zu verarbeitenden Datenträgers.



\## Ausführung



Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.



\*\*Beispielhafter Aufruf in einer `start.bat`:\*\*

@echo off

set AC\_NUMBER=AC\_0001

set DISK\_ID=CD\_01

python combined\_cleanup\_skript.py %AC\_NUMBER% %DISK\_ID%

pause



\### Ablauf der Ausführung



1\.  \*\*Validierung:\*\* Das Skript prüft die übergebenen Argumente und die Ordnerstruktur.

2\.  \*\*Menüanzeige:\*\* Dem Benutzer wird ein Menü mit den verfügbaren Aufräum-Aktionen (ODF löschen, WAV löschen, Beenden) angezeigt.

3\.  \*\*Aktion ausführen:\*\* Nach der Auswahl des Benutzers wird die entsprechende Funktion gestartet.

4\.  \*\*Suche \& Bestätigung:\*\* Das Skript sucht nach den relevanten Dateien, listet sie auf und fordert eine explizite Bestätigung (`j/n`) vom Benutzer.

5\.  \*\*Löschvorgang:\*\* Nach der Bestätigung werden die Dateien gelöscht.

6\.  \*\*Protokollierung:\*\* Die durchgeführten Aktionen werden in eine spezifische Log-Datei für die jeweilige Aufgabe geschrieben.

7\.  \*\*Rückkehr zum Menü:\*\* Nach Abschluss der Aktion kehrt das Skript zum Hauptmenü zurück.

8\.  \*\*Abschluss:\*\* Nachdem der Benutzer das Skript über das Menü beendet hat, wird gefragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.

