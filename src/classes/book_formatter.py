"""
book_formatter.py

Description:
    Used to format generated book into HTML
"""

class BookFormatter:
    """
    BookFormatter class. Used to format book contents into HTML code.
    """

    def __init__(self, book_dict):
        """
        Initialize BookFormatter object

        Parameters
        ----------
        book_dict : dict
            Contains `title`, `toc` and `sections`, where `sections` is of the
            form: {section: subsection: text} or {section: text}
        """
        self.book_dict = book_dict

        # Store HTML for pages
        self.title_html = None
        self.toc_html = None
        self.section_html = None


    # TODO: Implement this
    def format_book(self):
        """
        Formats book
        """
        raise NotImplementedError


    # TODO: Implement this
    def save_html(self, directory, fname="book.html"):
        """
        Save formatted HTML to a text file.

        Parameters
        ----------
        directory : str
            Directory to save HTML file in
        fname : str
            Filename to save book as. Defaults to "book.html"
        """
        raise NotImplementedError

