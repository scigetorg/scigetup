#!/usr/bin/env python3

import json
import os
import stat
import argparse
from pathlib import Path
import sys

DESKTOP_DIR = Path.home() / "Desktop"
BASE_FOLDER_NAME = "Software Applications"

def create_desktop_file(category_path: Path, app_info: dict):
    """
    Generates a .desktop file for a given application.

    Args:
        category_path: The Path object for the category directory.
        app_info: A dictionary containing the software's details.
    """
    app_name = app_info["name"]
    executable = app_info["executable"]
    is_gui = app_info.get("gui", False)
    notes = app_info.get("notes", f"Launch the {app_name} application/environment.")
    
    # Define the command to be executed by the launcher.
    # For command-line tools, it opens an interactive bash shell.
    # For GUI tools, it launches them directly and exits the terminal.
    if is_gui:
        command = f"module load {app_name}; {executable}"
    else:
        command = (
            f"module load {app_name}; "
            f"echo '*** Environment for {app_name} is now loaded. ***'; "
            f"echo '*** To run the tool, type: {executable} ***'; "
            "echo '*** Type `exit` to close this terminal. ***'; "
            "exec bash"
        )

    # Define the content of the .desktop file using the freedesktop.org standard
    desktop_file_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={notes}
Icon=utilities-terminal
Exec=x-terminal-emulator -- bash -c "{command}"
Terminal=false
Categories=Science;Education;
"""

    file_path = category_path / f"{app_name}.desktop"
    
    try:
        with open(file_path, "w") as f:
            f.write(desktop_file_content)
        
        # Make the .desktop file executable for the user and group
        # This is required for the "Allow Launching" option to appear
        file_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        
        print(f"  - Created launcher for {app_name}")
    except IOError as e:
        print(f"  [ERROR] Failed to write launcher for {app_name}: {e}", file=sys.stderr)


def main():
    """Main function to parse arguments and drive the launcher creation."""
    parser = argparse.ArgumentParser(
        description="Create desktop launchers for software from a JSON config file.",
        epilog="For more information on the scigetup project, visit https://github.com/scigetorg/scigetup"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the JSON file containing the software configuration."
    )
    args = parser.parse_args()

    print("--- Desktop Launcher Creator ---")

    # --- Pre-run Checks ---
    if not args.json_file.is_file():
        print(f"[ERROR] The specified JSON file does not exist: {args.json_file}", file=sys.stderr)
        sys.exit(1)

    # --- Main Logic ---
    base_path = DESKTOP_DIR / BASE_FOLDER_NAME
    print(f"Launchers will be created in: {base_path}\n")

    try:
        with open(args.json_file, "r") as f:
            software_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Could not parse the JSON file. Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] Could not read the JSON file: {e}", file=sys.stderr)
        sys.exit(1)

    # Create the base directory on the Desktop
    base_path.mkdir(parents=True, exist_ok=True)

    for category, details in software_data.items():
        print(f"Processing category: {category}")
        category_path = base_path / category.replace(" ", "_").replace("&", "and")
        category_path.mkdir(exist_ok=True)
        
        if not details.get("software"):
            print(f"  - No software listed in this category, skipping.")
            continue

        for app in details["software"]:
            create_desktop_file(category_path, app)
        print("-" * 30)

    print("\nScript finished successfully.")
    print(f"Check your Desktop for the '{BASE_FOLDER_NAME}' folder.")
    print("On first use, you may need to right-click each launcher and select 'Allow Launching'.")


if __name__ == "__main__":
    main()
