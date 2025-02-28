"""Split text into chunks with XML tags while preserving paragraph breaks and natural segments.

Each chunk will respect the max_tokens limit for a LLM input and maintain original text structure.
"""

import os
import tiktoken  # pip install tiktoken
import argparse


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

    # Define end marker with placeholder for chunk number
    end_marker_template = "\n[END_OF_CHUNK_{chunk_num}_FOR_AI_TRANSLATION]\n"

    # We'll calculate end marker tokens for each chunk since the number length varies
    def get_end_marker(chunk_num):
        return end_marker_template.format(chunk_num=chunk_num)

    # Split text into paragraphs while preserving empty lines
    paragraphs = []
    current_paragraph = []
    line_counter = 1

    for line in text.split("\n"):
        if line.strip():
            current_paragraph.append(f"\nID{line_counter}={line}")
            line_counter += 1
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

        # Calculate tokens for the XML tags and end marker for current chunk
        current_end_marker = get_end_marker(chunk_number)
        chunk_tag_tokens = len(
            enc.encode(f"<chunk{chunk_number}></chunk{chunk_number}>")
        )
        end_marker_tokens = len(enc.encode(current_end_marker))

        # Check if adding this paragraph would exceed the limit
        if (
            current_token_count
            + paragraph_tokens
            + chunk_tag_tokens
            + end_marker_tokens
            > max_tokens
            and current_chunk
        ):
            # Join the current chunk and add XML tags with numbered end marker
            chunk_text = "\n".join(current_chunk).replace(
                "\n\n\n", "\n\n"
            )  # Replace triple with double newlines
            chunks.append(
                f"<chunk{chunk_number}>\n{chunk_text}{get_end_marker(chunk_number)}\n</chunk{chunk_number}>"
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
        chunk_text = "\n".join(current_chunk).replace(
            "\n\n\n", "\n\n"
        )  # Replace triple with double newlines

        chunks.append(
            f"<chunk{chunk_number}>\n{chunk_text}{get_end_marker(chunk_number)}\n</chunk{chunk_number}>"
        )

    return chunks


def create_english_md(output_file_english):
    if not os.path.exists(output_file_english):
        with open(output_file_english, "w", encoding="utf-8") as f:
            f.write(
                """<info>\n**WARNING: THIS IS AN AI-TRANSLATED EXPERIMENT.**

- Please do not blindly trust the LLM output. LLMs can produce errors. If you are uncertain, refer to the original Pāḷi text for verification.

- The main purpose of this page is to facilitate quick searches using English keywords to locate relevant Pāḷi passages. Searching in English is more convenient for us.\n</info>\n\n\n"""
            )
        print(f"Created: {output_file_english} for English translation.")
    else:
        print(f"=> File exist (untouch): {output_file_english}")


def save_chunks(chunks: list, input_file: str):
    chunked_text = "\n\n".join(chunks)
    base, ext = os.path.splitext(input_file)

    # Include token count in filenames
    output_base_chunk = f"{base}_{len(chunks)}_chunks"
    output_xml_chunk = f"{output_base_chunk}.xml"
    output_translated_f1 = f"{output_base_chunk}_translated_1.xml"
    output_translated_f2 = f"{output_base_chunk}_translated_2.xml"
    output_translated_f3 = f"{output_base_chunk}_translated_3.xml"

    with open(output_xml_chunk, "w", encoding="utf-8") as f:
        f.write(chunked_text)
    print(f"Saved: {output_xml_chunk}!")

    create_english_md(output_translated_f1)
    create_english_md(output_translated_f2)
    create_english_md(output_translated_f3)
    
    print(f"\nTHERE ARE {len(chunks)} chunks!")
    print(f"Run: chunk_copier_run_2.py to help you copy each of these {len(chunks)} chunks with the system prompt faster.")


def process_directory(
    dir_path: str, max_tokens: int = 8000, model: str = "gpt-3.5-turbo"
):
    """
    Process all .txt files in the specified directory.

    Args:
        dir_path (str): Path to the directory containing .txt files
        max_tokens (int): Maximum tokens per chunk (default: 8000)
        model (str): Model name for token counting (default: gpt-3.5-turbo)
    """
    if not os.path.exists(dir_path):
        print(f"Error: Directory '{dir_path}' does not exist.")
        return

    txt_files = [f for f in os.listdir(dir_path) if f.endswith(".txt")]

    if not txt_files:
        print(f"No .txt files found in '{dir_path}'")
        return

    for n, txt_file in enumerate(txt_files, 1):
        file_path = os.path.join(dir_path, txt_file)
        print(f"\n{n}/{len(txt_files)}. Processing: {txt_file}")
        try:
            chunked_text = split_text_into_chunks(
                read_full_text(file_path), max_tokens=max_tokens, model=model
            )
            save_chunks(chunked_text, file_path, max_tokens)
        except Exception as e:
            print(f"Error processing {txt_file}: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split text file into chunks for AI translation with XML tags while preserving structure."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--file", type=str, help="Path to the input text file to be processed"
    )
    group.add_argument(
        "-d",
        "--directory",
        type=str,
        help="Path to directory containing .txt files to process",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8000,
        help="Maximum tokens per chunk (default: 8000)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="Model name for token counting (default: gpt-3.5-turbo)",
    )

    args = parser.parse_args()

    if args.file:
        chunked_text = split_text_into_chunks(
            read_full_text(args.file), max_tokens=args.max_tokens, model=args.model
        )
        save_chunks(chunked_text, args.file)
    else:
        process_directory(args.directory, args.max_tokens, args.model)
