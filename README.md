<!-- ─────────────────────────────────────────────── -->
<!--  FileSorter  •  README.md  •  GPL © NotPhoeniXx -->
<!-- ─────────────────────────────────────────────── -->

<div align="center">

# Simple File Sorter  
_A dead-simple file-organizer that tidies everything into labeled folders—no setup, no bloat._

</div>


---

## 📑 Table of Contents
- [TL;DR](https://github.com/HaxOrWot/Simple-File-Sorter?tab=readme-ov-file#%EF%B8%8F-tldr)
- [Installation](#-installation)
- [First-Run Notes](https://github.com/HaxOrWot/Simple-File-Sorter?tab=readme-ov-file#%EF%B8%8F-first-run-notes)
- [Usage](https://github.com/HaxOrWot/Simple-File-Sorter?tab=readme-ov-file#-usage)
- [Tech Stack](https://github.com/HaxOrWot/Simple-File-Sorter?tab=readme-ov-file#%EF%B8%8F-tech-stack)
- [Roadmap](https://github.com/HaxOrWot/Simple-File-Sorter?tab=readme-ov-file#%EF%B8%8F-roadmap)
- [Contributing / Issues](https://github.com/HaxOrWot/Simple-File-Sorter?tab=readme-ov-file#-contributing--issues)
- [License](#-license)

---

## ⏱️ TL;DR
1. Double-click the EXE.  
2. Pick (or create) an install folder, and select location for both `Drop` & `Where you wanna store the sorted items`.  
3. Drop messy folders onto the `Drop` folder → instantly sorted.
4. Download [FileSorter](https://github.com/HaxOrWot/Simple-File-Sorter/releases/tag/windows-tool-v3) to Get Started.

---

## 📥 Installation

| Requirement | Status |
|-------------|--------|
| OS          | **Any** – Windows, macOS, Linux |
| Runtime     | **None** – single portable EXE |
| Disk space  | < 1 MB |

1. Download `FileSorter.exe` from [Releases](https://github.com/HaxOrWot/Simple-File-Sorter/releases/tag/windows-tool-v1).  
2. Run it → choose an install folder as well as a Folder for Drop & Sorted items.    
3. Done. *(All files & Folders will be auto-created for you.)*

---

## ⚙️ First-Run Notes
- **Important files**  
  `categories.json` • `extensions.json` • `drop_dest.txt` • `app_base_path.txt` • `sort_dest.txt`

- **Never move or delete** `app_base_path.txt`; it tells FileSorter where it lives.  
- If the file is missing, the app will simply ask again for the install folder.

---

## 🚀 Usage

| Step | Action |
|------|--------|
| 1 | Launch `FileSorter.exe`. |
| 2 | Drag any messy folder into Drop folder it created. |
| 3 | Watch files vanish into neat sub-folders by type (`Images`, `Docs`, `Audio`, …etc). |

No menus. No settings. One window. Click on Start and Boom. 🎉

---

## 🛠️ Tech Stack
- **Language**: Python  
- **GUI**: `tkinter` + `messagebox` + `filedialog` + `scrolledtext`  
- **Core**: `os`, `threading`

---

## 🗺️ Roadmap
- [x] Cleaner, more immersive GUI  
- [x] Custom category rules  
- [ ] Dark mode

---

## 🤝 Contributing / Issues
Found a bug or want a feature?  
Ping me on Discord → `.notphoenixx`

---

## 📄 License
GPL-3.0 – see [LICENSE](LICENSE).

---

# Change Log: Major Update

## Additions
- Added More Immersive GUI 
- Added Custom Gui to Edit Categories and Extensions
- Fixed some minor Bugs

## Removed
- Removed FOLDER SORTING Feature (Complexity)

## Coming Soon
- Dark Mode

<div align="center">

Made with ☕ by **NotPhoeniXx**

</div>

<!-- quick-return link -->
<sup>[↑ Back to top](#fileSorter)</sup>
