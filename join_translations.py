import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.validation import Validator, ValidationError
from unidecode import unidecode

from check_translate import check_translation_completeness


def extract_id_and_text(line: str) -> Tuple[Optional[int], Optional[str]]:
    """Extract ID and text from a line tag with an id attribute, handling both closed and unclosed cases."""

    match = re.match(r'<line id="(\d+)">(.*?)(?:</line>)?$', line.strip())

    if match:
        line_id = int(match.group(1))
        text = match.group(2).strip() if match.group(2) else None
        return line_id, text

    return None, None  # Return None if no valid <line> tag is found


def get_heading_level(text: str) -> Optional[int]:
    """Get heading level from text starting with #"""
    if not text.startswith("#"):
        return None
    count = len(text) - len(text.lstrip("#"))
    return count if 0 < count <= 6 else None


def get_lines_dict_from_file(file_path: Path) -> Dict[int, str]:
    """Read XML file and return dictionary of ID -> text mappings"""
    lines = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                id_num, text = extract_id_and_text(line)
                if id_num:
                    if id_num in lines:
                        print(
                            f"Warning: Duplicate ID {id_num} found in {file_path.name}.  Overwriting previous entry."
                        )
                    lines[id_num] = text.strip()
        print(
            f"Final check by joiner: {len(lines.keys())} line IDs in: {file_path.name}\n\n"
        )
        return lines
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
        return {}


def escape_dot_li(text):
    """
    Replaces the first '.' with '\.' only if it appears immediately after a number at the start of the text.
    This is to fix pandoc adding li to the heading
    """
    return re.sub(r"^(\d+)\.", r"\1\.", text)


def create_multilingual_md(source_file: str, num_translations: int = 3) -> None:
    """Create multilingual markdown from source and target files"""
    print(f"\n** Creating a markdown file with {num_translations}-translations...")

    source_path = Path(source_file)
    if not source_path.exists():
        print(f"Error: Source file {source_file} not found")
        return

    base_name = source_path.stem
    md_output_file = source_path.parent / f"{base_name}_{num_translations}_translations.md"

    # Read source and translation files
    source_lines = get_lines_dict_from_file(source_path)
    translations = []
    for i in range(1, num_translations + 1):
        trans_file = source_path.parent / f"{base_name}_translated_{i}.xml"

        check_translation_completeness(source_file, str(trans_file))

        translations.append(get_lines_dict_from_file(trans_file))

    with open(md_output_file, "w", encoding="utf-8") as fo:

        # Write content
        for id_num in sorted(source_lines.keys()):
            fo.write(f"<p><i>ID{id_num}</i></p>\n\n")
            source_text = source_lines[id_num]

            heading_num = get_heading_level(source_text)
            if heading_num:
                # Create heading ID based on text content, removing special chars and spaces
                heading_text = source_text.strip().lstrip("#").strip()

                heading_id = re.sub(
                    r"[^a-zA-Z0-9]+", "-", unidecode(heading_text.lower()).lower()
                ).strip("-")

                # Add ID number to ensure uniqueness for same text

                heading_id = f"{heading_id}-id{id_num}"
                fo.write(
                    f"<h{heading_num} id='{heading_id}' class='hs'>{escape_dot_li(heading_text)}</h{heading_num}>\n\n"
                )

                for x, trans in enumerate(translations, 1):
                    trans_text = (
                        trans.get(
                            id_num, f"[MISSING TRANSLATION in translated file {x}]"
                        )
                        .strip()
                        .lstrip("#")
                        .strip()
                    )
                    trans_h_id = re.sub(
                        r"[^a-zA-Z0-9]+", "-", unidecode(trans_text).lower()
                    ).strip("-")

                    # Add ID number to ensure uniqueness for same text
                    trans_h_id = f"{trans_h_id}-id{id_num}-t{x}"

                    fo.write(
                        f"<h{heading_num} id='{trans_h_id}' class='ht ht{x}'>{escape_dot_li(trans_text)}</h{heading_num}>\n\n"
                    )
            else:
                fo.write(f"<p class='s1'>{escape_dot_li(source_text)}</p>\n\n")
                for i, trans in enumerate(translations, 1):
                    trans_t_i = trans.get(
                        id_num, f"[MISSING TRANSLATION in translated file {i}]"
                    )
                    fo.write(f"<p class='t{i}'>{escape_dot_li(trans_t_i)}</p>\n\n")

            fo.write("---\n\n")

        # Write footer
        fo.flush()

    print(f"\n=== Multilingual markdown created: {md_output_file}")
    print(f"\n\nTo convert to HTML (Tipitakapali.org template):\n\npython3 gen_tpo_html.py --md-file {md_output_file} --translations {num_translations} --title TITLE_HERE")
    print(
        f"\n** Or using pandoc CLI"
    )


class NumberValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message="Please enter a number")
        try:
            num = int(text)
            if num < 1:
                raise ValidationError(message="Number must be greater than 0")
        except ValueError:
            raise ValidationError(message="Please enter a valid number")


def get_validated_input(message: str, validator=None, completer=None) -> str:
    """Get input with validation and completion"""
    try:
        return prompt(
            message,
            validator=validator,
            completer=completer,
            complete_while_typing=True,
        ).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled by user")
        sys.exit(0)


def main():
    # Interactive mode if no arguments provided
    if len(sys.argv) == 1:
        print("Interactive mode - Use path completion with Tab key")
        path_completer = PathCompleter()
        number_validator = NumberValidator()

        xml_source_file = get_validated_input(
            "Enter the source XML chunks file path: ", completer=path_completer
        )
        num_translations = int(
            get_validated_input(
                "Enter the number of translations to include: ",
                validator=number_validator,
            )
        )

        # Create the markdown file
        create_multilingual_md(xml_source_file, num_translations=num_translations)
    else:
        # Command line argument mode
        parser = argparse.ArgumentParser(
            description="Create multilingual markdown from source and target files",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "xml_source_file",
            help="Source language file (format: name_n_chunks.xml)",
            type=str,
        )
        parser.add_argument(
            "-n",
            "--translations",
            help="Number of translated files to include",
            type=int,
            required=True,
        )

        args = parser.parse_args()

        # Create the markdown file
        create_multilingual_md(
            args.xml_source_file, num_translations=args.translations
        )


if __name__ == "__main__":
    main()
