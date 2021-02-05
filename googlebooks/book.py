import typing
import string
import datetime

from lxml import etree
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

    @property
    def description_xml(self,) -> str:
        """ A synopsis of the book volume. Formatted in HTML and includes
        simple formatting elements, such as b, i, and br tags. """

        data = self._access('volumeInfo', 'description')

        if data is not None:
            return f'<p>{data}</p>'

        return None

    @property
    def description_html(self,) -> str:
        """ A synopsis of the book volume. Formatted in HTML and includes
        simple formatting elements, such as b, i, and br tags. Same as the
        `description_xml` property. """
        return self.description_xml

    @property
    def description(self,) -> str:
        """ A synopsis of the book volume. """

        if self.description_xml is None:
            return None

        try:
            # pylint: disable=c-extension-no-member
            tree = etree.XML(self.description_xml)
            return etree.tostring(tree, method='text', encoding='unicode')

        except Exception:  # pylint: disable=broad-except
            return None

    def _identifier(self, identifier_name: str) -> str:
        """ Industry standard identifiers for this book volume. This method
        recives the name of the identifier, and returns its value. If the
        identifier doesn't exist, returns None. """

        identifiers = self._access('volumeInfo', 'industryIdentifiers')

        try:
            return next(
                identifier['identifier']
                for identifier in identifiers
                if identifier['type'] == identifier_name
            )

        except StopIteration:
            # If identifier is not in the list of identifiers
            return None

    @property
    def isbn(self,) -> str:
        """ The 'International Standarad Book Number' for this current volume
        (13 characters). An alias of the `isbn_13` property. """
        return self.isbn_13

    @property
    def isbn_13(self,) -> str:
        """ The 'International Standarad Book Number' for this current volume
        (13 characters). """
        return self._identifier('ISBN_13')

    @property
    def isbn_10(self,) -> str:
        """ The 'International Standarad Book Number' for this current volume
        (10 characters). """
        return self._identifier('ISBN_10')

    @property
    def issn(self,) -> str:
        """ The 'International Standard Serial Number' for this current book
        volume. """
        return self._identifier('ISSN')

    @property
    def pages(self,) -> int:
        """ Total number of pages in this book volume. """
        return self._access('volumeInfo', 'pageCount')

    @staticmethod
    def _dimension_str_to_float(dimension: str) -> typing.Optional[float]:
        """ Recives a dimension string (for example '69.00 cm'), and returns
        the dimension as a float. """

        if dimension is None:
            return None

        valid_chars = string.digits + '.'
        new_dimension = ''.join(
            char for char in dimension if char in valid_chars)
        return float(new_dimension)

    @property
    def height_str(self,) -> str:
        """ Height or length of this book volume, as a readable string. """
        return self._access('volumeInfo', 'dimensions', 'height')

    @property
    def height(self,) -> float:
        """ Height or length of this book volume (in cm). """
        return self._dimension_str_to_float(self.height_str)

    @property
    def width_str(self,) -> str:
        """ Width of this book volume, as a readable string. """
        return self._access('volumeInfo', 'dimensions', 'width')

    @property
    def width(self,) -> float:
        """ Height or length of this book volume (in cm). """
        return self._dimension_str_to_float(self.width_str)

    @property
    def thickness_str(self,) -> str:
        """ Thickness of this book volume, as a readable string. """
        return self._access('volumeInfo', 'dimensions', 'thickness')

    @property
    def thickness(self,) -> float:
        """ Thickness of this book volume (in cm). """
        return self._dimension_str_to_float(self.thickness_str)

    @property
    def is_book(self,) -> bool:
        """ `True` only if this book volume is a book (not a
        magazine). """
        return self._access('volumeInfo', 'printType') == 'BOOK'

    @property
    def is_magazine(self,) -> bool:
        """ `True` only if this book volume is actually a magazine. """
        return self._access('volumeInfo', 'printType') == 'MAGAZINE'

    @property
    def is_mature(self,) -> bool:
        """ `True` only if the maturity rating for this book volume is
        'mature'. """
        return self._access('volumeInfo', 'maturityRating') == 'MATURE'

    @property
    def ratings_count(self,) -> int:
        """ The number of review ratings for this book volume. """

        count = self._access('volumeInfo', 'ratingsCount')
        if count is None:
            return 0

        return count

    @property
    def rating(self,) -> typing.Optional[float]:
        """ The mean review rating for this bok volume (min = 1.0,
        max = 5.0). `None` if there are no rating. """
        return self._access('volumeInfo', 'averageRating')

    @property
    def content_version(self,) -> str:
        """ An identifier for the version of the volume content (text &
        images). """
        return self._access('volumeInfo', 'contentVersion')

    @property
    def image_url_small_thumbnail(self,) -> typing.Optional[str]:
        """	Image link for small thumbnail size (width of ~80 pixels). """
        return self._access('volumeInfo', 'imageLinks', 'thumbnail')

    @property
    def image_url_thumbnail(self,) -> typing.Optional[str]:
        """	Image link for thumbnail size (width of ~128 pixels). """
        return self._access('volumeInfo', 'imageLinks', 'thumbnail')

    @property
    def image_url_small(self,) -> typing.Optional[str]:
        """ Image link for small size (width of ~300 pixels). """
        return self._access('volumeInfo', 'imageLinks', 'small')

    @property
    def image_url_medium(self,) -> typing.Optional[str]:
        """ Image link for medium size (width of ~575 pixels). """
        return self._access('volumeInfo', 'imageLinks', 'medium')

    @property
    def image_url_large(self,) -> typing.Optional[str]:
        """ Image link for large size (width of ~800 pixels). """
        return self._access('volumeInfo', 'imageLinks', 'large')

    @property
    def image_url_extra_large(self,) -> typing.Optional[str]:
        """ Image link for extra large size (width of ~1280 pixels). """
        return self._access('volumeInfo', 'imageLinks', 'extraLarge')

    @property
    def image_url(self,) -> typing.Optional[str]:
        """ Image link for the largest image avaliable. """

        try:
            return next(
                link for link in (
                    self.image_url_extra_large,
                    self.image_url_large,
                    self.image_url_medium,
                    self.image_url_small,
                    self.image_url_thumbnail,
                    self.image_url_small_thumbnail,
                )
                if link is not None
            )

        except StopIteration:
            # If there is no avaliable image url
            return None
