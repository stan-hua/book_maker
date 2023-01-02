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

    # Load login configurations from `config.json` in `data` directory
    config = load_config(args.config_path)

    # Start session
    book_maker = BookMaker(
        config=config,
        topic=args.topic,
        language=language,
        title=args.title
    )

    # Create book
    book_maker.create_book()

    # Save book contents to JSON file
    book_maker.save(os.path.join(
        args.directory, args.fname.replace(".epub", ".content.json")))

    # Get book contents
    book_dict = book_maker.get_book_dict()

    # Format book
    book_formatter = BookFormatter(
        authors=args.authors,
        book_dict=book_dict,
        language=code)
    book_formatter.format_book()

    # Save book as EPUB
    book_formatter.save_epub(directory=args.directory, fname=args.fname)


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
        "config_path": "Path to JSON file containing Chatbot login "
                       "configurations",

        "topic": "Topic of desired book",
        "authors": "Names of book authors",
        "language": "Language to write book in",
        "title": "Custom book title. If not specified, title will be "
                 "generated.",

        "directory": "Directory to save books in. Saves to the current "
                     "working directory by default.",
        "fname": "Filename to save EPUB book as. Saves as 'book.epub' by "
                 "default",
    }

    # Arguments for Connecting to Chatbot
    parser.add_argument("--config_path",
                        default=os.path.join(constants.DIR_DATA, "config.json"),
                        help=arg_help["config_path"])

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
                        default="book.epub",
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


def load_config(path):
    """
    Returns configuration found at path provided

    Note
    ----
    Please look at revChatGPT GitHub docs on how to create a proper login config
    file. Link: https://github.com/acheong08/ChatGPT/wiki/Setup

    Parameters
    ----------
    path : str
        Path to JSON file containing Chatbot login configurations

    Returns
    -------
    dict
        Containing login configurations
    """
    with open(path, "r") as handler:
        config = json.load(handler)
    return config


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
