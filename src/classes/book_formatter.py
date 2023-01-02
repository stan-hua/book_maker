"""
book_formatter.py

Description:
    Used to format generated book into HTML
"""

# Standard libraries
import logging
import os
import re

# Non-standard libraries
from ebooklib import epub

# Custom libraries
from src.utils import template_utils


################################################################################
#                                  Constants                                   #
################################################################################
# Create logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# Mapping of section part to template filename
SECTION_TO_TEMPLATE_FNAME = {
    "book_format": "book_format.txt.jj",
}

# HTML tag for section header
SECTION_TAG = "h1"
# HTML tag for subsection header
SUBSECTION_TAG = "h2"
# HTML tag for code
CODE_TAG = "code"
# HTML tag for paragraph
PAR_TAG = "p"


################################################################################
#                             BookFormatter Class                              #
################################################################################
class BookFormatter:
    """
    BookFormatter class. Used to format book contents into HTML code.
    """

    def __init__(self, authors, book_dict, language="en"):
        """
        Initialize BookFormatter object

        Parameters
        ----------
        authors : list
            List of book authors
        book_dict : dict
            Contains `title`, `toc` and `sections`, where `sections` is of the
            form: {section: subsection: text} or {section: text}
        language : str, optional
            Language identifier in 2-digit ISO format. Defaults to "en" for
            English.
        """
        self.authors = authors
        self.book_dict = book_dict
        self.language = language

        # Store HTML for pages
        self.toc_html = None

        # Mapping of section/subsection name to its EpubHtml objects
        self.name_to_epubhtml = {}

        # Store final rendered HTML
        self.rendered_html = None

        # EPUB object to store book elements
        self.book = None

        # Book spine, to accumulate sections and subsections
        self.spine = ["nav"]


    def init_book(self):
        """
        Initialize EPUB book
        """
        book = epub.EpubBook()

        # Add title
        book.set_title(self.book_dict["title"])

        # Add language
        book.set_language(self.language)

        # Add authors
        for author in self.authors:
            book.add_author(author)

        # TODO: Add CSS
        style = 'body { font-family: Times, Times New Roman, serif; }'
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style)
        book.add_item(nav_css)

        # Set book as internal attribute
        self.book = book


    def save_epub(self, directory, fname="book.epub"):
        """
        Save formatted HTML to a EPUB file.

        Parameters
        ----------
        directory : str
            Directory to save EPUB file in
        fname : str
            Filename to save book as. Defaults to "book.epub"
        """
        # CHECK: All HTML text has been generated
        if self.book.toc is None:
            LOGGER.warning("HTML for table of contents page is not yet made!")
            return
        if not self.name_to_epubhtml:
            LOGGER.warning("HTML for sections is not yet made!")
            return
        if self.book is None:
            LOGGER.warning("The EPUB book object is not initialized!")
            return

        # Save EPUB to path specified
        epub.write_epub(os.path.join(directory, fname), self.book)


    def format_book(self):
        """
        Main function to format book's parts
        """
        # Initialize EPUB book
        self.init_book()

        # Add body of book
        self.add_body()

        # Add table of contents
        # NOTE: Must come after creating body of book
        self.add_toc()

        # Add NCX and Navigation tiles for EPUB
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # Set spine
        self.book.spine = self.spine


    def add_toc(self):
        """
        Add table of contents (ToC) to the book.
        """
        # Fill in TOC with sections and subsections
        toc = []
        for section, subsections in self.book_dict["sections"].items():
            epub_section = epub.Section(section)
            chapters = []
            # If section does not have subsections
            if subsections is None:
                chapters.append(self.name_to_epubhtml[section])
            # If there are subsections, add them
            else:
                for subsection in subsections:
                    chapters.append(self.name_to_epubhtml[subsection])

            # Add section (and subsections) to TOC
            toc.append((epub_section, chapters))

        # Self convert TOC to tuple and store
        self.book.toc = tuple(toc)


    def add_body(self):
        """
        Add body of the book (i.e., all its sections/subsections)
        """
        for section, subsections in self.book_dict["sections"].items():
            # If no subsections, create chapter for section text
            if subsections is None:
                self.add_chapter(section)
            # If there are subsections, create chapters for them
            else:
                for i, subsection in enumerate(subsections):
                    self.add_chapter(section, subsection, i)


    def add_chapter(self, section, subsection=None, subsection_num=None):
        """
        Adds body text for a section or its subsection.

        Parameters
        ----------
        section : str
            Name of section
        subsection : str, optional
            If provided, adds subsection chapter of the specified section.
            Defaults to None.
        subsection_num : int, optional
            If provided, specifies which order of the subsection provided,
            in the range [0, inf). Defaults to None.
        """
        # If subsection provided, that's the chapter name. Otherwise, section
        chapter_name = subsection or section
        # Create filename for chapter xHTML
        chapter_fname = chapter_name_to_filename(chapter_name) + '.xhtml'

        # Create EpubHTML object
        epub_html = epub.EpubHtml(
            title=chapter_name,
            file_name=chapter_fname,
            lang=self.language)

        # Prepare content (in HTML)
        content = self.prepare_chapter_content(
            section, subsection,
            subsection_num=subsection_num)

        # Add content
        epub_html.set_content(content)

        # Add to book
        self.book.add_item(epub_html)

        # Store EpubHTML object
        self.name_to_epubhtml[chapter_name] = epub_html

        # Add to spine
        self.spine.append(epub_html)


    def prepare_chapter_content(self, section, subsection=None,
                                subsection_num=None):
        """
        Prepares body HTML for a section or its subsection.

        Parameters
        ----------
        section : str
            Name of section
        subsection : str, optional
            If provided, prepares HTML for the specified subsection. Defaults to
            None.
        subsection_num : int, optional
            If provided, specifies which order of the subsection provided,
            in the range [0, inf). Defaults to None.

        Returns
        -------
        str
            HTML text for section/subsection
        """
        # Body HTML to accumulate
        content = ""

        # Flag if generating chapter for section or subsection
        is_subsection = (subsection is not None)

        # Choose header tag, depending on if it's a subsection or not
        header_tag = SUBSECTION_TAG if is_subsection else SECTION_TAG

        # Create header
        # NOTE: If the first subsection, add section header too
        if is_subsection and subsection_num == 0:
            content += f"<{SECTION_TAG}>{section}</{SECTION_TAG}>\n"

        # Add section/subsection header
        header = subsection if is_subsection else section
        content += f"<{header_tag}>{header}</{header_tag}>"

        # Get current body text
        body_text = self.book_dict["sections"][section][subsection] \
            if is_subsection else self.book_dict["sections"][section]

        # Convert code sections to use <code> tag
        body_text = replace_with_code_tag(body_text)

        # Wrap paragraphs in <p> tag
        body_text = wrap_paragraphs_in_par_tag(body_text)

        # Add body text to content
        content += "\n" + body_text

        return content


