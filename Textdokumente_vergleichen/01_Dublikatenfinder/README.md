SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com
---

# 01_Dublikatenfinder/README.md

```markdown
# 🧹 01_Dublikatenfinder.py

Dieses Skript identifiziert und entfernt 100%ige Dateidubletten basierend auf SHA-256-Prüfsummen. Es ist der empfohlene erste Schritt in der Pipeline, um den Datenbestand zu verschlanken und nachfolgende Textvergleiche drastisch zu beschleunigen.

## ⚙️ Funktionsweise
1. **Größen-Filter**: Gruppiert alle Dateien nach ihrer exakten Byte-Größe (nur Dateien gleicher Größe können Dubletten sein).
2. **SHA-256-Hashing**: Berechnet Prüfsummen nur für die potenziellen Dubletten, was extrem ressourcenschonend ist.
3. **Vorschau-Modus**: Erstellt eine CSV-Datei mit allen gefundenen Dubletten und öffnet diese automatisch zur Kontrolle.
4. **Sichere Löschung**: Löscht nach expliziter Bestätigung alle Duplikate, behält aber immer genau eine Datei pro Gruppe als "Original".

## 🔧 Konfiguration
Öffne die Datei und passe bei Bedarf folgende Variable an:
```python
DRY_RUN = False  # Auf True setzen, um das Skript nur zu simulieren, ohne Dateien zu löschen