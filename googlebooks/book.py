import typing
import string

import requests


class Book:

    BOOK_ID_API_URL = 'https://www.googleapis.com/books/v1/volumes/{id}'

    @classmethod
    def from_id(cls, book_id: str):
        """ Generates and returns a `BookVolume` instance out of a book id. """

        cls.__assert_valid_id(book_id)
        url = cls.BOOK_ID_API_URL.replace('{id}', book_id)
        response = requests.get(url=url)

        # Raise an error if something went wrong
        if response.status_code == 404:
            # If the id doesn't match any book
            raise ValueError("Book with the given id is not found")

        # Check for other error that may have occurred
        response.raise_for_status()

        # Generates the instance and returns it
        return cls(response.json())

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
