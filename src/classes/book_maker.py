"""
book_maker.py

Description:
    Wrapper over reverse-engineered Chatbot
"""

# Non-standard libraries
from revChatGPT.ChatGPT import Chatbot

# Custom libraries
from src.data import constants
from src.utils import template_utils


################################################################################
#                                  Constants                                   #
################################################################################
# Mapping of section part to template filename
SECTION_TO_TEMPLATE_FNAME = {
    "start_book_making": "start_book_making.txt.jj",
    "create_title": "create_title.txt.jj",
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

        # Store parts of book
        self._book = {
            "title": title,
            "toc": None,
            "sections": {}
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


    # TODO: Finish implementing this
    def create_book(self):
        """
        Main method to create book.
        """
        # TODO: Generate title of book
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


    # TODO: Implement this
    def create_title(self):
        """
        Create and store title of book
        """
        if self._book["title"] is not None:
            return

        # Create title using ChatGPT



        raise NotImplementedError


    # TODO: Implement this
    def create_toc(self):
        """
        Create and store table of contents (TOC)
        """
        raise NotImplementedError


    def extract_sections_from_toc(self):
        """
        Extract section names from table of contents.
        """
        raise NotImplementedError


    # TODO: Implement this
    def create_toc(self):
        raise NotImplementedError
