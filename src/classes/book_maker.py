"""
book_maker.py

Description:
    Wrapper over reverse-engineered Chatbot, to generate a book and its content.
"""

# Standard libraries
import json
import logging
from collections import OrderedDict
from difflib import SequenceMatcher

# Non-standard libraries
from Levenshtein import distance as levenshtein_distance
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
    "create_section": "create_section.txt.jj",
    "check_if_finished": "follow_up.txt.jj",
    "create_description": "create_description.txt.jj",
    "create_keywords": "create_keywords.txt.jj",
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

        # Attempt to create connection to Chatbot
        for i in range(1, 4):
            try:
                self._chatbot = Chatbot(
                    constants.DEFAULT_CONFIG,
                    conversation_id=conversation_id,
                    parent_id=parent_id)
                break
            except Exception:
                LOGGER.warning(f"Failed to connect to ChatGPT ({i}/3)! "
                               "Retrying...")
        if not hasattr(self, "_chatbot"):
            raise RuntimeError("Unable to create connection to ChatGPT!")

        # Store creation progress for each section
        self.progress = {
            "title": title is not None,
            "toc": False,
            "sections": False,
            "description": False,
            "keywords": False,
        }

        # Store parts of book
        # NOTE: `sections` will be {section: subsection: text} / {section: text}
        self._book = {
            "title": title,
            "toc": None,
            "sections": None,
            "description": None,
            "keywords": None,
        }

        # Start conversation about the book, if conversation ID not provided
        if conversation_id is None:
            self.start_book_making()


    def save(self, path):
        """
        Save generated book elements to path specified, as a JSON file.

        Note
        ----
        Requires that all book elements are generated successfully.

        Parameters
        ----------
        path : str
            Path to save JSON 

        Returns
        -------
        bool
            True iff saved successfully, and False otherwise.
        """
        # Early return, if not all book elements are generated
        if not all(self.progress.values()):
            return False

        # Save book contents to JSON file
        with open(path, "w") as handler:
            json.dump(self._book, handler, indent=4)

        LOGGER.info("SUCCESS: Saved book contents to JSON file")


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


    def create_book(self):
        """
        Main method to create book.
        """
        # Generate title of book
        self.create_title()

        # Create table of contents
        self.create_toc()

        # Create short paragraph description
        self.create_description()

        # Create 3 keywords for the book
        self.create_keywords()

        # Prepare sections/subsections to generate, based on table of contents
        self.extract_sections_from_toc()

        # Create each section of the book
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
        template_vars = {"language": self.language}

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

        # Create table of contents using ChatGPT
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["create_toc"]
        template_vars = {"language": self.language}

        # 1. Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        try:
            text_output = self._chatbot.ask(prompt)["message"]

            # Remove unneeded start/end paragraphs from Chatbot
            toc = extract_utils.extract_central_text(text_output)

            # Store generated table of contents
            self._book["toc"] = toc
            LOGGER.info("SUCCESS: Created table of contents.")

            # Update progress
            self.progress["toc"] = True
        except Exception as error_msg:
            LOGGER.error("FAIL: Failed to create table of contents!")
            LOGGER.error(error_msg)


    def extract_sections_from_toc(self):
        """
        Extract book section/chapter names from table of contents, and prepare
        locations to store each subsection (if available).
        """
        # CHECK: If section names were already extracted
        if self._book["sections"]:
            return

        # CHECK: Table of Contents was generated
        toc = self._book["toc"]
        if toc is None:
            LOGGER.warning("FAIL: Failed to extract book chapters/sections. "
                           "Table of Contents has not yet been generated!")

        # Accumulate mapping of sections to None (or list of subsections)
        section_to_subsections = extract_utils.extract_sections_from_toc(toc)

        # Early return, if no sections found
        if not section_to_subsections:
            LOGGER.warning("FAIL: Failed to extract book chapters/sections "
                           "from Table of Contents!")
            return

        # For each section, check if there are subsections extracted
        for section in list(section_to_subsections.keys()):
            subsections = section_to_subsections[section]
            if subsections is None:
                continue

            # Replace subsections with an ordered dictionary
            # NOTE: Subsections must be a list if not empty
            section_to_subsections[section] = OrderedDict.fromkeys(subsections)

        # Store section (to dictionary of subsections)
        self._book["sections"] = section_to_subsections
        LOGGER.info("SUCCESS: Extracted book chapters/sections.")


    def create_sections(self):
        """
        For each uncreated section, generate its contents.

        Note
        ----
        If it has subsections, it will generate those.
        """
        # CHECK: If sections were generated
        sections = self._book["sections"]
        if sections is None:
            LOGGER.warning("FAIL: Book chapters/sections have not yet been "
                           "extracted from the Table of Contents!")
            return

        # For each section, check if it has a subsection
        for section, subsections in self._book["sections"].items():
            # If no subsections
            if subsections is None:
                self.create_section(section)
                continue

            # Iteratively create each subsection
            for subsection in subsections:
                self.create_section(section, subsection)

        LOGGER.info(f"SUCCESS: Created all sections!")
        # Update progress
        self.progress["sections"] = True


    def create_section(self, section, subsection=None):
        """
        Generate and store content for a specific section (and subsection, if
        specified).

        Parameters
        ----------
        section : str
            Name of book's section
        subsection : str, optional
            Name of section subsection, by default None
        """
        # 0. Create string containing section and subsection, for later logging
        log_str = f"section `{section}`: `{subsection}`" if subsection \
            else f"section {section}"

        # Create section using ChatGPT
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["create_section"]
        template_vars = {
            "language": self.language,
            "section": section,
            "subsection": subsection,
        }

        # 1. Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        try:
            text_output = self._chatbot.ask(prompt)["message"]

            # Remove unneeded start/end paragraphs from Chatbot
            section_text = extract_utils.extract_central_text(text_output)

            # Attempt to get full response from Chatbot
            section_text = self._iter_check_if_finished(text=section_text)

            # Store generated section/subsection
            if subsection:
                self._book["sections"][section][subsection] = section_text
            else:
                self._book["sections"][section] = section_text
            LOGGER.info(f"SUCCESS: Created {log_str}")
        except Exception as error_msg:
            LOGGER.error(f"FAIL: Failed to create {log_str}!")
            LOGGER.error(error_msg)


    def create_description(self):
        """
        Create and store short description of book
        """
        if self._book["description"] is not None:
            return

        # Create title using ChatGPT
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["create_description"]
        template_vars = {"language": self.language}

        # 1. Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        try:
            text_output = self._chatbot.ask(prompt)["message"]

            # Remove unneeded start/end paragraphs from Chatbot
            description = extract_utils.extract_central_text(text_output)

            # Remove double quotes, if any
            description = description.replace('"', "")

            # Store generated description
            self._book["description"] = description
            LOGGER.info("SUCCESS: Created short description.")

            # Set progress as done
            self.progress["description"] = True
        except Exception as error_msg:
            LOGGER.error("FAIL: Failed to create description!")
            LOGGER.error(error_msg)


    def create_keywords(self, num_keywords=3):
        """
        Create and store 3 keywords for book

        Parameters
        ----------
        num_keywords : int, optional
            Number of keywords to generate. Defaults to 3.
        """
        if self._book["keywords"] is not None:
            return

        # Create title using ChatGPT
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["create_keywords"]
        template_vars = {
            "num_keywords": num_keywords,
        }

        # 1. Render text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        try:
            text_output = self._chatbot.ask(prompt)["message"]

            # Remove unneeded start/end paragraphs from Chatbot
            text_output = extract_utils.extract_central_text(text_output)

            # Extract list of keywords
            keywords = extract_utils.extract_list_from_numbered_list_text(
                text_output)

            # Store generated description
            self._book["keywords"] = keywords
            LOGGER.info("SUCCESS: Created keywords for the book.")

            # Set progress as done
            self.progress["keywords"] = True
        except Exception as error_msg:
            LOGGER.error("FAIL: Failed to create keywords for the book!")
            LOGGER.error(error_msg)


    ############################################################################
    #                           Helper Functions                               #
    ############################################################################
    def _iter_check_if_finished(self, text=None):
        """
        Iteratively check that last prompt was finished. If not, continues to
        append to text provided

        Parameters
        ----------
        text : str, optional
           Last output from chatbot. If provided, continues to append unfinished
           text to this, by default None

        Returns
        -------
        str
            Accumulated text from last prompt
        """
        # INPUT: Ensure will start appending from string
        text = text if text else ""

        # Iteratively check for more text, until prompt is completely finished
        last_text = text
        while True:
            new_text = self._check_if_finished(last_text)
            # Break, if chatbot is done with last prompt
            if new_text is None:
                break

            # 1. Preprocess newly-generated text
            new_text = extract_utils.extract_central_text(new_text)

            # 2. Merge new text to already existing text
            matcher = SequenceMatcher(None, text, new_text)
            match = matcher.find_longest_match(0, len(text), 0, len(new_text))
            text = text[:match.a] + new_text[match.b:]

            # Update last text
            last_text = new_text

        return text


    def _check_if_finished(self, text=None):
        """
        Check if the Chatbot is done with the last prompt. If not, returns
        follow-up output of Chatbot.

        Note
        ----
        If given the Chatbot's latest output, will check Levenshtein distance
        between newly generated text and provided text. If it's close, will
        assume that it's done.

        Parameters
        ----------
        text : str
            Latest output from the chatbot. If provided, will compare against
            the generated text to check for similarity.

        Returns
        -------
        str
            Follow-up output of Chatbot, or returns None, if finished.
        """
        # 0. Prepare to render text prompt
        template_fname = SECTION_TO_TEMPLATE_FNAME["check_if_finished"]
        template_vars = {"language": self.language}

        # 1. Render follow-up text prompt
        prompt = template_utils.render_template(template_fname, template_vars)

        # 2. Feed prompt to chatbot
        text_output = self._chatbot.ask(prompt)["message"]

        # CHECK: If chatbot is finished
        # CASE 1: Its output will start with "Done."
        if text_output.startswith("Done."):
            return None
        # CASE 2: It will return something similar to the last text
        if text:
            # Calculate num. of single character edits to make texts the same
            num_edits = levenshtein_distance(text, text_output)
            # NOTE: Let metric be num. of edits divided by size of  larger text
            metric = num_edits / max(len(text), len(text_output))
            # Assume the output is the same if < 5% of characters need to change
            if metric < 0.05:
                return None

        return text_output


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    topic = "Coding basic computer vision projects in PyTorch"
    book_maker = BookMaker(topic=topic)
    book_maker.create_book()
    book_maker.save(constants.DIR_SRC + "/output/pytorch_book.json")

    print("Success!")
