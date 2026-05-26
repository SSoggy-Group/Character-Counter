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

THEMES = {
    "light": {
        "bg": "#f5f6f8",
        "card_bg": "#ffffff",
        "fg": "#2c3e50",
        "fg_muted": "#7f8c8d",
        "accent": "#2980b9",
        "text_bg": "#ffffff",
        "text_fg": "#2c3e50",
        "text_insert": "#2c3e50",
        "canvas_bg": "#ffffff",
        "chart_colors": ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f", "#9b59b6"],
        "border_color": "#dcdde1"
    },
    "dark": {
        "bg": "#1e1e24",
        "card_bg": "#2d2d3a",
        "fg": "#f5f6f8",
        "fg_muted": "#a4b0be",
        "accent": "#6ab04c",
        "text_bg": "#25252f",
        "text_fg": "#f5f6f8",
        "text_insert": "#f5f6f8",
        "canvas_bg": "#25252f",
        "chart_colors": ["#686de0", "#4cd137", "#e84118", "#fbc531", "#9c88ff"],
        "border_color": "#3f3f50"
    }
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

import random

def toSpongeCase(text):
    return "".join(random.choice([char.upper(), char.lower()]) if char.isalpha() else char for char in text)

def toSentenceCase(text):
    sentences = re.split(r'((?:(?<=[.!?])\s+)|(?:\n+))', text)
    result = []
    for part in sentences:
        if not part:
            continue
        if part.isspace():
            result.append(part)
        else:
            match = re.search(r'\w', part)
            if match:
                idx = match.start()
                first_letter = part[idx].upper()
                rest = part[idx+1:].lower()
                result.append(part[:idx] + first_letter + rest)
            else:
                result.append(part)
    return "".join(result)

def cleanSpaces(text):
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r'[ \t]+', ' ', line).strip()
        lines.append(cleaned)
    content = "\n".join(lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()

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
        self.root.geometry("780x640")
        self.root.minsize(780, 580)
        self.currentTheme = "light"
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.mainFrame = ttk.Frame(self.root, padding=15, style='TFrame')
        self.mainFrame.grid(row=0, column=0, sticky='nsew')
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(1, weight=1) # text box holds expansion
        self.mainFrame.rowconfigure(4, weight=1) # Notebook holds vertical expansion too
        
        # 1. Header Frame
        self.headerFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.headerFrame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        self.titleLabel = ttk.Label(self.headerFrame, text="character counter", style='Title.TLabel')
        self.titleLabel.pack(side=tk.LEFT, anchor='w')
        
        self.themeBtn = ttk.Button(self.headerFrame, text="🌙 dark mode", command=self.toggleTheme)
        self.themeBtn.pack(side=tk.RIGHT, anchor='e')
        
        # 2. Text Frame
        self.textFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.textFrame.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
        self.textFrame.columnconfigure(0, weight=1)
        self.textFrame.rowconfigure(0, weight=1)
        
        self.textInput = scrolledtext.ScrolledText(
            self.textFrame, wrap=tk.WORD, font=('Courier New', 11),
            bg='#ffffff', fg='#2c3e50', insertbackground='#2c3e50',
            bd=1, relief='solid', padx=5, pady=5, height=8
        )
        self.textInput.grid(row=0, column=0, sticky='nsew')
        self.textInput.focus_set()
        
        self.textInput.bind('<<Modified>>', self.onTextModified)
        self.textInput.bind('<KeyRelease>', self.onKeyRelease)
        
        # 3. Case Conversion Toolbar
        self.caseFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.caseFrame.grid(row=2, column=0, sticky='ew', pady=(0, 5))
        
        ttk.Label(self.caseFrame, text="format text:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.caseFrame, text="UPPER", command=lambda: self.modifyText(str.upper)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.caseFrame, text="lower", command=lambda: self.modifyText(str.lower)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.caseFrame, text="Title", command=lambda: self.modifyText(str.title)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.caseFrame, text="Sentence", command=lambda: self.modifyText(toSentenceCase)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.caseFrame, text="rAnDoM", command=lambda: self.modifyText(toSpongeCase)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.caseFrame, text="Clean", command=lambda: self.modifyText(cleanSpaces)).pack(side=tk.LEFT, padx=2)
        
        # 4. Controls Frame
        self.controlsFrame = ttk.Frame(self.mainFrame, style='TFrame')
        self.controlsFrame.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(self.controlsFrame, text="page model:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        
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
        
        self.copyBtn = ttk.Button(self.controlsFrame, text="copy report", command=self.copyResults)
        self.copyBtn.pack(side=tk.RIGHT, padx=5)
        
        # 5. Analysis Tabs (Notebook)
        self.notebook = ttk.Notebook(self.mainFrame)
        self.notebook.grid(row=4, column=0, sticky='nsew')
        
        # Create Tab Frames
        self.overviewTab = ttk.Frame(self.notebook, style='TFrame')
        self.readabilityTab = ttk.Frame(self.notebook, style='TFrame')
        self.keywordsTab = ttk.Frame(self.notebook, style='TFrame')
        self.charTab = ttk.Frame(self.notebook, style='TFrame')
        
        self.notebook.add(self.overviewTab, text="overview")
        self.notebook.add(self.readabilityTab, text="readability & timing")
        self.notebook.add(self.keywordsTab, text="keywords")
        self.notebook.add(self.charTab, text="character frequency")
        
        # --- TAB 1: OVERVIEW CARD GRID ---
        self.overviewTab.columnconfigure(0, weight=1)
        self.overviewTab.rowconfigure(0, weight=1)
        
        self.resultsGridFrame = ttk.Frame(self.overviewTab, style='TFrame', padding=10)
        self.resultsGridFrame.grid(row=0, column=0, sticky='nsew')
        for col in range(4):
            self.resultsGridFrame.columnconfigure(col, weight=1, uniform="equal")
        self.resultsGridFrame.rowconfigure(0, weight=1, uniform="row_equal")
        self.resultsGridFrame.rowconfigure(1, weight=1, uniform="row_equal")
        
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
            span = 2 if name == "est. pages" else 1
            card = ttk.Frame(self.resultsGridFrame, style='Card.TFrame', padding=10)
            card.grid(row=row, column=col, columnspan=span, padx=4, pady=4, sticky='nsew')
            
            nameLbl = ttk.Label(card, text=name, style='MetricName.TLabel')
            nameLbl.pack(anchor='w')
            
            valLbl = ttk.Label(card, text="0", style='MetricValue.TLabel')
            valLbl.pack(anchor='w', pady=(4, 0))
            
            self.metricCards[name] = valLbl
            
        # --- TAB 2: READABILITY & TIMING LAYOUT ---
        self.readabilityFrame = ttk.Frame(self.readabilityTab, style='TFrame', padding=10)
        self.readabilityFrame.pack(fill='both', expand=True)
        self.readabilityFrame.columnconfigure(0, weight=1, uniform="equal")
        self.readabilityFrame.columnconfigure(1, weight=1, uniform="equal")
        self.readabilityFrame.rowconfigure(0, weight=1)
        
        # Readability metrics card
        self.readCard = ttk.Frame(self.readabilityFrame, style='Card.TFrame', padding=15)
        self.readCard.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.readCardTitle = ttk.Label(self.readCard, text="Readability Index", style='ReadabilityTitle.TLabel')
        self.readCardTitle.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.readCard, text="Flesch Reading Ease:", style='MetricName.TLabel').pack(anchor='w', pady=(5, 0))
        self.easeScoreLbl = ttk.Label(self.readCard, text="100.0", style='MetricValue.TLabel')
        self.easeScoreLbl.pack(anchor='w', pady=(0, 2))
        
        self.easeInterpLbl = ttk.Label(self.readCard, text="very easy (5th grade)", style='CardText.TLabel')
        self.easeInterpLbl.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.readCard, text="Flesch-Kincaid Grade Level:", style='MetricName.TLabel').pack(anchor='w', pady=(5, 0))
        self.gradeLevelLbl = ttk.Label(self.readCard, text="0.0", style='MetricValue.TLabel')
        self.gradeLevelLbl.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.readCard, text="Total Syllables:", style='MetricName.TLabel').pack(anchor='w', pady=(5, 0))
        self.syllablesLbl = ttk.Label(self.readCard, text="0", style='MetricValue.TLabel')
        self.syllablesLbl.pack(anchor='w')
        
        # Timing card
        self.timeCard = ttk.Frame(self.readabilityFrame, style='Card.TFrame', padding=15)
        self.timeCard.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        self.timeCardTitle = ttk.Label(self.timeCard, text="Speech & Timing", style='ReadabilityTitle.TLabel')
        self.timeCardTitle.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(self.timeCard, text="Silent Reading:", style='MetricName.TLabel').pack(anchor='w', pady=(5, 0))
        self.readTimeLbl = ttk.Label(self.timeCard, text="0s", style='MetricValue.TLabel')
        self.readTimeLbl.pack(anchor='w', pady=(0, 15))
        
        ttk.Label(self.timeCard, text="Speaking Time:", style='MetricName.TLabel').pack(anchor='w', pady=(5, 0))
        self.speakTimeLbl = ttk.Label(self.timeCard, text="0s", style='MetricValue.TLabel')
        self.speakTimeLbl.pack(anchor='w', pady=(0, 15))
        
        self.paceInfoLbl = ttk.Label(
            self.timeCard, 
            text="Calculated at 200 WPM (reading) and 130 WPM (speaking).\nIdeal for presentation planning.", 
            style='CardText.TLabel',
            wraplength=160,
            justify=tk.LEFT
        )
        self.paceInfoLbl.pack(anchor='w', pady=(10, 0))
        
        # --- TAB 3: KEYWORDS LAYOUT ---
        self.keywordsFrame = ttk.Frame(self.keywordsTab, style='TFrame', padding=10)
        self.keywordsFrame.pack(fill='both', expand=True)
        self.keywordsFrame.columnconfigure(0, weight=1, uniform="equal")
        self.keywordsFrame.columnconfigure(1, weight=1, uniform="equal")
        self.keywordsFrame.rowconfigure(0, weight=1)
        
        self.kwListCard = ttk.Frame(self.keywordsFrame, style='Card.TFrame', padding=15)
        self.kwListCard.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.kwListTitle = ttk.Label(self.kwListCard, text="Top Keywords", style='ReadabilityTitle.TLabel')
        self.kwListTitle.pack(anchor='w', pady=(0, 15))
        
        self.kwRows = []
        for i in range(5):
            row_frame = ttk.Frame(self.kwListCard, style='TFrame')
            row_frame.pack(fill='x', pady=4)
            lbl_word = ttk.Label(row_frame, text="-", style='CardTextBold.TLabel', wraplength=100)
            lbl_word.pack(side=tk.LEFT, fill='x', expand=True)
            lbl_stats = ttk.Label(row_frame, text="", style='MetricName.TLabel')
            lbl_stats.pack(side=tk.RIGHT)
            self.kwRows.append((lbl_word, lbl_stats))
            
        self.kwChartCard = ttk.Frame(self.keywordsFrame, style='Card.TFrame', padding=15)
        self.kwChartCard.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        self.kwChartTitle = ttk.Label(self.kwChartCard, text="Density Chart", style='ReadabilityTitle.TLabel')
        self.kwChartTitle.pack(anchor='w', pady=(0, 10))
        
        self.keywordCanvas = tk.Canvas(self.kwChartCard, bg='#ffffff', bd=0, highlightthickness=1)
        self.keywordCanvas.pack(fill='both', expand=True)
        
        # --- TAB 4: CHARACTER FREQUENCY LAYOUT ---
        self.charsTabFrame = ttk.Frame(self.charTab, style='TFrame', padding=10)
        self.charsTabFrame.pack(fill='both', expand=True)
        self.charsTabFrame.columnconfigure(0, weight=1, uniform="equal")
        self.charsTabFrame.columnconfigure(1, weight=1, uniform="equal")
        self.charsTabFrame.rowconfigure(0, weight=1)
        
        self.charListCard = ttk.Frame(self.charsTabFrame, style='Card.TFrame', padding=15)
        self.charListCard.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.charListTitle = ttk.Label(self.charListCard, text="Top Characters", style='ReadabilityTitle.TLabel')
        self.charListTitle.pack(anchor='w', pady=(0, 15))
        
        self.charRows = []
        for i in range(8):
            row_frame = ttk.Frame(self.charListCard, style='TFrame')
            row_frame.pack(fill='x', pady=2)
            lbl_char = ttk.Label(row_frame, text="-", style='CardTextBold.TLabel', wraplength=100)
            lbl_char.pack(side=tk.LEFT, fill='x', expand=True)
            lbl_stats = ttk.Label(row_frame, text="", style='MetricName.TLabel')
            lbl_stats.pack(side=tk.RIGHT)
            self.charRows.append((lbl_char, lbl_stats))
            
        self.charChartCard = ttk.Frame(self.charsTabFrame, style='Card.TFrame', padding=15)
        self.charChartCard.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        self.charChartTitle = ttk.Label(self.charChartCard, text="Frequency Chart", style='ReadabilityTitle.TLabel')
        self.charChartTitle.pack(anchor='w', pady=(0, 10))
        
        self.charCanvas = tk.Canvas(self.charChartCard, bg='#ffffff', bd=0, highlightthickness=1)
        self.charCanvas.pack(fill='both', expand=True)
        
        # Bind canvas resize to redraw charts
        self.keywordCanvas.bind('<Configure>', self.onKwConfigure)
        self.charCanvas.bind('<Configure>', self.onCharConfigure)
        
        self.applyTheme()
        self.updateAnalysis()

    def onKwConfigure(self, event):
        if hasattr(self, '_kw_last_width') and self._kw_last_width == event.width:
            return
        self._kw_last_width = event.width
        self.updateCharts()

    def onCharConfigure(self, event):
        if hasattr(self, '_char_last_width') and self._char_last_width == event.width:
            return
        self._char_last_width = event.width
        self.updateCharts()

    def toggleTheme(self):
        if self.currentTheme == "light":
            self.currentTheme = "dark"
            self.themeBtn.config(text="☀ light mode")
        else:
            self.currentTheme = "light"
            self.themeBtn.config(text="🌙 dark mode")
        self.applyTheme()

    def applyTheme(self):
        theme = THEMES[self.currentTheme]
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('.', font=('Helvetica', 10), foreground=theme["fg"], background=theme["bg"])
        style.configure('TFrame', background=theme["bg"])
        style.configure('Card.TFrame', background=theme["card_bg"], relief='solid', borderwidth=1)
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'), foreground=theme["fg"], background=theme["bg"])
        style.configure('TLabel', foreground=theme["fg"], background=theme["bg"])
        style.configure('MetricName.TLabel', font=('Helvetica', 9), foreground=theme["fg_muted"], background=theme["card_bg"])
        style.configure('MetricValue.TLabel', font=('Helvetica', 12, 'bold'), foreground=theme["accent"], background=theme["card_bg"])
        style.configure('CardText.TLabel', font=('Helvetica', 10), foreground=theme["fg"], background=theme["card_bg"])
        style.configure('CardTextBold.TLabel', font=('Helvetica', 10, 'bold'), foreground=theme["fg"], background=theme["card_bg"])
        style.configure('ReadabilityTitle.TLabel', font=('Helvetica', 11, 'bold'), foreground=theme["accent"], background=theme["card_bg"])
        
        style.configure('TNotebook', background=theme["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', font=('Helvetica', 9, 'bold'), padding=(8, 4))
        style.map('TNotebook.Tab', 
                  background=[('selected', theme["card_bg"]), ('!selected', theme["bg"])],
                  foreground=[('selected', theme["fg"]), ('!selected', theme["fg_muted"])])
        
        style.configure('TButton', background=theme["card_bg"], foreground=theme["fg"], bordercolor=theme["border_color"])
        style.map('TButton', background=[('active', theme["bg"])])
        
        style.configure('TCombobox', fieldbackground=theme["text_bg"], background=theme["bg"], foreground=theme["fg"])
        
        self.root.config(bg=theme["bg"])
        self.textInput.config(
            bg=theme["text_bg"], 
            fg=theme["text_fg"], 
            insertbackground=theme["text_insert"],
            highlightbackground=theme["border_color"],
            bd=1,
            relief='solid'
        )
        
        self.keywordCanvas.config(bg=theme["canvas_bg"], highlightbackground=theme["border_color"])
        self.charCanvas.config(bg=theme["canvas_bg"], highlightbackground=theme["border_color"])
        
        self.updateCharts()

    def modifyText(self, transform_func):
        try:
            start = self.textInput.index(tk.SEL_FIRST)
            end = self.textInput.index(tk.SEL_LAST)
            selected_text = self.textInput.get(start, end)
            transformed = transform_func(selected_text)
            self.textInput.delete(start, end)
            self.textInput.insert(start, transformed)
            self.textInput.tag_add(tk.SEL, start, f"{start} + {len(transformed)} chars")
        except tk.TclError:
            entire_text = self.textInput.get("1.0", tk.END)
            if entire_text.endswith("\n"):
                entire_text = entire_text[:-1]
            transformed = transform_func(entire_text)
            self.textInput.delete("1.0", tk.END)
            self.textInput.insert("1.0", transformed)
        self.updateAnalysis()

    def onTextModified(self, event):
        if not self.textInput.edit_modified():
            return
        self.textInput.edit_modified(False)
        self.updateAnalysis()

    def onKeyRelease(self, event):
        self.updateAnalysis()

    def updateAnalysis(self):
        text = self.textInput.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
            
        metrics = analyzeText(text)
        self.last_metrics = metrics
        
        modelStr = self.pageModelVar.get()
        modelKey = "words" if "words" in modelStr else "characters"
        pages = calculatePages(metrics["words"], metrics["characters"], modelKey)
        
        # 1. Update Overview Tab
        self.metricCards["characters"].config(text=str(metrics["characters"]))
        self.metricCards["words"].config(text=str(metrics["words"]))
        self.metricCards["char (no spaces)"].config(text=str(metrics["characters_no_spaces"]))
        self.metricCards["sentences"].config(text=str(metrics["sentences"]))
        self.metricCards["lines"].config(text=str(metrics["lines"]))
        self.metricCards["paragraphs"].config(text=str(metrics["paragraphs"]))
        self.metricCards["est. pages"].config(text=str(pages))
        
        # 2. Update Readability Tab
        self.easeScoreLbl.config(text=f"{metrics['readability_ease']:.1f}")
        self.easeInterpLbl.config(text=getReadabilityInterpretation(metrics['readability_ease']))
        self.gradeLevelLbl.config(text=f"{metrics['readability_grade']:.1f}")
        self.syllablesLbl.config(text=str(metrics['syllables']))
        self.readTimeLbl.config(text=formatTime(metrics['reading_time']))
        self.speakTimeLbl.config(text=formatTime(metrics['speaking_time']))
        
        # 3. Update Keywords Tab Listings
        for idx, (lbl_word, lbl_stats) in enumerate(self.kwRows):
            if idx < len(metrics["keywords"]):
                w, count, pct = metrics["keywords"][idx]
                lbl_word.config(text=f"{idx+1}. {w}")
                lbl_stats.config(text=f"{count} ({pct:.1f}%)")
            else:
                lbl_word.config(text="-")
                lbl_stats.config(text="")
                
        # 4. Update Character Tab Listings
        for idx, (lbl_char, lbl_stats) in enumerate(self.charRows):
            if idx < len(metrics["char_dist"]):
                c, count, pct = metrics["char_dist"][idx]
                lbl_char.config(text=f"{idx+1}. '{c}'")
                lbl_stats.config(text=f"{count} ({pct:.1f}%)")
            else:
                lbl_char.config(text="-")
                lbl_stats.config(text="")
                
        # 5. Redraw the canvas charts
        self.updateCharts(metrics)

    def drawCanvasChart(self, canvas, data, theme):
        canvas.delete("all")
        if not data:
            canvas.create_text(150, 80, text="no data to display", fill=theme["fg_muted"], font=('Helvetica', 10, 'italic'))
            return
            
        canvas_width = canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 300
            
        x_label = 15
        x_bar_start = 75
        x_bar_max_width = canvas_width - x_bar_start - 65
        y_start = 15
        y_spacing = 22
        bar_height = 11
        
        max_val = max(item[1] for item in data) if data else 1
        
        for idx, item in enumerate(data):
            label, count, pct = item
            y = y_start + idx * y_spacing
            
            display_label = label
            if len(display_label) > 8:
                display_label = display_label[:6] + ".."
                
            canvas.create_text(x_label, y + bar_height/2, text=display_label, fill=theme["fg"], font=('Helvetica', 9, 'bold'), anchor='w')
            
            bar_width = (count / max_val) * x_bar_max_width if max_val > 0 else 0
            if count > 0:
                bar_width = max(3, bar_width)
                
            color = theme["chart_colors"][idx % len(theme["chart_colors"])]
            
            canvas.create_rectangle(
                x_bar_start, y, 
                x_bar_start + bar_width, y + bar_height,
                fill=color, outline="", width=0
            )
            
            val_text = f"{count} ({pct:.1f}%)"
            canvas.create_text(
                x_bar_start + bar_width + 8, y + bar_height/2,
                text=val_text, fill=theme["fg_muted"], font=('Helvetica', 8), anchor='w'
            )

    def updateCharts(self, metrics=None):
        if metrics is None:
            metrics = getattr(self, 'last_metrics', None)
            if metrics is None:
                text = self.textInput.get("1.0", tk.END)
                if text.endswith("\n"):
                    text = text[:-1]
                metrics = analyzeText(text)
                self.last_metrics = metrics
            
        theme = THEMES[self.currentTheme]
        self.drawCanvasChart(self.keywordCanvas, metrics["keywords"], theme)
        self.drawCanvasChart(self.charCanvas, metrics["char_dist"], theme)

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
            f"est. pages ({modelStr}): {pages}\n"
            f"readability ease: {metrics['readability_ease']:.1f} ({getReadabilityInterpretation(metrics['readability_ease'])})\n"
            f"readability grade: {metrics['readability_grade']:.1f}\n"
            f"reading time: {formatTime(metrics['reading_time'])}\n"
            f"speaking time: {formatTime(metrics['speaking_time'])}"
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
