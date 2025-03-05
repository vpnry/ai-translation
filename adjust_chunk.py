import xml.etree.ElementTree as ET


def ensure_root(file_path):
    """Ensures the XML content has a single root element before parsing."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if content.startswith("<root>") and content.endswith("</root>"):
        return content

    return f"<root>\n{content}\n</root>"


def wrap_lines_in_chunk(source_file, target_file, output_file):
    # Read and ensure root for both source and target XMLs
    source_content = ensure_root(source_file)
    target_content = ensure_root(target_file)

    # Parse source and target XML structures
    source_root = ET.fromstring(source_content)
    target_root = ET.fromstring(target_content)

    # Create a new root element for the output
    output_root = ET.Element("root")

    # Store target <line> elements in a dictionary by ID

    target_lines = {
        line.attrib["id"]: line for line in target_root if "id" in line.attrib
    }

    # Warn if any <line> elements in target.xml are missing an id
    missing_ids = [
        ET.tostring(line, encoding="unicode")
        for line in target_root
        if "id" not in line.attrib
    ]
    if missing_ids:
        print(
            f"Warning: Some <line> elements are missing 'id' attributes:\n{missing_ids}"
        )

    # Process each chunk while preserving its original structure

    for chunk in source_root:
        if chunk.tag.startswith("chunk"):  # Ensure it's a chunk
            new_chunk = ET.Element(chunk.tag)
            for line in chunk.findall("line"):
                line_id = line.attrib.get("id")
                if line_id and line_id in target_lines:
                    new_chunk.append(target_lines[line_id])
                else:
                    new_chunk.append(line)  # Keep original if no replacement exists

            output_root.append(new_chunk)

    # Write the output file
    output_tree = ET.ElementTree(output_root)
    output_tree.write(output_file, encoding="utf-8", xml_declaration=False)


def re_lineid_nochunk(source_file, outputfile):
    """Asign ID in line again orderly, no chunks"""
    source_content = ensure_root(source_file)
    source_root = ET.fromstring(source_content)

    # Create a new root element for the output
    output_root = ET.Element("root")

    idn = 0
    for line in source_root:
        if line.tag.startswith("line"):
            new_line = ET.Element("line")
            idn += 1
            new_line.set("id", str(idn))
            new_line.text = line.text
            new_line.tail = line.tail
            for child in line:
                new_line.append(child)
            output_root.append(new_line)
        else:  # copy other elements to root.
            output_root.append(line)

    # Write the output file (assuming you want to write to a file)
    output_tree = ET.ElementTree(output_root)
    output_tree.write(outputfile, encoding="utf-8", xml_declaration=False)


def re_id_in_source_chunk(source_file, outputfile):
    """Asign ID in chunk again orderly
    Used in some cases where the stanzas were manually combined
    Re-assigns line IDs within each chunk, keeping the chunk tags.
    """
    source_content = ensure_root(source_file)
    source_root = ET.fromstring(source_content)

    # Create a new root element for the output
    output_root = ET.Element("root")

    idn = 0
    for chunk in source_root:
        if chunk.tag.startswith("chunk"):
            new_chunk = ET.Element(chunk.tag)
            for line in chunk.findall("line"):
                idn += 1
                line.set("id", str(idn))  # Re-assign line ID
                new_chunk.append(line)
            output_root.append(new_chunk)
        else:  # copy other elements to root.
            output_root.append(chunk)

    # Write the output file (assuming you want to write to a file)
    output_tree = ET.ElementTree(output_root)
    output_tree.write(outputfile, encoding="utf-8", xml_declaration=False)


