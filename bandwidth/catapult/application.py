from .lazy_enumerable import get_lazy_enumerator


class ApplicationMixin:
    """
    Application API
    """
    def get_applications(self, query=None):
        """
        Get a list of user's applications

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of applications

        :Example:
        list = api.get_applications()
        """
        path = '/users/%s/applications' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_application(self, data):
        """
        Creates an application that can handle calls and messages for one of your phone number.

        Parameters
            name
                A name you choose for this application (required).
            incomingCallUrl
                A URL where call events will be sent for an inbound call.
            incomingCallUrlCallbackTimeout
                Determine how long should the platform wait for inconmingCallUrl's response
                before timing out in milliseconds.
            incomingCallFallbackUrl
                The URL used to send the callback event if the request to incomingCallUrl fails.
            incomingMessageUrl
                A URL where message events will be sent for an inbound SMS message
            incomingMessageUrlCallbackTimeout
                Determine how long should the platform wait for incomingMessageUrl's response before
                timing out in milliseconds.
            incomingMessageFallbackUrl
                The URL used to send the callback event if the request to incomingMessageUrl fails.
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                (If not set the default is HTTP POST)
            autoAnswer
                Determines whether or not an incoming call should be automatically answered.
                Default value is 'true'.

        :rtype: str
        :returns: id of crested application

        :Example:
        id = api.create_application({'name': 'MyApp'})
        """
        return self._make_request('post', '/users/%s/applications' % self.user_id, json=data)[2]

    def get_application(self, id):
        """
        Gets information about an application

        :type id: str
        :param id: id of an application

        :rtype: dict
        :returns: application information

        :Example:
        data = api.get_application('appId')
        """
        return self._make_request('get', '/users/%s/applications/%s' % (self.user_id, id))[0]

    def delete_application(self, id):
        """
        Remove an application

        :type id: str
        :param id: id of an application

        :Example:
        api.delete_application('appId')
        """
        self._make_request('delete', '/users/%s/applications/%s' % (self.user_id, id))
