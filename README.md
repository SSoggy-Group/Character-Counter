# character counter

a simple python script to count characters, words, sentences, lines, paragraphs, and estimated pages. works in both gui (tkinter) and terminal modes.

## usage

### gui mode
run the script with no arguments to open the gui:
```bash
python3 src/main.py
```

### cli mode
run with `--cli` or `-c` to use in the terminal:
```bash
python3 src/main.py --cli
```

you can also analyze a file by passing its path:
```bash
python3 src/main.py path/to/file.txt
```

or pipe text directly:
```bash
echo "some text" | python3 src/main.py
```

## requirements
- python 3
- tkinter
