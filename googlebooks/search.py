import typing
from .utils.search import SearchFilters, SearchPrintType, SearchSorting


class SearchQueryType:
    """ This object represents a single query type in the book search object.
    Using this object, the user can easily manage the search queries, and the
    object automatically generates the find query string. """

    def __init__(self, name: str = None):
        self._name = name
        self._include = set()
        self._exclude = set()

    @staticmethod
    def __assert_valid_query(query: str) -> None:
        """ Asserts that the given query is a valid query, and raises a
        `TypeError` if it is not! """

        if not isinstance(query, str):
            raise TypeError(
                f"Invalid query type. Must be a string (not {type(query)})"
            )

    def include(self, query: str, exact: bool = False) -> None:
        """ Add a query to the search (string). By default each word (seperated
        by spaces) will be considered as a separate query. If you want to find
        books with the exact given string, you should set the `exact` keyword
        argument to `True`. """

        self.__assert_valid_query(query)
        query = {f'"{query}"'} if exact else set(query.split())
        self._include.update(query)
        self._exclude -= query

    def exclude(self, query: str, exact: bool = False) -> None:
        """ Remove a query from the search (string) and makes sure that the
        resulting books WON'T include the given query. By default each word
        (seperated by spaces) will be considered as a separate query. If you
        want to exclude books with the exact given string, you should set the
        `exact` keyword argument to `True`. """

        self.__assert_valid_query(query)
        query = {f'"{query}"'} if exact else set(query.split())
        self._exclude.update(query)
        self._include -= query

    def __generate_single_query_str(self,
                                    query: str,
                                    exclude: bool = False,
                                    ) -> str:
        """ Recives a query string, and returns the string that represents
        the query in whole query type string. """

        prefix = '-' if exclude else '+'
        name = f'{self._name}:' if self._name is not None else str()
        return f'{prefix}{name}{query}'

    def __str__(self,) -> str:
        """ Converts the search query into a string, that can be used when
        sending request to the Google Books API. """

        include_string = ''.join(self.__generate_single_query_str(
            query, exclude=False) for query in self._include)
        exclude_string = ''.join(self.__generate_single_query_str(
            query, exclude=True) for query in self._exclude)

        return include_string + exclude_string


class SearchAdvancedQuery:
    """ A collection of `SearchQueryType` instances. Use the properties of
    this object to access different query types! """

    __AVALIABLE_QUERY_TYPES = {
        'intitle', 'inauthor', 'inpublisher', 'subject',
        'isbn', 'lccn', 'oclc',
    }

    def __init__(self):
        self._main_query = SearchQueryType()
        self._queries = {
            name: SearchQueryType(name)
            for name in self.__AVALIABLE_QUERY_TYPES
        }

    def include(self, query: str, exact: bool = False) -> None:
        """ Add a query to the search (string). By default each word (seperated
        by spaces) will be considered as a separate query. If you want to find
        books with the exact given string, you should set the `exact` keyword
        argument to `True`. """
        return self._main_query.include(query, exact)

    def exclude(self, query: str, exact: bool = False) -> None:
        """ Remove a query from the search (string) and makes sure that the
        resulting books WON'T include the given query. By default each word
        (seperated by spaces) will be considered as a separate query. If you
        want to exclude books with the exact given string, you should set the
        `exact` keyword argument to `True`. """
        return self._main_query.exclude(query, exact)

    @property
    def title(self,) -> SearchQueryType:
        """ Search the queries in book titles only """
        return self._queries['intitle']

    @property
    def author(self,) -> SearchQueryType:
        """ Search the queries in book authors and editors only """
        return self._queries['inauthor']

    @property
    def publisher(self,) -> SearchQueryType:
        """ Search the queries in book publishers only """
        return self._queries['inpublisher']

    @property
    def subject(self,) -> SearchQueryType:
        """ Search the queries in subject (categories) only """
        return self._queries['subject']

    @property
    def isbn(self,) -> SearchQueryType:
        """ Search the queries in book ISBN numbers only """
        return self._queries['isbn']

    @property
    def lccn(self,) -> SearchQueryType:
        """ Search the queries in book 'Library of Congress Control' numbers only """
        return self._queries['lccn']

    @property
    def oclc(self,) -> SearchQueryType:
        """ Search the queries in book 'Online Computer Library Center' number only """
        return self._queries['oclc']

    def __str__(self,):
        """ Generates the 'final' search query that is used to make the
        book search request. """

        queries = [self._main_query] + list(self._queries.values())
        return ''.join(str(value) for value in queries)


