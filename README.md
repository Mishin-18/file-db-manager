# File DB Manager

[![GitHub release](https://img.shields.io/badge/release-v1.1.0-blue.svg)](https://github.com/Mishin-18/file-db-manager/releases/tag/v1.1.0)

🇷🇺 [Русская версия](README.ru.md)

A professional file indexing and management tool with SQLite backend.  
Scan folders, track files, verify path lists against the database, and resolve ambiguities manually.

---

## ✨ Features

- 📁 **File indexing in SQLite** (name, path, size, hash, modification time)
- 📂 **Scan one folder or multiple non-nested folders** into a single database
- 🔄 **Incremental database updates** without a full rebuild
- 🔍 **Fuzzy search** with Unicode normalization
- 📊 **Path list comparison** from clipboard, TXT, and Excel
- 🎯 **Three statuses**: `FOUND` / `MISSING` / `AMBIGUOUS`
- 🌐 **UI with 6 languages** and live language switching
- 🇨🇭 **Includes German, French, Italian, and Romansh support** relevant to Switzerland
- 📈 **Expanded progress window** with total file count, processed/total view, percentage, and progress bar
- 🖥️ **Windows integration** — "Show in folder" with file highlighting (Win10/Win11)
- 🧪 **Automated tests with pytest** — current local status: **12 passed**

---

## 🧱 Project evolution

This repository shows the project evolution across three stages:

1. **Original monolith**  
   The initial working single-file implementation of the application.

2. **Prepared monolith**  
   A transitional single-file version reorganized for a safer future split into modules.

3. **Modular version**  
   A refactored multi-module architecture representing the next stage of the project.

### Why this matters

The goal was not only to add features, but also to improve the internal structure of the project step by step.

This evolution demonstrates:
- preservation of the original working implementation
- an intermediate refactoring stage instead of a risky full rewrite
- transition to a modular architecture
- cleaner test organization
- continued focus on maintainability and project clarity

---

## 📁 Project structure

- `file_db_manager.py` — original monolithic version
- `prepared_monolith_for_split.py` — transitional monolithic version prepared for future modular split
- `modular_version/` — modular version of the application
- `tests/` — automated test suite
- `screenshots/` — application screenshots

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher

### Installation

```bash
git clone https://github.com/Mishin-18/file-db-manager.git
cd file-db-manager
pip install -r requirements.txt
```

### Run the original monolith

```bash
python file_db_manager.py
```

### Run the modular version

```bash
python modular_version/main.py
```

### Run tests

```bash
python -m pytest -q
```

---

## 📦 Release

Latest release: **File DB Manager 1.1.0**

Windows executable:
- `File_DB_Manager_v1.1_Win_11.10.exe`

---

## 📜 License

MIT License.
