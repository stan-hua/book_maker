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
        # Check if line starts with "1. " or "1) "
        match = re.search(r"^1(\.|\)) (.*)", line)
        if match is not None:
            return match.group(2)

        # Check if line starts with "- "
        match = re.search(r"- (.*)", line)
        if match is not None:
            return match.group(1)

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
    # CASE 1: Table of Contents be split into paragraphs
    if len(toc_text.split("\n\n")) > 1:
        return extract_sections_subsections_by_paragraphs(toc_text)
    # CASE 2: Table of Contents can only be parsed line-by-line
    # NOTE: This is less robust to un-numbered section headers.
    else:
        return extract_sections_subsections_by_line(toc_text)


def extract_sections_subsections_by_line(toc_text):
    """
    Attempt to extract sections and subsections from ToC line-by-line

    Note
    ----
    May not be robust to non-numbered section headers.

    Parameters
    ----------
    toc_text : str
        Text containing table of contents

    Returns
    -------
    OrderedDict
        Ordered mapping of {sections: [subsections]}
    """
    section_to_subsections = OrderedDict()

    # Iterate over lines
    # Accumulate sections/subsections
    lines = [line for line in toc_text.split("\n") if line]
    curr_section = None
    curr_subsections = None
    for i, line in enumerate(lines):
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
                # HACK: Assume last line was a section header w/o a number
                if i != 0 and lines[i-1]:
                    curr_section = lines[i-1]
                    curr_subsections = []
                else:
                    raise RuntimeError("Subsection occurs without a section "
                                       "header!")
            curr_subsections.append(subsection)
            continue

    # If last section not saved, store section/subsections
    if curr_section is not None and curr_section not in section_to_subsections:
        # NOTE: Rather store `None` if no subsections, instead of []
        section_to_subsections[curr_section] = curr_subsections \
            if curr_subsections else None

    return section_to_subsections


def extract_sections_subsections_by_paragraphs(toc_text):
    """
    Attempt to extract sections and subsections from ToC, where ToC splits
    sections by paragraphs (marked by 2 newlines).

    Note
    ----
    More robust to non-numbered section headers compared to extracting by line.

    Parameters
    ----------
    toc_text : str
        Text containing table of contents, where sections are separated by two
        newlines

    Returns
    -------
    OrderedDict
        Ordered mapping of {sections: [subsections]}
    """
    section_to_subsections = OrderedDict()

    # Iterate over paragraphs (each is 1 section + subsections)
    # Accumulate sections/subsections
    paragraphs = [par for par in toc_text.split("\n\n") if par]
    for par in paragraphs:
        curr_section, curr_subsections = parse_one_section_to_subsections(par)
        # NOTE: If no subsections, replaced with None
        curr_subsections = curr_subsections if curr_subsections else None

        # Store sections and subsections
        section_to_subsections[curr_section] = curr_subsections
    return section_to_subsections


def parse_one_section_to_subsections(text):
    """
    Return a tuple of section and list of subsections.

    Note
    ----
    Text must be 2+ text lines, where:
        1) the first line is the section header, and
        2) suceeding lines are subsection headers for the section headers

    Parameters
    ----------
    text : str
        First line is a section header, and line 2+ are possible subsection
        headers

    Returns
    -------
    tuple of (str, list)
        First is the section header, and second is an ordered list of
        subsections
    """
    # Split into lines
    lines = [sent for sent in text.split("\n") if sent]

    # Get section header (first line)
    # NOTE: Default to whole line (if doesn't contain number)
    section = parse_numbered_list_item_from_line(lines[0])
    section = section if section else lines[0]

    # Get subsections
    subsections = []
    for line in lines[1:]:
        subsections.append(parse_unordered_list_item_from_line(line))

    return section, subsections


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
    match = re.search(r"(\w*\s*)(\d+)(\.|:|\)) (.*)", line)
    if match is None:
        return None

    # Get numbered item
    numbered_item = match.group(4)
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


def extract_list_from_numbered_list_text(text):
    """
    Given text containing a numbered list of items, extract items into a list.

    Parameters
    ----------
    text : str
        Text containing numbered list items

    Returns
    -------
    list
        List of items as strings
    """
    # Split into lines
    lines = text.split("\n")

    # Get all numbered items
    items = []
    for line in lines:
        item = parse_numbered_list_item_from_line(line)
        if item is not None:
            items.append(item)

    return items


def split_non_text_from_line(line):
    """
    Splits line into:
        (1) left-side non-text (e.g., special characters), and
        (2) right-side text segments.

    Parameters
    ----------
    line : str
        Text line

    Returns
    -------
    tuple of (str, str)
        Left-side non-text string (with whitespace appended) and
        right-side text string
    """
    match = re.search("(\W*) (.*)", line)
    # CASE 1: Of the form: "\n\n SomethingSomething"
    if match.group(1):
        return match.group(1) + " ", match.group(2)

    # CASE 2: Of the form: " SomethingSomething"
    match = re.search("(\s*)(.*)", line)
    if match.group(1):
        return match.group(1), match.group(2)

    # CASE 3: Of the form: "SomethingSomething"
    # NOTE: There is no left side
    return "", line