class BooksSearch:

    def __init__(self,
                 query: typing.Union[SearchAdvancedQuery, str],
                 lang: str = None,
                 search_filter: str = None,
                 print_type: str = None,
                 order: str = None,
                 downloadable_only: bool = False,
                 ):

        self.__params = self.__generate_params(
            query=query, lang=lang, search_filter=search_filter,
            print_type=print_type, order=order,
            downloadable_only=downloadable_only
        )

    @classmethod
    def __generate_params(cls,
                          query: typing.Union[SearchAdvancedQuery, str],
                          lang: str = None,
                          search_filter: str = None,
                          print_type: str = None,
                          order: str = None,
                          downloadable_only: bool = False,
                          ) -> typing.Dict[str, str]:

        # Handle the 'query' argument
        query = cls.__generate_query_string(query)

        # Handle the 'lang' argument
        if lang is not None:
            cls.__asserts_valid_language(lang)

        # Handle the 'search_filter' argument
        if search_filter is not None:
            SearchFilters.assert_valid_option(search_filter)

        # Handle the 'print_type' argument
        if print_type is not None:
            SearchPrintType.assert_valid_option(print_type)

        # Handle the 'order' argument
        if order is not None:
            SearchSorting.assert_valid_option(order)

        # Handle the 'downloadable_only' argument
        downloadable_only = 'epub' if downloadable_only else None

        # - - generate request params - - #

        # Essential parameters only
        params = {
            'q': query,

            # lets the Google Books API  know that we want to download
            # all content of resulting books, and not just the most important
            # data ('full' and not 'lite')
            'projection': 'full',
        }

        # Extra params that the not required, but are optional
        extra_params = {

            key: value
            for key, value in {
                'langRestrict': lang,
                'filter': search_filter,
                'printType': print_type,
                'orderBy': order,
                'download': downloadable_only,
            }.items()

            # Removes params where the values are `None`
            if value is not None
        }

        # Merges the two parameter dicts
        params.update(extra_params)
        return params

    @staticmethod
    def __asserts_valid_language(lang_iso: str) -> None:
        """ Sets the book search langauge to the given language code.
        We use the `ISO 639-1` code format. Find more about language codes
        here:  https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes """

        if not isinstance(lang_iso, str):
            raise TypeError("Language code must be a 2 char string")

        if len(lang_iso) != 2:
            raise ValueError("Language code must be a 2 char string")

    @staticmethod
    def __generate_query_string(
            query: typing.Union[SearchAdvancedQuery, str]) -> str:

        # pylint: disable=invalid-name
        REPLACE_CHARS = {
            (
                ('+', '-', ':'),
                ' ',
            ),
            (
                ('"', "'"),
                '',
            ),
        }

        if isinstance(query, str):
            # If the given query is a simple query (string)

            # Replace invalid strings in the query
            for replace_from_tuple, replace_to in REPLACE_CHARS:
                for replace_from in replace_from_tuple:
                    query = query.replace(replace_from, replace_to)

            # Return the 'fixed' string
            return query

        if isinstance(query, SearchAdvancedQuery):
            # If the query is an advanced query:
            # Generates the query string and returns it
            return str(query)

        # If the given query is not a string or an advanced query
        # Raises an error!

        #pylint: disable=line-too-long
        raise TypeError(
            f"Search query must be a string or an `SearchAdvancedQuery` instance (not {type(query)})"
        )
