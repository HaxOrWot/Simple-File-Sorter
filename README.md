<!-- ─────────────────────────────────────────────── -->
<!--  FileSorter  •  README.md  •  MIT © NotPhoeniXx -->
<!-- ─────────────────────────────────────────────── -->

<div align="center">

# FileSorter  
_A dead-simple file-organizer that tidies everything into labeled folders—no setup, no bloat._

![Management]([https://user-images.githubusercontent.com/your-gif-link.gif](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYW40empjdHhybzRhMHppYXA5Y29jajU0ZTg3ZDIwZnpuaTB0dGdxZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ENeLuI1PyqUnJv4NMl/giphy.gif))

</div>

---

### ⏱️ TL;DR
1. Double-click the EXE.  
2. Pick (or create) an install folder.  
3. Drop messy folders onto the window → instantly sorted.

---

## 📥 Installation

| Requirement | Status |
|-------------|--------|
| OS          | **Any** – Windows, macOS, Linux |
| Runtime     | **None** – single portable EXE |
| Disk space  | < 1 MB |

1. Download `FileSorter.exe` from [Releases](https://github.com/NotPhoeniXx/FileSorter/releases).  
2. Run it → choose an install folder.  
3. Done. *(Four tiny files will be auto-created for you.)*

---

## ⚙️ First-Run Notes
- **Important files**  
  `categories.json` • `config.json` • `logs.txt` • `app_base_path.txt`

- **Never move or delete** `app_base_path.txt`; it tells FileSorter where it lives.  
- If the file is missing, the app will simply ask again for the install folder.

---

## 🚀 Usage

| Step | Action |
|------|--------|
| 1 | Launch `FileSorter.exe`. |
| 2 | Drag any messy folder into the window. |
| 3 | Watch files vanish into neat sub-folders by type (`Images`, `Docs`, `Audio`, …). |

No menus. No settings. One window. 🎉

---

## 🛠️ Tech Stack
- **Language**: 100 % Python  
- **GUI**: `tkinter` + `messagebox` + `filedialog` + `scrolledtext`  
- **Core**: `os`, `threading`

---

## 🗺️ Roadmap
- [ ] Cleaner, more immersive GUI  
- [ ] Custom category rules  
- [ ] Dark mode

---

## 🤝 Contributing / Issues
Found a bug or want a feature?  
Ping me on Discord → `.notphoenixx`

---

## 📄 License
GPL-3.0 – see [LICENSE](LICENSE).

---

<div align="center">

Made with ☕ by **NotPhoeniXx**

</div>
