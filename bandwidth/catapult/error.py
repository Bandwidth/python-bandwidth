from .lazy_enumerable import get_lazy_enumerator


class ErrorMixin:

    def get_errors(self, query=None):
        """
        Get a list of errors

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of calls

        :Example:
        list = api.get_errors()
        """

        path = '/users/%s/errors' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def get_error(self, id):
        """
        Get information about an error

        :type id: str
        :param id: id of an error

        :rtype: dict
        :returns: error information

        :Example:
        data = api.get_error('errorId')
        """
        return self._make_request('get', '/users/%s/errors/%s' % (self.user_id, id))[0]
