"""Translate files matching a pattern in a specified directory using the Gemini API."""

import os
import argparse
import fnmatch
import re
from datetime import datetime
import time

from translator_gemini import gemini_translate, gemini_translator, set_gemini_key_file


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


def retry_failed_chunks(directory, matching_files, key_file):
    print("\nChecking for failed chunks...")
    for file_path in matching_files:
        base_name = os.path.splitext(file_path)[0]
        log_file = os.path.join(directory, f"{base_name}_translated_1.log")
        translated_file = os.path.join(directory, f"{base_name}_translated_1.xml")

        if not os.path.exists(log_file) or not os.path.exists(translated_file):
            continue

        # Read log file to find failed chunks
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
            failed_chunks = re.findall(r"Chunk (\d+): CHUNK_FAILED", log_content)

        if failed_chunks:
            print(f"\nFound {len(failed_chunks)} failed chunks in: {translated_file}")
            print("Re-translating failed chunks:")

            # Read original file content
            with open(os.path.join(directory, file_path), "r", encoding="utf-8") as f:
                content = f.read()

            # Read current translated content
            with open(translated_file, "r", encoding="utf-8") as f:
                translated_content = f.read()

            # Process each failed chunk
            fixed_chunks_ok = []
            for chunk_num in failed_chunks:
                try:
                    # Find the specific chunk using its number
                    chunk_pattern = f"<chunk{chunk_num}>(.*?)</chunk{chunk_num}>"
                    chunk_match = re.search(chunk_pattern, content, re.DOTALL)

                    if chunk_match:
                        full_chunk = chunk_match.group(
                            0
                        )  # Get the complete chunk with tags
                        print(f"Processing chunk {chunk_num}...")
                        translated_text = gemini_translate(full_chunk, key_file)

                        # fix of fix
                        if not translated_text:
                            print(
                                f"Translating still failed for chunk {chunk_num}...\n Will retry again after 5s"
                            )
                            time.sleep(5)
                            translated_text = gemini_translate(full_chunk, key_file)
                            if translated_text:
                                print(
                                    "\n2nd Re-translated successfully chunk: ",
                                    chunk_num,
                                )
                        if translated_text:
                            # Replace the failed chunk in the translated file
                            translated_content = re.sub(
                                f"<chunk{chunk_num}>.*?</chunk{chunk_num}>",
                                translated_text,
                                translated_content,
                                flags=re.DOTALL,
                            )

                            # Update the log file
                            # Update the log file - mark the original failure as fixed
                            with open(log_file, "r", encoding="utf-8") as log_f:
                                updated_log = log_f.read()
                                updated_log = re.sub(
                                    f"Chunk {chunk_num}: CHUNK_FAILED",
                                    f"Chunk {chunk_num}: FIXED_CHUNK_FAILED",
                                    updated_log,
                                )
                            with open(log_file, "w", encoding="utf-8") as log_f:
                                log_f.write(updated_log)
                                log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                log_f.write(
                                    f"\nRetry successful - Chunk {chunk_num}: {log_time}\n"
                                )
                            fixed_chunks_ok.append(chunk_num)

                            print("\nRe-translated successfully chunk: ", chunk_num)
                    else:
                        print(f"Could not find chunk {chunk_num} in original file")

                except Exception as e:
                    print(f"Error retrying chunk {chunk_num}: {str(e)}")
                    continue

            # Write updated content back to file
            with open(translated_file, "w", encoding="utf-8") as f:
                f.write(translated_content)

            remaining = [num for num in failed_chunks if num not in fixed_chunks_ok]
            print(
                f"File: {translated_file}\nFixed/Total: {len(fixed_chunks_ok)}/{len(failed_chunks)}\nFailed chunks: {failed_chunks}. Fixed chunks: {fixed_chunks_ok}. Remaining CHUNKS: {remaining}"
            )


def process_files(
    directory=".", file_pattern="*_chunks.xml", key_file="gemini_key_project_1.txt"
):

    print(f"Using file filter pattern: {file_pattern}")

    # Get all files in the specified directory
    all_files = os.listdir(directory)

    # Filter files matching the pattern using fnmatch and sort them
    matching_files = sorted([f for f in all_files if fnmatch.fnmatch(f, file_pattern)])

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
        f"Reminder: Free tier Gemini API call limit is 1,500 requests/per project/ per day. This session will use ~ {total_chunks} requests of your project limit."
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
            print(f"---------\nProcessing file: {file_path}")
            n_file = f"File {n} of {len(matching_files)}"
            gemini_translator(os.path.join(directory, file_path), n_file, key_file)
            print(f"{n_file}. Translated: {file_path}\n")

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    # After all files are processed, retry any failed chunks
    retry_failed_chunks(directory, matching_files, key_file)


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

    parser.add_argument(
        "-k",
        "--key-file",
        default="./gemini_key_project_1.txt",
        help="Path to the Gemini API key file (default: ./gemini_key_project_1.txt)",
    )

    args = parser.parse_args()

    # Setting key-file on translator_gemini.py
    set_gemini_key_file(args.key_file)

    print(f"Starting translation of files in {args.directory}...")

    process_files(args.directory, args.pattern, args.key_file)

    print(
        "Translation tasks completed!\nPlease search 'CHUNK_FAILED' in the log files to see any failed chunks"
    )
