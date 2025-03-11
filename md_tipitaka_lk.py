"""Converts JSON files containing Sinhala text to Markdown format.
The JSON files:
https://github.com/pathnirvana/tipitaka.lk/tree/master/public/static/text
"""

import json
import os
import sys
import re
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


def remove_line_xml_tag(text):
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
                    entry["text"] = f"Pi {id_pali} = {entry['text'].strip()}"
                else:
                    entry["text"] = f"Pi {id_pali} = @@"
            id_pali += 1

        # Process Sinhala entries
        for entry in page["sinh"]["entries"]:
            if "text" in entry:
                if entry["text"].strip():
                    entry["text"] = f"Si {id_sinh} = {entry['text'].strip()}"
                else:
                    entry["text"] = f"Si {id_sinh} = @@"

            id_sinh += 1

        # Process Pali footnotes
        if page["pali"]["footnotes"]:
            for footnote in page["pali"]["footnotes"]:
                footnote["Fp"] = f"{id_footer_pali}"
                ## sometimes, only 1 of the lang has footnote
                # so, use one id for footnote
                id_footer_pali += 1

        # Process Sinhala footnotes
        if page["sinh"]["footnotes"]:
            for footnote in page["sinh"]["footnotes"]:
                footnote["Fs"] = f"{id_footer_sinh}"
                id_footer_sinh += 1

    return json_data


def parse_line_for_id(line: str):
    line = line.strip()
    if not line:
        return None, None
    # Apply XML tag removal and clean up
    # <line id="821"> ##### Si 821 = End of the Commentary on the Mahāparinibbāna Sutta. </line>
    line = remove_line_xml_tag(line).strip().lstrip("#").strip()
    if not line:
        return None, None

    prefixes = {
        "Pi": r"^Pi \d+ = ",
        "Si": r"^Si \d+ = ",
        # Footer ids
        "Fp": r"^Fp \d+ = ",
        "Fs": r"^Fs \d+ = ",
    }

    # Iterate over prefixes to match line format
    for prefix, pattern in prefixes.items():
        if not re.match(pattern, line):
            continue
        # Split once and validate
        parts = line.split(" = ", 1)
        # Key has space
        key = parts[0].strip()
        value = parts[1].strip()

        # Validate key format: prefix + space + digits
        if key.startswith(prefix) and key[len(prefix) :].strip().isdigit():
            return key, value
    return None, None


def put_translation_to_id(
    json_file_path: str,
    trans_file: str,
    out_dir="attha_sinh_json_eng",
    lang_key: str = "sinh",
):

    lang_key = lang_key.strip()
    trans_dict = {}
    with open(trans_file, "r", encoding="utf-8") as file:
        for line in file:
            k, v = parse_line_for_id(line)
            if k and v:
                trans_dict[k] = f"{v}"

    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    has_not_found = False
    for page in json_data["pages"]:
        # only for removing empty pali ID
        for entry in page["pali"]["entries"]:
            if not "text" in entry:
                continue
            line = entry["text"].strip()
            if re.match(r"^Pi \d+ = ", line):
                pparts = line.split(" = ", 1)
                pli = pparts[1].strip()
                if pli == "@@":
                    entry["text"] = ""

        # put Eng trans of Sinh
        for entry in page[lang_key]["entries"]:
            line = entry["text"].strip()
            k, v = parse_line_for_id(line)
            if k and v:
                if k in trans_dict:
                    if trans_dict[k].strip():
                        # remove ID
                        if trans_dict[k].strip().lower() == "@@":
                            entry["text"] = ""
                        else:
                            entry["text"] = f"{k} = {trans_dict[k].strip()}"
                else:
                    print(
                        f"---NotFound: {k} in {trans_file} . Source has: {json_file_path} "
                    )
                    has_not_found = True

        # Process footnotes
        if page[lang_key]["footnotes"]:
            footer_key = f"F{lang_key[0].lower()}"
            for footnote in page[lang_key]["footnotes"]:
                if footer_key in footnote:
                    # key has a space
                    k = f"{footer_key} {footnote[footer_key]}"
                    if k in trans_dict:
                        footnote["text"] = f"{k} = {trans_dict[k]}"
                    else:
                        print(
                            f"---NotFound: {k} in {trans_file} . Source has: {json_file_path} "
                        )

                        has_not_found = True

    # save
    output_json_path = os.path.join(
        out_dir,
        os.path.splitext(os.path.basename(json_file_path))[0] + ".json",
    )

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    # print(f"Added translations to {json_file_path}")
    if has_not_found:
        print("\n")


def extract_sinh_to_markdown(json_file_path, output_directory):
    # Read JSON file
    with open(json_file_path, "r", encoding="utf-8") as file:
        input_json = json.load(file)

    # assign Si  to each
    modified_json = assign_ids_to_json(input_json)

    output_json_path = os.path.join(
        output_directory,
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
                            no_sfooter = footnote["Fs"]
                            # key has a space
                            out_file.write(f"Fs {no_sfooter} = {footnote['text']}\n")

            # Add page separator
            out_file.write("\n")


def prepare_atthakatha_json_files(
    input_directory="attha_sinh_json", output_directory="attha_sinh_mdjson_id"
):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs("attha_sinh_mdjson_id", exist_ok=True)
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


def prepare_mula_json_files(
    input_directory="mula_sinh_json", output_directory="mula_sinh_mdjson_id"
):

    os.makedirs(output_directory, exist_ok=True)
    os.makedirs("mula_sinh_json_eng", exist_ok=True)

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
    filter_pattern="_chunks_translated_1.xml",
    translated_dir="input",
    output_directory="output",
):
    os.makedirs(output_directory, exist_ok=True)

    # Ensure the input directory exists
    if not os.path.exists(translated_dir):
        print(f"Error: Directory '{translated_dir}' does not exist.")
        return

    # Get all JSON files in the directory
    translated_files = [
        f for f in os.listdir(translated_dir) if f.endswith(f"{filter_pattern}")
    ]

    # Process each JSON file
    for n, tr_file in enumerate(translated_files, 1):
        parts = re.split(r"_\d+_chunks_translated", tr_file, 1)
        if len(parts) != 2:
            print(f"Filename issue, skipped: {tr_file}")
            continue
        json_fn = f"{parts[0]}.json"
        json_id_path = os.path.join(translated_dir, json_fn)

        trans_path = os.path.join(translated_dir, tr_file)
        put_translation_to_id(json_id_path, trans_path, output_directory)
        print(f"{n}/{len(translated_files)} Done: {tr_file}")

    print(f"Processed {len(translated_files)} JSON files.")


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
    # prepare_mula_json_files()

    put_translation_json_files(
        translated_dir="mula_sinh_mdjson_id", output_directory="./mula_sinh_json_eng"
    )

    # prepare_atthakatha_json_files()
    # put_translation_json_files(translated_dir="attha_sinh_mdjson_id", output_directory = "attha_sinh_json_eng")

    # put_translation_to_id("attha_sinh_json_id/atta-an-1-14-3.json", "attha_sinh_md_id/atta-an-1-14-3_36_chunks_20250308_211731_gemini-2.0-flash.xml")
