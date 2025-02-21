"""Split text into chunks with XML tags while preserving paragraph breaks and natural segments.

Each chunk will respect the max_tokens limit for a LLM input and maintain original text structure.
"""

import os
import tiktoken


def read_full_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def split_text_into_chunks(text, max_tokens=8000, model="gpt-3.5-turbo"):
    """
    Split text into chunks with XML tags while preserving paragraph breaks and natural segments.
    Each chunk will respect the max_tokens limit and maintain original text structure.

    Args:
        text (str): The input text to be split
        max_tokens (int): Maximum number of tokens per chunk (default: 8000)
        model (str): The model name to use for token counting (default: gpt-3.5-turbo).
        some others: "gpt-4o"

    Returns:
        str: Text split into XML chunks with preserved formatting
    """
    # Initialize the tokenizer
    enc = tiktoken.encoding_for_model(model)

    # Split text into paragraphs while preserving empty lines
    paragraphs = []
    current_paragraph = []

    for line in text.split("\n"):
        if line.strip():
            current_paragraph.append(line)
        else:
            if current_paragraph:
                paragraphs.append("\n".join(current_paragraph))
                current_paragraph = []
            paragraphs.append("")  # Preserve empty lines

    if current_paragraph:
        paragraphs.append("\n".join(current_paragraph))

    chunks = []
    current_chunk = []
    current_token_count = 0
    chunk_number = 1

    for paragraph in paragraphs:
        # Calculate tokens for this paragraph
        paragraph_tokens = len(enc.encode(paragraph))

        # Calculate tokens for the XML tags
        chunk_tag_tokens = len(
            enc.encode(f"<chunk{chunk_number}></chunk{chunk_number}>")
        )

        # Check if adding this paragraph would exceed the limit
        if (
            current_token_count + paragraph_tokens + chunk_tag_tokens > max_tokens
            and current_chunk
        ):
            # Join the current chunk and add XML tags
            chunk_text = "\n".join(current_chunk)
            chunks.append(
                f"<chunk{chunk_number}>\n\n{chunk_text}\n</chunk{chunk_number}>"
            )

            # Reset for next chunk
            current_chunk = []
            current_token_count = 0
            chunk_number += 1

        # Add paragraph to current chunk
        if paragraph:
            current_chunk.append(paragraph)
            current_token_count += paragraph_tokens
        else:
            # Preserve empty lines within chunks
            current_chunk.append("")

    # Handle the last chunk
    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        chunks.append(f"<chunk{chunk_number}>{chunk_text}</chunk{chunk_number}>")

    return chunks


def create_english_md(output_file_english):
    if not os.path.exists(output_file_english):
        with open(output_file_english, "w", encoding="utf-8") as f:
            f.write(
                "Translated with AI.\nIt can make mistakes, please check the original text\n\n---\n\n"
            )
        print(f"Created: {output_file_english} for English translation.")


def save_chunks(chunks: list, input_file: str):
    chunked_text = "\n\n".join(chunks)
    base, ext = os.path.splitext(input_file)
    
    output_xml_chunk = f"{base}_chunks.xml"
    output_eng_md = f"{base}_English.md"
    create_english_md(output_eng_md)

    # if os.path.exists(output_xml_chunk):
        # print(f"File already exists: {output_xml_chunk}")
        # return

    with open(output_xml_chunk, "w", encoding="utf-8") as f:
        f.write(chunked_text)
    print(f"Saved: {output_xml_chunk}.\nTHERE ARE {len(chunks)} chunks!")


if __name__ == "__main__":
    input_file = "./015-Kaṅkhāvitaraṇī-aṭṭhakathā.md"
    chunked_text = split_text_into_chunks(read_full_text(input_file))

    save_chunks(chunked_text, input_file)
