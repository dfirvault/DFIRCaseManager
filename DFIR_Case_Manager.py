import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

CONFIG_FILE = "case_config.txt"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_seven_zip_path():
    """Get path to 7-Zip executable with improved error handling"""
    try:
        if getattr(sys, 'frozen', False):
            # In bundled mode
            base_path = sys._MEIPASS
            seven_zip_exe = os.path.join(base_path, '7z.exe')
            seven_zip_dll = os.path.join(base_path, '7z.dll')
            
            if not all(os.path.exists(f) for f in [seven_zip_exe, seven_zip_dll]):
                # Try alternative path if files not found
                seven_zip_exe = resource_path('7z.exe')
                seven_zip_dll = resource_path('7z.dll')
                
            if not all(os.path.exists(f) for f in [seven_zip_exe, seven_zip_dll]):
                raise FileNotFoundError("7-Zip files not found in executable bundle")
                
            return seven_zip_exe
        else:
            # In development mode
            default_path = r"C:\Program Files\7-Zip\7z.exe"
            if os.path.exists(default_path):
                return default_path
            raise FileNotFoundError("7-Zip not found at default location")
    except Exception as e:
        print(f"Error locating 7-Zip: {str(e)}")
        return None

def read_backup_location():
    """Read the backup location from config file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            location = f.read().strip()
            if os.path.isdir(location):
                return location
    return None

def write_backup_location(path):
    """Write the backup location to config file"""
    with open(CONFIG_FILE, "w") as f:
        f.write(path.strip())

def select_backup_location():
    """Open dialog to select backup location"""
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Case Backup Location")
    root.destroy()
    if folder and os.path.isdir(folder):
        write_backup_location(folder)
        return folder
    return None

def create_case():
    """Create a new case directory structure"""
    case_name = input("Enter the case name: ").strip()
    if not case_name:
        print("Invalid case name.")
        return

    os.makedirs(os.path.join(case_name, "01 - Evidence"), exist_ok=True)
    os.makedirs(os.path.join(case_name, "02 - Case"), exist_ok=True)
    os.makedirs(os.path.join(case_name, "03 - Malware"), exist_ok=True)
    extracted_evidence = os.path.join(case_name, "04 - Extracted Evidence")
    os.makedirs(extracted_evidence, exist_ok=True)
    subdirs = ["01 - Axiom", "02 - XWays", "03 - Thor", "04 - Hayabusa"]
    for sub in subdirs:
        os.makedirs(os.path.join(extracted_evidence, sub), exist_ok=True)
    
    open(os.path.join(case_name, "Keywords.txt"), "a").close()
    print(f"Case '{case_name}' created successfully.")
    os.startfile(os.path.abspath(case_name))

def list_folders():
    """List all folders in current directory"""
    return [f for f in os.listdir('.') if os.path.isdir(f)]

def archive_case(backup_location):
    """Archive a case folder with optional password protection"""
    folders = list_folders()
    if not folders:
        print("No folders found.")
        return

    for idx, folder in enumerate(folders, 1):
        print(f"[{idx}] {folder}")

    try:
        choice = int(input("Enter the number of the folder to archive: "))
        target_folder = folders[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    use_password = input("Do you want to password protect the ZIP file? (y/n): ").lower().startswith('y')
    zip_password = ""
    if use_password:
        zip_password = input("Enter password for ZIP file: ").strip()
        if not zip_password:
            print("No password entered, creating unprotected ZIP.")
            use_password = False

    root = tk.Tk()
    root.withdraw()
    zip_folder = filedialog.askdirectory(initialdir=backup_location, title="Select backup location for the ZIP")
    root.destroy()

    if not zip_folder:
        print("No location selected.")
        return

    zip_path = os.path.join(zip_folder, f"{target_folder}.zip")

    try:
        seven_zip_path = get_seven_zip_path()
        
        if use_password:
            result = subprocess.run([
                seven_zip_path, 'a', '-tzip', zip_path,
                os.path.join(target_folder, '*'),
                f'-p{zip_password}', '-mem=AES256'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            shutil.make_archive(base_name=os.path.splitext(zip_path)[0], format="zip", root_dir=target_folder)

        if os.path.exists(zip_path):
            shutil.rmtree(target_folder)
            print(f"Archived and deleted: {target_folder}")
        else:
            print("Failed to create archive.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Falling back to standard zip (no password support)")
        shutil.make_archive(base_name=os.path.splitext(zip_path)[0], format="zip", root_dir=target_folder)

def change_backup_location():
    """Change the configured backup location"""
    new_location = select_backup_location()
    if new_location:
        print(f"New backup location set: {new_location}")
    else:
        print("No backup location selected.")

def main():
    """Main program loop"""
    print("\nDeveloped by Jacob Wilson - Version 0.4")
    print("dfirvault@gmail.com\n")
    
    print("DFIR Case Manager")
    backup_location = read_backup_location()
    if not backup_location:
        print("No valid backup location configured.")
        backup_location = select_backup_location()
        if not backup_location:
            print("No backup location selected. Some features will not work.")

    while True:
        print("\n" + "=" * 40)
        print("         CASE MANAGEMENT MENU")
        print("=" * 40)
        print("[1] Create a new case")
        print("[2] Archive an existing case")
        print("[3] Change backup location")
        print("[0] Exit")
        print("=" * 40)
        print(f"Current backup location: {backup_location or 'Not Set'}")
        print("=" * 40)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_case()
        elif choice == "2":
            if not backup_location:
                print("Backup location not configured.")
                backup_location = select_backup_location()
                if not backup_location:
                    continue
            archive_case(backup_location)
        elif choice == "3":
            change_backup_location()
            backup_location = read_backup_location()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
