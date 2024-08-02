import os
import hashlib
from PyPDF2 import PdfReader
from docx import Document
from difflib import SequenceMatcher
from tabulate import tabulate

# Helper function to calculate file hash
def calculate_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Find duplicates in specific file types
def find_duplicates(directory, file_extension):
    files = {}
    duplicates = []

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(file_extension):
                filepath = os.path.join(root, filename)
                filehash = calculate_hash(filepath)

                if filehash in files:
                    duplicates.append((files[filehash], filepath))
                else:
                    files[filehash] = filepath

    return duplicates

# Find duplicates in any file type
def find_any_duplicates(directory):
    files = {}
    duplicates = []

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            filehash = calculate_hash(filepath)

            if filehash in files:
                duplicates.append((files[filehash], filepath))
            else:
                files[filehash] = filepath

    return duplicates

# Function to process text content of various file types for similarity
def get_file_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif ext == '.docx':
        doc = Document(filepath)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

# Function to calculate similarity percentage between two texts
def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

# Calculate similarity percentage among all files in the directory
def calculate_similarity_among_files(directory):
    file_texts = {}
    similarities = []

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            file_text = get_file_text(filepath)
            file_texts[filepath] = file_text

    filepaths = list(file_texts.keys())
    for i in range(len(filepaths)):
        for j in range(i + 1, len(filepaths)):
            file1 = filepaths[i]
            file2 = filepaths[j]
            similarity = calculate_similarity(file_texts[file1], file_texts[file2])
            similarities.append((os.path.basename(file1), os.path.basename(file2), similarity))

    return similarities

# Get directory input from user
directory = input("Enter the directory path: ")

# Find duplicates and calculate similarities
duplicates = find_any_duplicates(directory)
similarities = calculate_similarity_among_files(directory)

# Find the highest similarity
max_similarity = max(similarities, key=lambda x: x[2])

# Print results
print("Duplicates:")
duplicate_table = [[os.path.basename(dup[0]), os.path.basename(dup[1])] for dup in duplicates]
print(tabulate(duplicate_table, headers=["File 1", "File 2"]))

print("\nSimilarities:")
similarity_table = [
    [sim[0], sim[1], f"{sim[2] * 100:.2f}%"] if sim != max_similarity else [f"**{sim[0]}**", f"**{sim[1]}**", f"**{sim[2] * 100:.2f}%**"]
    for sim in similarities
]
print(tabulate(similarity_table, headers=["File 1", "File 2", "Similarity Percentage"]))

# Print highest similarity
print(f"\nHighest similarity between files: {max_similarity[0]} and {max_similarity[1]} with {max_similarity[2] * 100:.2f}% similarity.")
