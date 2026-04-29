import re

# Input text from user
text = input("Enter the text you want to analyze: ")

# Count total characters
total_characters = len(text)

# Count characters without spaces
characters_no_spaces = len(text.replace(" ", ""))

# Count words
words = text.split()
word_count = len(words)

# Count words without spaces (ignores empty strings)
word_count_no_spaces = len([w for w in words if w.strip()])

# Count sentences
sentences = re.split(r'[.!?]', text)  # Splits at ., !, or ?
sentence_count = len([s for s in sentences if s.strip()])

# Display results
print("\nAnalysis of the text:")
print(f"Total characters (including spaces): {total_characters}")
print(f"Total characters (without spaces): {characters_no_spaces}")
print(f"Total words: {word_count}")
print(f"Total words (ignoring spaces): {word_count_no_spaces}")
print(f"Total sentences: {sentence_count}")

input("\nPress Enter to exit...")
