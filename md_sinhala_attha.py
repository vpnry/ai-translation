"""Converts JSON files containing Sinhala text to Markdown format.
The JSON files:
https://github.com/pathnirvana/tipitaka.lk/tree/master/public/static/text
"""

import json
import os
import sys
import re


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


def remove_line_tags(text):
    """Removes all <line id="{number}"> and </line> tags from a string."""
    return re.sub(r'<line id="\d+">|</line>', "", text)


def assign_ids_to_json(json_data):
    id_pali = 1
    id_sinh = 1
    id_footer_pali = 1
    id_footer_sinh = 1

    for page in json_data["pages"]:
        # Process Pali entries
        for entry in page["pali"]["entries"]:
            if "text" in entry:
                if entry["text"].strip():
                    entry["text"] = f"SP{id_pali} = {entry['text'].strip()}"
                else:
                    entry["text"] = f"SP{id_pali} = @@"

        # Process Sinhala entries
        for entry in page["sinh"]["entries"]:
            if "text" in entry:
                if entry["text"].strip():
                    entry["text"] = f"SP{id_sinh} = {entry['text'].strip()}"
                else:
                    entry["text"] = f"SP{id_sinh} = @@"

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


def parse_line_for_id(line: str) -> tuple:
    line = line.strip()  # important

    line = remove_line_tags(line)
    line = line.lstrip("#").strip()

    if not line:
        return None, None
    if line.startswith("SP") and " = " in line:
        parts = line.split(" = ", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        if key.startswith("SP") and key[2:].isdigit():
            return key, value
    # footnote
    elif line.startswith("FSP") and " = " in line:
        parts = line.split(" = ", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        if key.startswith("FSP") and key[3:].isdigit():
            return key, value
    return None, None


def put_translation_to_id(
    json_file_path: str,
    trans_file: str,
    out_dir="attha_sinh_json_eng",
    lang_key: str = "sinh",
):

    trans_dict = {}
    with open(trans_file, "r", encoding="utf-8") as file:
        for line in file:

            k, v = parse_line_for_id(line)
            if k and v:
                trans_dict[k] = f"{v}"

    # print(trans_dict)

    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    for page in json_data["pages"]:
        for entry in page[lang_key]["entries"]:
            line = entry["text"].strip()
            k, v = parse_line_for_id(line)
            if k and v:
                if k in trans_dict:
                    if trans_dict[k].strip():
                        if trans_dict[k].strip().lower() == "@@":
                            entry["text"] = ""  # remove ID
                        else:
                            entry["text"] = f"{k} = {trans_dict[k].strip()}"
                else:
                    print(
                        f"---Error: {k} in {json_file_path} is not found in the translated file {trans_file}"
                    )

        # Process footnotes
        if page[lang_key]["footnotes"]:
            for footnote in page[lang_key]["footnotes"]:
                if "fid" in footnote:
                    k = f"FSP{footnote['fid']}"
                    if k in trans_dict:
                        footnote["text"] = f"{k} = {trans_dict[k]}"
                    else:
                        print(
                            f"---Error: {k} in {json_file_path} is not found in the translated file {trans_file}"
                        )

    # save
    output_json_path = os.path.join(
        out_dir,
        os.path.splitext(os.path.basename(json_file_path))[0] + ".json",
    )

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"Added translations to {json_file_path}")


def extract_sinh_to_markdown(json_file_path, output_directory):
    # Read JSON file
    with open(json_file_path, "r", encoding="utf-8") as file:
        input_json = json.load(file)

    # assign SP to each
    modified_json = assign_ids_to_json(input_json)

    output_json_path = os.path.join(
        "attha_sinh_json_id",
        os.path.splitext(os.path.basename(json_file_path))[0] + ".json",
    )

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(modified_json, f, indent=2, ensure_ascii=False)

    # use .txt to avoid auto numbering in markdown
    output_txt_path = os.path.join(
        output_directory, os.path.splitext(os.path.basename(json_file_path))[0] + ".txt"
    )

    # Open output file for writing
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        # Write metadata

        # out_file.write(f"# {modified_json['filename']}\n\n")

        # Process each page
        for page in modified_json["pages"]:
            # out_file.write(f"---\n###### Page {page['pageNum']}\n\n")

            # Process only sinh (Sinhala) content
            if "sinh" in page:
                # Process entries
                for entry in page["sinh"]["entries"]:
                    # Handle headings
                    if "level" in entry:
                        heading_level = get_heading(entry["level"])
                        if "text" in entry:
                            esc_text = entry["text"].replace("\n", " <br /> ")
                            out_file.write(f"{heading_level} {esc_text}\n\n")
                    elif "text" in entry:
                        esc_text = entry["text"].replace("\n", " <br /> ")
                        out_file.write(f"{esc_text}\n\n")

                # Process footnotes if present
                if "footnotes" in page["sinh"]:
                    for footnote in page["sinh"]["footnotes"]:
                        if footnote["type"] == "footnote":
                            fid = footnote["fid"]
                            out_file.write(f"FSP{fid} = {footnote['text']}\n")

            # Add page separator
            out_file.write("\n")


def prepare_atthakatha_json_files(input_directory="attha_sinh_json"):
    output_directory = "attha_sinh_md_id"
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs("attha_sinh_json_id", exist_ok=True)
    os.makedirs("attha_sinh_json_eng", exist_ok=True)

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


def put_translation_json_files(
    model="gemini-2.0-flash", input_directory="attha_sinh_md_id"
):
    output_directory = "attha_sinh_json_eng"
    os.makedirs(output_directory, exist_ok=True)
    sinh_json_id_dir = "attha_sinh_json_id"

    # Ensure the input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Directory '{input_directory}' does not exist.")
        return

    # Get all JSON files in the directory
    translated_xml_files = [
        f for f in os.listdir(input_directory) if f.endswith(f"{model}.xml")
    ]

    # Process each JSON file
    for n, tr_file in enumerate(translated_xml_files, 1):
        parts = re.split(r"_\d+_chunks_", tr_file, 1)
        json_fn = f"{parts[0]}.json"
        json_id_path = os.path.join(sinh_json_id_dir, json_fn)

        trans_path = os.path.join(input_directory, tr_file)
        put_translation_to_id(json_id_path, trans_path)
        print(f"{n}/{len(translated_xml_files)} Done: {tr_file}")

    print(f"Processed {len(translated_xml_files)} JSON files.")


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
    prepare_atthakatha_json_files()
    # put_translation_json_files()
    # put_translation_to_id("attha_sinh_json_id/atta-an-1-14-3.json", "attha_sinh_md_id/atta-an-1-14-3_36_chunks_20250308_211731_gemini-2.0-flash.xml")
