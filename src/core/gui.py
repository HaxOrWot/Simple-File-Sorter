import tkinter as tk
from tkinter import scrolledtext

from core import config, ini, operations, sorting, gui

def create_main_widgets(master, app_instance):
    # --- Path Input Frame ---
    path_frame = tk.LabelFrame(master, text="Configuration Paths", padx=10, pady=10)
    path_frame.pack(pady=10, padx=10, fill=tk.X)

    # Sort Destination Path
    tk.Label(path_frame, text="Sort Destination:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=2)
    sort_dest_entry = tk.Entry(path_frame, width=50, font=("Arial", 10))
    sort_dest_entry.grid(row=0, column=1, padx=5, pady=2)
    tk.Button(path_frame, text="Browse", command=app_instance.browse_sort_dest).grid(row=0, column=2, padx=5, pady=2)

    # Drop Folder Parent Location
    tk.Label(path_frame, text="Drop Folder Parent:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=2)
    drop_location_entry = tk.Entry(path_frame, width=50, font=("Arial", 10))
    drop_location_entry.grid(row=1, column=1, padx=5, pady=2)
    tk.Button(path_frame, text="Browse", command=app_instance.browse_drop_location).grid(row=1, column=2, padx=5, pady=2)

    # --- Control Buttons Frame ---
    button_frame = tk.Frame(master, pady=10)
    button_frame.pack()

    start_button = tk.Button(button_frame, text="Start Sorting", command=app_instance.start_sorting,
                              bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                              width=15, height=2, relief=tk.RAISED, bd=3)
    start_button.pack(side=tk.LEFT, padx=10)

    stop_button = tk.Button(button_frame, text="Stop Sorting", command=app_instance.stop_sorting,
                             bg="#f44336", fg="white", font=("Arial", 12, "bold"),
                             width=15, height=2, relief=tk.RAISED, bd=3, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, padx=10)

    # --- Status/Log Display ---
    log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=15, width=70,
                                         bg="#f0f0f0", fg="#333333", font=("Consolas", 10))
    log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    log_text.insert(tk.END, "Welcome to File Sorter!\n")
    log_text.config(state=tk.DISABLED) # Make it read-only

    return sort_dest_entry, drop_location_entry, start_button, stop_button, log_text
