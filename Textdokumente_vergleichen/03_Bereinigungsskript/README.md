SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com


---

# 03_Bereinigungsskript/README.md

```markdown
# 🗑️ 03_Bereinigungsskript.py

Entfernt automatisch bekannten, inhaltsleeren Dateimüll, der für die literarische Bewertung irrelevant ist und die nachfolgenden Analysen nur verlangsamen würde.

## ⚙️ Funktionsweise
Das Skript durchsucht das Verzeichnis rekursiv und markiert Dateien zur Löschung, wenn sie:
- Bestimmte Dateiendungen haben (z. B. `.tmp`, `.bak`, `.lnk`, `.ds_store`).
- Systemdateien sind (z. B. `Thumbs.db`, `desktop.ini`).
- Bestimmte Schlüsselwörter im Namen enthalten (z. B. `konvertierungslog`, `bereinigungslog`).
- Leere Ordner sind.

Wie beim Dublettenfinder gibt es einen **Vorschau-Modus** mit automatischer Öffnung der CSV-Liste vor der endgültigen Löschung.

## 🔧 Konfiguration
Passe die Listen im Konfigurationsbereich an deine spezifischen Bedürfnisse an:
```python
DRY_RUN = False  # Simulation ohne Löschung
DELETE_KEYWORDS = ["video_konvertierung", "konvertierungslog", ...]
SYSTEM_HIDDEN_FILES = ["Thumbs.db", "desktop.ini"]
DELETE_EXTENSIONS = [".tmp", ".bak", ".lnk", ...] # Umfangreiche Liste vordefinierter Endungen