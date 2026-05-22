# Character Counter

A simple Python script to count characters, words, sentences, lines, paragraphs, and estimated pages. Works in both GUI (Tkinter) and terminal modes.

## Usage

### GUI Mode
Run the script with no arguments to open the GUI:
```bash
python3 src/main.py
```

### CLI Mode
Run with `--cli` or `-c` to use in the terminal:
```bash
python3 src/main.py --cli
```

You can also analyze a file by passing its path:
```bash
python3 src/main.py path/to/file.txt
```

Or pipe text directly:
```bash
echo "some text" | python3 src/main.py
```

## Requirements
- Python 3
- Tkinter
