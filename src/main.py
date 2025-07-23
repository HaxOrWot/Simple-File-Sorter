import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import logging
import traceback
import os
import winshell
from win32com.client import Dispatch

# Add the src directory to Python path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path setup
try:
    from ui.app import FileSorterApp
    from core.errors import FileSorterError
    from core.config import set_workspace_path, save_recent_workspace
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)


def setup_logging():
    """Setup logging configuration for the application."""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "filesorter.log"
    
    # Create handlers list - always include file handler
    handlers = [logging.FileHandler(log_file, encoding='utf-8')]
    
    # Only add StreamHandler if stdout is available (not None in compiled EXE)
    if sys.stdout is not None:
        handlers.append(logging.StreamHandler(sys.stdout))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Reduce noise from some libraries
    logging.getLogger('watchdog').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    return logging.getLogger('FileSorter')


def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    # Check for optional dependencies
    optional_deps = {
        'watchdog': 'File system monitoring',
        'tqdm': 'Progress bars',
        'plyer': 'System notifications'
    }
    
    for dep, description in optional_deps.items():
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(f"  - {dep}: {description}")
    
    if missing_deps:
        print("Warning: Some optional dependencies are missing:")
        for dep in missing_deps:
            print(dep)
        print("\nInstall them with: pip install watchdog tqdm plyer")
        print("The application will still work with reduced functionality.\n")


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow Ctrl+C to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger('FileSorter')
    
    # Log the exception
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"Unhandled exception: {error_msg}")
    
    # Show user-friendly error dialog if Tkinter is available
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        if isinstance(exc_value, FileSorterError):
            # Show user-friendly error for our custom exceptions
            messagebox.showerror(
                "FileSorter Error",
                f"An error occurred:\n\n{str(exc_value)}\n\n"
                f"Please check the log file for more details."
            )
        else:
            # Show generic error for unexpected exceptions
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{exc_type.__name__}: {str(exc_value)}\n\n"
                f"Please check the log file for more details and consider reporting this bug."
            )
        
        root.destroy()
    except:
        # If we can't show a dialog, just print to console
        print(f"\nFatal error: {exc_type.__name__}: {exc_value}")
        print("Check the log file for more details.")


def create_desktop_shortcut():
    """Create a desktop shortcut (Windows only for now)."""
    try:
        if sys.platform == "win32":
            
            desktop = winshell.desktop()
            shortcut_path = Path(desktop) / "FileSorter.lnk"
            
            if not shortcut_path.exists():
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{Path(__file__).absolute()}"'
                shortcut.WorkingDirectory = str(Path(__file__).parent)
                shortcut.IconLocation = sys.executable
                shortcut.save()
                
                return True
    except ImportError:
        # winshell not available
        pass
    except Exception:
        # Any other error creating shortcut
        pass
    
    return False


def load_previous_workspace():
    """Try to load the previously used workspace."""
    logger = logging.getLogger('FileSorter')
    try:
        # Look for workspace config in common locations
        possible_configs = [
            Path.home() / "Documents" / "FileSorter" / "config" / "workspace.txt",
            Path(__file__).parent / "workspace.txt",
        ]
        
        # Try to load from a recently used workspaces list
        recent_workspaces_file = Path.home() / "AppData" / "Local" / "FileSorter" / "recent_workspaces.txt"
        if recent_workspaces_file.exists():
            try:
                recent_paths = recent_workspaces_file.read_text().strip().split("\n")
                for path_str in recent_paths:
                    if path_str:
                        path = Path(path_str)
                        # Check if this path has a FileSorter config
                        config_path = path / "FileSorter" / "config" / "workspace.txt"
                        if config_path.exists():
                            possible_configs.append(config_path)
            except Exception as e:
                logger.warning(f"Failed to read recent workspaces: {e}")
        
        for config_file in possible_configs:
            if config_file.exists():
                try:
                    workspace_path = Path(config_file.read_text().strip())
                    if workspace_path.exists() and workspace_path.is_dir():
                        logger.info(f"Found workspace at: {workspace_path}")
                        set_workspace_path(workspace_path)
                        
                        # Save this workspace to the recent workspaces list
                        save_recent_workspace(workspace_path)
                        
                        return workspace_path
                except Exception as e:
                    logger.warning(f"Failed to load workspace from {config_file}: {e}")
    except Exception as e:
        # If anything goes wrong, just continue without a workspace
        logger.error(f"Error in load_previous_workspace: {e}")
    
    return None


def main():
    """Main entry point for the FileSorter application."""
    # Setup logging first
    logger = setup_logging()
    logger.info("Starting FileSorter application")
    
    # Set up global exception handler
    sys.excepthook = handle_exception
    
    # Check for dependencies
    check_dependencies()
    
    try:
        # Create the main Tkinter window
        root = tk.Tk()
        
        # Set window properties
        root.title("FileSorter - Intelligent File Organization")
        
        # Try to set a nice icon (Windows)
        try:
            if sys.platform == "win32":
                # Try to use a built-in Windows icon
                root.iconbitmap(default="")  # This will use the default app icon
        except:
            pass
        
        # Load previous workspace if available
        previous_workspace = load_previous_workspace()
        if previous_workspace:
            logger.info(f"Loaded previous workspace: {previous_workspace}")
        
        # Create and run the application
        app = FileSorterApp(root)
        
        # If we have a previous workspace, set it
        if previous_workspace:
            app.workspace = previous_workspace
            app.set_workspace()
        
        logger.info("Application initialized successfully")
        
        # Try to create desktop shortcut on first run
        if create_desktop_shortcut():
            logger.info("Desktop shortcut created")
        
        # Start the main event loop
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())
        
        # Try to show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Startup Error",
                f"Failed to start FileSorter:\n\n{str(e)}\n\n"
                f"Please check the log file for more details."
            )
            root.destroy()
        except:
            print(f"Failed to start FileSorter: {e}")
        
        sys.exit(1)
    
    finally:
        logger.info("FileSorter application terminated")


if __name__ == "__main__":
    # Ensure we're running with Python 3.6+
    if sys.version_info < (3, 6):
        print("FileSorter requires Python 3.6 or higher.")
        print(f"You are running Python {sys.version}")
        sys.exit(1)
    
    # Change to the script directory for relative imports
    os.chdir(Path(__file__).parent)
    
    main()