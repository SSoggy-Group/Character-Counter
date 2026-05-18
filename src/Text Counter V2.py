import tkinter as tk
from tkinter import messagebox
import re
import math

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

result_label = tk.Label(frame, text="")
result_label.pack()

# Run the main loop
root.mainloop()
