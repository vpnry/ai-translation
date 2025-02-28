import argparse
import re
import sys
from pathlib import Path


def extract_id_and_text(line):
    """Extract ID and text from a line containing ID{number}="""
    match = re.match(r"ID(\d+)=\s*(.*)", line.strip())
    if match:
        return int(match.group(1)), match.group(2)
    return None, None


def get_heading_level(text):
    """Get heading level from text starting with #"""
    if not text.startswith("#"):
        return None
    count = 0
    for char in text:
        if char == "#":
            count += 1
        else:
            break
    return count if count > 0 and count <= 6 else None


def create_bilingual_md(source_file):
    """Create bilingual markdown from source and a target file"""

    print("\n\n** Creating bilingual markdown file..")

    # Derive paths
    source_path = Path(source_file)
    if not source_path.exists():
        print(f"Error: Source file {source_file} not found")
        sys.exit(1)

    # Get base name without _chunks.xml
    base_name = source_path.stem

    print(base_name)
    target_file = source_path.parent / f"{base_name}_tranlated_1.xml"
    output_file = source_path.parent / f"{base_name}_bilingual.md"

    # Read source and target files
    source_lines = {}
    target_lines = {}
    missing_ids = []

    # Read source file
    with open(source_file, "r", encoding="utf-8") as fsource:
        for line in fsource:
            id_num, text = extract_id_and_text(line)
            if id_num:
                source_lines[id_num] = text.strip()
    print(f"Source total IDs: {len(source_lines.keys())}")

    # Read target file 1
    try:
        with open(target_file, "r", encoding="utf-8") as fo:
            for line in fo:
                id_num, text = extract_id_and_text(line)
                if id_num:
                    target_lines[id_num] = text.strip()
    except FileNotFoundError:
        print(f"Warning: Translated file 1 {target_file} not found")
        return
    print(f"Translated file 1 total IDs: {len(target_lines.keys())}")

    # Check for missing translated IDs in the translated file 1
    for id_num in source_lines:
        if id_num not in target_lines:
            missing_ids.append(id_num)

    if missing_ids:
        print(
            f"\n⚠️  Missing {len(missing_ids)} IDs translation file 1 (Grok3 ?).\nThey are:",
            missing_ids,
        )
    else:
        print("[✅]: No missing translated IDs in the translated file 1")

    # Create trilingual markdown
    with open(output_file, "w", encoding="utf-8") as fo:
        # adding styles and meta tags
        # fo.write("""<!DOCTYPE html>\n\n""")
        fo.write("""<html lang="en">\n\n""")
        fo.write("""<head>\n\n""")
        fo.write("""<meta charset="UTF-8">\n\n""")
        fo.write(
            """<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\n"""
        )
        fo.write(f"""<title>{base_name}</title>\n\n""")
        fo.write(
            """<style>body {font-size: medium; font-family: 'Noto Sans', 'DejaVu Sans', 'Times Ext Roman', 'Indic Times', 'Doulos SIL', Tahoma, 'Arial Unicode MS', Gentium;} .s1 {text-align: left;border-left: 5px solid rgba(160, 82, 45, 0.5);  padding-left: 5px;background:linear-gradient(to right, transparent, rgba(160, 82, 45, 0.3), transparent);} .t1,.t2, .t3 {text-align: justify;} a {text-decoration: none;}</style><link href="https://tipitakapali.org/web/tp.css" rel="stylesheet" /><script src="https://tipitakapali.org/web/theme.js"></script>\n\n"""
        )
        fo.write("""</head><body>\n\n""")

        # for displaying dictionary div and floating toc button from (tipitakapali.org)
        fo.write(
            """<div id="dictionary-res"></div><p id="floatingTocButton"> 📜 </p><div id="tocDivBox" style="display: block;"></div>\n\n"""
        )

        # book title decoration
        fo.write(
            f"""<div style="border: 2px solid #8B4513; border-radius: 8px; padding: 20px; background: linear-gradient(to bottom, #FFF8DC, #FAEBD7); box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 800px;">
<h2 style="color: #8B4513; text-align: center; margin-bottom: 15px; font-size: 28px;">{base_name}</h2>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">

<p style="color: #DC3545; font-weight: bold; text-align: center; font-size: 16px; margin: 15px 0;">WARNING: THIS IS AN AI-TRANSLATED EXPERIMENT.</p>
<p>
Please do not blindly trust the LLM output. LLMs can produce errors. If you are uncertain, refer to the original Pāḷi text for verification.<br>
The main purpose of this page is to facilitate quick searches using English keywords to locate relevant Pāḷi passages. Searching in English is more convenient for us.
</p>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">
<p style="color: #444; font-size: 14px; margin: 8px 0;">
Code files for text processing: <span style="color: #0077ff;"><a href="https://github.com/vpnry/ai-translation" target="_blank">https://github.com/vpnry/ai-translation</a></span> (25 Feb 2025)
</p>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">

<p style="color: #444; font-size: 14px; margin: 8px 0;" class="s1">Source text: <a href="https://example.com" target="_blank">Your source text here</a> (DD MM YYYY)</p>

<p style="color: #444; font-size: 14px; margin: 8px 0;">Translation 1: <span style="color: #006400;">AI 1</span> (DD MM YYYY))</p>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">

</div>\n\n"""
        )
        fo.write(f"--- \n\n")

        for id_num in sorted(source_lines.keys()):

            fo.write(f"<p><i>ID{id_num}</i></p>\n\n")

            source_text = source_lines[id_num]
            heading_level = get_heading_level(source_text)

            if heading_level:
                # clean_text = source_text.lstrip("#").strip()
                fo.write(f"{source_text}\n\n")
                fo.write(
                    f"{target_lines.get(id_num, '[Translated file 1: MISSING TRANSLATION]').strip()}\n\n"
                )
            else:
                fo.write(f"<p class='s1'>{source_text}</p>\n\n")
                fo.write(
                    f"<p class='t1'>{target_lines.get(id_num, '[Translated file 1: MISSING TRANSLATION]')}</p>\n\n"
                )
            fo.write("---\n\n")
        #  for dictionary function from tipitakapali.org
        fo.write(
            """<script defer="" src="https://tipitakapali.org/web/paliscriptconverter_edited.js"></script><script defer="" src="https://tipitakapali.org/web/handleClick.js"></script><script defer="" src="https://tipitakapali.org/web/renderer.js"></script>"""
        )

        fo.write("</body></html>")

    print(f"Bilingual markdown created: {output_file}")


