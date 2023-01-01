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
def extract_central_text(text, include_start=False, include_end=False):
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
    include_start : bool, optional
        If True, does not discard FIRST paragraph from text. Defaults to False.
    include_end : bool, optional
        If True, does not discard LAST paragraph from text. Defaults to False.

    Returns
    -------
    str
        Central text with starting and ending paragraph removed, if any
    """
    # Split into 1+ blocks
    blocks = text.split("\n\n")

    # Remove paragraph equal to "---"
    blocks = [block for block in blocks if block != "---"]

    # Handle cases for differing num. of paragraphs
    if len(blocks) == 0:
        return ""
    elif len(blocks) == 1:
        return blocks[0]
    elif len(blocks) == 2:
        return blocks[1] if not include_start else "\n\n".join(blocks)
    else:
        # Unless specified, remove first paragraph
        start_idx = 0 if include_start else 1
        # Unless specifeid, remove last paragraph
        end_idx = len(blocks) if include_end else -1
        return "\n\n".join(blocks[start_idx:end_idx])


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

    # Iterate over lines
    # Accumulate sections/subsections
    lines = [line for line in toc_text.split("\n") if line]
    curr_section = None
    curr_subsections = None
    for line in lines:
        # Check if line is a section header
        section = parse_numbered_list_item_from_line(line)
        # If so, ready up to collect subsections
        if section is not None:
            # Store previous sections/subsections
            if curr_section is not None:
                # NOTE: Rather store `None` if no subsections, instead of []
                section_to_subsections[curr_section] = curr_subsections \
                    if curr_subsections else None

            # Reinitialize
            curr_section = section
            curr_subsections = []
            continue

        # Check if line is a subsection header
        subsection = parse_unordered_list_item_from_line(line)
        if subsection is not None:
            if curr_subsections is None:
                raise RuntimeError("Subsection occurs before section header!")
            curr_subsections.append(subsection)
            continue

    # If last section not saved, store section/subsections
    if curr_section is not None and curr_section not in section_to_subsections:
        # NOTE: Rather store `None` if no subsections, instead of []
        section_to_subsections[curr_section] = curr_subsections \
            if curr_subsections else None

    return section_to_subsections


def parse_numbered_list_item_from_line(line):
    """
    Given a text line, attempt to parse item from an ordered list, if possible.

    Note
    ----
    Numbered list item can appear as "1." or "1:" or "1)".

    Parameters
    ----------
    text : str
        Numbered list item, possibly with text before it.

    Example
    -------
    >>> line = "Chapter 1. The start"
    >>> parse_numbered_list_item_from_line(line)
    "The start"

    Returns
    -------
    str
        Item in ordered list item. Returns None, if not found
    """
    match = re.search(r"(\w*\s*)\d(\.|:|\)) (.*)", line)
    if match is None:
        return None

    # Get numbered item
    numbered_item = match.group(3)
    return numbered_item


def parse_unordered_list_item_from_line(line):
    """
    Given a text line, attempt to parse item from unordered list (bullet point),
    if possible.

    Note
    ----
    Unordered list item begins with the bullet point: "- "

    Parameters
    ----------
    line : str
        A line of text, possibly containing a bullet-pointed item

    Returns
    -------
    str
        Item in bullet point. Returns None, if not found
    """
    match = re.search(r"(\s*)- (.*)", line)
    if match is None:
        return None

    # Get unordered item
    item = match.group(2)
    return item
