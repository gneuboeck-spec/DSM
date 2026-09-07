SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com

# 📚 Elektronischer Nachlass-Analysator

Eine automatisierte Python-Pipeline zur systematischen Bewertung elektronischer Vor- und Nachlässe (z. B. von Autor:innen). Das Tool hilft Archivar:innen und Bewerter:innen dabei, den tatsächlichen Umfang, die Einzigartigkeit und den Wert eines Dokumentenbestands objektiv und effizient zu ermitteln.

## 🎯 Zielsetzung
Bei der monetären und archivischen Bewertung eines Nachlasses ist es entscheidend zu wissen, ob eine Sammlung aus hunderten einzigartigen Textdokumenten oder aus zahlreichen Kopien und Dubletten besteht. Diese Skriptsammlung automatisiert den Bereinigungs-, Analyse- und Visualisierungsprozess, um den *echten* textuellen Wert eines Bestands schnell sichtbar zu machen.

## 🚀 Workflow (Empfohlene Reihenfolge)
Die Skripte sind nummeriert und sollten idealerweise in dieser Reihenfolge über die zentrale `menu.py` ausgeführt werden:

1. **`01_Dublikatenfinder.py`**: Entfernt 100%ige Prüfsummendubletten, um den Datenbestand zu verschlanken und nachfolgende Schritte zu beschleunigen.
2. **`02_Analyse_Skript_Brunnhilde_Fixity.py`**: Erstellt einen tiefgehenden Überblick über alle vorhandenen Dateitypen und prüft auf Integrität und Schadsoftware (via Siegfried & ClamAV).
3. **`03_Bereinigungsskript.py`**: Entfernt systembedingten Dateimüll (z. B. `.tmp`, `Thumbs.db`, Konvertierungslogs), damit sich Bewerter:innen nicht mit irrelevanten Dateien abmühen müssen.
4. **`04_Dokumente_vergleichen.py`**: Führt hochperformante, mathematische Textvergleiche durch und ordnet ähnliche Dokumente in logische Versionsgruppen ein.
5. **`05_KI_Analyse.py`**: Nutzt semantische KI-Modelle, um kurze Texte (Abstracts, Zusammenfassungen, Rezensionen) zu erkennen und den Hauptdokumentengruppen zuzuordnen.
6. **`06_Visualisierung.py`**: Stellt die Ergebnisse der Gruppierung und KI-Analyse in intuitiven, interaktiven Diagrammen dar, um die Bedeutung des Nachlasses besser begreifbar zu machen.

## 🛠️ Voraussetzungen
- **Python**: 3.10 oder höher (empfohlen: 3.13)
- **Externe Tools** (für Skript 02): 
  - [Siegfried](https://www.itforarchivists.com/siegfried/) (`sf.exe`)
  - [ClamAV](https://www.clamav.net/) (`clamscan.exe`)
- **Python-Pakete**: `pip install -r requirements.txt`

### `requirements.txt`
```text
python-docx
pymupdf
openpyxl
sentence-transformers
torch
rapidfuzz
matplotlib