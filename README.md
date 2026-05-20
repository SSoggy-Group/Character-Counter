# Text Analyzer & Character Counter

A clean, modern, and efficient Python application to analyze text metrics. It provides real-time counts for characters, words, sentences, lines, and paragraphs, and estimates A4 page counts using standard page size models.

The application includes both an interactive Graphical User Interface (GUI) and a scriptable Command Line Interface (CLI).

## Features

- **Real-Time Analysis (GUI):** Results update dynamically as you type.
- **Multiple Estimation Models:** Supports words-based (250 words/page) and character-based (3300 characters/page) page calculations.
- **Utility Tools:** Quick actions to copy report results to the clipboard and clear input.
- **Flexible Modes:** Launch the modern graphical application or use standard terminal mode.
- **File & Pipeline Support (CLI):** Directly analyze files or pipe text streams from standard input.

## Getting Started

### Prerequisites

- Python 3.x
- Tkinter library (usually bundled with Python on Windows/macOS. For Linux/macOS Homebrew installations, ensure standard GUI modules are installed).

### Running the Application

#### 1. Graphical User Interface (GUI)
Simply run the script with no arguments to launch the GUI:
```bash
python3 src/main.py
```

#### 2. Command Line Interface (CLI)
For pipeline processing or terminal usage, run with the `--cli` or `-c` flag:

**Interactive mode:**
```bash
python3 src/main.py --cli
```

**Analyze a file directly:**
```bash
python3 src/main.py [path_to_file]
```

**Pipe output from another tool:**
```bash
echo "Hello, world!" | python3 src/main.py
```

## Structure
- [main.py](file:///Users/maaren/Character-Counter/src/main.py): Unified entrypoint containing GUI layout, CLI routing, and core text parsing logic.
- [LICENSE](file:///Users/maaren/Character-Counter/LICENSE): MIT License details.
