import shutil
import sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Import tqdm but handle the case where stdout is None (in compiled EXE)
try:
    from tqdm import tqdm
    # Check if stdout is available for tqdm
    if sys.stdout is None:
        # Create a dummy tqdm that doesn't output to stdout
        def tqdm(iterable, desc=None, **kwargs):
            return iterable
except ImportError:
    # Fallback if tqdm is not available
    def tqdm(iterable, desc=None, **kwargs):
        return iterable

def sort_folder(src: Path, dst: Path, progress_cb):
    from core.config import load_categories
    categories = load_categories()

    files = [p for p in src.rglob("*") if p.is_file()]
    plan = defaultdict(list)

    for file in files:
        ext = file.suffix.lstrip(".").lower()
        for cat, exts in categories.items():
            if ext in exts:
                plan[cat].append(file)
                break
        else:
            plan["Other"].append(file)

    total = len(files)
    done = 0
    with ThreadPoolExecutor() as pool:
        futures = []
        for cat, items in plan.items():
            tgt = dst / cat
            tgt.mkdir(exist_ok=True)
            for item in items:
                futures.append(pool.submit(shutil.move, item, tgt / item.name))
        
        # Use tqdm with stdout check, or fallback to simple iteration
        if sys.stdout is not None:
            progress_iter = tqdm(futures, desc="Sorting")
        else:
            progress_iter = futures
            
        for _ in progress_iter:
            done += 1
            progress_cb(done, total)

