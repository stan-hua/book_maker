"""
extract_utils.py

Description:
    Used to extract text from the text output from the Chatbot
"""

# Standard libraries
import re
from collections import OrderedDict


################################################################################
#                               Helper Functions                               #
################################################################################
def extract_central_text(text):
    """
    Extract central text, if there is a starting (and ending) paragraph.

    Note
    ----
    Used to remove unnecessary starting/ending paragraphs from Chatbot's
    response.

    Parameters
    ----------
    text : str
        Text to parse

    Returns
    -------
    str
        Central text with starting and ending paragraph removed, if any
    """
    # Split into 1+ blocks
    blocks = text.split("\n\n")

    # Handle cases for differing num. of paragraphs
    if len(blocks) == 0:
        return ""
    elif len(blocks) == 1:
        return blocks[0]
    elif len(blocks) == 2:
        return blocks[1]
    else:
        # if 3 or more, remove start AND end paragraphs
        return "\n\n".join(blocks[1:-1])


def extract_first_option(text):
    """
    Parse text output to get the first option, when provided a list of options.

    Parameters
    ----------
    text : str
        Text to parse for first option

    Returns
    -------
        First option, if given multiple options. Returns None, if unable to find
        options.
    """
    first_option = None

    # Split into lines
    lines = [line for line in text.split("\n") if line]

    # If only one line provided, use it
    if len(lines) == 1:
        return lines[0]

    # Iterate over each line to find the first option
    for line in lines:
        # Check if line starst with "1. " or "1) "
        match = re.search(r"^1(\.|\)) (.*)", line)
        if match is None:
            continue

        # Get first option
        first_option = match.group(2)
        break

    return first_option


def extract_sections_from_toc(toc_text):
    """
    Given the Table of Contents (TOC), extract sections (and subsections, if
    present)

    Parameters
    ----------
    toc_text : str
        Text containing table of contents

    Returns
    -------
    OrderedDict of {section: subsection}
        Contains mapping of section to `None` or list of subsections, if present
    """
    section_to_subsections = OrderedDict()

    # Iterate over section blocks
    section_blocks = toc_text.split("\n\n")
    for section_block in section_blocks:
        # Split into lines
        lines = section_block.split("\n")

        # First line should always be the section header
        section = parse_numbered_list_item(lines[0])

        # If there are more lines, these are subsections
        if len(lines) > 1:
            subsections = extract_list_from_bulletpoints("\n".join(lines[1:]))
        else:
            subsections = None

        # Store section/subsections found
        section_to_subsections[section] = subsections

    return section_to_subsections


def parse_numbered_list_item(text):
    """
    Remove unnecessary text to the left of a numbered list item.

    Parameters
    ----------
    text : str
        Numbered list item, possibly with text before it.

    Example
    -------
    >>> text = "Chapter 1. The start"
    >>> parse_numbered_list_item(text)
    "1. The start"

    Returns
    -------
    str
        Numbered list item. Returns None, if not found
    """
    match = re.search(r"(\w*\s*)(\d. .*)", text)
    if match is None:
        return None

    # Get numbered item
    numbered_item = match.group(2)
    return numbered_item


def extract_list_from_bulletpoints(text):
    """
    Given a text containing bullet-points, extract bullet-pointed items.

    Parameters
    ----------
    text : str
        Contains bullet-pointed text

    Returns
    -------
    list
        List of items from bullet-pointed text
    """
    items = []

    # Iterate over each line
    for line in text.split("\n"):
        # Filter for those starting with bullet point
        match = re.search(r"(\s*)- (.*)", line)
        if match is None:
            continue

        # Store found bullet-pointed item
        items.append(match.group(2))

    return items
