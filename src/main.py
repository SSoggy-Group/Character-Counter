#!/usr/bin/env python3
"""
Professional Text and Character Counter
Consolidates previous versions into a unified CLI and GUI interface.
"""

import sys
import re
import math
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def analyze_text(text):
    """
    Analyzes the input text and returns a dictionary of metrics.
    Handles empty text gracefully.
    """
    if not text:
        return {
            "characters": 0,
            "words": 0,
            "characters_no_spaces": 0,
            "sentences": 0,
            "lines": 0,
            "paragraphs": 0,
        }
    
    character_count = len(text)
    words = text.split()
    word_count = len(words)
    # Exclude spaces and newline characters
    character_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
    lines = text.splitlines()
    line_count = len(lines)
    sentences = re.split(r'[.!?]', text)
    sentence_count = len([s for s in sentences if s.strip()])
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_count = len(paragraphs)
    
    return {
        "characters": character_count,
        "words": word_count,
        "characters_no_spaces": character_count_no_spaces,
        "sentences": sentence_count,
        "lines": line_count,
        "paragraphs": paragraph_count,
    }

def calculate_pages(word_count, character_count, model):
    """
    Calculates estimated A4 pages based on word or character count models.
    """
    if model == "words":
        # Standard: 250 words per page
        return math.ceil(word_count / 250) if word_count > 0 else 0
    elif model == "characters":
        # Standard: 3300 characters per page
        return math.ceil(character_count / 3300) if character_count > 0 else 0
    return 0

