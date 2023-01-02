"""
create_book.py

Description:
    Creates book using OpenAI's ChatGPT.
"""

# Standard libraries
import argparse
import json
import logging
import os

# Custom libraries
from src.data import constants
from src.classes.book_maker import BookMaker
from src.classes.book_formatter import BookFormatter


################################################################################
#                                  Constants                                   #
################################################################################
# Create logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


################################################################################
#                                Main Functions                                #
################################################################################
def main(args):
    """
    Creates book based on arguments provided.

    Parameters
    ----------
    args : argparse.Namespace
        Parameters to create book
    """
    # INPUT: Preprocess language to 2-digit code
    language, code = get_language_and_code(args.language)

    # Start session
    book_maker = BookMaker(
        topic=args.topic,
        language=language,
        title=args.title
    )

    # Create book
    # TODO: Generate short description
    # TODO: Generate 3 keywords
    book_maker.create_book()

    # Get book contents
    book_dict = book_maker.get_book_dict()

    # TODO: Format book
    book_formatter = BookFormatter(
        authors=args.authors,
        book_dict=book_dict,
        language=code)
    book_formatter.format_book()

    # TODO: Save HTML book
    book_formatter.save_html(directory=args.directory, fname=args.fname)


################################################################################
#                               Helper Functions                               #
################################################################################
def init(parser):
    """
    Initializes ArgumentParser with arguments, needed to generate book.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        ArgumentParser object
    """
    arg_help = {
        "topic": "Topic of desired book",
        "authors": "Names of book authors",
        "language": "Language to write book in",
        "title": "Custom book title. If not specified, title will be "
                 "generated.",

        "directory": "Directory to save books in. Saves to the current "
                     "working directory by default.",
        "fname": "Filename to save HTML book as. Saves as 'book.html' by "
                 "default",
    }

    # Arguments for Book Generation
    parser.add_argument("--topic",
                        help=arg_help["topic"], required=True)
    parser.add_argument("--authors",
                        default=["[UNKNOWN]"],
                        nargs="+",
                        help=arg_help["authors"])
    parser.add_argument("--language",
                        default="English",
                        help=arg_help["language"])
    parser.add_argument("--title",
                        default=None,
                        help=arg_help["title"])

    # Arguments for File Saving
    parser.add_argument("--directory",
                        default=os.getcwd(),
                        help=arg_help["directory"])
    parser.add_argument("--fname",
                        default="book.html",
                        help=arg_help["fname"])


def get_language_and_code(language):
    """
    Given the full language name, return 2 digit ISO code.

    Parameters
    ----------
    language : str
        Language chosen for the book

    Returns
    -------
    tuple of (str, str)
        Contains 1) language name, and 2) 2 digit ISO code.
        If not found, defaults to English.
    """
    # Load mapping of language (in lower-case) to 2-digit code
    with open(constants.LANGUAGE_CODES_JSON, "r") as handler:
        language_to_code = json.load(handler)
    code_to_language = {v:k for k,v in language_to_code.items()}

    # Ensure input language is lower-case
    language = language.lower()

    # Use, if already 2-digit ISO code
    if language in language_to_code.values():
        code = language
        language = code_to_language[code]
        return language, code

    # If not in dictionary, default to English
    if language not in language_to_code:
        language = "english"
        LOGGER.warning(f"Language provided `{language}` is not supported! "
                       "Defaulting to English...")

    # Get 2-digit code
    code = language_to_code[language]

    return language, code


################################################################################
#                                  Main Flow                                   #
################################################################################
if __name__ == "__main__":
    # 0. Initialize ArgumentParser
    PARSER = argparse.ArgumentParser()
    init(PARSER)

    # 1. Get arguments from cmd
    ARGS = PARSER.parse_args()

    # 2. Create book!
    main(ARGS)

