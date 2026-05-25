#!/usr/bin/env python3
import sys
import re
import math
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import Counter
import json

STOPWORDS = {
    "the", "and", "a", "of", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on", 
    "are", "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", 
    "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", 
    "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if", "will", 
    "up", "other", "about", "out", "many", "then", "them", "these", "so", "some", "her", "would", 
    "make", "like", "him", "into", "has", "look", "two", "more", "write", "go", "see", "number", 
    "no", "way", "could", "people", "my", "than", "first", "water", "been", "call", "who", "oil", 
    "its", "now", "find", "long", "down", "day", "did", "get", "come", "made", "may", "part"
}

def countSyllablesInWord(word):
    word = word.lower().strip(",.?!:;()\"'-")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    if word.endswith('e') and not word.endswith('le'):
        count -= 1
    return max(1, count)

def calculateReadability(wordCount, sentenceCount, syllableCount):
    if wordCount == 0 or sentenceCount == 0:
        return 100.0, 0.0
    ease = 206.835 - 1.015 * (wordCount / sentenceCount) - 84.6 * (syllableCount / wordCount)
    grade = 0.39 * (wordCount / sentenceCount) + 11.8 * (syllableCount / wordCount) - 15.59
    return max(0.0, min(100.0, ease)), max(0.0, grade)

def getReadabilityInterpretation(ease):
    if ease >= 90:
        return "very easy (5th grade)"
    elif ease >= 80:
        return "easy (6th grade)"
    elif ease >= 70:
        return "fairly easy (7th grade)"
    elif ease >= 60:
        return "standard (8th-9th grade)"
    elif ease >= 50:
        return "fairly difficult (high school)"
    elif ease >= 30:
        return "difficult (college)"
    else:
        return "very difficult (college grad)"

def getKeywords(text, top_n=5):
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    content_words = [w for w in words if w not in STOPWORDS]
    if not content_words:
        return []
    counter = Counter(content_words)
    total_words = len(words)
    top = counter.most_common(top_n)
    return [(w, count, (count / total_words) * 100 if total_words > 0 else 0.0) for w, count in top]

def getCharacterDistribution(text, top_n=8):
    chars = [c.lower() for c in text if c.isalnum()]
    if not chars:
        return []
    counter = Counter(chars)
    total_chars = len(chars)
    top = counter.most_common(top_n)
    return [(c, count, (count / total_chars) * 100 if total_chars > 0 else 0.0) for c, count in top]

def countPatternOccurrences(text, pattern, is_regex=False):
    if not pattern:
        return 0
    try:
        if is_regex:
            return len(re.findall(pattern, text, re.IGNORECASE))
        else:
            return text.lower().count(pattern.lower())
    except Exception:
        return 0

def formatTime(minutes):
    if minutes <= 0:
        return "0s"
    total_seconds = int(round(minutes * 60))
    mins = total_seconds // 60
    secs = total_seconds % 60
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"

def analyzeText(text):
    if not text:
        return {
            "characters": 0,
            "words": 0,
            "characters_no_spaces": 0,
            "sentences": 0,
            "lines": 0,
            "paragraphs": 0,
            "syllables": 0,
            "readability_ease": 100.0,
            "readability_grade": 0.0,
            "reading_time": 0.0,
            "speaking_time": 0.0,
            "keywords": [],
            "char_dist": []
        }
    
    charCount = len(text)
    words = text.split()
    wordCount = len(words)
    charNoSpaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
    lines = text.splitlines()
    lineCount = len(lines)
    
    sentences = re.split(r'[.!?]', text)
    sentenceCount = len([s for s in sentences if s.strip()])
    
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraphCount = len(paragraphs)
    
    word_tokens = re.findall(r'\b[a-zA-Z\']+\b', text)
    syllableCount = sum(countSyllablesInWord(w) for w in word_tokens)
    
    ease, grade = calculateReadability(wordCount, sentenceCount, syllableCount)
    reading_time = wordCount / 200.0
    speaking_time = wordCount / 130.0
    
    keywords = getKeywords(text)
    char_dist = getCharacterDistribution(text)
    
    return {
        "characters": charCount,
        "words": wordCount,
        "characters_no_spaces": charNoSpaces,
        "sentences": sentenceCount,
        "lines": lineCount,
        "paragraphs": paragraphCount,
        "syllables": syllableCount,
        "readability_ease": ease,
        "readability_grade": grade,
        "reading_time": reading_time,
        "speaking_time": speaking_time,
        "keywords": keywords,
        "char_dist": char_dist
    }

def calculatePages(wordCount, characterCount, model):
    if model == "words":
        return math.ceil(wordCount / 250) if wordCount > 0 else 0
    elif model == "characters":
        return math.ceil(characterCount / 3300) if characterCount > 0 else 0
    return 0

class TextCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("character counter")
        self.root.geometry("600x520")
        self.root.minsize(500, 400)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('Helvetica', 10))
        style.configure('TFrame', background='#f5f6f8')
        style.configure('Card.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'), foreground='#2c3e50', background='#f5f6f8')
        style.configure('MetricName.TLabel', font=('Helvetica', 9), foreground='#7f8c8d', background='#ffffff')
        style.configure('MetricValue.TLabel', font=('Helvetica', 12, 'bold'), foreground='#2980b9', background='#ffffff')
        
        self.mainFrame = ttk.Frame(self.root, padding=15, style='TFrame')
        self.mainFrame.grid(row=0, column=0, sticky='nsew')
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(1, weight=1)
        
        self.headerFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.headerFrame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        self.titleLabel = ttk.Label(self.headerFrame, text="character counter", style='Title.TLabel')
        self.titleLabel.pack(anchor='w')
        
        self.textFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.textFrame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        self.textFrame.columnconfigure(0, weight=1)
        self.textFrame.rowconfigure(0, weight=1)
        
        self.textInput = scrolledtext.ScrolledText(
            self.textFrame, wrap=tk.WORD, font=('Courier New', 11),
            bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50',
            bd=1, relief='solid', padx=5, pady=5
        )
        self.textInput.grid(row=0, column=0, sticky='nsew')
        self.textInput.focus_set()
        
        self.textInput.bind('<<Modified>>', self.onTextModified)
        self.textInput.bind('<KeyRelease>', self.onKeyRelease)
        
        self.controlsFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.controlsFrame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(self.controlsFrame, text="page model:", background='#f5f6f8').pack(side=tk.LEFT, padx=(0, 5))
        
        self.pageModelVar = tk.StringVar(value="words-based (250/pg)")
        self.pageModelCombo = ttk.Combobox(
            self.controlsFrame, textvariable=self.pageModelVar, 
            values=["words-based (250/pg)", "characters-based (3300/pg)"],
            state="readonly", width=25
        )
        self.pageModelCombo.pack(side=tk.LEFT, padx=5)
        self.pageModelCombo.bind("<<ComboboxSelected>>", lambda e: self.updateAnalysis())
        
        self.clearBtn = ttk.Button(self.controlsFrame, text="clear", command=self.clearText)
        self.clearBtn.pack(side=tk.RIGHT, padx=5)
        
        self.copyBtn = ttk.Button(self.controlsFrame, text="copy", command=self.copyResults)
        self.copyBtn.pack(side=tk.RIGHT, padx=5)
        
        self.resultsFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.resultsFrame.grid(row=3, column=0, sticky='ew')
        
        for col in range(4):
            self.resultsFrame.columnconfigure(col, weight=1, uniform="equal")
            
        self.metricCards = {}
        metricsLayout = [
            ("characters", 0, 0),
            ("words", 0, 1),
            ("char (no spaces)", 0, 2),
            ("sentences", 0, 3),
            ("lines", 1, 0),
            ("paragraphs", 1, 1),
            ("est. pages", 1, 2)
        ]
        
        for name, row, col in metricsLayout:
            card = ttk.Frame(self.resultsFrame, style='Card.TFrame', padding=8)
            span = 2 if name == "est. pages" else 1
            card.grid(row=row, column=col, columnspan=span, padx=3, pady=3, sticky='nsew')
            
            nameLbl = ttk.Label(card, text=name, style='MetricName.TLabel')
            nameLbl.pack(anchor='w')
            
            valLbl = ttk.Label(card, text="0", style='MetricValue.TLabel')
            valLbl.pack(anchor='w', pady=(2, 0))
            
            self.metricCards[name] = valLbl
            
        self.updateAnalysis()

    def onTextModified(self, event):
        self.textInput.edit_modified(False)
        self.updateAnalysis()

    def onKeyRelease(self, event):
        self.updateAnalysis()

    def updateAnalysis(self):
        text = self.textInput.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyzeText(text)
        
        modelStr = self.pageModelVar.get()
        modelKey = "words" if "words" in modelStr else "characters"
        pages = calculatePages(metrics["words"], metrics["characters"], modelKey)
        
        self.metricCards["characters"].config(text=str(metrics["characters"]))
        self.metricCards["words"].config(text=str(metrics["words"]))
        self.metricCards["char (no spaces)"].config(text=str(metrics["characters_no_spaces"]))
        self.metricCards["sentences"].config(text=str(metrics["sentences"]))
        self.metricCards["lines"].config(text=str(metrics["lines"]))
        self.metricCards["paragraphs"].config(text=str(metrics["paragraphs"]))
        self.metricCards["est. pages"].config(text=str(pages))

    def clearText(self):
        self.textInput.delete("1.0", tk.END)
        self.updateAnalysis()
        self.textInput.focus_set()

    def copyResults(self):
        text = self.textInput.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyzeText(text)
        modelStr = self.pageModelVar.get()
        modelKey = "words" if "words" in modelStr else "characters"
        pages = calculatePages(metrics["words"], metrics["characters"], modelKey)
        
        report = (
            f"characters: {metrics['characters']}\n"
            f"characters (no spaces): {metrics['characters_no_spaces']}\n"
            f"words: {metrics['words']}\n"
            f"sentences: {metrics['sentences']}\n"
            f"lines: {metrics['lines']}\n"
            f"paragraphs: {metrics['paragraphs']}\n"
            f"est. pages ({modelStr}): {pages}"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        messagebox.showinfo("success", "report copied to clipboard")

def runCli(filePath=None, args=None):
    text = ""
    if filePath:
        try:
            with open(filePath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("enter text (ctrl+d / ctrl+z to finish):")
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\ncancelled")
            sys.exit(0)
            
    metrics = analyzeText(text)
    pagesWord = calculatePages(metrics["words"], metrics["characters"], "words")
    pagesChar = calculatePages(metrics["words"], metrics["characters"], "characters")
    
    queryCount = 0
    if args and args.query:
        queryCount = countPatternOccurrences(text, args.query, is_regex=args.regex)
        
    if args and args.json:
        out_dict = {
            "characters": metrics["characters"],
            "characters_no_spaces": metrics["characters_no_spaces"],
            "words": metrics["words"],
            "sentences": metrics["sentences"],
            "lines": metrics["lines"],
            "paragraphs": metrics["paragraphs"],
            "pages_words_based": pagesWord,
            "pages_chars_based": pagesChar,
            "syllables": metrics["syllables"],
            "readability": {
                "ease_score": round(metrics["readability_ease"], 2),
                "grade_level": round(metrics["readability_grade"], 2),
                "interpretation": getReadabilityInterpretation(metrics["readability_ease"])
            },
            "estimated_time": {
                "reading": formatTime(metrics["reading_time"]),
                "speaking": formatTime(metrics["speaking_time"])
            },
            "top_keywords": [{"word": w, "count": cnt, "density_pct": round(pct, 2)} for w, cnt, pct in metrics["keywords"]],
            "top_characters": [{"char": c, "count": cnt, "density_pct": round(pct, 2)} for c, cnt, pct in metrics["char_dist"]]
        }
        if args.query:
            out_dict["query_matches"] = {
                "query": args.query,
                "count": queryCount,
                "is_regex": args.regex
            }
        print(json.dumps(out_dict, indent=2))
    else:
        active_filters = False
        if args:
            if args.words or args.chars or args.chars_no_spaces or args.lines or args.sentences or args.paragraphs or args.readability or args.query is not None:
                active_filters = True
                
        if active_filters:
            if args.chars:
                print(f"characters: {metrics['characters']}")
            if args.chars_no_spaces:
                print(f"characters (no spaces): {metrics['characters_no_spaces']}")
            if args.words:
                print(f"words: {metrics['words']}")
            if args.sentences:
                print(f"sentences: {metrics['sentences']}")
            if args.lines:
                print(f"lines: {metrics['lines']}")
            if args.paragraphs:
                print(f"paragraphs: {metrics['paragraphs']}")
            if args.readability:
                print(f"readability ease: {round(metrics['readability_ease'], 2)} ({getReadabilityInterpretation(metrics['readability_ease'])})")
                print(f"readability grade: {round(metrics['readability_grade'], 2)}")
            if args.query is not None:
                print(f"query matches ('{args.query}'): {queryCount}")
        else:
            print(f"characters: {metrics['characters']}")
            print(f"characters (no spaces): {metrics['characters_no_spaces']}")
            print(f"words: {metrics['words']}")
            print(f"sentences: {metrics['sentences']}")
            print(f"lines: {metrics['lines']}")
            print(f"paragraphs: {metrics['paragraphs']}")
            print(f"pages (250 words/pg): {pagesWord}")
            print(f"pages (3300 chars/pg): {pagesChar}")
            print(f"readability ease: {round(metrics['readability_ease'], 2)} ({getReadabilityInterpretation(metrics['readability_ease'])})")
            print(f"readability grade: {round(metrics['readability_grade'], 2)}")
            print(f"reading time: {formatTime(metrics['reading_time'])}")
            print(f"speaking time: {formatTime(metrics['speaking_time'])}")
            if metrics["keywords"]:
                k_str = ", ".join([f"{w} ({cnt})" for w, cnt, _ in metrics["keywords"]])
                print(f"top keywords: {k_str}")

def main():
    parser = argparse.ArgumentParser(description="text character and word counter")
    parser.add_argument("--cli", "-c", action="store_true", help="force cli mode")
    parser.add_argument("file", nargs="?", type=str, help="file to analyze")
    parser.add_argument("--json", "-j", action="store_true", help="output in json format")
    parser.add_argument("--words", "-w", action="store_true", help="output word count only")
    parser.add_argument("--chars", action="store_true", help="output character count only (with spaces)")
    parser.add_argument("--chars-no-spaces", action="store_true", help="output character count only (without spaces)")
    parser.add_argument("--lines", "-l", action="store_true", help="output line count only")
    parser.add_argument("--sentences", "-s", action="store_true", help="output sentence count only")
    parser.add_argument("--paragraphs", "-p", action="store_true", help="output paragraph count only")
    parser.add_argument("--readability", "-r", action="store_true", help="output readability metrics only")
    parser.add_argument("--query", "-q", type=str, default=None, help="pattern or word to count")
    parser.add_argument("--regex", action="store_true", help="treat query as a regular expression")
    
    args = parser.parse_args()

    if args.cli or args.file or not sys.stdin.isatty():
        runCli(args.file, args)
    else:
        root = tk.Tk()
        app = TextCounterGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
