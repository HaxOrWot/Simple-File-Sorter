import os, shutil, time

from core import config, ini, operations, sorting, gui


def get_file_category_and_extension_folder(file_extension, extensions_map):
    normalized_extension = file_extension.lower()

    for category, extensions_list in extensions_map.items():
        normalized_extensions_list = [ext.lower() for ext in extensions_list]
        if normalized_extension in normalized_extensions_list:
            extension_folder_name = file_extension.lstrip('.').upper()
            return category, extension_folder_name
    
    return config.UNSORTED_FOLDER_NAME, None 

def run_sorting_process(
    sort_dest_path, 
    drop_folder_full_path, 
    categories, 
    extensions_map, 
    log_callback, 
    error_callback, 
    ensure_dir_callback, # This is a callback to file_operations.ensure_directory_exists
    sorting_active_check_callback # This is a callback to check the sorting_active flag in main_app
):
    """
    The core file and folder sorting logic, designed to run in a separate thread.
    
    Args:
        sort_dest_path (str): The main destination directory for sorted files.
        drop_folder_full_path (str): The full path to the 'Drop' folder.
        categories (list): List of defined categories.
        extensions_map (dict): Dictionary mapping categories to lists of extensions.
        log_callback (function): Callback function for logging messages to the GUI.
        error_callback (function): Callback function for displaying error popups.
        ensure_dir_callback (function): Callback function to ensure a directory exists (from file_operations).
        sorting_active_check_callback (function): A callable that returns True if sorting should continue.
    """
    while sorting_active_check_callback(): # Check if sorting is still active
        # Ensure the 'Drop' folder exists at the specified parent location
        if not ensure_dir_callback(drop_folder_full_path):
            log_callback(f"Sorting paused: Could not access or create '{config.DROP_FOLDER_NAME}' at '{drop_folder_full_path}'.")
            time.sleep(5)
            continue

        # Ensure all category folders exist in the destination
        for category in categories:
            category_path = os.path.join(sort_dest_path, category)
            ensure_dir_callback(category_path)
        
        # Ensure the 'Unsorted' folder exists
        unsorted_full_path = os.path.join(sort_dest_path, config.UNSORTED_FOLDER_NAME)
        ensure_dir_callback(unsorted_full_path)

        log_callback(f"\nMonitoring '{drop_folder_full_path}' for new items...")

        # Get all items (files and directories) in the 'Drop' folder
        try:
            items_to_process = os.listdir(drop_folder_full_path)
        except OSError as e:
            error_callback("Directory Read Error", f"Could not read contents of '{drop_folder_full_path}': {e}. Skipping scan.")
            time.sleep(5)
            continue

        if not items_to_process:
            log_callback("No new items found in 'Drop' folder.")
        else:
            log_callback(f"Found {len(items_to_process)} item(s) to process.")
            for item_name in items_to_process:
                source_item_path = os.path.join(drop_folder_full_path, item_name)
                
                if os.path.isfile(source_item_path):
                    file_name_without_ext, file_extension = os.path.splitext(item_name)
                    log_callback(f"Processing file: '{item_name}' (Extension: '{file_extension}')")

                    category, extension_folder_name = get_file_category_and_extension_folder(file_extension, extensions_map)

                    if category == config.UNSORTED_FOLDER_NAME:
                        target_dir = unsorted_full_path
                        log_callback(f"  -> Extension '{file_extension}' not found. Moving to '{config.UNSORTED_FOLDER_NAME}'.")
                    else:
                        target_category_path = os.path.join(sort_dest_path, category)
                        target_extension_path = os.path.join(target_category_path, extension_folder_name)
                        
                        ensure_dir_callback(target_extension_path)
                        target_dir = target_extension_path
                        log_callback(f"  -> Identified as '{category}'. Moving to '{os.path.join(category, extension_folder_name)}'.")
                
                elif os.path.isdir(source_item_path):
                    target_dir = unsorted_full_path
                    log_callback(f"Processing folder: '{item_name}'. Moving directly to '{config.UNSORTED_FOLDER_NAME}'.")
                else:
                    log_callback(f"Skipping unknown item type: '{item_name}'.")
                    continue

                try:
                    destination_item_path = os.path.join(target_dir, item_name)
                    shutil.move(source_item_path, destination_item_path)
                    log_callback(f"  -> Successfully moved '{item_name}' to '{destination_item_path}'.")
                except shutil.Error as e:
                    error_callback("Move Error", f"Error moving '{item_name}': {e}. Item might be in use or already exists.")
                except Exception as e:
                    error_callback("Unexpected Error", f"An unexpected error occurred while moving '{item_name}': {e}")
            
        log_callback("--- Scan complete. Waiting for 5 seconds before next scan. ---")
        time.sleep(5) # Pause for 5 seconds before the next loop iteration