def create_trilingual_md(source_file):
    """Create trilingual markdown from source and target files (translated to English by Grok3 and Gemini)"""

    print("\n\n** Creating trilingual markdown file..")

    # Derive paths
    source_path = Path(source_file)
    if not source_path.exists():
        print(f"Error: Source file {source_file} not found")
        sys.exit(1)

    base_name = source_path.stem

    output_file_trilang = source_path.parent / f"{base_name}_trilingual.md"

    # translated files
    translated_file_1 = source_path.parent / f"{base_name}_tranlated_1.xml"
    translated_file_2 = source_path.parent / f"{base_name}_tranlated_2.xml"
    translated_file_3 = source_path.parent / f"{base_name}_tranlated_3.xml"

    # Read source and target files
    source_lines = {}

    lines_translated_file_1 = {}
    lines_translated_file_2 = {}
    lines_translated_file_3 = {}

    missing_ids = []
    missing_ids_gemini = []
    missing_ids_deepseek = []

    # Read source file
    with open(source_file, "r", encoding="utf-8") as fsource:
        for line in fsource:
            id_num, text = extract_id_and_text(line)
            if id_num:
                source_lines[id_num] = text.strip()

    print(f"Source total IDs: {len(source_lines.keys())}")

    # Read target file 1
    try:
        with open(translated_file_1, "r", encoding="utf-8") as fo:
            for line in fo:
                id_num, text = extract_id_and_text(line)
                if id_num:
                    lines_translated_file_1[id_num] = text.strip()
    except FileNotFoundError:
        print(f"Warning: Translated file 1 {translated_file_1} not found")
        return
    print(f"Translated file 1 total IDs: {len(lines_translated_file_1.keys())}")

    # Translated file 2
    try:
        with open(translated_file_2, "r", encoding="utf-8") as f2:
            for line in f2:
                id_num, text = extract_id_and_text(line)
                if id_num:
                    lines_translated_file_2[id_num] = text.strip()

    except FileNotFoundError:
        print(f"Warning: Translated file 2 {translated_file_2} not found")
        print("Exiting...not creating trilingual markdown file")
        return

    print(f"Translated file 2 total IDs: {len(lines_translated_file_2.keys())}")

    # Translated file 3
    try:
        with open(translated_file_3, "r", encoding="utf-8") as f3:
            for line in f3:
                id_num, text = extract_id_and_text(line)
                if id_num:
                    lines_translated_file_3[id_num] = text.strip()

    except FileNotFoundError:
        print(f"Warning: Translated file 3 {translated_file_3} not found")
    print(f"Translated file 3 total IDs: {len(lines_translated_file_3.keys())}")

    # Check for missing translated IDs in the translated file 1
    for id_num in source_lines:
        if id_num not in lines_translated_file_1:
            missing_ids.append(id_num)

    if missing_ids:
        print(
            f"\n⚠️  Missing {len(missing_ids)} IDs translation file 1 (Grok3 ?).\nThey are:",
            missing_ids,
        )
    else:
        print("[✅]: No missing translated IDs in the translated file 1")

    # Check for missing translated IDs in the translated file 2
    for id_num in source_lines:
        if id_num not in lines_translated_file_2:
            missing_ids_gemini.append(id_num)

    if missing_ids_gemini:
        print(
            f"\n⚠️  Missing {len(missing_ids_gemini)} IDs translation file 2 (_Gemini ?).\nThey are:",
            missing_ids_gemini,
        )
    else:
        print("[✅]: No missing translated IDs in the translated file 2")

    # Check for missing translated IDs in the translated file 3
    for id_num in source_lines:
        if id_num not in lines_translated_file_3:
            missing_ids_deepseek.append(id_num)

    if missing_ids_deepseek:
        print(
            f"\n⚠️  Missing {len(missing_ids_deepseek)} IDs translation file 3 (_Deepseek ?).\nThey are:",
            missing_ids_deepseek,
        )
    else:
        print("[✅]: No missing translated IDs in the translated file 3")

    # Create trilingual markdown
    with open(output_file_trilang, "w", encoding="utf-8") as fo:
        # adding styles and meta tags
        # fo.write("""<!DOCTYPE html>\n\n""")
        fo.write("""<html lang="en">\n\n""")
        fo.write("""<head>\n\n""")
        fo.write("""<meta charset="UTF-8">\n\n""")
        fo.write(
            """<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\n"""
        )
        fo.write(f"""<title>{base_name}</title>\n\n""")
        fo.write(
            """<style>body {font-size: medium; font-family: 'Noto Sans', 'DejaVu Sans', 'Times Ext Roman', 'Indic Times', 'Doulos SIL', Tahoma, 'Arial Unicode MS', Gentium;} .s1 {text-align: left;border-left: 5px solid rgba(160, 82, 45, 0.5);  padding-left: 5px;background:linear-gradient(to right, transparent, rgba(160, 82, 45, 0.3), transparent);} .t1,.t2, .t3 {text-align: justify;} a {text-decoration: none;}</style><link href="https://tipitakapali.org/web/tp.css" rel="stylesheet" /><script src="https://tipitakapali.org/web/theme.js"></script>\n\n"""
        )
        fo.write("""</head><body>\n\n""")

        # for displaying dictionary div and floating toc button from (tipitakapali.org)
        fo.write(
            """<div id="dictionary-res"></div><p id="floatingTocButton"> 📜 </p><div id="tocDivBox" style="display: none;"></div>\n\n"""
        )

        # book title decoration
        fo.write(
            f"""<div style="border: 2px solid #8B4513; border-radius: 8px; padding: 20px; background: linear-gradient(to bottom, #FFF8DC, #FAEBD7); box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 800px;">
<h2 style="color: #8B4513; text-align: center; margin-bottom: 15px; font-size: 28px;">{base_name}</h2>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">

<p style="color: #DC3545; font-weight: bold; text-align: center; font-size: 16px; margin: 15px 0;">WARNING: THIS IS AN AI-TRANSLATED EXPERIMENT.</p>
<p>
Please do not blindly trust the LLM output. LLMs can produce errors. If you are uncertain, refer to the original Pāḷi text for verification.<br>
The main purpose of this page is to facilitate quick searches using English keywords to locate relevant Pāḷi passages. Searching in English is more convenient for us.
</p>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">
<p style="color: #444; font-size: 14px; margin: 8px 0;">
Code files for text processing: <span style="color: #0077ff;"><a href="https://github.com/vpnry/ai-translation" target="_blank">https://github.com/vpnry/ai-translation</a></span> (25 Feb 2025)
</p>

<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">

<p style="color: #444; font-size: 14px; margin: 8px 0;" class="s1">Source text: <a href="https://example.com" target="_blank">Your source text here</a> (DD MM YYYY)</p>

<p style="color: #444; font-size: 14px; margin: 8px 0;">Translation 1: <span style="color: #006400;">AI 1</span> (DD MM YYYY)</p>
<p style="color: #444; font-size: 14px; margin: 8px 0;">Translation 2: <span style="color: #006400;">AI 2</span> (DD MM YYYY)</p>
<p style="color: #444; font-size: 14px; margin: 8px 0;">Translation 3: <span style="color: #006400;">AI 3 </span> (DD MM YYYY)</p>
<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #8B4513, transparent); margin: 15px 0;">
</div>\n\n"""
        )
        fo.write(f"--- \n\n")

        for id_num in sorted(source_lines.keys()):

            fo.write(f"<p><i>ID{id_num}</i></p>\n\n")

            source_text = source_lines[id_num]
            heading_level = get_heading_level(source_text)

            if heading_level:
                # clean_text = source_text.lstrip("#").strip()
                fo.write(f"{source_text}\n\n")
                fo.write(
                    f"{lines_translated_file_1.get(id_num, '[Translated file 1: MISSING TRANSLATION]').strip()}\n\n"
                )
                fo.write(
                    f"{lines_translated_file_2.get(id_num, '[Translated file 2: MISSING TRANSLATION]').strip()}\n\n"
                )
                fo.write(
                    f"{lines_translated_file_3.get(id_num, '[Translated file 3: MISSING TRANSLATION]').strip()}\n\n"
                )
            else:
                fo.write(f"<p class='s1'>{source_text}</p>\n\n")
                fo.write(
                    f"<p class='t1'>{lines_translated_file_1.get(id_num, '[Translated file 1: MISSING TRANSLATION]')}</p>\n\n"
                )
                fo.write(
                    f"<p class='t2'>{lines_translated_file_2.get(id_num, '[Translated file 2: MISSING TRANSLATION]')}</p>\n\n"
                )
                fo.write(
                    f"<p class='t3'>{lines_translated_file_3.get(id_num, '[Translated file 3: MISSING TRANSLATION]')}</p>\n\n"
                )

            fo.write("---\n\n")
        #  for dictionary function from tipitakapali.org
        fo.write(
            """<script defer="" src="https://tipitakapali.org/web/paliscriptconverter_edited.js"></script><script defer="" src="https://tipitakapali.org/web/handleClick.js"></script><script defer="" src="https://tipitakapali.org/web/renderer.js"></script>"""
        )

        fo.write("</body></html>")

    print(f"Trilingual markdown created: {output_file_trilang}")


def main():
    parser = argparse.ArgumentParser(
        description="Create bilingual markdown from source and target files"
    )
    parser.add_argument(
        "source_file", help="Source language file (format: name_chunks.xml)"
    )
    args = parser.parse_args()

    create_bilingual_md(args.source_file)
    create_trilingual_md(args.source_file)


if __name__ == "__main__":
    main()

    print(
        "\n** Done! To it convert into HTML: pandoc in.md -o out.html --toc --toc-depth=3"
    )
    print("** And to add TOC: python3 addToc.py out.html\n")
