""" A collection of objects that are used to help the book searching operations
in the Google Books API. """

from .utils import OptionCollection


class SearchFilters(OptionCollection):
    """ Google Books API can filter the search results by volume type and
    availability.

    - Partial
        Restrict results to volumes where at least part of the text are
        previewable.

    - Full
        Restrict results to volumes where all of the text is viewable.

    - FreeEbooks
        Restrict results to free Google eBooks.

    - PaidEbooks
        Restrict results to Google eBooks with a price for purchase.

    - Ebooks
        Restrict results to Google eBooks, paid or free. 
        Examples of non-eBooks would be publisher content that is available in
        limited preview and not for sale, or magazines.

    """

    Partial = 'partial'
    Full = 'full'
    FreeEbooks = 'free-ebooks'
    PaidEbooks = 'paid-ebooks'
    Ebooks = 'ebooks'

    AvaliableOptions = {Partial, Full, FreeEbooks, PaidEbooks, Ebooks}


class SearchPrintType(OptionCollection):
    """ Google Books API can restrict the search results to a specific print
    or publication type by setting it to one of the following values:

    - All
        Does not restrict by print type (default).

    - Books
        Returns only results that are books.

    - Magazines
        Returns results that are magazines.

    """

    All = 'all'
    Books = 'books'
    Magazines = 'magazines'

    AvaliableOptions = {All, Books, Magazines}
