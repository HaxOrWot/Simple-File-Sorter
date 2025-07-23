import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.sorter import sort_folder
from ui.toast import notify

class DropHandler(FileSystemEventHandler):
    def __init__(self, drop_dir: Path, sorted_dir: Path):
        super().__init__()
        self.drop_dir = drop_dir
        self.sorted_dir = sorted_dir

    def on_created(self, event):
        if event.is_directory:
            time.sleep(0.3)
            sort_folder(Path(event.src_path), self.sorted_dir, lambda c, t: None)
            notify("FileSorter", f"Sorted {Path(event.src_path).name}")

def start_watching(drop_dir: Path, sorted_dir: Path):
    handler = DropHandler(drop_dir, sorted_dir)
    obs = Observer()
    obs.schedule(handler, str(drop_dir), recursive=False)
    obs.start()
    return obs
