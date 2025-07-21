import os
import json
import shutil
import time
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import sys # Import the sys module

# --- Configuration File Paths ---
SORT_DEST_FILE = 'sort_dest.txt' # Stores the sorting destination path
DROP_LOCATION_FILE = 'drop_dest.txt' # Stores the parent location for the 'Drop' folder
CATEGORIES_FILE = 'categories.json' # Stores file categories
EXTENSIONS_FILE = 'extensions.json' # Stores file extensions mapping to categories
DROP_FOLDER_NAME = 'Drop Here' # The actual name of the folder where files are dropped
UNSORTED_FOLDER_NAME = 'Unsorted' # Folder for files with unknown extensions
ASST_FOLDER = 'asst' # Folder for configuration JSON files (categories.json, extensions.json)
APP_BASE_PATH_MARKER = 'app_base_path.txt' # Marker file to store the chosen base directory

# --- Default Configurations ---
DEFAULT_CATEGORIES = ["Video", "Music", "Code", "Image", "Document", "Archive", "Executable", "Other"]

DEFAULT_EXTENSIONS = {
    "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".alac"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".swift", ".kt", ".json", ".xml", ".yml", ".yaml", ".sh", ".bat", ".ps1", ".md"],
    "Image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico", ".raw", ".heif", ".heic"],
    "Document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".epub", ".mobi"],
    "Archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "Executable": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".apk"],
    "Other": []
}

