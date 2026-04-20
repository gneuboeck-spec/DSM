import os
import subprocess
import sys
from pathlib import Path

def print_header(ac_number, disk_id):
    """Zeigt den Header mit den aktuellen Werten an."""
    print("===================================================")
    print(" PYTHON SKRIPT STARTER (Umgebung: .venv ist aktiv)")
    print("===================================================")
    print(f" Aktuelle AC-Nummer:     {ac_number}")
    print(f" Aktuelle Datenträger-ID: {disk_id}")
    print("---------------------------------------------------")
    print("\n Verfuegbare Skripte:\n")

def main():
    """Zeigt ein Menü an, verwaltet AC-Nummer/Disk-ID und führt Skripte aus."""
    
    # Empfängt die Werte von der start.bat
    if len(sys.argv) >= 3:
        ac_number = sys.argv[1]
        disk_id = sys.argv[2]
    else:
        print("Fehler: AC-Nummer und Datenträger-ID wurden nicht übergeben.")
        ac_number = "NICHT GESETZT"
        disk_id = "NICHT GESETZT"

    script_dir = Path(__file__).resolve().parent
    
    while True:
        print_header(ac_number, disk_id)

        scripts = sorted([f for f in script_dir.glob('*.py') if f.name != 'Python_Skript_Starter_menu.py'])
        
        for i, script_path in enumerate(scripts, 1):
            print(f"   {i} - {script_path.name}")

        print("\n   N - Neue Nummern eingeben")
        print("   Q - Beenden\n")
        print("===================================================")
        
        choice = input("Bitte Nummer des Skripts eingeben (oder N / Q): ").strip().lower()

        if choice == 'q':
            break
        elif choice == 'n':
            print("\n--- Bitte neue Werte eingeben ---")
            ac_number = input(f"Neue AC-Nummer (alt: {ac_number}): ").strip()
            disk_id = input(f"Neue Datenträger-ID (alt: {disk_id}): ").strip()
            continue

        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]
                
                print(f"\n--- Starte Skript: {script_to_run.name} ---")
                print(f"Uebergebe AC-Nummer: {ac_number}")
                print(f"Uebergebe Datenträger-ID: {disk_id}\n")
                
                # Übergibt die Werte als Kommandozeilen-Argumente an das Zielskript
                subprocess.run([sys.executable, str(script_to_run), ac_number, disk_id])
                
                print("\n----------------------------------------------------")
                input("Skript-Ausfuehrung beendet. Druecken Sie Enter, um zum Menue zurueckzukehren.")
            else:
                print("\nUngueltige Auswahl.")
                input("Druecken Sie Enter, um fortzufahren.")
        except ValueError:
            print("\nUngueltige Eingabe. Bitte eine Nummer, 'N' oder 'Q' eingeben.")
            input("Druecken Sie Enter, um fortzufahren.")
        except Exception as e:
            print(f"\nEin unerwarteter Fehler ist aufgetreten: {e}")
            input("Druecken Sie Enter, um fortzufahren.")

if __name__ == "__main__":
    main()