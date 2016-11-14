from .lazy_enumerable import get_lazy_enumerator


class PhoneNumberMixin:
    """
    PhoneNumber API
    """
    def get_phone_numbers(self, query=None):
        """
        Get a list of user's phone numbers

        Query parameters
            applicationId
                Used to filter the retrieved list of numbers by an associated application ID.
            state
                Used to filter the retrieved list of numbers allocated for the authenticated
                user by a US state.
            name
                Used to filter the retrieved list of numbers allocated for the authenticated
                user by it's name.
            city
                Used to filter the retrieved list of numbers allocated for the authenticated user
                by it's city.
            numberState
                Used to filter the retrieved list of numbers allocated for the authenticated user
                by the number state.
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of phone numbers

        :Example:
        list = api.get_phone_numbers()
        """
        path = '/users/%s/phoneNumbers' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_phone_number(self, data):
        """
        Allocates a number so user can use it to make and receive calls and send
        and receive messages.

        Parameters
            number
                An available telephone number you want to use
            name
                A name you choose for this number.
            applicationId
                The unique id of an Application you want to associate with this number.
            fallbackNumber
                Number to transfer an incoming call when the callback/fallback events can't
                be delivered.

        :rtype: str
        :returns: id of created phone number

        :Example:
        id = api.create_phone_number({'number': '+1234567890'})
        """
        return self._make_request('post', '/users/%s/phoneNumbers' % self.user_id, json=data)[2]

    def get_phone_number(self, id):
        """
        Get information about a phone number

        :type id: str
        :param id: id of a phone number

        :rtype: dict
        :returns: number information

        :Example:
        data = api.get_phone_number('numberId')
        """
        return self._make_request('get', '/users/%s/phoneNumbers/%s' % (self.user_id, id))[0]

    def update_phone_number(self, id, data):
        """
        Update information about a phone number

        :type id: str
        :param id: id of a phone number

        Parameters
            name
                A name you choose for this number.
            applicationId
                The unique id of an Application you want to associate with this number.
            fallbackNumber
                Number to transfer an incoming call when the callback/fallback events can't
                be delivered.

        :Example:
        data = api.update_phone_number('numberId', {'applicationId': 'appId1'})
        """
        self._make_request('post', '/users/%s/phoneNumbers/%s' % (self.user_id, id), json=data)

    def delete_phone_number(self, id):
        """
        Remove a phone number

        :type id: str
        :param id: id of a phone number

        :Example:
        api.delete_phone_number('numberId')
        """
        self._make_request('delete', '/users/%s/phoneNumbers/%s' % (self.user_id, id))
