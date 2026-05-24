#!/usr/bin/env python3
import sys
import re
import math
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def analyzeText(text):
    if not text:
        return {
            "characters": 0,
            "words": 0,
            "characters_no_spaces": 0,
            "sentences": 0,
            "lines": 0,
            "paragraphs": 0,
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
    
    return {
        "characters": charCount,
        "words": wordCount,
        "characters_no_spaces": charNoSpaces,
        "sentences": sentenceCount,
        "lines": lineCount,
        "paragraphs": paragraphCount,
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

def runCli(filePath=None):
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
    
    print(f"characters: {metrics['characters']}")
    print(f"characters (no spaces): {metrics['characters_no_spaces']}")
    print(f"words: {metrics['words']}")
    print(f"sentences: {metrics['sentences']}")
    print(f"lines: {metrics['lines']}")
    print(f"paragraphs: {metrics['paragraphs']}")
    print(f"pages (250 words/pg): {pagesWord}")
    print(f"pages (3300 chars/pg): {pagesChar}")

def main():
    parser = argparse.ArgumentParser(description="text character and word counter")
    parser.add_argument("--cli", "-c", action="store_true")
    parser.add_argument("file", nargs="?", type=str)
    args = parser.parse_args()

    if args.cli or args.file or not sys.stdin.isatty():
        runCli(args.file)
    else:
        root = tk.Tk()
        app = TextCounterGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
