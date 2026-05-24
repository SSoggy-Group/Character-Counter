import tkinter as tk
from tkinter import messagebox
import re
import math

def analyze_text():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showerror("Error", "Please enter text to count.")
        return

    # Metrics calculations
    character_count = len(text)
    words = text.split()
    word_count = len(words)
    character_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    lines = text.splitlines()
    line_count = len(lines)
    sentences = re.split(r'[.!?]', text)
    sentence_count = len([s for s in sentences if s.strip()])
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_count = len(paragraphs)

    # Calculate pages based on characters (3300 chars per A4 page)
    chars_per_page = 3300
    page_count = math.ceil(character_count / chars_per_page)

    # Display results
    results_text = (
        f"Total characters: {character_count}\n"
        f"Total words: {word_count}\n"
        f"Total characters (excluding spaces): {character_count_no_spaces}\n"
        f"Total sentences: {sentence_count}\n"
        f"Total lines: {line_count}\n"
        f"Total paragraphs: {paragraph_count}\n"
        f"Total pages (A4, ~3200 chars/page): {page_count}"
    )
    result_label.config(text=results_text)

root = tk.Tk()
root.title("Text Character Counter V2+")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

title_label = tk.Label(frame, text="Text Character Counter V2+", font=("Helvetica", 16, "bold"))
title_label.pack(pady=5)

text_input = tk.Text(frame, width=50, height=10, wrap=tk.WORD, font=("Helvetica", 12))
text_input.pack(pady=5)

analyze_button = tk.Button(frame, text="Count Text", command=analyze_text, font=("Helvetica", 12), bg="lightblue")
analyze_button.pack(pady=5)

result_label = tk.Label(frame, text="", font=("Helvetica", 12), justify="left", anchor="w")
result_label.pack(pady=5)

root.mainloop()
