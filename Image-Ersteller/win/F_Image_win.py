# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import tarfile
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# HINZUGEFÜGT: Version des Skripts für das Logging
SCRIPT_NAME = Path(__file__).name
SCRIPT_VERSION = "1.0"

def setup_and_validate_paths(ac_number, disk_archive_id):
    """
    Erstellt und validiert die Projekt-Pfade für das Image-Skript.
    """
    project_base_path = Path.home() / "Documents/data" / ac_number / disk_archive_id
    transfer_folder = project_base_path / f"3_{disk_archive_id}_for-transfer"
    source_folder = transfer_folder / "files"
    output_folder = project_base_path / f"5_{disk_archive_id}_LZA"
    image_base_name = f"5_{disk_archive_id}_LZA_derivation-image"
    
    paths = {
        "source_folder": source_folder,
        "output_folder": output_folder,
        "image_filepath": output_folder / f"{image_base_name}.img",
        "log_filepath": output_folder / f"{image_base_name}.log"
    }

    if not paths["source_folder"].is_dir():
        print(f"Fehler: Der Quell-Ordner 'Files' wurde nicht gefunden:\n{paths['source_folder']}")
        return None
    
    try:
        paths["output_folder"].mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Fehler: Der Ziel-Ordner konnte nicht erstellt werden:\n{e}")
        return None

    return paths

# ==============================================================================
# --- LOGGING-KONFIGURATION ---
# ==============================================================================

def setup_logging(log_filepath):
    """Konfiguriert das Logging."""
    logger = logging.getLogger('ImageCreator')
    logger.setLevel(logging.INFO)
    if logger.hasHandlers(): logger.handlers.clear()
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)
    fh = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(fh)
    return logger

# ==============================================================================
# --- SKRIPT-LOGIK ---
# ==============================================================================

def create_tar_image(source_dir: Path, image_path: Path, logger: logging.Logger):
    """
    Erstellt ein TAR-Archiv (.img) und gibt bei Erfolg True zurück.
    """
    logger.info(f"Starte die Erstellung des Archiv-Images mit '{SCRIPT_NAME} v{SCRIPT_VERSION}'.")
    logger.info(f"Quellverzeichnis: {source_dir}")
    logger.info(f"Zieldatei: {image_path}")
    try:
        with tarfile.open(image_path, "w") as tar:
            tar.add(source_dir, arcname='Files')
        logger.info(f"Archiv-Image wurde erfolgreich erstellt.")
        return True
    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}", exc_info=True)
        return False

def calculate_sha512(filepath: Path, logger: logging.Logger) -> str:
    """Berechnet den SHA-512 Hash einer Datei."""
    logger.info(f"Berechne SHA-512 Hash für: {filepath.name}")
    sha512_hash = hashlib.sha512()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha512_hash.update(byte_block)
        hex_digest = sha512_hash.hexdigest()
        logger.info(f"SHA-512 Hash erfolgreich berechnet.")
        return hex_digest
    except Exception as e:
        logger.error(f"Fehler bei der Hash-Berechnung: {e}")
        return None

# ==============================================================================
# --- HAUPT-AUSFÜHRUNGSBLOCK ---
# ==============================================================================
if __name__ == "__main__":
    try:
        ac_number_input = sys.argv[1]
        disk_archive_id_input = sys.argv[2]
    except IndexError:
        print("FEHLER: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        ac_number_input = input("AC-Nummer eingeben: ")
        disk_archive_id_input = input("Datenträger-ID eingeben: ")

    validated_paths = setup_and_validate_paths(ac_number_input, disk_archive_id_input)

    if validated_paths:
        logger = setup_logging(validated_paths["log_filepath"])
        image_filepath = validated_paths["image_filepath"]
        
        proceed = True
        if image_filepath.exists():
            print(f"\nWARNUNG: Die Zieldatei existiert bereits:\n{image_filepath}")
            confirm = input("Möchten Sie diese Datei wirklich ersetzen? (j/n): ").lower()
            if confirm != 'j':
                proceed = False
                logger.warning("Vorgang vom Benutzer abgebrochen, da die Zieldatei bereits existiert.")
                print("Vorgang abgebrochen.")

        if proceed:
            logger.info("Skript gestartet.")
            
            success = create_tar_image(
                source_dir=validated_paths["source_folder"],
                image_path=image_filepath,
                logger=logger
            )

            if success:
                hash_value = calculate_sha512(image_filepath, logger)
                file_size = image_filepath.stat().st_size
                
                # HINZUGEFÜGT: Erstellt einen sauberen, maschinenlesbaren Block für PREMIS
                if hash_value:
                    logger.info("\n--- PREMIS DATA BLOCK START ---")
                    logger.info(f"executingAgent: {SCRIPT_NAME} v{SCRIPT_VERSION}")
                    logger.info(f"objectIdentifier: {image_filepath.name}")
                    logger.info(f"size: {file_size}")
                    logger.info(f"formatName: TAR (Tape Archive)")
                    logger.info(f"pronomId: x-fmt/265")
                    logger.info(f"fixity-sha512: {hash_value}")
                    logger.info("--- PREMIS DATA BLOCK END ---\n")
            
            logger.info("Skript beendet.")

        destination_folder = validated_paths["output_folder"]
        open_folder = input("\nZielordner oeffnen? (j/n): ").lower()
        if open_folder == 'j':
            if sys.platform == "win32":
                subprocess.run(['explorer', str(destination_folder)])
            else:
                subprocess.run(["xdg-open", str(destination_folder)])
    else:
        print("\nSkript wird aufgrund von Konfigurationsfehlern beendet.")

    print("\nSkript beendet.")