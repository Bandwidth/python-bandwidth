from .lazy_enumerable import get_lazy_enumerator


class AccountMixin:
    """
    Account API
    """

    def get_account(self):
        """
        Get an Account object

        :rtype: dict
        :returns: account data

        :Example:
        data = api.get_account()
        """
        return self._make_request('get', '/users/%s/account' % self.user_id)[0]

    def get_account_transactions(self, query=None):
        """
        Get the transactions from the user's account

        Query parameters
            maxItems
                Limit the number of transactions that will be returned.
            toDate
                Return only transactions that are newer than the parameter. Format: "yyyy-MM-dd'T'HH:mm:ssZ"
            fromDate
                Return only transactions that are older than the parameter. Format: "yyyy-MM-dd'T'HH:mm:ssZ"
            type
                Return only transactions that are this type.
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)

        :rtype: types.GeneratorType
        :returns: list of transactions

        :Example:
        list = api.get_account_transactions({'type': 'charge'})
        """
        path = '/users/%s/account/transactions' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))
