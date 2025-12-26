# Smart File Organizer

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**The Foundation** — An intelligent, automated agent designed to reclaim order within your file system.  
Built with **Clean Architecture** principles and a *Safety First* philosophy.

---

## 🚀 Key Features

- **🛡️ Safety by Default**  
  Always runs in **Dry Run** mode (simulation) unless explicitly authorized to write to disk.

- **🧠 Intelligent Deduplication**  
  Uses a multi-stage filtering pipeline (Size → Buffered SHA256) to identify duplicates without exhausting RAM.

- **⚡ Parallel Processing**  
  Leverages multi-core CPUs for high-speed file hashing.

- **🏗️ Clean Architecture**  
  Core business logic is completely decoupled from the file system, ensuring stability and testability.

- **🔧 Zero-Dependency Runtime**  
  The core application runs using only the Python Standard Library (`os`, `shutil`, `pathlib`, `hashlib`).

---

## 📦 Installation

### Option A: Standard Installation

Ensure you have **Python 3.10+** installed.

```bash
git clone https://github.com/RoswellCityUK/SmartFileOrganizer.git
cd SmartFileOrganizer
pip install -e .
```

You can now use the `smart-organizer` command globally.

### Option B: Dev Container (Recommended for Development)

This project is configured with a **VS Code Dev Container**, providing a fully reproducible environment with all tools pre-installed (`black`, `mypy`, `pytest`).

1. Open the project folder in VS Code  
2. Click **“Reopen in Container”** when prompted (or use the Command Palette `F1`)  
3. The environment will build automatically  

---

## 🛠️ Usage

The tool operates via a **Command Line Interface (CLI)**.  
All commands default to **Dry Run** mode.

### 1. Scan a Directory

Get a quick report of file counts and total size.

```bash
smart-organizer scan --root /path/to/downloads
```

### 2. Find Duplicates

Identify wasted space using cryptographic hashing.

```bash
smart-organizer dedupe --root /path/to/documents
```

### 3. Organize Files

Sort files into folders. Supports sorting by **Extension** (default) or **Date**.

#### Simulation (Safe)

```bash
smart-organizer organize --root /path/to/files --by-date
```

Outputs proposed moves to the console without touching files.

#### Execution (Live)

```bash
smart-organizer organize --root /path/to/files --by-date --execute
```

> **Note:** You will be prompted to confirm before any action is taken.

#### Options

- `--by-ext` — Sort into folders like `JPG/`, `PDF/`, `DOCX/`
- `--by-date` — Sort into `YYYY/MM/` based on modification time
- `--cleanup` — Remove empty directories after moving files

---

## 👨‍💻 Development Workflow

This project uses a **Makefile** to standardize common development tasks.

| Command        | Description                                                   |
|----------------|---------------------------------------------------------------|
| `make install` | Install the package and all dev dependencies                  |
| `make test`    | Run the test suite with coverage reporting                    |
| `make lint`    | Run static analysis (MyPy) and pre-commit checks              |
| `make format`  | Auto-format code using Black                                  |
| `make clean`   | Remove build artifacts and cache files                        |

### Running Tests

The project enforces **100% code coverage** (at least trying too... currently 97%).

```bash
make test
```

### Pre-commit Hooks

Git hooks ensure code quality. They run automatically on `git commit`, but can also be run manually:

```bash
pre-commit run --all-files
```

---

## 🏗️ Architecture

The codebase follows **Clean Architecture** principles:

- **Domain (Core)**  
  Entities (`FileNode`) and rules (`OrganizationRule`). Zero dependencies.

- **Use Cases**  
  Application logic (`Organizer`, `DuplicateFinder`, `Scanner`).

- **Infrastructure**  
  Implementation details (`RealFileSystem`, `DryRunFileSystem`, `HashService`).

- **CLI**  
  Interface adapters (`argparse`, `logging`).

### Dependency Injection

The `ServiceContainer` wires these layers together.  
It injects the `DryRunFileSystem` by default, ensuring **Safe Mode** is physically incapable of writing to disk—write methods are virtual mocks.
