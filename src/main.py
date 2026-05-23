#!/usr/bin/env python3
import sys
import re
import math
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def analyze_text(text):
    if not text:
        return {
            "characters": 0,
            "words": 0,
            "characters_no_spaces": 0,
            "sentences": 0,
            "lines": 0,
            "paragraphs": 0,
        }
    
    char_count = len(text)
    words = text.split()
    word_count = len(words)
    char_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
    lines = text.splitlines()
    line_count = len(lines)
    
    sentences = re.split(r'[.!?]', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_count = len(paragraphs)
    
    return {
        "characters": char_count,
        "words": word_count,
        "characters_no_spaces": char_no_spaces,
        "sentences": sentence_count,
        "lines": line_count,
        "paragraphs": paragraph_count,
    }

def calculate_pages(word_count, character_count, model):
    if model == "words":
        return math.ceil(word_count / 250) if word_count > 0 else 0
    elif model == "characters":
        return math.ceil(character_count / 3300) if character_count > 0 else 0
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
        
        self.main_frame = ttk.Frame(self.root, padding=15, style='TFrame')
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        self.header_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        self.title_label = ttk.Label(self.header_frame, text="character counter", style='Title.TLabel')
        self.title_label.pack(anchor='w')
        
        self.text_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.text_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(
            self.text_frame, wrap=tk.WORD, font=('Courier New', 11),
            bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50',
            bd=1, relief='solid', padx=5, pady=5
        )
        self.text_input.grid(row=0, column=0, sticky='nsew')
        self.text_input.focus_set()
        
        self.text_input.bind('<<Modified>>', self.on_text_modified)
        self.text_input.bind('<KeyRelease>', self.on_key_release)
        
        self.controls_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.controls_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(self.controls_frame, text="page model:", background='#f5f6f8').pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_model_var = tk.StringVar(value="words-based (250/pg)")
        self.page_model_combo = ttk.Combobox(
            self.controls_frame, textvariable=self.page_model_var, 
            values=["words-based (250/pg)", "characters-based (3300/pg)"],
            state="readonly", width=25
        )
        self.page_model_combo.pack(side=tk.LEFT, padx=5)
        self.page_model_combo.bind("<<ComboboxSelected>>", lambda e: self.update_analysis())
        
        self.clear_btn = ttk.Button(self.controls_frame, text="clear", command=self.clear_text)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        self.copy_btn = ttk.Button(self.controls_frame, text="copy", command=self.copy_results)
        self.copy_btn.pack(side=tk.RIGHT, padx=5)
        
        self.results_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.results_frame.grid(row=3, column=0, sticky='ew')
        
        for col in range(4):
            self.results_frame.columnconfigure(col, weight=1, uniform="equal")
            
        self.metric_cards = {}
        metrics_layout = [
            ("characters", 0, 0),
            ("words", 0, 1),
            ("char (no spaces)", 0, 2),
            ("sentences", 0, 3),
            ("lines", 1, 0),
            ("paragraphs", 1, 1),
            ("est. pages", 1, 2)
        ]
        
        for name, row, col in metrics_layout:
            card = ttk.Frame(self.results_frame, style='Card.TFrame', padding=8)
            span = 2 if name == "est. pages" else 1
            card.grid(row=row, column=col, columnspan=span, padx=3, pady=3, sticky='nsew')
            
            name_lbl = ttk.Label(card, text=name, style='MetricName.TLabel')
            name_lbl.pack(anchor='w')
            
            val_lbl = ttk.Label(card, text="0", style='MetricValue.TLabel')
            val_lbl.pack(anchor='w', pady=(2, 0))
            
            self.metric_cards[name] = val_lbl

        self.update_analysis()

    def on_text_modified(self, event):
        self.text_input.edit_modified(False)
        self.update_analysis()

    def on_key_release(self, event):
        self.update_analysis()

    def update_analysis(self):
        text = self.text_input.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyze_text(text)
        
        model_str = self.page_model_var.get()
        model_key = "words" if "words" in model_str else "characters"
        pages = calculate_pages(metrics["words"], metrics["characters"], model_key)
        
        self.metric_cards["characters"].config(text=str(metrics["characters"]))
        self.metric_cards["words"].config(text=str(metrics["words"]))
        self.metric_cards["char (no spaces)"].config(text=str(metrics["characters_no_spaces"]))
        self.metric_cards["sentences"].config(text=str(metrics["sentences"]))
        self.metric_cards["lines"].config(text=str(metrics["lines"]))
        self.metric_cards["paragraphs"].config(text=str(metrics["paragraphs"]))
        self.metric_cards["est. pages"].config(text=str(pages))

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.update_analysis()
        self.text_input.focus_set()

    def copy_results(self):
        text = self.text_input.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyze_text(text)
        model_str = self.page_model_var.get()
        model_key = "words" if "words" in model_str else "characters"
        pages = calculate_pages(metrics["words"], metrics["characters"], model_key)
        
        report = (
            f"characters: {metrics['characters']}\n"
            f"characters (no spaces): {metrics['characters_no_spaces']}\n"
            f"words: {metrics['words']}\n"
            f"sentences: {metrics['sentences']}\n"
            f"lines: {metrics['lines']}\n"
            f"paragraphs: {metrics['paragraphs']}\n"
            f"est. pages ({model_str}): {pages}"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        messagebox.showinfo("success", "report copied to clipboard")

def run_cli(file_path=None):
    text = ""
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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
            
    metrics = analyze_text(text)
    pages_word = calculate_pages(metrics["words"], metrics["characters"], "words")
    pages_char = calculate_pages(metrics["words"], metrics["characters"], "characters")
    
    print(f"characters: {metrics['characters']}")
    print(f"characters (no spaces): {metrics['characters_no_spaces']}")
    print(f"words: {metrics['words']}")
    print(f"sentences: {metrics['sentences']}")
    print(f"lines: {metrics['lines']}")
    print(f"paragraphs: {metrics['paragraphs']}")
    print(f"pages (250 words/pg): {pages_word}")
    print(f"pages (3300 chars/pg): {pages_char}")

def main():
    parser = argparse.ArgumentParser(description="text character and word counter")
    parser.add_argument("--cli", "-c", action="store_true")
    parser.add_argument("file", nargs="?", type=str)
    args = parser.parse_args()

    if args.cli or args.file or not sys.stdin.isatty():
        run_cli(args.file)
    else:
        root = tk.Tk()
        app = TextCounterGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
