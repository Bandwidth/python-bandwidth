class AvailableNumberMixin:
    """
    Available number API
    """
    def search_available_numbers(self, number_type='local', query=None):
        """
        Searches for available local or toll free numbers.

        :type number_type: str
        :param number_type: type of number to search ('local' or 'tollFree')

        Query parameters for local numbers
            city
                A city name
            state
                A two-letter US state abbreviation
            zip
                A 5-digit US ZIP code
            areaCode
                A 3-digit telephone area code
            localNumber
                It is defined as the first digits of a telephone number inside an area code
                for filtering the results. It must have at least 3 digits and the areaCode
                field must be filled.
            inLocalCallingArea
                Boolean value to indicate that the search for available numbers must consider
                overlayed areas.
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)
            pattern
                A number pattern that may include letters, digits, and the wildcard characters

        Query parameters for toll free numbers
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)
            pattern
                A number pattern that may include letters, digits, and the wildcard characters

        :rtype: list
        :returns: list of numbers

        :Example:
        numbers = api.search_available_numbers('local', {'areaCode': '910', 'quantity': 3})
        """
        return self._make_request('get', '/availableNumbers/%s' % number_type, params=query)[0]

    def search_and_order_available_numbers(self, number_type='local', query=None):
        """
        Searches and orders for available local or toll free numbers.

        :type number_type: str
        :param number_type: type of number to search ('local' or 'tollFree')

        Query parameters for local numbers
            city
                A city name
            state
                A two-letter US state abbreviation
            zip
                A 5-digit US ZIP code
            areaCode
                A 3-digit telephone area code
            localNumber
                It is defined as the first digits of a telephone number inside an area code
                for filtering the results. It must have at least 3 digits and the areaCode
                field must be filled.
            inLocalCallingArea
                Boolean value to indicate that the search for available numbers must consider
                overlayed areas.
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)

        Query parameters for toll free numbers
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)

        :rtype: list
        :returns: list of ordered numbers

        :Example:
        ordered_numbers = api.search_and_order_available_numbers('local', {'areaCode': '910', 'quantity': 3})
        """
        list = self._make_request('post', '/availableNumbers/%s' % number_type, params=query)[0]
        for item in list:
            item['id'] = item.get('location', '').split('/')[-1]
        return list
