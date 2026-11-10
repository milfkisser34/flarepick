
<div align="center">
  <h1>flarepick</h1>
</div>

**flarepick** is a tool made to easily organize your photos into pretty galleries

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.14-blue">
  <img src="https://img.shields.io/badge/PyQt6-GUI-green">
</p>

## ✨ Features

- 🗂️  **Collections**  -  Organize photos into custom collections.
- 🏷️  **EXIF Metadata**  -  View camera settings, ISO, shutter speed, and aperture.
- 🚩 **Pick & Reject** — Quickly mark photos as selected or rejected.
- 🖥️ **Desktop Interface**  —  Manage through a native PyQt6 application.

## ⚙️ Tech Specs

<p align="left">
  <img src="https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white">
  <img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black">
</p>


### Installation

If you want to run *flarepick* directly from the source code without building an executable, follow these steps:

1. Clone the repository.
2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Run the application:
```bash
python3 main.py
```

### Data Storage

Photos remain in their original locations and are not copied or modified by *flarepick*.

The SQLite database stores only collections and references to marked photos (picked or rejected).

### Libraries
- PyQt6 - GUI
- sqlite3 - Database
