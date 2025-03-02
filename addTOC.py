"""This script adds a Table of Contents (TOC like the tipitakapali.org) to an HTML file. To be used with HTML files that have headings with IDs."""

from bs4 import BeautifulSoup
import re


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

        # Make the TOC div visible.
        # toc_div['style'] = 'display: block;' # Or any other style you prefer

        # Create the TOC list (unordered list)
        toc_list = soup.new_tag("ul")

        # Find all heading tags (h1, h2, h3, h4)
        headings = soup.find_all(re.compile(r"^h[1-4]$"))

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
            f.write("<!DOCTYPE html>\n" + str(soup))
        print(f"TOC added and saved to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: File not found: {html_file_path}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 addTOC.py <input_html_file> [output_html_file]")
        print("Example: python3 addTOC.py input.html output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    add_toc(input_file, output_file)
