# File DB Manager

[![GitHub release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://github.com/Mishin-18/file-db-manager/releases/tag/v1.0.0)

🇷🇺 [Русская версия](README.ru.md)

A professional file indexing and management tool with SQLite backend.  
Scan folders, track files, verify lists against database, and resolve ambiguities manually.

---

## ✨ Features

- 📁 **Full-text file index** in SQLite (name, path, size, hash, modification time)
- 🔍 **Fuzzy search** with Unicode normalization (works with Cyrillic, accents, etc.)
- 📊 **Set management** — compare any path list (clipboard/TXT/Excel) against database
- 🎯 **Three statuses**: `FOUND` / `MISSING` / `AMBIGUOUS`
- 🌐 **Bilingual UI** (English/Russian) with live language switching
- ⚡ **Incremental updates** — no full rescan needed
- 🖥️ **Windows integration** — "Show in folder" with file highlighting (Win10/Win11)
- 🧪 **Comprehensive test suite** with pytest (8 tests, core logic covered)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Mishin-18/file-db-manager.git
cd file-db-manager

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python file_db_manager.py
