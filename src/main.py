import os, threading, tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

from core import config, ini, operations, sorting, gui


class FileSorterApp:
    def __init__(self, master):
        self.master = master
        master.title("File Sorter")
        master.geometry("600x550")
        master.resizable(False, False)

        self.sorting_active = False
        self.sorting_thread = None
        self.app_root_dir, initial_logs, initial_error_msg = ini.get_application_root_directory(tk, messagebox)
        self.script_dir = self.app_root_dir 
        self.asst_folder_full_path = os.path.join(self.script_dir, config.ASST_FOLDER)
        self.sort_dest_entry, self.drop_location_entry, \
        self.start_button, self.stop_button, self.log_text = \
            gui.create_main_widgets(master, self)
        
        for msg in initial_logs:
            self.log_message(msg)
        if initial_error_msg:
            self.show_error_popup("Initialization Error", initial_error_msg)

        operations.ensure_directory_exists(self.asst_folder_full_path, self.log_message, self.show_error_popup)
        
        self.load_initial_paths()
        self.load_json_configs()

    def log_message(self, message):
        if hasattr(self, 'log_text'): 
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END) # Scroll to the end
            self.log_text.config(state=tk.DISABLED)

    def show_error_popup(self, title, message):
        self.log_message(f"ERROR: {message}") 
        messagebox.showerror(title, message)

    def browse_sort_dest(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.sort_dest_entry.delete(0, tk.END)
            self.sort_dest_entry.insert(0, folder_selected)

    def browse_drop_location(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.drop_location_entry.delete(0, tk.END)
            self.drop_location_entry.insert(0, folder_selected)

    def validate_paths(self):
        sort_dest_path = self.sort_dest_entry.get().strip()
        drop_parent_path = self.drop_location_entry.get().strip()

        is_valid = operations.validate_paths_and_save(
            sort_dest_path, drop_parent_path, self.script_dir, 
            self.log_message, self.show_error_popup
        )
        
        if is_valid:
            self.current_sort_dest = sort_dest_path
            self.current_drop_parent = drop_parent_path
            self.current_drop_folder_full_path = os.path.join(self.current_drop_parent, config.DROP_FOLDER_NAME)
        return is_valid

    def load_initial_paths(self):
        operations.load_path_from_txt(self.script_dir, config.SORT_DEST_FILE, self.sort_dest_entry, "MySortedFiles", self.log_message, self.show_error_popup)
        operations.load_path_from_txt(self.script_dir, config.DROP_LOCATION_FILE, self.drop_location_entry, "MyDropFolderParent", self.log_message, self.show_error_popup)

    def load_json_configs(self):
        self.categories = operations.load_json_config(self.asst_folder_full_path, config.CATEGORIES_FILE, config.DEFAULT_CATEGORIES, self.log_message, self.show_error_popup)
        self.extensions_map = operations.load_json_config(self.asst_folder_full_path, config.EXTENSIONS_FILE, config.DEFAULT_EXTENSIONS, self.log_message, self.show_error_popup)

    def start_sorting(self):
        if not self.sorting_active:
            self.log_message("Attempting to start sorting...")
            
            if not self.validate_paths():
                return

            self.sorting_active = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_message("Sorting started. Monitoring files and folders...")
            
            self.sorting_thread = threading.Thread(
                target=sorting.run_sorting_process,
                args=(
                    self.current_sort_dest,
                    self.current_drop_folder_full_path,
                    self.categories,
                    self.extensions_map,
                    self.log_message,
                    self.show_error_popup,
                    lambda path: operations.ensure_directory_exists(path, self.log_message, self.show_error_popup), # Pass ensure_directory_exists with callbacks
                    lambda: self.sorting_active # Pass a callable that returns the current state of sorting_active
                ),
                daemon=True
            )
            self.sorting_thread.start()
        else:
            self.log_message("Sorting is already running.")

    def stop_sorting(self):
        """Stops the file sorting process."""
        if self.sorting_active:
            self.sorting_active = False
            self.log_message("Stopping sorting. Please wait...")
            if self.sorting_thread and self.sorting_thread.is_alive():
                pass 
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("Sorting stopped.")
        else:
            self.log_message("Sorting is not currently running.")

# --- Main Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FileSorterApp(root)
    root.mainloop()
