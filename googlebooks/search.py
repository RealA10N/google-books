class BookSearchQueryType:
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


class BookSearchQueries:
    """ A collection of `BookSearchQueryType` instances. Use the properties of
    this object to access different query types! """

    __AVALIABLE_QUERY_TYPES = {
        'intitle', 'inauthor', 'inpublisher', 'subject',
        'isbn', 'lccn', 'oclc',
    }

    def __init__(self):
        self._main_query = BookSearchQueryType()
        self._queries = {
            name: BookSearchQueryType(name)
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
    def title(self,) -> BookSearchQueryType:
        """ Search the queries in book titles only """
        return self._queries['intitle']

    @property
    def author(self,) -> BookSearchQueryType:
        """ Search the queries in book authors and editors only """
        return self._queries['inauthor']

    @property
    def publisher(self,) -> BookSearchQueryType:
        """ Search the queries in book publishers only """
        return self._queries['inpublisher']

    @property
    def subject(self,) -> BookSearchQueryType:
        """ Search the queries in subject (categories) only """
        return self._queries['subject']

    @property
    def isbn(self,) -> BookSearchQueryType:
        """ Search the queries in book ISBN numbers only """
        return self._queries['isbn']

    @property
    def lccn(self,) -> BookSearchQueryType:
        """ Search the queries in book 'Library of Congress Control' numbers only """
        return self._queries['lccn']

    @property
    def oclc(self,) -> BookSearchQueryType:
        """ Search the queries in book 'Online Computer Library Center' number only """
        return self._queries['oclc']

    def __str__(self,):
        """ Generates the 'final' search query that is used to make the
        book search request. """

        queries = [self._main_query] + list(self._queries.values())
        return ''.join(str(value) for value in queries)
