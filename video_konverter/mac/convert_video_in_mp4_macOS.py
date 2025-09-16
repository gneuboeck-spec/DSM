import os
import subprocess
import sys
from datetime import datetime

# --- KONFIGURATION ---
input_folder = "/Users/gregorneuboeck/Desktop/Videodateien_konvertieren"
log_file_path = os.path.join(input_folder, "video_konvertierung.log")

# Liste der zu verarbeitenden Quellformate.
# .mp4 wird HIER NICHT aufgeführt, da Original-MP4-Dateien ignoriert werden sollen.
source_video_extensions = {".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".vob", ".m2ts"}
# --- ENDE DER KONFIGURATION ---


def log(message):
    """Schreibt eine Nachricht mit Zeitstempel in die Log-Datei und auf die Konsole."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(timestamp + message + "\n")
    except Exception as e:
        print(f"KRITISCHER FEHLER: Konnte nicht in Log-Datei schreiben: {e}")
    print(timestamp + message)


def convert_to_mp4(input_path, output_path):
    """
    Konvertiert eine Videodatei nach MP4 mit FFmpeg.
    Überschreibt die Zieldatei dank des '-y' Parameters automatisch.
    Gibt True bei Erfolg, False bei Fehler zurück.
    """
    log(f"Starte Konvertierung: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    
    command = [
        "ffmpeg",
        "-y",  # Zieldatei ohne Nachfrage überschreiben
        "-i", input_path,
        "-c:v", "libx264",    # Video-Codec: H.264 (sehr kompatibel)
        "-preset", "fast",     # Guter Kompromiss zwischen Geschwindigkeit und Dateigröße
        "-crf", "22",          # Qualitätsfaktor (niedriger=besser, 18-28 ist ein guter Bereich)
        "-c:a", "aac",         # Audio-Codec: AAC (sehr kompatibel)
        "-b:a", "192k",        # Audio-Bitrate
        "-movflags", "+faststart", # Optimiert für Streaming/Web-Wiedergabe
        output_path
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        log(f"[OK] Erfolgreich konvertiert: {os.path.basename(output_path)}")
        return True
    except FileNotFoundError:
        log("[KRITISCHER FEHLER] ffmpeg wurde nicht gefunden. Ist es installiert und im System-PATH?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        log(f"[FEHLER] Konvertierung fehlgeschlagen für: {os.path.basename(input_path)}")
        log(f"         FFmpeg-Fehler: {e.stderr.strip()}")
        return False


# --- HAUPTPROGRAMM ---
log("Starte Video-Konvertierungsskript (Modus: Überschreiben).")

# Schritt 1: Finde alle relevanten Quelldateien
source_files = []
for root, _, files in os.walk(input_folder):
    for filename in files:
        if filename.startswith('.') or filename.startswith('~'):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext in source_video_extensions:
            source_files.append(os.path.join(root, filename))

if not source_files:
    log("Keine zu konvertierenden Videodateien gefunden. Skript wird beendet.")
    sys.exit()

log(f"{len(source_files)} Quelldateien gefunden. Beginne Verarbeitung...")

# Schritt 2: Verarbeite jede Quelldatei
converted_count = 0
for input_path in source_files:
    root, filename = os.path.split(input_path)
    
    # Definiere den Zieldateinamen basierend auf dem Original-Dateinamen
    mp4_target_path = os.path.join(root, f"{filename}.mp4")
    
    log(f"--- Verarbeite '{filename}' ---")
    
    # Die Konvertierung wird immer ausgeführt.
    # Da die Zieldatei (z.B. video.mov.mp4) von einer Quelldatei (video.mov) abhängt,
    # wird eine originale MP4-Datei (die nicht in der Quell-Liste ist) niemals überschrieben.
    if convert_to_mp4(input_path, mp4_target_path):
        converted_count += 1

log(f"Videokonvertierung abgeschlossen. {converted_count} von {len(source_files)} Dateien erfolgreich konvertiert.")