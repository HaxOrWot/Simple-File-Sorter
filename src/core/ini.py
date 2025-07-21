import os, sys, tkinter as tk
from tkinter import messagebox, filedialog

from core import config, ini, operations, sorting, gui


def get_application_root_directory(tk_module, messagebox_module):
    # Determine where the EXE/script is located
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    marker_file_path = os.path.join(exe_dir, config.APP_BASE_PATH_MARKER)
    
    initial_messages = []
    initial_error = None
    app_base_path = None

    if os.path.exists(marker_file_path):
        # Not the first run, try to read the stored base path
        try:
            with open(marker_file_path, 'r') as f:
                stored_path = f.readline().strip()
            if os.path.isdir(stored_path):
                app_base_path = stored_path
                initial_messages.append(f"Application base directory loaded from '{config.APP_BASE_PATH_MARKER}': {app_base_path}")
            else:
                initial_messages.append(f"Stored base path '{stored_path}' in '{config.APP_BASE_PATH_MARKER}' is invalid or missing. Re-initializing setup.")
        except Exception as e:
            initial_messages.append(f"Error reading '{config.APP_BASE_PATH_MARKER}': {e}. Re-initializing setup.")
    
    if app_base_path is None:
        initial_messages.append("First run or base path not found. Asking user to select location for 'FileSorter' folder.")
        
        # Create a temporary, hidden Tkinter root for the filedialog.
        temp_root = tk_module.Tk()
        temp_root.withdraw()

        chosen_dir = filedialog.askdirectory(
            parent=temp_root,
            title="Select Location for 'FileSorter' Application Folder",
            initialdir=os.path.expanduser("~")
        )
        temp_root.destroy()

        if chosen_dir:
            final_app_dir = os.path.join(chosen_dir, "FileSorter")
        else:
            final_app_dir = os.path.join(exe_dir, "FileSorter")
            initial_messages.append(f"User cancelled selection. Defaulting 'FileSorter' folder to: {final_app_dir}")

        # Create the 'FileSorter' folder at the determined location
        try:
            os.makedirs(final_app_dir, exist_ok=True)
            initial_messages.append(f"Ensured 'FileSorter' directory exists: {final_app_dir}")
            app_base_path = final_app_dir
        except OSError as e:
            initial_error = f"Failed to create 'FileSorter' folder at '{final_app_dir}': {e}. Using executable directory as fallback for configs."
            initial_messages.append(initial_error)
            app_base_path = exe_dir # Fallback to EXE directory if creation fails

        # Store the chosen/default path for future runs in the marker file next to the EXE
        try:
            with open(marker_file_path, 'w') as f:
                f.write(app_base_path)
            initial_messages.append(f"Application base directory saved for future runs in '{config.APP_BASE_PATH_MARKER}'.")
        except Exception as e:
            initial_error = f"Could not save application base path to '{marker_file_path}': {e}"
            initial_messages.append(initial_error)

    return app_base_path, initial_messages, initial_error