################################################################################
#                               Helper Functions                               #
################################################################################
def create_html_list(lst, type="ordered"):
    """
    Create list of ordered/unordered list items.

    Parameters
    ----------
    lst : list
        List of items
    type : str, optional
        One of "ordered" or "unordered". Defaults to "ordered".

    Returns
    -------
    str
        HTML for creating list
    """
    # Create each list item
    list_items = ["\n\t" + "<li>{item}</li>".format(item=item) for item in lst]
    list_items = "".join(list_items)

    # Assemble HTML
    outer_html = "<ol>{list_items}\n</ol>" if type == "ordered" \
        else "<ul>{list_items}\n</ul>"
    list_html = outer_html.format(list_items=list_items)

    return list_html


def chapter_name_to_filename(chapter_name):
    """
    Given a chapter name, convert it to a usable filename.

    Parameters
    ----------
    chapter_name : str
        Chapter name

    Returns
    -------
    str
        Name that can be used as a filename
    """
    # Make lower-case
    fname = chapter_name.lower()

    # Replace spaces with underscore
    fname = fname.replace(" ", "_")

    # Remove special characters
    remove_chars = "!@#$%^&*()+?=,.<>/\\:;" + "'" + '"'
    for char in remove_chars:
        fname = fname.replace(char, "")

    return fname


