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


def assign_ids_to_json(json_data):
    id_pali = 1
    id_sinh = 1
    id_footer_pali = 1
    id_footer_sinh = 1

    for page in json_data["pages"]:
        # Process Pali entries
        for entry in page["pali"]["entries"]:
            entry["text"] = f"ID{id_pali}={entry['text'].strip()}"
            id_pali += 1

        # Process Sinhala entries
        for entry in page["sinh"]["entries"]:
            entry["text"] = f"ID{id_sinh}={entry['text'].strip()}"
            id_sinh += 1

        # Process Pali footnotes
        if page["pali"]["footnotes"]:
            for footnote in page["pali"]["footnotes"]:
                footnote["fid"] = f"{id_footer_pali}"
                ## sometimes, only 1 of the lang has footnote
                # so, use one id for footnote 
                id_footer_pali += 1 

        # Process Sinhala footnotes
        if page["sinh"]["footnotes"]:
            for footnote in page["sinh"]["footnotes"]:
                footnote["fid"] = f"{id_footer_sinh}"
                id_footer_sinh += 1

    return json_data


def extract_sinh_to_markdown(json_file_path, output_directory):
    # Read JSON file
    with open(json_file_path, "r", encoding="utf-8") as file:
        input_json = json.load(file)

    # assign ID to each
    modified_json = assign_ids_to_json(input_json)
    
    output_json_path = os.path.join(
        "attha_sinh_json_id", os.path.splitext(os.path.basename(json_file_path))[0] + ".json"
    )

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(modified_json, f, indent=2, ensure_ascii=False)

    # use .txt to avoid auto numbering in markdown
    output_txt_path = os.path.join(
        output_directory, os.path.splitext(os.path.basename(json_file_path))[0] + ".txt"
    )

    # Open output file for writing
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        # Write metadata
        out_file.write(f"# {modified_json['filename']}\n\n")

        # Process each page
        for page in modified_json["pages"]:
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
                            fid = footnote['fid']
                            out_file.write(f"FID{fid}={footnote['text']}\n")

            # Add page separator
            out_file.write("\n")


def process_atthakatha_json_files(input_directory="attha_sinh_json"):
    output_directory = "attha_sinh_md_id"
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs('attha_sinh_json_id', exist_ok=True)

    # Ensure the input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Directory '{input_directory}' does not exist.")
        return

    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(input_directory) if f.endswith(".json")]

    # Process each JSON file
    for n, json_file in enumerate(json_files, 1):
        full_path = os.path.join(input_directory, json_file)
        extract_sinh_to_markdown(full_path, output_directory)
        print(f"{n}/{len(json_files)} converted: {json_file}")

    print(f"Processed {len(json_files)} JSON files.")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {os.path.basename(sys.argv[0])} <input_json_file>")
        sys.exit(1)

    input_file = os.path.join("attha_sinh_json", sys.argv[1])

    # Validate input file
    if not input_file.endswith(".json"):
        print("Error: Input file must be a .json file")
        sys.exit(1)

    extract_sinh_to_markdown(input_file)


if __name__ == "__main__":
    # main()
    process_atthakatha_json_files()
