SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com

---

# 02_Analyse_Skript_Brunnhilde_Fixity/README.md

```markdown
# 🔍 02_Analyse_Skript_Brunnhilde_Fixity.py

Dieses Skript nutzt das Tool **Brunnhilde** (in Kombination mit Siegfried und ClamAV), um eine tiefgehende Analyse des Dateibestands durchzuführen. Es ist entscheidend, um festzustellen, wie viele *echte* Textdokumente in einem Nachlass vorhanden sind, im Gegensatz zu reinen Metadaten- oder Systemdateien.

## ⚙️ Funktionsweise
1. **Fixity-Check**: Berechnet SHA-256-Prüfsummen für alle Dateien zur Sicherstellung der Integrität.
2. **Virenscan**: Führt einen ClamAV-Scan durch (mit automatischer Warnung bei veralteten Virendefinitionen).
3. **Format-Identifikation**: Nutzt Siegfried, um den wahren Dateityp (unabhängig von der Dateiendung) zu ermitteln.
4. **Berichterstellung**: Generiert einen `tree.txt` (Verzeichnisstruktur) und eine zusammenfassende JSON-Datei direkt im Berichtsordner.

## 🔧 Voraussetzungen
Die Pfade zu den externen Tools müssen im Skript korrekt hinterlegt sein:
```python
SIEGFRIED_DIR = r"C:\Program Files\Siegfried"
CLAMAV_DIR = r"C:\Program Files\ClamAV" 