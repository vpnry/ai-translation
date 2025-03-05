"""Convert markdown into HTML (dictionary function and TOC like the tipitakapali.org)
- Should use only #RRGGBB color codes for colors so that the Microsoft Words can display them correctly

"""

import re
import sys
import os
import argparse

from datetime import datetime
from typing import Tuple
from pathlib import Path

import pypandoc
from unidecode import unidecode
from bs4 import BeautifulSoup


def replace_smart_quotes_md(md_filepath) -> str:
    """
    Replaces smart quotes in a file with their HTML entity equivalents.

    VRI use smart quotes which causes **‘‘text** bold format issues. This use html to fix them
    """
    try:
        fix_quotes_save = str(md_filepath) + "_fixed_quotes.md"

        with open(md_filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Perform the replacements
        content = content.replace("‘‘", "&ldquo;")
        content = content.replace("’’", "&rdquo;")

        # Replace en dash (–) with hyphen (-)
        # content = content.replace("–", "-")

        with open(fix_quotes_save, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nSmart quotes replaced with HTML entities in {md_filepath}")

    except FileNotFoundError:
        print(f"Error: File not found at {md_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return fix_quotes_save


def convert_markdown_to_html(md_file, output_file):
    """Converts a Markdown file to HTML using pypandoc."""

    fixed_smart_quotes_filepath = replace_smart_quotes_md(md_file)

    try:
        output = pypandoc.convert_file(
            fixed_smart_quotes_filepath,
            to="html",
            outputfile=output_file,
            extra_args=["--wrap=none"],
        )
        if output == "":
            print(f"\nSuccessfully converted {md_file} to {output_file}")
        else:
            print(f"Conversion may have warnings: {output}")
    except RuntimeError as e:
        print(f"Error during conversion: {e}")


def generate_translation_info(md_file, num_translations: int):
    # script to hide/show translations
    translation_toggles = "\n".join(
        [
            f'<label style="margin-right: 15px; padding: 2px 6px; border-radius: 4px;"><input type="checkbox" id="toggle_t{i}" checked onchange="toggleTranslation({i})">Translation {i}</label>'
            for i in range(1, num_translations + 1)
        ]
    )

    # showing translation order/format
    source_path = Path(md_file)
    if not source_path.exists():
        print(f"Error: Source file {md_file} not found")
        return "", ""
    base_name = source_path.stem
    base_name = str(base_name).split("_chunks_")
    if (len(base_name)) != 2:
        print("Not standard named {md_file}")
    base_name = base_name[0]

    translations_order = []
    for i in range(1, num_translations + 1):
        trans_number_i = source_path.parent / f"{base_name}_chunks_translated_{i}.xml"
        try:
            with open(trans_number_i, "r", encoding="utf-8") as f:
                file_content = f.read()
                # Use regex to find the <info> block.  The `re.DOTALL` flag makes . match newlines.
                info_match = re.search(r"<info>(.*?)</info>", file_content, re.DOTALL)
                if info_match:
                    info_block = info_match.group(1)  # Get the content inside <info>
                    # Find the TranslatedBy line within the <info> block.
                    translator_match = re.search(r"TranslatedBy=(.+)", info_block)
                    if translator_match:
                        translator = translator_match.group(1).strip()
                        translations_order.append(
                            f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">'
                            f'Translation {i}: <span style="color: #066a06;">{translator}</span></p>'
                        )
                        print(f"{trans_number_i} by: {translator}")
                    else:
                        # Handle case of no TranslatedBy= line.
                        print(f"Could not find TranslatedBy= line in {trans_number_i}")

                        translations_order.append(
                            f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">'
                            f'Translation {i}: <span style="color: #8b0000;">AI {i} (DD MM YYY)</span></p>'
                        )
                else:
                    # Handle case of no <info> tag
                    print(f"Could not find <info> tag in {trans_number_i}")

                    translations_order.append(
                        f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">'
                        f'Translation {i}: <span style="color: #8b0000;">AI {i} (DD MM YYY)</span></p>'
                    )

        except FileNotFoundError:
            print(f"File note found {trans_number_i}")
            translations_order.append(
                f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">'
                f'Translation {i}: <span style="color: #8b0000;">AI {i} (DD MM YYY)</span></p>'
            )
        except Exception as e:
            # Catch any other exceptions during file processing.
            print(f"File processing error: {trans_number_i}")

            translations_order.append(
                f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">'
                f'Translation {i}: <span style="color: #8b0000;">AI {i} (DD MM YYY)</span></p>'
            )
    return translation_toggles, "\n".join(translations_order)


def add_toc(html_file_path, output_file_path=None):
    """
    Adds a Table of Contents (TOC) to an HTML file.

    Args:
        html_file_path: Path to the input HTML file.
        output_file_path: (Optional) Path to save the modified HTML.
                          If None, overwrites the input file.
    """
    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Find the TOC div
        toc_div = soup.find("div", id="tocDivBox")

        if toc_div is None:
            raise ValueError("Could not find div with id='tocDivBox'")

        toc_list = soup.new_tag("ul")

        # Find all heading tags (h1, h2, h3, h4, h5)
        headings = soup.find_all(re.compile(r"^h[1-5]$"))

        for heading in headings:

            # Get the heading text and ID
            heading_text = heading.get_text(strip=True)
            heading_id = heading.get("id")

            if heading_id is None:
                # print(f"Warning: Heading '{heading_text}' has no ID. Skipping in TOC.")
                continue  # Skip headings without id

            # Create a list item for the TOC
            list_item = soup.new_tag("li")
            # Add style according heading level.
            if heading.name == "h1":
                list_item["style"] = "margin-left: 0em;"
            elif heading.name == "h2":
                list_item["style"] = "margin-left: 1em;"
            elif heading.name == "h3":
                list_item["style"] = "margin-left: 2em;"
            elif heading.name == "h4":
                list_item["style"] = "margin-left: 3em;"
            elif heading.name == "h5":
                list_item["style"] = "margin-left: 4em;"

            # Create a link to the heading
            link = soup.new_tag("a", href=f"#{heading_id}")
            link.string = heading_text

            if "hs" in heading.get("class", []):
                list_item["class"] = list_item.get("class", []) + ["stoc"]
            elif "ht" in heading.get("class", []):
                # Remove "ht" and add "ttoc"
                current_classes = heading.get("class", [])
                list_item["class"] = ["ttoc"] + [c for c in current_classes if c != "ht"]
            else:
                pass

            list_item.append(link)
            toc_list.append(list_item)

        # Add the TOC list to the TOC div
        # toc_div.append(copy.deepcopy(toc_list))
        toc_div.append(toc_list)

        # Save the modified HTML (either overwrite or to a new file)
        if output_file_path is None:
            output_file_path = html_file_path  # Overwrite

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"TOC added and saved to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: File not found: {html_file_path}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def convert_addTOC(
    md_file,
    file_title,
    output_file=None,
    num_translations=4,
    tpo_template="./tpo_html_template.html",
):
    """Convert Markdown to HTML, add TOC, and apply translations template."""

    # If output_file is not provided, derive it from md_file
    if output_file is None:

        output_file = os.path.splitext(md_file)[0] + ".html"
        print(f"OK: No output html filename provided, using {output_file}")

    convert_markdown_to_html(md_file, output_file)

    # Manually update the template
    TRANSLATIONS_TOGGLE, TRANSLATIONS_ORDER = generate_translation_info(
        md_file, num_translations=num_translations
    )

    print(f"\n\nUsing {tpo_template}")

    with open(tpo_template, "r", encoding="utf-8") as tpo:
        html = tpo.read()

    # Generate dynamic file titles
    FILE_HTML_TITLE_TAG = f"{file_title.title()}-Pali-Eng-AI-Generated-Translations"
    FILE_HTML_TITLE_TAG = unidecode(FILE_HTML_TITLE_TAG.lower()).lower()

    FILE_PAGE_TITLE = f"{file_title.title()}"
    FILE_PAGE_SUBTITLE = "(Pāḷi-English AI-Generated Translations)"
    FILE_HTML_DESCRIPTION = f"{FILE_PAGE_TITLE} Pāḷi-English (AI Translations)"

    # Replace placeholders in the HTML template
    html = (
        html.replace("$FILE_HTML_TITLE_TAG", FILE_HTML_TITLE_TAG)
        .replace("$FILE_HTML_DESCRIPTION", FILE_HTML_DESCRIPTION)
        .replace("$FILE_PAGE_TITLE", FILE_PAGE_TITLE)
        .replace("$FILE_PAGE_SUBTITLE", FILE_PAGE_SUBTITLE)
        .replace("$TRANSLATIONS_TOGGLE", TRANSLATIONS_TOGGLE)
        .replace("$TRANSLATIONS_ORDER", TRANSLATIONS_ORDER)
        .replace(
            "$FILE_LAST_MODIFIED",
            f"This file was last modified on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
    )

    # Inject the converted HTML content
    with open(output_file, "r", encoding="utf-8") as fhtml:
        html = html.replace("$FILE_HTML", fhtml.read())

    # Save the final HTML file
    with open(output_file, "w", encoding="utf-8") as fdone:
        fdone.write(html)

    # Adding TOC
    add_toc(output_file)

    print(f"\nDone all. Check {output_file}")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with TOC and translations support"
    )

    parser.add_argument(
        "--md-file", required=True, help="Input Markdown file to convert"
    )

    parser.add_argument("--title", required=True, help="Title for the HTML document")

    parser.add_argument(
        "--translations",
        type=int,
        help="Number of translations to include (default: 4)",
        default=4,
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output HTML file (default: input filename with .html extension)",
        default=None,
    )

    parser.add_argument(
        "--template",
        help="Custom HTML template file (default: ./tpo_html_template.html)",
        default="./tpo_html_template.html",
    )

    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> Tuple[str, str, str]:
    """Validate input arguments and return processed values."""
    input_md_file = args.md_file
    template_file = args.template

    if not os.path.exists(input_md_file):
        raise FileNotFoundError(f"Input file not found: {input_md_file}")

    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Generate output filename if not provided
    output_file = (
        args.output if args.output else os.path.splitext(input_md_file)[0] + ".html"
    )

    # Use input filename as title if not provided
    title = (
        args.title
        if args.title
        else os.path.splitext(os.path.basename(input_md_file))[0]
    )

    return input_md_file, output_file, title


def main():
    """Main entry point for the script."""
    try:
        args = parse_arguments()
        md_file, output_file, title = validate_inputs(args)

        convert_addTOC(
            md_file=md_file,
            file_title=title,
            output_file=output_file,
            num_translations=args.translations,
            tpo_template=args.template,
        )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
