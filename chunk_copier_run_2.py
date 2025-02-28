import pyperclip # pip install pyperclip 
import webbrowser
import re
import time
from typing import List, Tuple

def load_file_content(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def extract_chunks(content: str) -> List[Tuple[int, str]]:
    chunks = []
    # Updated pattern to match XML-style chunks
    pattern = r'<chunk(\d+)>([\s\S]*?)</chunk\1>'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        chunk_num = int(match.group(1))
        chunk_content = match.group(2).strip()
        chunks.append((chunk_num, chunk_content))
    
    # Debug information
    if not chunks:
        print("Debug: No chunks found. First 200 characters of content:")
        print(content[:200])
        print("\nPattern used:", pattern)
    else:
        print(f"Debug: Found {len(chunks)} chunks")
    
    return sorted(chunks)

def copy_chunks(system_prompt: str, chunks: List[Tuple[int, str]], 
                start_chunk: int, num_chunks: int, website_url: str) -> int:
    if not chunks:
        print("No chunks found in the file!")
        return 0

    # Find the starting point
    start_idx = 0
    for idx, (chunk_num, _) in enumerate(chunks):
        if chunk_num >= start_chunk:
            start_idx = idx
            break

    # Get the chunks to copy
    end_idx = min(start_idx + num_chunks, len(chunks))
    selected_chunks = chunks[start_idx:end_idx]
    
    if not selected_chunks:
        print("No more chunks to copy!")
        return 0

    # Prepare the text to copy
    text_to_copy = system_prompt.strip() + "\n\n"
    for chunk_num, content in selected_chunks:
        # Add the chunk tags back in the copied text
        text_to_copy += f"<chunk{chunk_num}>\n\n{content}\n\n</chunk{chunk_num}>\n\n"

    # Copy to clipboard
    pyperclip.copy(text_to_copy.strip())
    
    # Print copied chunks info
    chunk_numbers = [chunk_num for chunk_num, _ in selected_chunks]
    print(text_to_copy)
    print(f"Copied chunks {chunk_numbers} to clipboard")
    
    # Open the specified website
    if website_url:
        webbrowser.open(website_url) # For default browser
    
    return selected_chunks[-1][0]  # Return the last chunk number

def main():
    # Get file paths

    system_prompt_path = input("Enter the system prompt file path: ").strip()
    chunk_file_path = input("Enter the chunk file path: ").strip()
    chunks_per_copy = int(input("How many chunks to copy at once: ").strip())
    website_url = input("Enter the website URL to open after copying: ").strip()

    # manually enter the file paths
    # system_prompt_path = "./prompt_Pali_English.md"
    # chunk_file_path = "khuddasikkha-mulasikkha/khuddasikkha/khudadasikkha-pura-abhinava-tika_206_chunks.xml"
    # chunks_per_copy = 1
    # website_url = "https://www.meta.ai"
    # website_url = "https://aistudio.google.com/prompts/new_chat"
    # website_url = "https://chat.qwenlm.ai"


    # Load files
    system_prompt = load_file_content(system_prompt_path)
    chunk_content = load_file_content(chunk_file_path)
    
    if not system_prompt or not chunk_content:
        return

    # Extract chunks
    chunks = extract_chunks(chunk_content)
    last_copied_chunk = 0

    while True:
        user_input = input(f"\nEnter chunk number to start from (or press Enter for next chunk): ").strip()
        
        if user_input == "":
            # Start from next chunk or from 1
            start_chunk = last_copied_chunk + 1 if last_copied_chunk else 1
        else:
            try:
                start_chunk = int(user_input)
            except ValueError:
                print("Invalid input. Please enter a number or press Enter.")
                continue

        last_copied_chunk = copy_chunks(system_prompt, chunks, start_chunk, chunks_per_copy, website_url)
        
        if last_copied_chunk == 0:
            break

        print("\nPress Enter to continue with next chunks, or enter a specific chunk number.")

if __name__ == "__main__":
    main()