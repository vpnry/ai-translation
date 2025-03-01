import re
import argparse
import sys
from pathlib import Path


def extract_ids_from_source_xml(xml_file: str) -> set:
    """Extract all ID numbers from the XML chunks file."""
    with open(xml_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all instances of <line id="number"> in the text
    id_pattern = r'<line id="(\d+)">'
    return set(map(int, re.findall(id_pattern, content)))


def extract_ids_from_translated_file(md_file: str) -> set:
    """Extract all ID numbers from the English markdown file."""
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all instances of <line id="number"> in the text
    id_pattern = r'<line id="(\d+)">'
    return set(map(int, re.findall(id_pattern, content)))


def check_translation_completeness(
    xml_source_file: str, xml_translated_file: str
) -> bool:
    """
    Check if all IDs from XML chunks exist in the English translation.
    Returns True if all IDs are present, False otherwise.
    """
    if not Path(xml_translated_file).exists():
        print(f"Error: Translation file not found: {xml_translated_file}")
        return False

    source_xml_ids = extract_ids_from_source_xml(xml_source_file)
    translated_ids = extract_ids_from_translated_file(xml_translated_file)

    # Find missing IDs
    missing_ids = source_xml_ids - translated_ids

    if missing_ids:
        print(f"❌ Missing translations for {len(missing_ids)} lines:")
        print(f"Missing IDs: {sorted(missing_ids)}")
        return False

    # Find extra IDs in MD that don't exist in XML
    extra_ids = translated_ids - source_xml_ids
    if extra_ids:
        print(f"⚠️ Warning: Found {len(extra_ids)} extra IDs in translation file:")
        print(f"Extra IDs: {sorted(extra_ids)}")

    print(f"✅ All {len(source_xml_ids)} lines are translated!")
    return True


def main():
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

    try:
        if not check_translation_completeness(
            args.xml_source_file, args.xml_translated_file
        ):
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