class FileSorterApp:
    def __init__(self, master):
        self.master = master
        master.title("File Sorter")
        master.geometry("600x550")
        master.resizable(False, False) # Make window non-resizable

        self.sorting_active = False
        self.sorting_thread = None
        
        # --- Determine the correct base directory for the application ---
        # This must happen before create_widgets if it involves filedialog
        # and logging to self.log_text.
        # We'll get the path and any initial messages/errors from this method.
        self.app_root_dir, initial_logs, initial_error_msg = self._get_application_root_directory()

        # Set script_dir to the determined app_root_dir for all config file operations
        self.script_dir = self.app_root_dir 
        self.asst_folder_full_path = os.path.join(self.script_dir, ASST_FOLDER)

        self.create_widgets() # Create widgets first, including self.log_text
        
        # Log any messages/errors gathered during _get_application_root_directory
        for msg in initial_logs:
            self.log_message(msg)
        if initial_error_msg:
            messagebox.showerror("Initialization Error", initial_error_msg)

        # Ensure 'asst' folder exists within the determined app_root_dir
        # This call will now use self.log_text correctly.
        self.ensure_directory_exists(self.asst_folder_full_path) 
        
        self.load_initial_paths() # Load paths from .txt files (now relative to app_root_dir)
        self.load_json_configs() # Load categories and extensions (now relative to asst_folder_full_path)

    def _get_application_root_directory(self):
        """
        Determines the base directory for the application's configuration files.
        On first run, it prompts the user to select a location for the 'FileSorter' folder.
        This location is then saved in a marker file next to the executable for future runs.
        Returns (app_base_path, initial_messages_list, initial_error_message).
        """
        # Determine where the EXE/script is located
        if getattr(sys, 'frozen', False): # Running as a PyInstaller executable
            exe_dir = os.path.dirname(sys.executable)
        else: # Running as a normal Python script
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        marker_file_path = os.path.join(exe_dir, APP_BASE_PATH_MARKER)
        
        initial_messages = []
        initial_error = None
        app_base_path = None

        if os.path.exists(marker_file_path):
            # Not first run, read the stored base path
            try:
                with open(marker_file_path, 'r') as f:
                    stored_path = f.readline().strip()
                if os.path.isdir(stored_path):
                    app_base_path = stored_path
                    initial_messages.append(f"Application base directory loaded from '{APP_BASE_PATH_MARKER}': {app_base_path}")
                else:
                    initial_messages.append(f"Stored base path '{stored_path}' in '{APP_BASE_PATH_MARKER}' is invalid or missing. Re-initializing.")
            except Exception as e:
                initial_messages.append(f"Error reading '{APP_BASE_PATH_MARKER}': {e}. Re-initializing.")
        
        if app_base_path is None: # First run or stored path invalid/missing
            initial_messages.append("First run or base path not found. Asking user to select location for 'FileSorter' folder.")
            
            # Create a dummy Tkinter root for the filedialog as self.master is not ready yet
            temp_root = tk.Tk()
            temp_root.withdraw() # Hide the dummy root window

            chosen_dir = filedialog.askdirectory(
                parent=temp_root, # Use the dummy root for dialog parent
                title="Select Location for 'FileSorter' Folder",
                initialdir=os.path.expanduser("~") # Start in user's home directory
            )
            temp_root.destroy() # Destroy the dummy root

            if chosen_dir:
                final_app_dir = os.path.join(chosen_dir, "FileSorter")
            else:
                # User cancelled, default to exe directory
                final_app_dir = os.path.join(exe_dir, "FileSorter")
                initial_messages.append(f"User cancelled selection. Defaulting 'FileSorter' folder to: {final_app_dir}")

            # Create the FileSorter folder
            try:
                os.makedirs(final_app_dir, exist_ok=True)
                initial_messages.append(f"Ensured 'FileSorter' directory exists: {final_app_dir}")
                app_base_path = final_app_dir
            except OSError as e:
                initial_error = f"Failed to create 'FileSorter' folder at '{final_app_dir}': {e}. Using executable directory as fallback for configs."
                initial_messages.append(initial_error)
                app_base_path = exe_dir # Fallback if folder creation fails

            # Store the chosen/default path for future runs in the marker file next to the EXE
            try:
                with open(marker_file_path, 'w') as f:
                    f.write(app_base_path)
                initial_messages.append(f"Application base directory saved for future runs in '{APP_BASE_PATH_MARKER}'.")
            except Exception as e:
                initial_error = f"Could not save application base path to '{marker_file_path}': {e}"
                initial_messages.append(initial_error)

        return app_base_path, initial_messages, initial_error

    def create_widgets(self):
        """Creates the GUI elements for the application."""
        # --- Path Input Frame ---
        path_frame = tk.LabelFrame(self.master, text="Configuration Paths", padx=10, pady=10)
        path_frame.pack(pady=10, padx=10, fill=tk.X)

        # Sort Destination Path
        tk.Label(path_frame, text="Sort Destination:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.sort_dest_entry = tk.Entry(path_frame, width=50, font=("Arial", 10))
        self.sort_dest_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(path_frame, text="Browse", command=self.browse_sort_dest).grid(row=0, column=2, padx=5, pady=2)

        # Drop Folder Parent Location
        tk.Label(path_frame, text="Drop Folder Parent:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=2)
        self.drop_location_entry = tk.Entry(path_frame, width=50, font=("Arial", 10))
        self.drop_location_entry.grid(row=1, column=1, padx=5, pady=2)
        tk.Button(path_frame, text="Browse", command=self.browse_drop_location).grid(row=1, column=2, padx=5, pady=2)

        # --- Control Buttons Frame ---
        button_frame = tk.Frame(self.master, pady=10)
        button_frame.pack()

        self.start_button = tk.Button(button_frame, text="Start Sorting", command=self.start_sorting,
                                      bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                      width=15, height=2, relief=tk.RAISED, bd=3)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop Sorting", command=self.stop_sorting,
                                     bg="#f44336", fg="white", font=("Arial", 12, "bold"),
                                     width=15, height=2, relief=tk.RAISED, bd=3, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # --- Status/Log Display ---
        self.log_text = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=15, width=70,
                                                 bg="#f0f0f0", fg="#333333", font=("Consolas", 10))
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.log_text.insert(tk.END, "Welcome to File Sorter!\n")
        self.log_text.config(state=tk.DISABLED) # Make it read-only

    def log_message(self, message):
        """Appends a message to the scrolled text widget."""
        # Ensure log_text is configured before attempting to modify it
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END) # Scroll to the end
            self.log_text.config(state=tk.DISABLED)

    def show_error_popup(self, title, message):
        """Displays an error message box and logs it."""
        self.log_message(f"ERROR: {message}") # Log first, then show popup
        messagebox.showerror(title, message)

    def ensure_directory_exists(self, path):
        """Ensures a directory exists, creating it if necessary."""
        try:
            os.makedirs(path, exist_ok=True)
            self.log_message(f"Ensured directory exists: {path}")
            return True
        except OSError as e:
            self.show_error_popup("Directory Creation Error", f"Error creating directory {path}: {e}")
            return False

    def load_path_from_txt(self, filename, entry_widget, placeholder_suffix):
        """
        Loads a path from a .txt file and populates the given Entry widget.
        If the file doesn't exist, it creates it with a placeholder.
        """
        # Use self.app_root_dir as the base for these config files
        filepath_full = os.path.join(self.app_root_dir, filename) 
        
        if not os.path.exists(filepath_full):
            self.log_message(f"'{filename}' not found. Creating it at '{filepath_full}' with a placeholder path.")
            try:
                placeholder_path = os.path.join(os.path.expanduser("~"), placeholder_suffix)
                with open(filepath_full, 'w') as f:
                    f.write(placeholder_path)
                self.log_message(f"Default '{filename}' created at '{filepath_full}'. Please verify and update.")
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, placeholder_path)
            except IOError as e:
                self.show_error_popup("File Creation Error", f"Error creating '{filepath_full}': {e}")
        else:
            try:
                with open(filepath_full, 'r') as f:
                    content = f.readline().strip()
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, content)
                self.log_message(f"Loaded path from '{filename}'.")
            except Exception as e:
                self.show_error_popup("File Read Error", f"Error reading '{filepath_full}': {e}")

    def save_path_to_txt(self, filename, path_content):
        """Saves a path to a .txt file."""
        # Use self.app_root_dir as the base for these config files
        filepath_full = os.path.join(self.app_root_dir, filename)
        try:
            with open(filepath_full, 'w') as f:
                f.write(path_content)
            self.log_message(f"Saved path to '{filename}'.")
            return True
        except IOError as e:
            self.show_error_popup("File Write Error", f"Error saving to '{filepath_full}': {e}")
            return False

    def load_initial_paths(self):
        """Loads paths for sort_dest and drop_dest from their respective .txt files."""
        self.load_path_from_txt(SORT_DEST_FILE, self.sort_dest_entry, "MySortedFiles")
        self.load_path_from_txt(DROP_LOCATION_FILE, self.drop_location_entry, "MyDropFolderParent")

    def load_json_configs(self):
        """Loads categories and extensions from JSON files."""
        # Load categories
        cat_filepath = os.path.join(self.asst_folder_full_path, CATEGORIES_FILE)
        if not os.path.exists(cat_filepath):
            self.log_message(f"Creating default '{CATEGORIES_FILE}' in '{self.asst_folder_full_path}'...")
            try:
                with open(cat_filepath, 'w') as f:
                    json.dump(DEFAULT_CATEGORIES, f, indent=4)
                self.categories = DEFAULT_CATEGORIES
                self.log_message(f"Default '{CATEGORIES_FILE}' created successfully.")
            except IOError as e:
                self.show_error_popup("JSON Write Error", f"Error writing default '{CATEGORIES_FILE}': {e}")
                self.categories = DEFAULT_CATEGORIES # Fallback
        else:
            try:
                with open(cat_filepath, 'r') as f:
                    self.categories = json.load(f)
                self.log_message(f"Loaded '{CATEGORIES_FILE}'.")
            except json.JSONDecodeError as e:
                self.show_error_popup("JSON Read Error", f"Error decoding '{CATEGORIES_FILE}': {e}. Using default.")
                self.categories = DEFAULT_CATEGORIES
            except Exception as e:
                self.show_error_popup("File Read Error", f"Error loading '{CATEGORIES_FILE}': {e}. Using default.")
                self.categories = DEFAULT_CATEGORIES

        # Load extensions
        ext_filepath = os.path.join(self.asst_folder_full_path, EXTENSIONS_FILE)
        if not os.path.exists(ext_filepath):
            self.log_message(f"Creating default '{EXTENSIONS_FILE}' in '{self.asst_folder_full_path}'...")
            try:
                with open(ext_filepath, 'w') as f:
                    json.dump(DEFAULT_EXTENSIONS, f, indent=4)
                self.extensions_map = DEFAULT_EXTENSIONS
                self.log_message(f"Default '{EXTENSIONS_FILE}' created successfully.")
            except IOError as e:
                self.show_error_popup("JSON Write Error", f"Error writing default '{EXTENSIONS_FILE}': {e}")
                self.extensions_map = DEFAULT_EXTENSIONS # Fallback
        else:
            try:
                with open(ext_filepath, 'r') as f:
                    self.extensions_map = json.load(f)
                self.log_message(f"Loaded '{EXTENSIONS_FILE}'.")
            except json.JSONDecodeError as e:
                self.show_error_popup("JSON Read Error", f"Error decoding '{EXTENSIONS_FILE}': {e}. Using default.")
                self.extensions_map = DEFAULT_EXTENSIONS
            except Exception as e:
                self.show_error_popup("File Read Error", f"Error loading '{EXTENSIONS_FILE}': {e}. Using default.")
                self.extensions_map = DEFAULT_EXTENSIONS

    def browse_sort_dest(self):
        """Opens a directory chooser for the sort destination."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.sort_dest_entry.delete(0, tk.END)
            self.sort_dest_entry.insert(0, folder_selected)

    def browse_drop_location(self):
        """Opens a directory chooser for the drop folder's parent location."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.drop_location_entry.delete(0, tk.END)
            self.drop_location_entry.insert(0, folder_selected)

    def validate_paths(self):
        """Validates the paths entered in the GUI fields."""
        sort_dest_path = self.sort_dest_entry.get().strip()
        drop_parent_path = self.drop_location_entry.get().strip()

        if not sort_dest_path:
            self.show_error_popup("Validation Error", "Sort Destination path cannot be empty.")
            return False
        if not os.path.isdir(sort_dest_path):
            self.show_error_popup("Validation Error", f"Sort Destination path '{sort_dest_path}' does not exist or is not a directory.")
            return False
        
        if not drop_parent_path:
            self.show_error_popup("Validation Error", "Drop Folder Parent path cannot be empty.")
            return False
        if not os.path.isdir(drop_parent_path):
            self.show_error_popup("Validation Error", f"Drop Folder Parent path '{drop_parent_path}' does not exist or is not a directory.")
            return False
        
        # Save valid paths to their respective .txt files for persistence
        self.save_path_to_txt(SORT_DEST_FILE, sort_dest_path)
        self.save_path_to_txt(DROP_LOCATION_FILE, drop_parent_path)

        # Store validated paths for sorting logic
        self.current_sort_dest = sort_dest_path
        self.current_drop_parent = drop_parent_path
        self.current_drop_folder_full_path = os.path.join(self.current_drop_parent, DROP_FOLDER_NAME)

        return True

    def get_file_category_and_extension_folder(self, file_extension):
        """
        Determines the category and the folder name for a given file extension.
        Returns (category, extension_folder_name) or (UNSORTED_FOLDER_NAME, None) if not found.
        """
        normalized_extension = file_extension.lower()
        for category, extensions_list in self.extensions_map.items():
            normalized_extensions_list = [ext.lower() for ext in extensions_list]
            if normalized_extension in normalized_extensions_list:
                extension_folder_name = file_extension.lstrip('.').upper()
                return category, extension_folder_name
        return UNSORTED_FOLDER_NAME, None

    def sort_files_logic(self):
        """The core file sorting logic, run in a separate thread."""
        while self.sorting_active:
            # Re-load JSON configs in each cycle to pick up external changes
            self.load_json_configs() 

            # Ensure the 'Drop' folder exists at the specified parent location
            if not self.ensure_directory_exists(self.current_drop_folder_full_path):
                self.log_message(f"Sorting paused: Could not access or create '{DROP_FOLDER_NAME}' at '{self.current_drop_folder_full_path}'.")
                time.sleep(5)
                continue

            # Ensure all category folders exist in the destination
            for category in self.categories:
                category_path = os.path.join(self.current_sort_dest, category)
                self.ensure_directory_exists(category_path)
            
            # Ensure the 'Unsorted' folder exists
            unsorted_full_path = os.path.join(self.current_sort_dest, UNSORTED_FOLDER_NAME)
            self.ensure_directory_exists(unsorted_full_path)

            self.log_message(f"\nMonitoring '{self.current_drop_folder_full_path}' for new files...")

            files_to_process = [f for f in os.listdir(self.current_drop_folder_full_path) if os.path.isfile(os.path.join(self.current_drop_folder_full_path, f))]

            if not files_to_process:
                self.log_message("No new files found in 'Drop' folder.")
            else:
                self.log_message(f"Found {len(files_to_process)} file(s) to process.")
                for filename in files_to_process:
                    source_file_path = os.path.join(self.current_drop_folder_full_path, filename)
                    file_name_without_ext, file_extension = os.path.splitext(filename)
                    
                    self.log_message(f"Processing: '{filename}' (Extension: '{file_extension}')")

                    category, extension_folder_name = self.get_file_category_and_extension_folder(file_extension)

                    if category == UNSORTED_FOLDER_NAME:
                        target_dir = unsorted_full_path
                        self.log_message(f"  -> Extension '{file_extension}' not found. Moving to '{UNSORTED_FOLDER_NAME}'.")
                    else:
                        target_category_path = os.path.join(self.current_sort_dest, category)
                        target_extension_path = os.path.join(target_category_path, extension_folder_name)
                        
                        self.ensure_directory_exists(target_extension_path)
                        target_dir = target_extension_path
                        self.log_message(f"  -> Identified as '{category}'. Moving to '{os.path.join(category, extension_folder_name)}'.")

                    try:
                        destination_file_path = os.path.join(target_dir, filename)
                        shutil.move(source_file_path, destination_file_path)
                        self.log_message(f"  -> Successfully moved '{filename}' to '{destination_file_path}'.")
                    except shutil.Error as e:
                        self.show_error_popup("File Move Error", f"Error moving '{filename}': {e}. File might be in use or already exists.")
                    except Exception as e:
                        self.show_error_popup("Unexpected Error", f"An unexpected error occurred moving '{filename}': {e}")
            
            self.log_message("--- Scan complete. Waiting for 5 seconds before next scan. ---")
            time.sleep(5) # Pause for 5 seconds before the next loop iteration

    def start_sorting(self):
        """Starts the file sorting process in a new thread."""
        if not self.sorting_active:
            self.log_message("Attempting to start sorting...")
            
            # Validate paths from GUI input fields
            if not self.validate_paths():
                return # Stop if validation fails

            self.sorting_active = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_message("Sorting started. Monitoring files...")
            
            # Start the sorting logic in a separate thread
            self.sorting_thread = threading.Thread(target=self.sort_files_logic, daemon=True)
            self.sorting_thread.start()
        else:
            self.log_message("Sorting is already running.")

    def stop_sorting(self):
        """Stops the file sorting process."""
        if self.sorting_active:
            self.sorting_active = False
            self.log_message("Stopping sorting. Please wait...")
            # Give the thread a moment to finish its current loop iteration
            if self.sorting_thread and self.sorting_thread.is_alive():
                # In a real-world app, you might use a more robust signal/event for graceful shutdown
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