def replace_with_code_tag(text):
    """
    Replace ``` in text to <code> or </code>.

    Parameters
    ----------
    text : str
        Text possibly containing code blocks

    Returns
    -------
    str
        Text where code blocks are now wrapped by <code> </code> instead of ```
    """
    identifier = "```"

    # Find all occurences of code block identifiers
    # NOTE: There must be an even number of these
    num_occurrences = len(re.findall(identifier, text))
    assert num_occurrences % 2 == 0, \
        f"Number of code block identifiers ({identifier}) must be even!"

    # Iteratively update identifier to code tag
    # NOTE: Flips between using open (<code>) vs. closed (</code>) tag
    open_flag = True
    for _ in range(num_occurrences):
        code_tag = f"<{CODE_TAG}>" if open_flag else f"</{CODE_TAG}>"
        text = text.replace(identifier, code_tag, 1)

        # Flip tag
        open_flag = not open_flag

    return text


def wrap_paragraphs_in_par_tag(text):
    """
    Wrap paragraphs in paragraph tag (<p>)

    Parameters
    ----------
    text : str
        Text to add paragraph tags to

    Returns
    -------
    str
        Text, where opening/closing paragraph tags are added
    """
    # Split into paragraphs
    paragraphs = text.split("\n\n")

    # Update each paragraph to add paragraph tag
    new_paragraphs = []
    for paragraph in paragraphs:
        # CASE: If code in paragraph, separate and create it's own paragraph
        if f"<{CODE_TAG}>" in paragraph:
            # NOTE: Currently only handles case where there's only 1 CODE block
            before_code = ""
            code = ""
            after_code = ""

            # Split on opening tag, and get paragraph BEFORE code
            before_par_split = paragraph.split(f"<{CODE_TAG}>")
            # Remove empty strings
            before_par_split = [i for i in before_par_split if i]
            if len(before_par_split) > 2:
                raise RuntimeError("Unhandled Case: Two code blocks in the "
                                   "same paragraph!")
            elif len(before_par_split) == 2:
                remaining_par = f"<{CODE_TAG}>" + before_par_split[1]
                # Handle paragraph before <code>
                # NOTE: Ensure no newlines before/after adding <p> tags
                before_code = prepend_before_char(
                    before_par_split[0], f"<{PAR_TAG}>", "\n")
                before_code = append_before_char(
                    before_code, f"</{PAR_TAG}>", "\n")
                before_code += "\n"
            else:
                # If only code block, means there's nothing before
                remaining_par = f"<{CODE_TAG}>" + before_par_split[0]

            # Split remaining on closing tag, and get paragraph AFTER code
            after_par_split = remaining_par.split(f"</{CODE_TAG}>")
            # Remove empty strings
            after_par_split = [i for i in after_par_split if i]
            if len(after_par_split) == 2:
                code = after_par_split[0] + f"</{CODE_TAG}>"
                # Handle paragraph after <code>
                # NOTE: Ensure no newlines after adding opening <p> tag
                after_code = prepend_before_char(
                    after_par_split[1], f"\n<{PAR_TAG}>", "\n")
                after_code = append_before_char(
                    after_code, f"</{PAR_TAG}>", "\n")
            else:
                # If only code block, means there's nothing after
                code = remaining_par

            # Assemble new paragraph
            new_paragraphs.append(before_code + code + after_code)
        else:
            new_paragraphs.append(f"<{PAR_TAG}>" + paragraph + f"</{PAR_TAG}>")

    # Reassemble paragraphs
    text = "\n\n".join(new_paragraphs)

    return text


def append_before_char(text, to_add, char="\n"):
    """
    Append text to another text, but only before a specific character.

    Parameters
    ----------
    text : str
        Original string
    to_add : str
        String to add
    char : str, optional
        String to append before, by default "\n"

    Returns
    -------
    str
        New text, where <to_add> is inserted before the last <char>
    """
    # Find last index to append <to_add>
    last_idx = len(text)
    i = last_idx
    while text[i-1] == char:
        i -= 1

    # Assemble new text
    new_text = text[:i] + to_add + text[i: last_idx]
    return new_text


def prepend_before_char(text, to_add, char="\n"):
    """
    Prepend text to another text, but only after a specific character.

    Parameters
    ----------
    text : str
        Original string
    to_add : str
        String to add
    char : str, optional
        String to prepend after, by default "\n"

    Returns
    -------
    str
        New text, where <to_add> is prepended after the first contiguous set of
        <char>
    """
    # Find last index to append <to_add>
    last_idx = len(text)
    i = 0
    for i in range(last_idx):
        if text[i] != char:
            break

    # Assemble new text
    new_text = text[:i] + to_add + text[i: last_idx]
    return new_text
