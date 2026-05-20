import tkinter as tk
from tkinter import messagebox
import re
import math

# Function to analyze text
def analyze_text():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter text to count.")
        return

    # Metrics calculations
    character_count = len(text)
    words = text.split()
    word_count = len(words)
    character_count_no_spaces = len(text.replace(" ", ""))
    lines = text.splitlines()
    line_count = len(lines)
    sentences = re.split(r'[.!?]', text)
    sentence_count = len([s for s in sentences if s.strip()])
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_count = len(paragraphs)

    # Calculate pages (assuming 250 words per page, typical for A4 format)
    words_per_page = 250
    page_count = math.ceil(word_count / words_per_page)

    # Display results
    results_text = (
        f"Total characters: {character_count}\n"
        f"Total words: {word_count}\n"
        f"Total characters (excluding spaces): {character_count_no_spaces}\n"
        f"Total sentences: {sentence_count}\n"
        f"Total lines: {line_count}\n"
        f"Total paragraphs: {paragraph_count}\n"
        f"Total pages (A4, 250 words/page): {page_count}"
    )
    result_label.config(text=results_text)

# Create the main window
root = tk.Tk()
root.title("Text Character Counter V2+")

# Create and place widgets
frame = tk.Frame(root)
frame.pack()

title_label = tk.Label(frame, text="Text Character Counter V2+")
title_label.pack()

text_input = tk.Text(frame, width=50, height=10)
text_input.pack()

analyze_button = tk.Button(frame, text="Count Text", command=analyze_text)
analyze_button.pack()

result_label = tk.Label(frame, text="")
result_label.pack()

# Run the main loop
root.mainloop()
