import os
import subprocess
from datetime import datetime
import sys

# --- KONFIGURATION (Für Windows 11 anpassen) ---

# 1. Geben Sie hier den Pfad zum Ordner ein, der Ihre Bilder enthält.
#    Verwenden Sie normale Slashes (/), Python wandelt sie korrekt um.
input_folder = "C:/Users/Digit/Desktop/Bildformate_konvertieren"

# 2. Pfad für die Log-Datei (wird automatisch im input_folder erstellt)
logfile_path = os.path.join(input_folder, "konvertierungs_log.txt")

# 3. Pfade zu den Kommandozeilen-Tools
#    Wenn die Programme im System-PATH sind, reicht der Name der .exe-Datei.
imagemagick_path = "magick.exe"
inkscape_path = "inkscape.exe"
ghostscript_path = "gswin64c.exe" # Name für die Ghostscript-Kommandozeile

# 4. Listen der unterstützten Formate
raster_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tga", ".gif", ".jfif"}
# Formate, für die Ghostscript direkt zuständig ist
ghostscript_formats = {".eps", ".pdf", ".ai"}
# Restliche Vektorformate, für die Inkscape zuständig ist
vector_extensions = {".svg", ".wmf"}

# 5. Zieldateiendungen
raster_target_ext = ".tiff"
vector_target_ext = ".pdf"
# --- ENDE DER KONFIGURATION ---


# Ersetze "IhrBenutzername" im Pfad, falls es noch der Platzhalter ist
if "IhrBenutzername" in input_folder:
    print("="*60)
    print("BITTE BEARBEITEN SIE DAS SKRIPT!")
    print("Ersetzen Sie 'IhrBenutzername' in der Variable 'input_folder' mit Ihrem tatsächlichen Windows-Benutzernamen.")
    print("="*60)
    sys.exit(1)

# --- Sicherheits-Check ---
print("="*60)
print(f"INFO: Das Skript wird den folgenden Ordner durchsuchen:")
print(f"-> {input_folder}")
if not os.path.isdir(input_folder):
    print("\nFEHLER: Der oben angegebene Ordner existiert nicht.")
    sys.exit(1)
print("="*60)


# --- Globale Variablen ---
converted_count = 0
error_count = 0
log_lines = []
all_files = []


# --- Dateisuche (KORRIGIERTE LOGIK) ---
print("Suche nach zu verarbeitenden Quelldateien...")
# Kombiniere alle bekannten Quellformate in einer Liste
valid_source_extensions = raster_extensions.union(vector_extensions).union(ghostscript_formats)

for root, _, files in os.walk(input_folder):
    for filename in files:
        if filename.startswith('.') or filename.startswith('~'):
            continue

        # Prüfe, ob die Datei eine unserer Derivat-Dateien ist
        # z.B. "name.jpg.tiff" oder "name.svg.pdf"
        parts = filename.lower().split('.')
        if len(parts) >= 3:
            original_ext = f".{parts[-2]}"
            derivat_ext = f".{parts[-1]}"
            if original_ext in valid_source_extensions and (derivat_ext.replace('.', '') == raster_target_ext.replace('.', '') or derivat_ext.replace('.', '') == vector_target_ext.replace('.', '')):
                # Dies ist eine Zieldatei, ignoriere sie als Quelle.
                continue
        
        # Normale Prüfung für Quelldateien
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_source_extensions:
            all_files.append(os.path.join(root, filename))

total = len(all_files)
print(f"{total} relevante Grafikdateien im angegebenen Ordner gefunden.")
if total == 0:
    sys.exit()

# --- Hauptverarbeitung ---
print("\nStarte universelle Grafik-Konvertierung...")

for idx, abs_path in enumerate(all_files, 1):
    rel_path = os.path.relpath(abs_path, input_folder)
    root, filename = os.path.split(abs_path)
    base, ext = os.path.splitext(filename)
    ext = ext.lower()

    percent = (idx / total) * 100
    print(f"[{idx}/{total}] {percent:6.2f}% → {rel_path}")
    log_lines.append(f"\n--- Verarbeite: {filename} ---")
    
    # --- Intelligente Weiche ---
    if ext in raster_extensions:
        tool_name = "ImageMagick"
        tool_path = imagemagick_path
        target_ext = raster_target_ext
        output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename)
        cmd = [tool_path, "-quiet", abs_path, output_path]

    elif ext in ghostscript_formats:
        tool_name = "Ghostscript"
        tool_path = ghostscript_path
        target_ext = vector_target_ext
        output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename)
        cmd = [tool_path, "-sDEVICE=pdfwrite", "-dBATCH", "-dNOPAUSE", f"-sOutputFile={output_path}", abs_path]

    elif ext in vector_extensions:
        tool_name = "Inkscape"
        tool_path = inkscape_path
        target_ext = vector_target_ext
        output_filename = f"{base}{ext}{target_ext}"
        output_path = os.path.join(root, output_filename)
        cmd = [tool_path, abs_path, f"--export-filename={output_path}", "--export-text-to-path", "--export-pdf-version=1.5"]
    
    else:
        log_lines.append(f"[INFO] Unbekannter Dateityp '{ext}', wird übersprungen.")
        continue

    # KORRIGIERTE ÜBERSCHREIB-LOGIK: Alte Zieldatei proaktiv löschen
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            log_lines.append(f"[INFO] Alte Zieldatei wird überschrieben: {output_filename}")
        except OSError as e:
            log_lines.append(f"[FEHLER] Alte Zieldatei konnte nicht gelöscht werden: {output_filename} ({e})")
            error_count += 1
            continue

    # Den passenden Befehl ausführen
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0 and os.path.exists(output_path):
            converted_count += 1
            log_lines.append(f"[OK] Konvertiert mit {tool_name}: {filename} → {output_filename}")
        else:
            error_count += 1
            log_lines.append(f"[FEHLER] {tool_name} hat KEINE Zieldatei erstellt für: {filename}")
            if result.stderr:
                log_lines.append(f"       Fehlermeldung: {result.stderr.strip()}")

    except FileNotFoundError:
        error_count += 1
        log_lines.append(f"[KRITISCHER FEHLER] Befehl '{tool_path}' nicht gefunden.")
    except Exception as e:
        error_count += 1
        log_lines.append(f"[FEHLER] Ein unerwartetes Problem ist aufgetreten bei: {filename} ({e})")

# --- Logfile schreiben ---
with open(logfile_path, "w", encoding="utf-8") as log_file:
    log_file.write(f"LOG VOM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    log_file.write("--- ZUSAMMENFASSUNG ---\n")
    log_file.write(f"Verarbeitete Dateien insgesamt: {total}\n")
    log_file.write(f"Erfolgreich konvertiert: {converted_count}\n")
    log_file.write(f"Fehler bei Konvertierung: {error_count}\n")
    log_file.write("\n--- DETAILLIERTES PROTOKOLL ---\n")
    log_file.write("".join(log_lines))

print(f"\nFertig. {converted_count} Dateien konvertiert, {error_count} Fehler.")
print(f"Log gespeichert unter: {logfile_path}")