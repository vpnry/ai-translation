"""Translate files matching a pattern in a specified directory using the Gemini API."""

import os
import argparse
import fnmatch
import re

from translator_gemini import gemini_translator


def count_chunks(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Find all occurrences of <chunk{number}> tags
            chunks = re.findall(r"<chunk\d+>", content)
            return len(chunks)
    except Exception as e:
        print(f"Error counting chunks in {file_path}: {str(e)}")
        return 0


def process_files(directory=".", file_pattern="*_chunks.xml"):
    print(f"Using file filter pattern: {file_pattern}")

    # Get all files in the specified directory
    all_files = os.listdir(directory)

    # Filter files matching the pattern using fnmatch
    matching_files = [f for f in all_files if fnmatch.fnmatch(f, file_pattern)]

    # Print the filtered list and count chunks
    print("\nMatching files found:")
    total_chunks = 0
    for file in matching_files:
        file_path = os.path.join(directory, file)
        chunks_count = count_chunks(file_path)
        total_chunks += chunks_count
        print(f"- {file} (chunks: {chunks_count})")
    print(f"\nTotal matching files: {len(matching_files)}")
    print(f"Total chunks across all files: {total_chunks}\n")

    # Ask for user confirmation
    print(
        f"Reminder: Free Gemini API call limit is 1,500 requests per day. This session will use ~ {total_chunks} requests"
    )
    response = input("Do you want to proceed with translation? (y/n): ").lower().strip()
    if response != "y":
        print("Translation cancelled by user.")
        return

    # Check if any files were found
    if not matching_files:
        print(f"No files found matching pattern: {file_pattern}")
        return

    # Process each file
    for n, file_path in enumerate(matching_files, 1):
        try:
            print(f"Processing file: {file_path}")
            gemini_translator(os.path.join(directory, file_path))
            print(f"{n}/{len(matching_files)}. Translated: {file_path}\n")

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Translate files matching a pattern in specified directory."
    )
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="Directory containing files to translate",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default="*_chunks.xml",
        help="File pattern to match (default: *_chunks.xml)",
    )

    args = parser.parse_args()

    print(f"Starting translation of files in {args.directory}...")
    process_files(args.directory, args.pattern)
    print("Translation process completed!")
