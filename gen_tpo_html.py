"""Convert markdown into HTML (dictionary function and TOC like the tipitakapali.org)
- Should use only #RRGGBB color codes for colors so that the Microsoft Words can display them correctly

"""

import re
from bs4 import BeautifulSoup
import sys
import os
import pypandoc
import argparse
from typing import Tuple


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
        with open(fix_quotes_save, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nSmart quotes replaced with HTML entities in {md_filepath}")

    except FileNotFoundError:
        print(f"Error: File not found at {md_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return fix_quotes_save


def convert_markdown_to_html(input_file, output_file):
    """Converts a Markdown file to HTML using pypandoc."""

    fixed_smart_quotes_filepath = replace_smart_quotes_md(input_file)

    try:
        output = pypandoc.convert_file(
            fixed_smart_quotes_filepath,
            to="html",
            outputfile=output_file,
            extra_args=["--toc", "--toc-depth=5", "--wrap=none"],
        )
        if output == "":
            print(f"\nSuccessfully converted {input_file} to {output_file}")
        else:
            print(f"Conversion may have warnings: {output}")
    except RuntimeError as e:
        print(f"Error during conversion: {e}")


def generate_translation_info(num_translations: int) -> str:
    # script to hide/show translations

    translation_toggles = "\n".join(
        [
            f'<label style="margin-right: 15px; padding: 2px 6px; border-radius: 4px;"><input type="checkbox" id="toggle_t{i}" checked onchange="toggleTranslation({i})">Translation {i}</label>'
            for i in range(1, num_translations + 1)
        ]
    )
    # translation_toggles = "\n".join(
    #     [
    #         f'<label style="margin-right: 15px;"><input type="checkbox" id="toggle_t{i}" checked onchange="toggleTranslation({i})">Translation {i}</label>'
    #         for i in range(1, num_translations + 1)
    #     ]
    # )
    # showing translation order/format
    translations_order = "\n".join(
        [
            f'<p style="color: #444; font-size: 14px; margin: 8px 0;" class="t{i}">Translation {i}: <span style="color: #006400;">AI {i}</span> (DD MM YYYY)</p>'
            for i in range(1, num_translations + 1)
        ]
    )

    return translation_toggles, translations_order


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
            list_item.append(link)
            toc_list.append(list_item)
            # toc_list.append(soup.new_tag('li'))

        # Add the TOC list to the TOC div
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
    md_file, file_title, num_translations=4, tpo_template="./tpo_html_template.html"
):
    html_output = os.path.splitext(md_file)[0] + ".html"

    convert_markdown_to_html(md_file, html_output)

    # manually update the template

    TRANSLATIONS_TOGGLE, TRANSLATIONS_ORDER = generate_translation_info(
        num_translations=num_translations
    )

    with open(tpo_template, "r", encoding="utf-8") as tpo:
        html = tpo.read()
    html = html.replace("$FILE_TITLE", file_title).replace(
        "$TRANSLATIONS_TOGGLE", TRANSLATIONS_TOGGLE
    )

    html = html.replace("$TRANSLATIONS_ORDER", TRANSLATIONS_ORDER)

    with open(html_output, "r", encoding="utf-8") as fhtml:
        html = html.replace("$FILE_HTML", fhtml.read())

    with open(html_output, "w", encoding="utf-8") as fdone:
        fdone.write(html)

    # adding TOC
    add_toc(html_output)

    print(f"\nDone all. Check {html_output}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with TOC and translations support"
    )
    parser.add_argument("input_file", help="Input Markdown file to convert")
    parser.add_argument(
        "--title", "-t", help="Title for the HTML document", default=None
    )
    parser.add_argument(
        "--translations",
        "-n",
        type=int,
        help="Number of translations to include (default: 4)",
        default=4,
    )
    parser.add_argument(
        "--template",
        help="Custom HTML template file (default: ./tpo_html_template.html)",
        default="./tpo_html_template.html",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output HTML file (default: input filename with .html extension)",
        default=None,
    )

    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> Tuple[str, str, str]:
    """Validate input arguments and return processed values."""
    if not os.path.exists(args.input_file):
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    if not os.path.exists(args.template):
        raise FileNotFoundError(f"Template file not found: {args.template}")

    # Generate output filename if not provided
    output_file = args.output or os.path.splitext(args.input_file)[0] + ".html"

    # Use input filename as title if not provided
    title = args.title or os.path.splitext(os.path.basename(args.input_file))[0]

    return args.input_file, output_file, title


def main():
    """Main entry point for the script."""
    try:
        args = parse_arguments()
        input_file, output_file, title = validate_inputs(args)

        convert_addTOC(
            md_file=input_file,
            file_title=title,
            num_translations=args.translations,
            tpo_template=args.template,
        )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
