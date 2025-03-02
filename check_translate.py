"""Check for any missing/additional translations in the translated XML file."""

import re
import argparse
import sys
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter


def check_fix_unclosed_tag(inputfile: str) -> bool:
    """Fix unclosed <line> tags in an XML file and save the corrected content.

    Args:
        inputfile (str): Path to the XML file to process

    Returns:
        bool: True if changes were made and saved, False otherwise
    """
    try:
        # Read file content once
        with open(inputfile, "r", encoding="utf-8") as f:
            content = f.read()

        # Compile regex pattern once
        unclosed_pattern = re.compile(r'(<line id="(\d+)">[^<\n]*)$', re.MULTILINE)

        # Find all matches and track if any changes needed
        matches = list(unclosed_pattern.finditer(content))
        print(f"\n--- Checking for unclosed tags in {inputfile}:")
        if not matches:
            print("Good! No unclosed tags found")
            return False

        # Print found issues
        for match in matches:
            print(f"Found unclosed tag at line ID: {match.group(2)}")

        # Ask for confirmation
        if (
            input(
                "Do you want to overwrite the XML file? A backup will be created (y/n): "
            ).lower()
            != "y"
        ):
            print("Operation cancelled. No changes saved.")
            return False

        # Create backup
        backup_file = f"{inputfile}_unclosed_backup.xml"
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Backup created: {backup_file}")

        # Fix content and save
        fixed_content = unclosed_pattern.sub(r"\1</line>", content)
        with open(inputfile, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        print(f"Overwritten: {inputfile}")

        return True

    except Exception as e:
        print(f"Error processing file: {e}")
        return False


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


def extract_ids_from_file(xml_file: str) -> tuple[set, dict]:
    """
    Extract all ID numbers from the XML file.
    Returns a tuple of (unique_ids, duplicate_ids_dict)
    """
    try:
        with open(xml_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all instances of <line id="number"> in the text
        id_pattern = r'<line id="(\d+)">'
        all_ids = [int(id_) for id_ in re.findall(id_pattern, content)]
        unique_ids = set(all_ids)

        # Find duplicates
        duplicates = {}
        for id_ in all_ids:
            if all_ids.count(id_) > 1:
                duplicates[id_] = all_ids.count(id_)

        return unique_ids, duplicates
    except Exception as e:
        print(f"Error reading source file: {e}")
        return set(), {}


def check_translation_completeness(
    xml_source_file: str, xml_translated_file: str
) -> bool:
    """
    Check if all IDs from XML chunks exist in the English translation.
    Also checks for duplicate IDs in both files.
    Returns True if all IDs are present and no duplicates found, False otherwise.
    """
    if not Path(xml_translated_file).exists():
        print(f"Error: Translation file not found: {xml_translated_file}")
        return False

    # sometimes AI forgets to close the </line> tag
    check_fix_unclosed_tag(xml_translated_file)

    source_xml_ids, source_duplicates = extract_ids_from_file(xml_source_file)
    translated_ids, translated_duplicates = extract_ids_from_file(xml_translated_file)

    if not source_xml_ids:
        print("Error: No IDs found in source file or file couldn't be read")
        return False

    has_errors = False

    # Check for duplicates in source file
    if source_duplicates:
        print("❌ Found duplicate IDs in source file:")
        for id_, count in sorted(source_duplicates.items()):
            print(f"  ID {id_} appears {count} times")
        has_errors = True

    # Check for duplicates in translated file
    if translated_duplicates:
        print("❌ Found duplicate IDs in translation file:")
        for id_, count in sorted(translated_duplicates.items()):
            print(f"  ID {id_} appears {count} times")
        has_errors = True

    # Find missing IDs
    missing_ids = source_xml_ids - translated_ids
    if missing_ids:
        print(f"❌ Missing translations for {len(missing_ids)} lines:")
        print(f"Missing IDs: {sorted(missing_ids)}")
        has_errors = True

    # Find extra IDs in translation that don't exist in source
    extra_ids = translated_ids - source_xml_ids
    if extra_ids:
        print(f"⚠️ Warning: Found {len(extra_ids)} extra IDs in translation file:")
        print(f"Extra IDs: {sorted(extra_ids)}")

    if not has_errors:
        print(f"✅ Found {len(source_xml_ids)} line ids == with the source file")
        return True
    

    return False


def main():
    # Setup path completer for file paths
    path_completer = PathCompleter()

    # Interactive mode if no arguments provided
    if len(sys.argv) == 1:
        print("Interactive mode - Use path completion with Tab key")
        xml_source_file = get_validated_input(
            "Enter the source XML chunks file path: ", completer=path_completer
        )
        xml_translated_file = get_validated_input(
            "Enter the translated file path: ", completer=path_completer
        )
    else:
        # Command line argument mode
        parser = argparse.ArgumentParser(
            description="Check if all lines from XML chunks are translated in English.md"
        )
        parser.add_argument(
            "xml_source_file",
            type=str,
            help="Path to the source XML chunks file (e.g., file_chunks_2000.xml)",
        )
        parser.add_argument(
            "xml_translated_file",
            type=str,
            help="Path to the translated file (e.g., chunks_2000_tranlated_1.xml)",
        )
        args = parser.parse_args()
        xml_source_file = args.xml_source_file
        xml_translated_file = args.xml_translated_file

    try:
        if not check_translation_completeness(xml_source_file, xml_translated_file):
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
