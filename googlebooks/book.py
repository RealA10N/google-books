import typing
import string
import datetime

import dateparser
import requests

from .utils import BooksResource


class Book(BooksResource):

    BOOK_ID_API_URL = 'https://www.googleapis.com/books/v1/volumes/{id}'

    @classmethod
    def from_id(cls, book_id: str):
        """ Generates and returns a `BookVolume` instance out of a book id. """

        cls.__assert_valid_id(book_id)
        url = cls.BOOK_ID_API_URL.replace('{id}', book_id)

        try:
            data = cls._request(url)

        except requests.exceptions.HTTPError as error:
            # If the response status code is not 200
            raise ValueError(
                f'Book with id {book_id} is unavailable.'
            ) from error

        # Generates the instance and returns it
        return cls(data)

    @staticmethod
    def __assert_valid_id(book_id: str):
        """ Recives a book ID, and raises an error if the ID is not valid. """

        if not isinstance(book_id, str):
            raise TypeError(
                f"Book ID must be a 12 char string, not {type(book_id).__name__}")

        if len(book_id) != 12:
            raise ValueError("Book ID must be a 12 char string")

        valid_chars = string.ascii_letters + string.digits + string.punctuation
        for char in book_id:
            if char not in valid_chars:
                raise ValueError("Invalid book ID")

    @staticmethod
    def __combine_strings(strings: typing.List[str]) -> str:
        """ Recives a list of strings, combines and returns them as a single
        string seperated by commas and 'and'. """

        if len(strings) == 0:
            return 'Unknown'

        main = list(strings[:-1])
        tail = strings[-1]

        if len(strings) == 2:
            return f'{main[0]} and {tail}'

        if len(strings) == 1:
            return tail

        main.append(f'and {tail}')
        return ', '.join(main)

    @property
    def id(self,) -> str:  # pylint: disable=invalid-name
        """ Unique identifier for the book volume. """
        return self._access('id')

    @property
    def etag(self,) -> str:
        """ Opaque identifier for a specific version of a book volume
        resource. """
        return self._access('etag')

    @property
    def title(self,) -> str:
        """ The title of the book volume. """
        return self._access('volumeInfo', 'title')

    @property
    def subtitle(self,) -> str:
        """ The subtitle of the book volume. """
        return self._access('volumeInfo', 'subtitle')

    @property
    def authors(self,) -> typing.Tuple[str]:
        """ The names of the authors and/or editors of the book volume. """
        authors = self._access('volumeInfo', 'authors')
        value = tuple(authors) if authors is not None else tuple()
        return value

    @property
    def authors_str(self,) -> str:
        """ The names of the authors and/or editors of the book volume, as
        a single string. """
        return self.__combine_strings(self.authors)

    @property
    def publisher(self,) -> str:
        """ The publisher of the book volume. """
        return self._access('volumeInfo', 'publisher')

    @property
    def published_str(self,) -> str:
        """ The date of publication of the book volume. """
        return self._access('volumeInfo', 'publishedDate')

    @property
    def published(self,) -> datetime.datetime:
        """ The date of publication of the book volume. Returned as a datetime
        instance. """

        if self.published_str is None:
            return None

        relative_to = dateparser.parse('january 1st')
        return dateparser.parse(
            self.published_str,
            settings={'RELATIVE_BASE': relative_to},
        )