class TextCounterGUI:
    """
    Tkinter graphical interface featuring modern styling, real-time live counting,
    clearing, and result copying utilities.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Text Analyzer & Character Counter")
        self.root.geometry("620x580")
        self.root.minsize(580, 500)
        
        # Configure grid expansion
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Modern color palette & style settings
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('.', font=('Helvetica', 10))
        self.style.configure('TFrame', background='#f5f6f8')
        self.style.configure('Card.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'), foreground='#2c3e50', background='#f5f6f8')
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 9), foreground='#7f8c8d', background='#f5f6f8')
        self.style.configure('MetricName.TLabel', font=('Helvetica', 10, 'bold'), foreground='#34495e', background='#ffffff')
        self.style.configure('MetricValue.TLabel', font=('Helvetica', 14, 'bold'), foreground='#2980b9', background='#ffffff')
        self.style.configure('Action.TButton', font=('Helvetica', 10, 'bold'))
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding=20, style='TFrame')
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Header Section
        self.header_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        self.title_label = ttk.Label(self.header_frame, text="Text Analyzer & Character Counter", style='Title.TLabel')
        self.title_label.pack(anchor='w')
        self.sub_label = ttk.Label(self.header_frame, text="Enter or paste your text below for live analysis.", style='Subtitle.TLabel')
        self.sub_label.pack(anchor='w', pady=(2, 0))
        
        # Text Input Area
        self.text_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.text_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(
            self.text_frame, wrap=tk.WORD, font=('Courier New', 11),
            bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50',
            bd=1, relief='solid', padx=5, pady=5
        )
        self.text_input.grid(row=0, column=0, sticky='nsew')
        self.text_input.focus_set()
        
        # Bind events for live counting
        self.text_input.bind('<<Modified>>', self.on_text_modified)
        self.text_input.bind('<KeyRelease>', self.on_key_release)
        
        # Control & Calculation Parameters Frame
        self.controls_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.controls_frame.grid(row=2, column=0, sticky='ew', pady=(0, 15))
        
        ttk.Label(self.controls_frame, text="Page Estimation Model:", font=('Helvetica', 10), background='#f5f6f8').pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_model_var = tk.StringVar(value="Words-based (250 words/pg)")
        self.page_model_combo = ttk.Combobox(
            self.controls_frame, textvariable=self.page_model_var, 
            values=["Words-based (250 words/pg)", "Characters-based (3300 chars/pg)"],
            state="readonly", width=30
        )
        self.page_model_combo.pack(side=tk.LEFT, padx=5)
        self.page_model_combo.bind("<<ComboboxSelected>>", lambda e: self.update_analysis())
        
        self.clear_btn = ttk.Button(self.controls_frame, text="Clear Text", command=self.clear_text)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        self.copy_btn = ttk.Button(self.controls_frame, text="Copy Results", command=self.copy_results)
        self.copy_btn.pack(side=tk.RIGHT, padx=5)
        
        # Results Frame (Grid of metric cards)
        self.results_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.results_frame.grid(row=3, column=0, sticky='ew')
        
        # Configure columns for grid of metrics
        for col in range(4):
            self.results_frame.columnconfigure(col, weight=1, uniform="equal")
            
        self.metric_cards = {}
        metrics_layout = [
            ("Characters", 0, 0),
            ("Words", 0, 1),
            ("Char (no spaces)", 0, 2),
            ("Sentences", 0, 3),
            ("Lines", 1, 0),
            ("Paragraphs", 1, 1),
            ("Est. Pages", 1, 2)
        ]
        
        for name, row, col in metrics_layout:
            card = ttk.Frame(self.results_frame, style='Card.TFrame', padding=10)
            # Use span=2 for Est. Pages to make the grid look balanced
            column_span = 2 if name == "Est. Pages" else 1
            card.grid(row=row, column=col, columnspan=column_span, padx=4, pady=4, sticky='nsew')
            
            name_lbl = ttk.Label(card, text=name.upper(), style='MetricName.TLabel')
            name_lbl.pack(anchor='w')
            
            val_lbl = ttk.Label(card, text="0", style='MetricValue.TLabel')
            val_lbl.pack(anchor='w', pady=(4, 0))
            
            self.metric_cards[name] = val_lbl

        # Perform initial calculation
        self.update_analysis()

    def on_text_modified(self, event):
        """Triggers when text modification flag changes (pasting, code edits, etc.)."""
        # Reset the modification flag so subsequent modifications continue to trigger
        self.text_input.edit_modified(False)
        self.update_analysis()

    def on_key_release(self, event):
        """Triggers on standard keystrokes."""
        self.update_analysis()

    def update_analysis(self):
        """Computes metrics and updates GUI fields."""
        text = self.text_input.get("1.0", tk.END)
        # Tkinter adds a trailing newline, remove it for correct metrics
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyze_text(text)
        
        # Calculate Pages
        model_str = self.page_model_var.get()
        model_key = "words" if "Words-based" in model_str else "characters"
        pages = calculate_pages(metrics["words"], metrics["characters"], model_key)
        
        # Update values
        self.metric_cards["Characters"].config(text=str(metrics["characters"]))
        self.metric_cards["Words"].config(text=str(metrics["words"]))
        self.metric_cards["Char (no spaces)"].config(text=str(metrics["characters_no_spaces"]))
        self.metric_cards["Sentences"].config(text=str(metrics["sentences"]))
        self.metric_cards["Lines"].config(text=str(metrics["lines"]))
        self.metric_cards["Paragraphs"].config(text=str(metrics["paragraphs"]))
        self.metric_cards["Est. Pages"].config(text=str(pages))

    def clear_text(self):
        """Clears all text from input box."""
        self.text_input.delete("1.0", tk.END)
        self.update_analysis()
        self.text_input.focus_set()

    def copy_results(self):
        """Formats and copies the results output to clipboard."""
        text = self.text_input.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyze_text(text)
        model_str = self.page_model_var.get()
        model_key = "words" if "Words-based" in model_str else "characters"
        pages = calculate_pages(metrics["words"], metrics["characters"], model_key)
        
        report = (
            f"--- Text Analysis Report ---\n"
            f"Characters (with spaces): {metrics['characters']}\n"
            f"Characters (no spaces):   {metrics['characters_no_spaces']}\n"
            f"Words:                     {metrics['words']}\n"
            f"Sentences:                 {metrics['sentences']}\n"
            f"Lines:                     {metrics['lines']}\n"
            f"Paragraphs:                {metrics['paragraphs']}\n"
            f"Estimated Pages ({model_str}): {pages}\n"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        messagebox.showinfo("Success", "Analysis report copied to clipboard.")

def run_cli_mode(file_path=None):
    """
    Runs in Terminal command-line mode.
    Reads from a file, stdin, or interactive shell input.
    """
    text = ""
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Read from pipeline stdin (e.g. echo "hello" | python3 main.py)
        text = sys.stdin.read()
    else:
        # Interactive console prompts
        print("Text Character Counter CLI")
        print("Enter or paste your text. Press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter to finish:")
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)
            
    metrics = analyze_text(text)
    
    # Calculate both models for CLI report completeness
    pages_word = calculate_pages(metrics["words"], metrics["characters"], "words")
    pages_char = calculate_pages(metrics["words"], metrics["characters"], "characters")
    
    print("\n" + "=" * 40)
    print("           TEXT ANALYSIS REPORT")
    print("=" * 40)
    print(f"Characters (with spaces):  {metrics['characters']}")
    print(f"Characters (no spaces):    {metrics['characters_no_spaces']}")
    print(f"Words:                      {metrics['words']}")
    print(f"Sentences:                  {metrics['sentences']}")
    print(f"Lines:                      {metrics['lines']}")
    print(f"Paragraphs:                 {metrics['paragraphs']}")
    print("-" * 40)
    print(f"Est. Pages (250 words/pg):  {pages_word}")
    print(f"Est. Pages (3300 chars/pg): {pages_char}")
    print("=" * 40 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Professional Text Character and Word Counter")
    parser.add_argument("--cli", "-c", action="store_true", help="Launch command line interface mode")
    parser.add_argument("file", nargs="?", type=str, help="Optional text file to analyze (runs in CLI mode)")
    args = parser.parse_args()

    # If --cli flag is set, or a file is provided, or input is being piped/redirected:
    if args.cli or args.file or not sys.stdin.isatty():
        run_cli_mode(args.file)
    else:
        # Launch GUI
        root = tk.Tk()
        app = TextCounterGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
