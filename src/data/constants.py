"""
constants.py

Description:
    Contains global constants
"""

# Standard libraries
import os


################################################################################
#                                    Paths                                     #
################################################################################
DIR_SRC = os.path.dirname(os.path.dirname(__file__))
DIR_TEMPLATES = os.path.join(DIR_SRC, "templates")
DIR_DATA = os.path.join(DIR_SRC, "data")

# Path to JSON file with language (lower-case) to 2-digit ISO code
LANGUAGE_CODES_JSON = os.path.join(DIR_DATA, "language_to_code.json")

# Path to book's CSS file
BOOK_CSS = os.path.join(DIR_DATA, "book_styling.css")
