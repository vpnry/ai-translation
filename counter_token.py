import os
import tiktoken
from bs4 import BeautifulSoup

def extract_text_from_html(file_path):
    """Extract text from an HTML file."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "xml")
        return soup.get_text()

def count_tokens(text, model="gpt-4"):
    """Count tokens using tiktoken with the specified model."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def process_directory(directory, model="gpt-4"):
    """Process all HTML files in a directory and count total tokens."""
    total_tokens = 0
    file_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                text = extract_text_from_html(file_path)
                tokens = count_tokens(text, model)
                total_tokens += tokens
                file_count += 1
                print(f"{file}: {tokens} tokens")

    print("\nSummary:")
    print(f"Processed {file_count} HTML files")
    print(f"Total tokens: {total_tokens}")

if __name__ == "__main__":
    directory_path = input("Enter the directory path: ").strip()
    process_directory(directory_path)
