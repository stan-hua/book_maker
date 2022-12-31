"""
book_maker.py

Description:
    Wrapper over reverse-engineered Chatbot
"""

# Standard libraries
import logging

# Non-standard libraries
from revChatGPT.ChatGPT import Chatbot

# Custom libraries
from src.data import constants
from src.utils import extract_utils, template_utils


################################################################################
#                                  Constants                                   #
################################################################################
# Create logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Mapping of section part to template filename
SECTION_TO_TEMPLATE_FNAME = {
    "start_book_making": "start_book_making.txt.jj",
    "create_title": "create_title.txt.jj",
    "create_toc": "create_toc.txt.jj",
}


################################################################################
#                               BookMaker Class                                #
################################################################################
class BookMaker:
    """
    BookChatbot class. Used to create parts of book.
    """

    def __init__(self, topic, conversation_id=None, parent_id=None,
                 title=None, language="English"):
        """
        Starts ChatGPT session

        Parameters
        ----------
        topic : str
            Topic of book
        conversation_id : int
            ChatGPT Conversation ID
        parent_id : int
            ChatGPT Parent ID
        title : str, optional
            If provided, use this as the title of the book
        language : str, optional
            Language to generate book in
        """
        # Store topic and language
        self.topic = topic
        self.language = language

        # Create connection to Chatbot
        self._chatbot = Chatbot(
            constants.config, 
            conversation_id=conversation_id,
            parent_id=parent_id)

        # Store creation progress for each section
        self.progress = {
            "title": title is not None,
            "toc": False,
            "sections": False
        }

        # Store mapping of section name to subsection name
        self.section_to_subsections = {}

        # Store parts of book
        self._book = {
            "title": title,
            "toc": None,
            "sections": self.section_to_subsections,
        }

        # Start conversation about the book, if conversation ID not provided
        if conversation_id is None:
            self.start_book_making()


    # TODO: Implement this
    def save(self, path):
        """
        Save conversation ID and parent ID to path

        Parameters
        ----------
        path : str
            Path to save 
        """
        raise NotImplementedError


    def start_book_making(self):
        """
        Start Chatbot conversation to prime creation of the book.
        """
        # Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["start_book_making"]
        template_vars = {
            "topic": self.topic,
            "language": self.language
        }

        # Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # Feed prompt to chatbot, to prime for creating book
        self._chatbot.ask(prompt)

        LOGGER.info("START: Priming for book creation...")


    # TODO: Finish implementing this
    def create_book(self):
        """
        Main method to create book.
        """
        # Generate title of book
        self.create_title()

        # TODO: Create table of contents
        self.create_toc()

        # TODO: Fill in sections based on table of contents
        self.extract_sections_from_toc()

        # TODO: Create each section of the book
        self.create_sections()


    def get_book_dict(self):
        """
        Return dictionary, containing book contents.
        """
        return self._book


    def create_title(self):
        """
        Create and store title of book
        """
        if self._book["title"] is not None:
            return

        # Create title using ChatGPT
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["create_title"]
        template_vars = {}

        # 1. Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        try:
            text_output = self._chatbot.ask(prompt)["message"]

            # Remove unneeded start/end paragraphs from Chatbot
            text_output = extract_utils.extract_central_text(text_output)

            # Get first option
            title = extract_utils.extract_first_option(text_output)
            if title is None:
                LOGGER.warning("FAIL: Unable to find options for title from "
                               "Chatbot output!")
                return

            # Remove double quotes, if any
            title = title.replace('"', "")

            # Store generated title
            self._book["title"] = title
            LOGGER.info("SUCCESS: Created title.")

            # Set progress as done
            self.progress["title"] = True
        except Exception as error_msg:
            LOGGER.error("FAIL: Failed to create title!")
            LOGGER.error(error_msg)


    def create_toc(self):
        """
        Create and store table of contents (TOC)
        """
        if self._book["toc"] is not None:
            return

        # Create title using ChatGPT
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["create_toc"]
        template_vars = {}

        # 1. Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        try:
            text_output = self._chatbot.ask(prompt)["message"]

            # Remove unneeded start/end paragraphs from Chatbot
            toc = extract_utils.extract_central_text(text_output)

            # Store generated title
            self._book["toc"] = toc
            LOGGER.info("SUCCESS: Created table of contents.")
        except Exception as error_msg:
            LOGGER.error("FAIL: Failed to create table of contents!")
            LOGGER.error(error_msg)


    def extract_sections_from_toc(self):
        """
        Extract book section/chapter names from table of contents.
        """
        toc = self._book["toc"]
        if toc is None:
            LOGGER.warning("FAIL: Failed to extract book chapters/sections. "
                           "Table of Contents has not yet been generated!")

        # Accumulate mapping of sections to subsections
        # NOTE: If no subsections provided
        section_to_subsections = extract_utils.extract_sections_from_toc(toc)

        # Store section
        self.section_to_subsections = section_to_subsections


    # TODO: Implement this
    def create_sections(self):
        raise NotImplementedError

    # TODO: Implement this
    def create_subsections(self):
        raise NotImplementedError


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    topic = "Coding basic computer vision projects in PyTorch"
    book_maker = BookMaker(topic=topic)

    book_maker.create_title()
    book_maker.create_toc()

    print("Success!")
