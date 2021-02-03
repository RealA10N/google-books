""" A collection of general utilities and objects that are used in various
places across the API. """


from abc import ABC, abstractmethod


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
