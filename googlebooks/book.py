import typing
import string
import datetime
import warnings

import dateparser
import requests


class Book:

    BOOK_ID_API_URL = 'https://www.googleapis.com/books/v1/volumes/{id}'

    @classmethod
    def from_id(cls, book_id: str):
        """ Generates and returns a `BookVolume` instance out of a book id. """

        cls.__assert_valid_id(book_id)
        url = cls.BOOK_ID_API_URL.replace('{id}', book_id)

        try:
            data = cls.__request(url)

        except requests.exceptions.HTTPError as error:
            # If the response status code is not 200
            raise ValueError(
                f'Book with id {book_id} is unavailable.'
            ) from error

        # Generates the instance and returns it
        return cls(data)

    @staticmethod
    def __request(url: str):
        """ Makes a get request to the given url and returns the json data.
        Raises an error if something goes wrong. """

        response = requests.get(url=url)

        # Check for other errors that may have occurred
        response.raise_for_status()
        return response.json()

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
    def __assert_valid_data(data):
        """ Recives book data, and raises an error if the data is invalid. """

        if not isinstance(data, dict):
            raise TypeError(
                f"Book data must be a dict, nor {type(data).__name__}")

        if ('kind' not in data) or (data['kind'] != 'books#volume'):
            raise ValueError("Invalid book data")

    def __init__(self, data: typing.Dict[str, str]):
        self.__assert_valid_data(data)
        self.__data = data

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

    def __access(self, *path: str, data: dict = None):
        """ Recives a list of strings (path) and 'travels' inside the
        given data dict following the given path. If the endpoint doesn't
        exist, returns None. """

        # The default data is the book data dictionary
        if data is None:
            data = self.__data

        # If the path is not given, returns the data (stop condition).
        if not path:
            return data

        try:
            # Tries to travel a single step in the path
            return self.__access(*path[1:], data=data[path[0]])

        except KeyError:
            # If the step is not valid, returns `None`
            return None

    @property
    def __self_link(self,) -> str:
        """ The URL to this resource. Used to reload the resource, if needed. """
        return self.__access('selfLink')

    def reload(self,) -> None:
        """ Reloads the resource. """

        try:
            self.__data = self.__request(self.__self_link)

        except requests.exceptions.HTTPError as error:
            warnings.warn(f'Reloading resource failed: {error}')

    @property
    def id(self,) -> str:  # pylint: disable=invalid-name
        """ Unique identifier for the book volume. """
        return self.__access('id')

    @property
    def etag(self,) -> str:
        """ Opaque identifier for a specific version of a book volume
        resource. """
        return self.__access('etag')

    @property
    def title(self,) -> str:
        """ The title of the book volume. """
        return self.__access('volumeInfo', 'title')

    @property
    def subtitle(self,) -> str:
        """ The subtitle of the book volume. """
        return self.__access('volumeInfo', 'subtitle')

    @property
    def authors(self,) -> typing.Tuple[str]:
        """ The names of the authors and/or editors of the book volume. """
        authors = self.__access('volumeInfo', 'authors')
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
        return self.__access('volumeInfo', 'publisher')

    @property
    def published_str(self,) -> str:
        """ The date of publication of the book volume. """
        return self.__access('volumeInfo', 'publishedDate')

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
