import os, json, tkinter as tk

from core import config, ini, operations, sorting, gui


def ensure_directory_exists(path, log_callback, error_callback):
    try:
        os.makedirs(path, exist_ok=True)
        log_callback(f"Ensured directory exists: {path}")
        return True
    except OSError as e:
        error_callback("Directory Creation Error", f"Error creating directory {path}: {e}")
        return False

def load_path_from_txt(base_dir, filename, entry_widget, placeholder_suffix, log_callback, error_callback):
    filepath_full = os.path.join(base_dir, filename) 
    
    if not os.path.exists(filepath_full):
        log_callback(f"'{filename}' not found. Creating it at '{filepath_full}' with a placeholder path.")
        try:
            placeholder_path = os.path.join(os.path.expanduser("~"), placeholder_suffix)
            with open(filepath_full, 'w') as f:
                f.write(placeholder_path)
            log_callback(f"Default '{filename}' created at '{filepath_full}'. Please verify and update.")
            entry_widget.delete(0, tk.END) # Use tk.END from the main_app context
            entry_widget.insert(0, placeholder_path)
        except IOError as e:
            error_callback("File Creation Error", f"Error creating '{filepath_full}': {e}")
    else:
        try:
            with open(filepath_full, 'r') as f:
                content = f.readline().strip()
            entry_widget.delete(0, tk.END) # Use tk.END from the main_app context
            entry_widget.insert(0, content)
            log_callback(f"Loaded path from '{filename}'.")
        except Exception as e:
            error_callback("File Read Error", f"Error reading '{filepath_full}': {e}")

def save_path_to_txt(base_dir, filename, path_content, log_callback, error_callback):
    filepath_full = os.path.join(base_dir, filename)
    try:
        with open(filepath_full, 'w') as f:
            f.write(path_content)
        log_callback(f"Saved path to '{filename}'.")
        return True
    except IOError as e:
        error_callback("File Write Error", f"Error saving to '{filepath_full}': {e}")
        return False

def load_json_config(base_dir, filename, default_data, log_callback, error_callback):
    filepath = os.path.join(base_dir, filename) 
    
    if not os.path.exists(filepath):
        log_callback(f"Creating default '{filename}' in '{base_dir}'...")
        try:
            ensure_directory_exists(base_dir, log_callback, error_callback) # Ensure base dir exists
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=4)
            log_callback(f"Default '{filename}' created successfully at '{filepath}'.")
            return default_data
        except IOError as e:
            error_callback("JSON Write Error", f"Error writing default '{filepath}': {e}")
            return default_data # Return default data even if writing fails
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        log_callback(f"Loaded '{filename}' from '{filepath}' successfully.")
        return data
    except json.JSONDecodeError as e:
        error_callback("JSON Read Error", f"Error decoding JSON from '{filepath}': {e}. Overwriting with default data.")
        try:
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=4)
            log_callback(f"'{filename}' at '{filepath}' reset to default due to corruption.")
        except IOError as write_error:
            error_callback("JSON Write Error", f"Error overwriting corrupted '{filepath}': {write_error}")
        return default_data
    except Exception as e:
        error_callback("File Read Error", f"An unexpected error occurred loading '{filepath}': {e}. Using default data.")
        return default_data
