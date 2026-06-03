# character counter

a cool python script and desktop utility to count characters, words, sentences, lines, paragraphs, and estimated pages. features a rich, multi-tab tkinter gui with advanced text metrics and full cli support.

install it with
```
pip install character-counter-maaren
```
and run with 
```
charcount
```
or download the .py file from github releases 
## features

### 1. advanced text metrics
- **readability indices:** flesch reading ease & flesch-kincaid grade level with educational grade interpretations.
- **speech & timing estimates:** reading time (at 200 wpm) and speaking time (at 130 wpm) formatted nicely.
- **keyword density analysis:** lists top 5 content-bearing keywords (excluding common english stopwords).
- **character frequency distribution:** tracks the most frequently used alphanumeric characters.

### 2. redesigned gui (tkinter)
- **multi-tab notebook layout:**
  - **overview:** standard grid of layout cards showing basic counts and page estimations.
  - **readability & timing:** detailed cards for reading ease levels and verbal/silent time tracking.
  - **keywords:** lists the top keywords side-by-side with a dynamic, custom canvas-drawn density bar chart.
  - **character frequency:** displays top characters side-by-side with a dynamic frequency bar chart.
- **dark mode toggle:** instantly switch between high-contrast light and low-strain dark themes.
- **text formatting toolbar:** selection-aware uppercase, lowercase, title case, sentence case, and whitespace cleaning converters.

### 3. command-line interface
- **json formatting:** output all metrics as structured json using `--json` or `-j`.
- **specific metric filtering:** filter output to print only words, characters, readability, or sentences.
- **regex querying:** search for and count custom strings or regular expressions via `--query` / `-q`.

---

## usage

### gui mode
run the script with no arguments to open the gui:
```bash
python3 src/main.py
```

### cli mode
run with `--cli` or `-c` to force use in the terminal:
```bash
python3 src/main.py --cli
```

#### examples:
- **analyze a file:**
  ```bash
  python3 src/main.py path/to/file.txt
  ```
- **pipe text directly:**
  ```bash
  echo "some text to analyze" | python3 src/main.py
  ```
- **get json output:**
  ```bash
  python3 src/main.py --json path/to/file.txt
  ```
- **extract only specific metrics (e.g. words & lines):**
  ```bash
  python3 src/main.py --words --lines path/to/file.txt
  ```
- **count regex pattern occurrences:**
  ```bash
  python3 src/main.py --query "[a-z]+ing" --regex path/to/file.txt
  ```

---

## requirements
- python 3
- tkinter (built-in)
- collections, json, math, re, argparse (built-in standard library)
