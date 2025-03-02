"""Converts JSON files containing Sinhala text to Markdown format.
The JSON files:
https://github.com/pathnirvana/tipitaka.lk/tree/master/public/static/text
"""

import json
import os
import sys
from typing import Dict, Any, Union


def get_heading(level) -> str:
    """Generates a heading string based on the 'level' in the entry.
    'level' can be: 1, 2, 3, 4, 5
    Corresponding to adding: #####, ####, ###, ##, #
    """
    if level is None:
        print("Warning: 'level' key not found in entry.")
        return ""
    if not isinstance(level, int):
        print(f"Warning: 'level' value is not an integer: {level}")
        return ""
    if not 1 <= level <= 5:
        print(f"Warning: 'level' value {level} is outside the valid range (1-5).")
        return ""
    return "#" * (6 - level)


def convert_json_to_markdown(json_file_path, output_directory):
    # Read JSON file
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # use .txt to avoid auto numbering in markdown
    output_file_path = os.path.join(
        output_directory, os.path.splitext(os.path.basename(json_file_path))[0] + ".txt"
    )

    # Open output file for writing
    with open(output_file_path, "w", encoding="utf-8") as out_file:
        # Write metadata
        out_file.write(f"# {data['filename']}\n\n")

        # Process each page
        for page in data["pages"]:
            out_file.write(f"---\n###### Page {page['pageNum']}\n\n")

            # Process only sinh (Sinhala) content
            if "sinh" in page:
                # Process entries
                for entry in page["sinh"]["entries"]:
                    # Handle headings
                    if entry["type"] == "heading":
                        heading_level = get_heading(entry["level"])
                        out_file.write(f"{heading_level} {entry['text']}\n\n")
                    # Handle paragraphs
                    elif entry["type"] == "paragraph":
                        out_file.write(f"{entry['text']}\n\n")

                # Process footnotes if present
                if "footnotes" in page["sinh"]:
                    for footnote in page["sinh"]["footnotes"]:
                        if footnote["type"] == "footnote":
                            out_file.write(f"> {footnote['text']}\n")

            # Add page separator
            out_file.write("\n")


def process_atthakatha_json_files(input_directory="atthakatha_json"):
    output_directory = "markdown_sinh_attha"
    os.makedirs(output_directory, exist_ok=True)

    # Ensure the input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Directory '{input_directory}' does not exist.")
        return

    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(input_directory) if f.endswith(".json")]

    # Process each JSON file
    for n, json_file in enumerate(json_files, 1):
        full_path = os.path.join(input_directory, json_file)
        convert_json_to_markdown(full_path, output_directory)
        print(f"{n}/{len(json_files)} converted: {json_file}")

    print(f"Processed {len(json_files)} JSON files.")


def main():
    # Check if input file is provided
    if len(sys.argv) < 2:
        print(f"Usage: python3 {os.path.basename(sys.argv[0])} <input_json_file>")
        sys.exit(1)

    input_file = os.path.join("atthakatha_json", sys.argv[1])

    # Validate input file
    if not input_file.endswith(".json"):
        print("Error: Input file must be a .json file")
        sys.exit(1)

    convert_json_to_markdown(input_file)


if __name__ == "__main__":
    # main()
    process_atthakatha_json_files()
