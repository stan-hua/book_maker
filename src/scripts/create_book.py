"""
create_book.py

Description:
    Creates book using OpenAI's ChatGPT.
"""

# Standard libraries
import argparse
import os

# Non-standard libraries
import jinja2

# Custom libraries
from src.classes.book_maker import BookMaker


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
    book_maker = BookMaker(topic=args.topic)

    # Create book
    book_maker.create_book()

    # TODO: Format book


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
        "topic": "What is the book about?",
    }

    parser.add_argument("--topic", help=arg_help["topic"])


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

