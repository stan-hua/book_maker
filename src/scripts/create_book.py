"""
create_book.py

Description:
    Creates book using OpenAI's ChatGPT.
"""

# Standard libraries
import argparse
import os

# Custom libraries
from src.classes.book_maker import BookMaker
from src.classes.book_formatter import BookFormatter


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
    # Start session
    book_maker = BookMaker(
        topic=args.topic,
        language=args.language,
        title=args.title
    )

    # Create book
    book_maker.create_book()

    # Get book contents
    book_dict = book_maker.get_book_dict()

    # TODO: Format book
    book_formatter = BookFormatter(book_dict=book_dict)
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

