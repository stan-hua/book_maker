"""
extract_utils.py

Description:
    Used to extract text from the text output from the Chatbot
"""

# Standard libraries
import re


################################################################################
#                               Helper Functions                               #
################################################################################
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

    return first_option


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
