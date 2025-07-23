import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
import json

from core.config import load_categories, save_user_categories
from core.utils import validate_extension, validate_category_name
from core.errors import (
    EmptyExtension,
    DuplicateExtension,
    EmptyCategoryName,
    InvalidExtensionFormat,
    ConfigWriteError
)


class ModernDialog(tk.Toplevel):
    """Custom dialog for adding categories and extensions with modern styling."""
    
    def __init__(self, parent, title, prompt, validate_func=None):
        super().__init__(parent)
        self.result = None
        self.validate_func = validate_func
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(prompt)
        self.entry.focus_set()
        
    def create_widgets(self, prompt):
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="30 20")
        main_frame.pack(fill="both", expand=True)
        
        # Icon and prompt
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(pady=(0, 20))
        
        ttk.Label(icon_frame, text="📝", font=("Segoe UI Emoji", 24), foreground="#000000").pack(side="left", padx=(0, 10))
        ttk.Label(icon_frame, text=prompt, font=("Segoe UI", 12), foreground="#000000").pack(side="left")
        
        # Entry field with modern styling
        self.entry = ttk.Entry(main_frame, font=("Segoe UI", 11), width=30)
        self.entry.pack(pady=(0, 20), ipady=8)
        self.entry.bind("<Return>", lambda e: self.ok_clicked())
        self.entry.bind("<Escape>", lambda e: self.cancel_clicked())
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0))
        
        ttk.Button(btn_frame, text="✓ OK", command=self.ok_clicked).pack(side="right", padx=(10, 0))
        ttk.Button(btn_frame, text="✗ Cancel", command=self.cancel_clicked).pack(side="right")
        
    def ok_clicked(self):
        value = self.entry.get().strip()
        if not value:
            return
            
        if self.validate_func:
            try:
                value = self.validate_func(value)
            except Exception as e:
                messagebox.showerror("Invalid Input", str(e), parent=self)
                return
                
        self.result = value
        self.destroy()
        
    def cancel_clicked(self):
        self.destroy()


class CategoryEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Category Manager - FileSorter")
        self.geometry("830x630")  # Increased window size by 30 pixels
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.minsize(780, 580)  # Increased minimum size by 30 pixels
        
        # Center the window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Set up custom styles
        self.setup_styles()
        
        self.categories = load_categories()
        
        # Initialize search variables
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        
        self.build_ui()
        self.refresh_tree()
        
        # Set up keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.new_category())
        self.bind("<Control-e>", lambda e: self.add_extension())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<F1>", lambda e: self.show_help())
        self.bind("<Delete>", lambda e: self.delete_selected())

    def setup_styles(self):
        """Set up custom styles for the application"""
        style = ttk.Style()
        
        # Define colors - more modern palette
        self.colors = {
            "primary": "#4361ee",  # Modern blue
            "secondary": "#3f37c9",
            "accent": "#4895ef",
            "success": "#4cc9f0",
            "warning": "#f72585",
            "danger": "#e63946",
            "light": "#f8f9fa",
            "dark": "#212529",
            "bg": "#ffffff",  # Clean white background
            "text": "#000000",  # Black text
            "text_light": "#000000"  # Black text
        }
        
        # Configure TFrame
        style.configure("Main.TFrame", background=self.colors["bg"])
        
        # Configure TButton styles with modern aesthetic
        style.configure("Primary.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=(15, 8),
                        background=self.colors["primary"],
                        foreground="#000000")
        
        style.configure("Success.TButton",
                        font=("Segoe UI", 9),
                        padding=(10, 6),
                        background=self.colors["success"],
                        foreground="#000000")
        
        style.configure("Danger.TButton",
                        font=("Segoe UI", 9),
                        padding=(10, 6),
                        background=self.colors["danger"],
                        foreground="#000000")
        
        # Add a neutral style for secondary buttons
        style.configure("Secondary.TButton",
                        font=("Segoe UI", 9),
                        padding=(10, 6),
                        background=self.colors["light"],
                        foreground="#000000")
        
        # Configure TLabel styles
        style.configure("Title.TLabel",
                        font=("Segoe UI", 14, "bold"),  # Reduced font size
                        foreground="#000000")
        
        style.configure("Subtitle.TLabel",
                        font=("Segoe UI", 10),  # Reduced font size
                        foreground="#000000")
        
        style.configure("Stats.TLabel",
                        font=("Segoe UI", 9, "bold"),  # Reduced font size from 10 to 9
                        foreground="#000000")
        
        style.configure("Status.TLabel",
                       font=("Segoe UI", 9),
                       foreground="#000000")
        
        # Configure Treeview
        style.configure("Treeview",
                        font=("Segoe UI", 9),  # Reduced font size
                        rowheight=22,  # Reduced row height
                        background="#f0f5ff",  # Slightly blue tint for better visibility
                        fieldbackground="#f0f5ff")
        
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 9, "bold"),  # Reduced font size
                        background=self.colors["primary"],
                        foreground="#000000")
        
        # Configure TLabelframe
        # Modern frame styling with subtle border
        style.configure("TLabelframe",
                        background=self.colors["bg"],
                        foreground="#000000")
        
        style.configure("TLabelframe.Label",
                        font=("Segoe UI", 10, "bold"),  # Reduced font size
                        foreground="#000000")
        
        # Add modern styling to the entire application
        self.configure(background=self.colors["bg"])
    
    def build_ui(self):
        """Build the modern, immersive UI with scrolling"""
        # Configure grid weights for responsive layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create main canvas and scrollbar for vertical scrolling
        main_canvas = tk.Canvas(self, highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas, style="Main.TFrame")
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # Configure canvas window to expand with content
        def configure_canvas(event):
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_canvas.bind('<Configure>', configure_canvas)
        
        # Grid the canvas and scrollbar
        main_canvas.grid(row=0, column=0, sticky="nsew")
        main_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Main container with modern styling
        main_frame = ttk.Frame(scrollable_frame, padding="15", style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Store references for scrolling
        self.main_canvas = main_canvas
        self.scrollable_frame = scrollable_frame
        
        # Header section
        self.create_header(main_frame)
        
        # Search and stats section (side by side)
        self.create_search_stats_section(main_frame)
        
        # Category list section
        self.create_category_list_section(main_frame)
        
        # Tree view section
        self.create_tree_section(main_frame)
        
        # Action buttons section
        self.create_action_section(main_frame)
        
        # Footer section
        self.create_footer_section(main_frame)
        
        # Bind mouse wheel scrolling
        self.bind_mousewheel()

    def create_header(self, parent):
        """Create the header section with title."""
        header_frame = ttk.Frame(parent, style="Main.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Icon and title
        title_frame = ttk.Frame(header_frame, style="Main.TFrame")
        title_frame.grid(row=0, column=0, sticky="w")
        
        ttk.Label(title_frame, text="🗂️", font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 8))  # Reduced size
        
        text_frame = ttk.Frame(title_frame, style="Main.TFrame")
        text_frame.pack(side="left")
        
        ttk.Label(text_frame, text="Category Manager", style="Title.TLabel").pack(anchor="w")
        ttk.Label(text_frame, text="Organize your file extensions with ease",
                 style="Subtitle.TLabel").pack(anchor="w")

    def create_search_stats_section(self, parent):
        """Create search bar and statistics section side by side."""
        search_stats_frame = ttk.Frame(parent, style="Main.TFrame")
        search_stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        search_stats_frame.columnconfigure(0, weight=1)
        search_stats_frame.columnconfigure(1, weight=1)
        
        # Search section (left side)
        search_frame = ttk.LabelFrame(search_stats_frame, text="🔍 Search", padding="8")
        search_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Search icon
        ttk.Label(search_frame, text="🔍", font=("Segoe UI Emoji", 12)).grid(row=0, column=0, padx=(0, 4))
        
        # Search entry
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                                     font=("Segoe UI", 11))
        self.search_entry.grid(row=0, column=1, sticky="ew", ipady=3)
        
        # Clear search button
        clear_btn = ttk.Button(search_frame, text="✕", width=3,
                              command=self.clear_search)
        clear_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Statistics section (right side)
        stats_frame = ttk.LabelFrame(search_stats_frame, text="📊 Statistics", padding="8")
        stats_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        # Create a container for stats
        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill="x", padx=5, pady=2)
        
        # Statistics labels in a horizontal layout
        self.stats_categories = ttk.Label(stats_container, text="Categories: 0",
                                         style="Stats.TLabel")
        self.stats_categories.pack(side="left", padx=(0, 15))
        
        self.stats_extensions = ttk.Label(stats_container, text="Extensions: 0",
                                         style="Stats.TLabel")
        self.stats_extensions.pack(side="left", padx=(0, 15))
        
        self.stats_custom = ttk.Label(stats_container, text="Custom: 0",
                                     style="Stats.TLabel")
        self.stats_custom.pack(side="left")
        
        # Add tooltips
        self.create_tooltip(self.search_entry, "Search for categories or extensions (Ctrl+F)")
        self.create_tooltip(clear_btn, "Clear search")
        self.create_tooltip(self.stats_categories, "Total number of categories")
        self.create_tooltip(self.stats_extensions, "Total number of extensions across all categories")
        self.create_tooltip(self.stats_custom, "Number of custom categories you've created")

    def create_category_list_section(self, parent):
        """Create category list section."""
        category_frame = ttk.LabelFrame(parent, text="📁 Quick Category Access", padding="8")
        category_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Create a scrollable frame for category buttons
        canvas = tk.Canvas(category_frame, height=60, highlightthickness=0)
        scrollbar = ttk.Scrollbar(category_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")
        
        # Store reference for updating
        self.category_buttons_frame = scrollable_frame
        self.category_canvas = canvas
        
        # Initial population of category buttons
        self.update_category_buttons()

    def update_category_buttons(self):
        """Update the category buttons in the quick access section."""
        # Clear existing buttons
        for widget in self.category_buttons_frame.winfo_children():
            widget.destroy()
        
        # Add category buttons
        for i, (cat, exts) in enumerate(sorted(self.categories.items())):
            btn = ttk.Button(self.category_buttons_frame,
                           text=f"📁 {cat} ({len(exts)})",
                           command=lambda c=cat: self.select_category_in_tree(c),
                           width=15)
            btn.pack(side="left", padx=2, pady=2)
            self.create_tooltip(btn, f"Click to select {cat} category in tree")
        
        # Update canvas scroll region
        self.category_buttons_frame.update_idletasks()
        self.category_canvas.configure(scrollregion=self.category_canvas.bbox("all"))

    def select_category_in_tree(self, category_name):
        """Select a category in the tree view."""
        for item in self.tree.get_children():
            item_text = self.tree.item(item, "text")
            if item_text == f"📁 {category_name}":
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

    def create_tree_section(self, parent):
        """Create the main tree view section."""
        tree_frame = ttk.LabelFrame(parent, text="📁 File Categories", padding="10")  # Reduced padding
        tree_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))  # Reduced bottom padding
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create treeview with modern styling
        tree_container = ttk.Frame(tree_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)  # Added small padding
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_container,
                                columns=("count", "extensions"),
                                show="tree headings",
                                height=15)
        
        # Configure columns - adjusted for better space utilization
        self.tree.heading("#0", text="📁 Category", anchor="w")
        self.tree.column("#0", width=180, minwidth=120)  # Reduced width
        
        self.tree.heading("count", text="📊 Count", anchor="center")
        self.tree.column("count", width=60, minwidth=50, anchor="center")  # Reduced width
        
        self.tree.heading("extensions", text="🏷️ Extensions", anchor="w")
        self.tree.column("extensions", width=400, minwidth=180)  # Reduced width
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Button-3>", self.on_tree_right_click)
        self.tree.bind("<Return>", lambda e: self.on_tree_enter_key())
        
        # Add tooltip to tree
        self.create_tooltip(self.tree, "Double-click to expand/collapse • Right-click for options")

    def create_action_section(self, parent):
        """Create action buttons section with modern aesthetic design."""
        action_frame = ttk.LabelFrame(parent, text="⚡ Quick Actions", padding="12")
        action_frame.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        action_frame.columnconfigure(0, weight=1)
        
        # Primary actions container
        primary_container = ttk.Frame(action_frame)
        primary_container.pack(fill="x", pady=(0, 8))
        primary_container.columnconfigure((0, 1), weight=1)
        
        # Primary action buttons - larger and more prominent
        new_cat_btn = ttk.Button(primary_container, text="📁 New Category",
                               style="Primary.TButton",
                               command=self.new_category)
        new_cat_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.create_tooltip(new_cat_btn, "Create a new category (Ctrl+N)")
        
        add_ext_btn = ttk.Button(primary_container, text="🏷️ Add Extension",
                               style="Primary.TButton",
                               command=self.add_extension)
        add_ext_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.create_tooltip(add_ext_btn, "Add extension to selected category (Ctrl+E)")
        
        # Secondary actions container
        secondary_container = ttk.Frame(action_frame)
        secondary_container.pack(fill="x", pady=(4, 0))
        secondary_container.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Secondary action buttons - smaller and uniform
        edit_btn = ttk.Button(secondary_container, text="✏️ Edit",
                            style="Success.TButton",
                            command=self.edit_selected)
        edit_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.create_tooltip(edit_btn, "Edit selected item")
        
        delete_btn = ttk.Button(secondary_container, text="🗑️ Delete",
                              style="Danger.TButton",
                              command=self.delete_selected)
        delete_btn.grid(row=0, column=1, sticky="ew", padx=(2, 2))
        self.create_tooltip(delete_btn, "Delete selected item (Delete)")
        
        refresh_btn = ttk.Button(secondary_container, text="🔄 Refresh",
                               style="Secondary.TButton",
                               command=self.refresh_tree)
        refresh_btn.grid(row=0, column=2, sticky="ew", padx=(2, 2))
        self.create_tooltip(refresh_btn, "Refresh category tree")
        
        help_btn = ttk.Button(secondary_container, text="❓ Help",
                            style="Secondary.TButton",
                            command=self.show_help)
        help_btn.grid(row=0, column=3, sticky="ew", padx=(2, 0))
        self.create_tooltip(help_btn, "Show help (F1)")

    def create_footer_section(self, parent):
        """Create footer section with save/close buttons."""
        footer_frame = ttk.Frame(parent, style="Main.TFrame")
        footer_frame.grid(row=5, column=0, sticky="ew")
        footer_frame.columnconfigure(0, weight=1)
        
        # Status label with better styling
        status_container = ttk.Frame(footer_frame, style="Main.TFrame")
        status_container.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        status_container.columnconfigure(1, weight=1)
        
        ttk.Label(status_container, text="📢", font=("Segoe UI Emoji", 10)).grid(row=0, column=0, padx=(0, 4))  # Reduced size
        self.status_label = ttk.Label(status_container, text="Ready", style="Status.TLabel")
        self.status_label.grid(row=0, column=1, sticky="w")
        
        # Keyboard shortcuts hint
        shortcut_text = "Shortcuts: Ctrl+N (New Category), Ctrl+E (Add Extension), Ctrl+F (Search), F1 (Help)"
        ttk.Label(footer_frame, text=shortcut_text, style="Status.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Action buttons
        btn_frame = ttk.Frame(footer_frame, style="Main.TFrame")
        btn_frame.grid(row=2, column=0, sticky="e")
        
        save_btn = ttk.Button(btn_frame, text="💾 Save & Close",
                            style="Success.TButton",
                            command=self.save_close)
        save_btn.pack(side="right", padx=(10, 0))
        self.create_tooltip(save_btn, "Save changes and close")
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Cancel",
                              command=self.destroy)
        cancel_btn.pack(side="right")
        self.create_tooltip(cancel_btn, "Close without saving")

    def update_stats(self):
        """Update the statistics display."""
        total_categories = len(self.categories)
        total_extensions = sum(len(exts) for exts in self.categories.values())
        
        # Count custom categories (assuming built-in ones are standard)
        built_in_cats = {"Images", "Videos", "Audio", "Docs", "Executable", 
                        "Archives", "Code", "Fonts", "Ebooks", "Sheets", "Other"}
        custom_categories = sum(1 for cat in self.categories.keys() if cat not in built_in_cats)
        
        self.stats_categories.config(text=f"Categories: {total_categories}")
        self.stats_extensions.config(text=f"Extensions: {total_extensions}")
        self.stats_custom.config(text=f"Custom: {custom_categories}")

    def refresh_tree(self):
        """Refresh the tree view with current categories."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add categories
        for cat, exts in sorted(self.categories.items()):
            # Format extensions list
            ext_display = ", ".join(f".{ext}" for ext in sorted(exts))
            if len(ext_display) > 50:
                ext_display = ext_display[:47] + "..."
            
            # Insert category
            parent = self.tree.insert("", "end", text=f"📁 {cat}", 
                                    values=(len(exts), ext_display))
            
            # Add individual extensions as children
            for ext in sorted(exts):
                self.tree.insert(parent, "end", text=f"🏷️ .{ext}", values=("", ""))
        
        self.update_stats()
        self.update_category_buttons()
        self.set_status("Tree refreshed")

    def set_status(self, message, duration=3000):
        """Set status message with auto-clear."""
        self.status_label.config(text=message)
        self.after(duration, lambda: self.status_label.config(text="Ready"))

    def on_tree_double_click(self, event):
        """Handle double-click on tree items."""
        item = self.tree.focus()
        if not item:
            return
        
        # If it's a category, toggle expansion
        if not self.tree.parent(item):
            children = self.tree.get_children(item)
            if children:
                if self.tree.item(item, "open"):
                    self.tree.item(item, open=False)
                else:
                    self.tree.item(item, open=True)

    def on_tree_right_click(self, event):
        """Handle right-click context menu."""
        # Get the item that was clicked on
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell" and region != "text":
            return
            
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        # Select the item
        self.tree.selection_set(item)
        self.tree.focus(item)
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Check if it's a category or extension
        parent = self.tree.parent(item)
        
        if parent:  # It's an extension
            context_menu.add_command(label="🗑️ Delete Extension",
                                   command=self.delete_selected)
            context_menu.add_separator()
            category_text = self.tree.item(parent, "text")
            category = category_text.replace("📁 ", "")
            ext_text = self.tree.item(item, "text")
            ext = ext_text.replace("🏷️ .", "")
            context_menu.add_command(label=f"📋 Copy '.{ext}'",
                                   command=lambda: self.copy_to_clipboard(f".{ext}"))
        else:  # It's a category
            category_text = self.tree.item(item, "text")
            category = category_text.replace("📁 ", "")
            
            context_menu.add_command(label="📁 Expand/Collapse",
                                   command=lambda: self.toggle_category(item))
            context_menu.add_command(label="🏷️ Add Extension",
                                   command=self.add_extension)
            
            if category != "Other":  # Can't delete "Other" category
                context_menu.add_command(label="🗑️ Delete Category",
                                       command=self.delete_selected)
            
            context_menu.add_separator()
            context_menu.add_command(label=f"📋 Copy '{category}'",
                                   command=lambda: self.copy_to_clipboard(category))
        
        # Display the context menu
        context_menu.tk_popup(event.x_root, event.y_root)
        
    def on_tree_enter_key(self):
        """Handle Enter key press on tree items."""
        item = self.tree.focus()
        if not item:
            return
            
        parent = self.tree.parent(item)
        if parent:  # It's an extension
            # Maybe show extension details in the future
            pass
        else:  # It's a category
            self.toggle_category(item)
            
    def toggle_category(self, item):
        """Toggle expansion of a category."""
        if self.tree.item(item, "open"):
            self.tree.item(item, open=False)
        else:
            self.tree.item(item, open=True)
            
    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.set_status(f"Copied to clipboard: {text}")

    def new_category(self):
        """Add a new category."""
        dialog = ModernDialog(self, "New Category", "Enter category name:", 
                            validate_category_name)
        self.wait_window(dialog)
        
        if not dialog.result:
            return
            
        name = dialog.result
        if name in self.categories:
            messagebox.showerror("Duplicate Category", 
                               f"Category '{name}' already exists.", parent=self)
            return
        
        self.categories[name] = []
        self.refresh_tree()
        self.set_status(f"Added category: {name}")

    def add_extension(self):
        """Add extension to selected category."""
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("No Selection", 
                                 "Please select a category first.", parent=self)
            return
        
        # Get the category (if extension is selected, get its parent)
        parent = self.tree.parent(item) or item
        category_text = self.tree.item(parent, "text")
        category = category_text.replace("📁 ", "")  # Remove icon
        
        dialog = ModernDialog(self, "Add Extension", 
                            f"Enter extension for '{category}':", 
                            validate_extension)
        self.wait_window(dialog)
        
        if not dialog.result:
            return
            
        ext = dialog.result
        if ext in self.categories[category]:
            messagebox.showerror("Duplicate Extension", 
                               f"Extension '.{ext}' already exists in '{category}'.", 
                               parent=self)
            return
        
        self.categories[category].append(ext)
        self.refresh_tree()
        self.set_status(f"Added .{ext} to {category}")

    def edit_selected(self):
        """Edit the selected item."""
        item = self.tree.focus()
        if not item:
            return
        
        parent = self.tree.parent(item)
        if parent:  # It's an extension
            messagebox.showinfo("Edit Extension", 
                              "To edit an extension, delete it and add a new one.", 
                              parent=self)
        else:  # It's a category
            messagebox.showinfo("Edit Category", 
                              "Category renaming not implemented yet.", parent=self)

    def delete_selected(self):
        """Delete the selected item."""
        item = self.tree.focus()
        if not item:
            return
        
        parent = self.tree.parent(item)
        
        if parent:  # Deleting an extension
            category_text = self.tree.item(parent, "text")
            category = category_text.replace("📁 ", "")
            
            ext_text = self.tree.item(item, "text")
            ext = ext_text.replace("🏷️ .", "")
            
            if messagebox.askyesno("Confirm Delete", 
                                 f"Delete extension '.{ext}' from '{category}'?", 
                                 parent=self):
                if ext in self.categories[category]:
                    self.categories[category].remove(ext)
                    self.refresh_tree()
                    self.set_status(f"Deleted .{ext} from {category}")
        else:  # Deleting a category
            category_text = self.tree.item(item, "text")
            category = category_text.replace("📁 ", "")
            
            if category == "Other":
                messagebox.showerror("Cannot Delete", 
                                   "The 'Other' category cannot be deleted.", 
                                   parent=self)
                return
            
            if messagebox.askyesno("Confirm Delete", 
                                 f"Delete category '{category}' and all its extensions?", 
                                 parent=self):
                if category in self.categories:
                    del self.categories[category]
                    self.refresh_tree()
                    self.set_status(f"Deleted category: {category}")

    def save_close(self):
        """Save categories and close the editor."""
        try:
            save_user_categories(self.categories)
            messagebox.showinfo("Success", 
                              "Categories saved successfully!", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Failed",
                               f"Could not save categories: {str(e)}", parent=self)
                               
    # ---- Tooltip functionality ----
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def enter(event):
            self.tooltip = tk.Toplevel(self)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+10}")
            
            frame = ttk.Frame(self.tooltip, borderwidth=1, relief="solid")
            frame.pack(fill="both", expand=True)
            
            label = ttk.Label(frame, text=text, justify="left",
                            background="#f8f9fa",
                            foreground="#000000",
                            font=("Segoe UI", 9),
                            wraplength=250,
                            padding=(5, 3))
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        
    # ---- Search functionality ----
    def on_search_change(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get().lower()
        if not search_text:
            # If search is cleared, just refresh the tree
            self.refresh_tree()
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Search in categories and extensions
        for cat, exts in sorted(self.categories.items()):
            cat_matches = search_text in cat.lower()
            matching_exts = [ext for ext in exts if search_text in ext.lower()]
            
            if cat_matches or matching_exts:
                # Format extensions list
                if matching_exts:
                    ext_display = ", ".join(f".{ext}" for ext in sorted(matching_exts))
                else:
                    ext_display = ", ".join(f".{ext}" for ext in sorted(exts))
                    
                if len(ext_display) > 50:
                    ext_display = ext_display[:47] + "..."
                
                # Insert category
                parent = self.tree.insert("", "end", text=f"📁 {cat}",
                                        values=(len(matching_exts) if matching_exts else len(exts),
                                               ext_display))
                
                # Add matching extensions as children
                for ext in sorted(matching_exts if matching_exts else exts):
                    if not matching_exts or search_text in ext.lower():
                        self.tree.insert(parent, "end", text=f"🏷️ .{ext}", values=("", ""))
                
                # Auto-expand categories with matching items
                if matching_exts and not cat_matches:
                    self.tree.item(parent, open=True)
        
        # Update status
        if self.tree.get_children():
            self.set_status(f"Search results for: {search_text}")
        else:
            self.set_status(f"No matches found for: {search_text}")
            
    def clear_search(self):
        """Clear the search field."""
        self.search_var.set("")
        self.search_entry.focus_set()
        
    # ---- Help section ----
    def show_help(self):
        """Show help dialog."""
        help_window = tk.Toplevel(self)
        help_window.title("Category Manager Help")
        help_window.geometry("600x500")
        help_window.transient(self)
        help_window.grab_set()
        
        # Center the window
        help_window.geometry("+%d+%d" % (self.winfo_rootx() + 50, self.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(help_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="Category Manager Help",
                 font=("Segoe UI", 16, "bold"), foreground="#000000").pack(pady=(0, 20))
        
        # Create scrollable text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        help_text = tk.Text(text_frame, wrap="word", font=("Segoe UI", 10),
                          yscrollcommand=scrollbar.set, padx=10, pady=10)
        help_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=help_text.yview)
        
        # Help content
        help_content = """
