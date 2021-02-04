""" A collection of general utilities and objects that are used in various
places across the API. """


import typing
import warnings
from abc import ABC, abstractmethod

import requests


class BooksResource:
    """ Base class for all Google Books API resources. """

    def __init__(self, data: typing.Dict[str, str]):
        self.__assert_valid_data(data)
        self._data = data

    @staticmethod
    def __assert_valid_data(data: typing.Dict[str, str]):
        """ Recives recourse data, and raises an error if the data is
        invalid. """

        if not isinstance(data, dict):
            raise TypeError(
                f"Resource data must be a dict, nor {type(data).__name__}")

        try:
            # Each resource must have a 'kind' and 'selfLink' properties
            assert 'kind' in data
            assert data['kind'].startswith('books#')
            assert 'selfLink' in data

        except AssertionError as error:
            raise ValueError("Invalid resource data") from error

    @staticmethod
    def _request(url: str,):
        """ Recives a url, makes an http get request to the given url and
        returns the JSON content. Raises an error if something went wrong. """

        response = requests.get(url=url)
        response.raise_for_status()
        return response.json()

    def _access(self, *path: str, data: dict = None):
        """ Recives a list of strings (path) and 'travels' inside the
        given data dict following the given path. If the endpoint doesn't
        exist, returns None. """

        # The default data is the resource data dictionary
        if data is None:
            data = self._data

        # If the path is not given, returns the data (stop condition).
        if not path:
            return data

        try:
            # Tries to travel a single step in the path
            return self._access(*path[1:], data=data[path[0]])

        except KeyError:
            # If the step is not valid, returns `None`
            return None

    def reload(self,) -> None:
        """ Reloads the resource by making a new http get request. """

        try:
            self._data = self._request(self._self_link)

        except requests.exceptions.HTTPError as error:
            warnings.warn(f'Reloading resource failed: {error}')

    @property
    def _self_link(self,) -> str:
        """ URL to the resource information. """
        return self._access('selfLink')

    @property
    def resource_kind(self,) -> str:
        """ The resource type, as a string. From the format 'book#{type}' """
        return self._access('kind')


class OptionCollection(ABC):
    """ An abstract object. Objects that inherit from `OptionCollection` are
    used by the API and the user to select a single option from a defined set
    of avaliable options.
    For example - When searching books using the API, it can filter the search
    results in 5 different ways. The `SearchFilters` object (that inheres this
    object) contains those options, and lets the user select one of the
    avaliable options only. """

    # pylint: disable=invalid-name

    @classmethod
    @property
    @abstractmethod
    def AvaliableOptions(cls) -> set:
        """ Abstract. A set with all avaliable options in the object. """

    @classmethod
    def assert_valid_option(cls, option):
        """ Recives an option and raises an error if the option is invalid. """

        if option not in cls.AvaliableOptions:
            raise ValueError(
                f"Invalid option '{option}'. The avaliable options are {cls.AvaliableOptions}"
            )
