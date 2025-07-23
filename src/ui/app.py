import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import time

from core.sorter import sort_folder
from core.config import load_categories, set_workspace_path, save_recent_workspace
from core.utils import ensure_workspace
from core.errors import NoLocationFound
from ui.category_editor import CategoryEditor

# Store workspace config in FileSorter subfolder
def get_workspace_config_file(workspace: Path):
    return workspace / "FileSorter" / "config" / "workspace.txt"


class AnimatedProgressBar:
    """Custom animated progress indicator"""
    def __init__(self, parent, width=300, height=6):
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               highlightthickness=0, relief='flat')
        self.width = width
        self.height = height
        self.progress = 0
        self.is_animating = False
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def start_pulse(self):
        """Start pulsing animation"""
        self.is_animating = True
        self.pulse_animation()
        
    def stop_pulse(self):
        """Stop pulsing animation"""
        self.is_animating = False
        self.canvas.delete("all")
        
    def pulse_animation(self):
        if not self.is_animating:
            return
            
        self.canvas.delete("all")
        
        # Create gradient effect with multiple rectangles
        for i in range(20):
            alpha = abs((i - 10)) / 10.0
            x1 = (self.width / 20) * i
            x2 = x1 + (self.width / 20)
            
            # Color interpolation for gradient effect
            intensity = int(100 + 155 * (1 - alpha))
            color = f"#{intensity:02x}{intensity//2:02x}ff"
            
            self.canvas.create_rectangle(x1, 0, x2, self.height, 
                                       fill=color, outline="")
        
        # Schedule next frame
        self.canvas.after(100, self.pulse_animation)


class StatusIndicator:
    """Animated status indicator with icons"""
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.icon_label = ttk.Label(self.frame, text="⭕", font=("Segoe UI Emoji", 16))
        self.text_label = ttk.Label(self.frame, text="Idle", font=("Segoe UI", 10, "bold"))
        
        self.icon_label.pack(side="left", padx=(0, 8))
        self.text_label.pack(side="left")
        
        self.states = {
            "idle": {"icon": "⭕", "text": "Ready to sort", "color": "#28a745"},
            "starting": {"icon": "🔄", "text": "Starting up...", "color": "#ffc107"},
            "scanning": {"icon": "🔍", "text": "Scanning for files", "color": "#17a2b8"},
            "sorting": {"icon": "⚡", "text": "Sorting files", "color": "#007bff"},
            "waiting": {"icon": "⏳", "text": "Waiting for next scan", "color": "#6c757d"},
            "error": {"icon": "❌", "text": "Error occurred", "color": "#dc3545"}
        }
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
    def set_state(self, state, custom_text=None):
        if state in self.states:
            config = self.states[state]
            self.icon_label.config(text=config["icon"])
            self.text_label.config(text=custom_text or config["text"], 
                                 foreground=config["color"])


class FileSorterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FileSorter - Intelligent File Organization")
        self.root.geometry("630x480")  # Increased by 30 pixels
        self.root.resizable(False, False)
        self.root.minsize(580, 820)  # Increased by 30 pixels

        # Configure window icon and styling
        try:
            self.root.iconname("FileSorter")
        except:
            pass

        self.workspace = Path()
        self.drop_dir = Path()
        self.sort_dir = Path()
        self.sorting = False
        self.next_scan = 5

        # Configure styles
        self.style = ttk.Style()
        self.setup_styles()
        
        self.build_modern_ui()
        self.on_startup()

    def setup_styles(self):
        """Setup custom styles for modern appearance"""
        # Configure custom button styles - more compact
        self.style.configure("Action.TButton",
                           font=("Segoe UI", 10, "bold"),
                           padding=(12, 8))
        
        self.style.configure("Primary.TButton",
                           font=("Segoe UI", 11, "bold"),
                           padding=(15, 10))
        
        self.style.configure("Icon.TButton",
                           font=("Segoe UI Emoji", 12),
                           padding=(8, 6))
        
        # Configure label styles
        self.style.configure("Title.TLabel",
                           font=("Segoe UI", 18, "bold"))
        
        self.style.configure("Subtitle.TLabel",
                           font=("Segoe UI", 11),
                           foreground="#000000")
        
        self.style.configure("Path.TLabel",
                           font=("Segoe UI", 10, "italic"),
                           padding=(10, 5))

    def build_modern_ui(self):
        """Build the modern, immersive UI"""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="25")
        main_container.pack(fill="both", expand=True)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(3, weight=1)  # Make middle section expandable

        # Header section
        self.create_header_section(main_container)
        
        # Workspace section
        self.create_workspace_section(main_container)
        
        # Status and progress section
        self.create_status_section(main_container)
        
        # Control section
        self.create_control_section(main_container)
        
        # Footer section
        self.create_footer_section(main_container)

    def create_header_section(self, parent):
        """Create the header with title"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        header_frame.columnconfigure(0, weight=1)
        
        # App title and icon
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0)
        
        # App icon
        icon_label = ttk.Label(title_frame, text="🗂️", font=("Segoe UI Emoji", 24))
        icon_label.pack(side="left", padx=(0, 12))
        
        # Title and subtitle
        text_frame = ttk.Frame(title_frame)
        text_frame.pack(side="left")
        
        ttk.Label(text_frame, text="FileSorter", style="Title.TLabel").pack(anchor="w")
        ttk.Label(text_frame, text="Intelligent file organization made simple", 
                 style="Subtitle.TLabel").pack(anchor="w")

    def create_workspace_section(self, parent):
        """Create the workspace selection section"""
        workspace_frame = ttk.LabelFrame(parent, text="  📁 Workspace Configuration  ", 
                                       padding="20")
        workspace_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        workspace_frame.columnconfigure(1, weight=1)
        
        # Workspace selection
        ttk.Label(workspace_frame, text="Current workspace:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Workspace path display with better styling
        self.workspace_frame = ttk.Frame(workspace_frame, relief="sunken", borderwidth=1)
        self.workspace_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        self.workspace_icon = ttk.Label(self.workspace_frame, text="📂", 
                                       font=("Segoe UI Emoji", 12))
        self.workspace_icon.pack(side="left", padx=(10, 5), pady=8)
        
        self.workspace_path = ttk.Label(self.workspace_frame, text="No workspace selected",
                                      style="Path.TLabel", foreground="#000000")
        self.workspace_path.pack(side="left", fill="x", expand=True, pady=5)
        
        # Workspace action button
        self.workspace_btn = ttk.Button(workspace_frame, text="🔍 Select Workspace", 
                                      style="Action.TButton", command=self.choose_workspace)
        self.workspace_btn.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Quick info panel
        info_frame = ttk.Frame(workspace_frame)
        info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        ttk.Label(info_frame, text="💡", font=("Segoe UI Emoji", 12)).pack(side="left", padx=(0, 8))
        ttk.Label(info_frame, text="FileSorter will create 'Drop' and 'Sorted' folders in your workspace",
                 font=("Segoe UI", 9), foreground="#000000").pack(side="left")

    def create_status_section(self, parent):
        """Create the status and progress section"""
        status_frame = ttk.LabelFrame(parent, text="  📊 System Status  ", padding="20")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        
        # Status indicator
        self.status_indicator = StatusIndicator(status_frame)
        self.status_indicator.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar(status_frame)
        self.progress_bar.pack(pady=(0, 15))
        
        # Statistics display
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill="x", pady=(10, 0))
        stats_frame.columnconfigure((0, 1, 2), weight=1)
        
        # Files processed counter
        self.files_processed = ttk.Label(stats_frame, text="Files: 0",
                                       font=("Segoe UI", 9), foreground="#000000")
        self.files_processed.grid(row=0, column=0, sticky="w")
        
        # Next scan countdown
        self.next_scan_label = ttk.Label(stats_frame, text="",
                                       font=("Segoe UI", 9), foreground="#000000")
        self.next_scan_label.grid(row=0, column=1)
        
        # Categories count
        self.categories_count = ttk.Label(stats_frame, text="Categories: 0",
                                        font=("Segoe UI", 9), foreground="#000000")
        self.categories_count.grid(row=0, column=2, sticky="e")

    def create_control_section(self, parent):
        """Create the main control section"""
        control_frame = ttk.LabelFrame(parent, text="  ⚡ File Sorting Control  ",
                                     padding="12")
        control_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(1, weight=1)
        
        # Main action button
        self.main_action_btn = ttk.Button(control_frame, text="🚀 Start Sorting",
                                        style="Primary.TButton", state="disabled",
                                        command=self.toggle_start_stop)
        self.main_action_btn.pack(pady=(0, 12))
        
        # Secondary actions in a horizontal layout
        secondary_frame = ttk.Frame(control_frame)
        secondary_frame.pack(fill="x")
        secondary_frame.columnconfigure((0, 1), weight=1)
        
        # Category management button - DISABLED initially
        self.category_btn = ttk.Button(secondary_frame, text="🗂️ Categories",
                                     style="Action.TButton", state="disabled",
                                     command=lambda: CategoryEditor(self.root))
        self.category_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=6)
        
        # Refresh/reload button - DISABLED initially
        self.refresh_btn = ttk.Button(secondary_frame, text="🔄 Refresh",
                                    style="Action.TButton", state="disabled",
                                    command=self.refresh_categories)
        self.refresh_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=6)
        
        # Quick stats display - more compact
        quick_stats = ttk.Frame(secondary_frame)
        quick_stats.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        
        self.drop_stats = ttk.Label(quick_stats, text="Drop folder: Ready",
                                  font=("Segoe UI", 8), foreground="#000000")
        self.drop_stats.pack()
        
        self.sort_stats = ttk.Label(quick_stats, text="Sort folder: Ready",
                                  font=("Segoe UI", 8), foreground="#000000")
        self.sort_stats.pack(pady=(2, 0))

    def create_footer_section(self, parent):
        """Create the footer with additional info"""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=4, column=0, sticky="ew")
        footer_frame.columnconfigure(1, weight=1)
        
        # Version info
        ttk.Label(footer_frame, text="v2.0",
                 font=("Segoe UI", 8), foreground="#000000").grid(row=0, column=0, sticky="w")
        
        # Help text
        help_text = "Drag files to Drop folder • Files are automatically sorted every 5 seconds"
        ttk.Label(footer_frame, text=help_text,
                 font=("Segoe UI", 8), foreground="#000000").grid(row=0, column=1, sticky="e")

    def refresh_categories(self):
        """Refresh category count and related info"""
        try:
            categories = load_categories()
            count = len(categories)
            self.categories_count.config(text=f"Categories: {count}")
            self.show_temporary_status("Categories refreshed", "scanning")
        except Exception as e:
            self.show_temporary_status("Failed to refresh categories", "error")

    def show_temporary_status(self, message, state, duration=2000):
        """Show a temporary status message"""
        self.status_indicator.set_state(state, message)
        self.root.after(duration, lambda: self.status_indicator.set_state("idle" if not self.sorting else "waiting"))

    def update_workspace_display(self):
        """Update the workspace path display"""
        if self.workspace.exists():
            # Truncate long paths for display
            path_str = str(self.workspace)
            if len(path_str) > 50:
                path_str = "..." + path_str[-47:]
            
            self.workspace_path.config(text=path_str, foreground="#000000")
            self.workspace_icon.config(text="✅")
            self.workspace_btn.config(text="📁 Change Workspace")
            
            # Update drop and sort folder stats
            drop_count = len([f for f in self.drop_dir.rglob("*") if f.is_file()]) if self.drop_dir.exists() else 0
            sort_count = len([f for f in self.sort_dir.rglob("*") if f.is_file()]) if self.sort_dir.exists() else 0
            
            self.drop_stats.config(text=f"Drop folder: {drop_count} files pending")
            self.sort_stats.config(text=f"Sort folder: {sort_count} files organized")
        else:
            self.workspace_path.config(text="No workspace selected", foreground="#000000")
            self.workspace_icon.config(text="📂")
            self.workspace_btn.config(text="🔍 Select Workspace")

    # ------------------------------------------------------------------
    # Workspace handling (updated to enable buttons)
    # ------------------------------------------------------------------
    def on_startup(self):
        """Try to find an existing workspace config file"""
        # This could be expanded to look for previous workspace configs
        self.update_workspace_display()

    def choose_workspace(self):
        ws = filedialog.askdirectory(title="Select workspace folder")
        if not ws:
            return
        self.workspace = Path(ws)
        self.set_workspace()
        
        # Save workspace config inside the FileSorter subfolder
        config_file = get_workspace_config_file(self.workspace)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(str(self.workspace))
        
        # Also save to recent workspaces list
        save_recent_workspace(self.workspace)

    def set_workspace(self):
        try:
            ensure_workspace(self.workspace)
            
            # Set the workspace path for config system
            set_workspace_path(self.workspace)
            
            # Create directory structure
            self.drop_dir = self.workspace / "Drop"
            self.sort_dir = self.workspace / "Sorted"
            
            # FileSorter folder with config goes inside workspace
            filesorter_dir = self.workspace / "FileSorter"
            config_dir = filesorter_dir / "config"
            
            # Create all necessary directories
            self.drop_dir.mkdir(exist_ok=True)
            self.sort_dir.mkdir(exist_ok=True)
            config_dir.mkdir(parents=True, exist_ok=True)

            # Enable all buttons now that workspace is set
            self.main_action_btn.config(state="normal")
            self.category_btn.config(state="normal")
            self.refresh_btn.config(state="normal")
            
            self.update_workspace_display()
            self.refresh_categories()
            self.show_temporary_status("Workspace configured successfully", "scanning")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            # Keep buttons disabled on error
            self.main_action_btn.config(state="disabled")
            self.category_btn.config(state="disabled")
            self.refresh_btn.config(state="disabled")
            self.show_temporary_status("Workspace setup failed", "error")

    # ------------------------------------------------------------------
    # Sorting callbacks (enhanced with better feedback)
    # ------------------------------------------------------------------
    def sort_done(self, current, total):
        if current == total and total > 0:
            self.status_indicator.set_state("waiting", f"Sorted {total} files - waiting for next scan")
            self.files_processed.config(text=f"Files: {total}")
            self.progress_bar.stop_pulse()
            self.update_workspace_display()  # Update file counts
        elif total > 0:
            self.status_indicator.set_state("sorting", f"Processing {current}/{total} files")
            if not self.progress_bar.is_animating:
                self.progress_bar.start_pulse()

    # ------------------------------------------------------------------
    # Start / Stop toggle (enhanced)
    # ------------------------------------------------------------------
    def toggle_start_stop(self):
        self.sorting = not self.sorting
        
        if self.sorting:
            self.main_action_btn.config(text="⏹️ Stop Sorting")
            self.status_indicator.set_state("starting")
            self.start_sorting()
        else:
            self.main_action_btn.config(text="🚀 Start Sorting")
            self.stop_sorting()

    def start_sorting(self):
        if not self.workspace.exists():
            messagebox.showerror("Error", "No workspace selected.")
            self.sorting = False
            self.main_action_btn.config(text="🚀 Start Sorting")
            return
            
        self.status_indicator.set_state("starting", "Initializing file sorting...")
        self.timer_loop()

    def stop_sorting(self):
        self.sorting = False
        self.progress_bar.stop_pulse()
        self.status_indicator.set_state("idle")
        self.next_scan_label.config(text="")

    def timer_loop(self):
        if not self.sorting:
            return
            
        if self.next_scan <= 0:
            try:
                self.status_indicator.set_state("scanning", "Scanning drop folder...")
                sort_folder(self.drop_dir, self.sort_dir, self.sort_done)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.show_temporary_status("Sorting failed", "error")
            self.next_scan = 5
        else:
            self.next_scan -= 1
            self.status_indicator.set_state("waiting", f"Next scan in {self.next_scan}s")
            self.next_scan_label.config(text=f"Next scan: {self.next_scan}s")
            
        self.root.after(1000, self.timer_loop)

    def run(self):
        self.root.mainloop()