🗂️ Category Manager

The Category Manager allows you to organize file extensions into categories for automatic file sorting.

📌 Basic Operations:
• Create new categories to group related file types
• Add extensions to categories
• Delete extensions or categories
• Search for categories or extensions

📌 Keyboard Shortcuts:
• Ctrl+N: Create a new category
• Ctrl+E: Add an extension to selected category
• Ctrl+F: Search for categories or extensions
• F1: Show this help
• Delete: Delete selected item

📌 Tips:
• Right-click on categories or extensions for additional options
• Double-click on a category to expand or collapse it
• Use the search bar to quickly find categories or extensions
• The "Other" category cannot be deleted as it's used for uncategorized files
• Changes are only saved when you click "Save & Close"

📌 Categories:
Categories help organize your files by type. Each category can contain multiple file extensions.
Built-in categories include: Images, Videos, Audio, Docs, Executable, Archives, Code, Fonts, Ebooks, Sheets, and Other.

📌 Extensions:
Extensions are file types (without the dot). For example: "pdf", "jpg", "mp3".
Each extension can only belong to one category.
        """
        
        help_text.insert("1.0", help_content)
        help_text.config(state="disabled")  # Make read-only
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=help_window.destroy).pack(pady=(20, 0))
    
    def bind_mousewheel(self):
        """Bind mouse wheel scrolling to the canvas"""
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.main_canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events
        self.main_canvas.bind('<Enter>', _bind_to_mousewheel)
        self.main_canvas.bind('<Leave>', _unbind_from_mousewheel)