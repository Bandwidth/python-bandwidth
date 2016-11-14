from .lazy_enumerable import get_lazy_enumerator


class MessageMixin:
    """
    Message API
    """
    def get_messages(self, query=None):
        """
        Get a list of user's messages

        Query parameters
            from
                The phone number to filter the messages that came from
            to
                The phone number to filter the messages that was sent to
            fromDateTime
                The starting date time to filter the messages
                (must be in yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
            toDateTime
                The ending date time to filter the messages (must be in
                yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
            direction
                Filter by direction of message, in - a message that came from the telephone
                 network to one of your numbers (an "inbound" message) or out - a message
                 that was sent from one of your numbers to the telephone network (an "outbound"
                 message)
            state
                The message state to filter. Values are 'received', 'queued', 'sending',
                'sent', 'error'
            deliveryState
                The message delivery state to filter. Values are 'waiting', 'delivered',
                'not-delivered'
            sortOrder
                How to sort the messages. Values are 'asc' or 'desc'
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of messages

        :Example:
        list = api.get_messages()
        """
        path = '/users/%s/messages' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def send_message(self, data):
        """
        Send a message (SMS or MMS)

        Parameters
            from
                One of your telephone numbers the message should come from
            to
                The phone number the message should be sent to
            text
                The contents of the text message
            media
                For MMS messages, a media url to the location of the media or list of medias to
                be sent send with the message.
            receiptRequested
                Requested receipt option for outbound messages: 'none', 'all', 'error'
            callbackUrl
                The server URL where the events related to the outgoing message will
                be sent to
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are get or post Default is post
            callbackTimeout
                Determine how long should the platform wait for callbackUrl's response
                before timing out (milliseconds).
            fallbackUrl
                The server URL used to send the message events if the request to callbackUrl fails.
            tag
                Any string, it will be included in the callback events of the message.
        :rtype: str
        :returns: id of created message

        :Example:
        # SMS
        id = api.send_message({'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'})
        # MMS
        id = api.send_message({'from': '+1234567980', 'to': '+1234567981', 'text': 'MMS message',
        'media': ['http://host/path/to/file']})
        """
        return self._make_request('post', '/users/%s/messages' % self.user_id, json=data)[2]

    def send_messages(self, messages_data):
        """
        Send some messages by one request

        :type messages_data: list
        :param messages_data: List of messages to send

        Parameters of each message
            from
                One of your telephone numbers the message should come from
            to
                The phone number the message should be sent to
            text
                The contents of the text message
            media
                For MMS messages, a media url to the location of the media or list of medias to
                be sent send with the message.
            receiptRequested
                Requested receipt option for outbound messages: 'none', 'all', 'error'
            callbackUrl
                The server URL where the events related to the outgoing message will
                be sent to
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are get or post Default is post
            callbackTimeout
                Determine how long should the platform wait for callbackUrl's response
                before timing out (milliseconds).
            fallbackUrl
                The server URL used to send the message events if the request to callbackUrl fails.
            tag
                Any string, it will be included in the callback events of the message.
        :rtype: list
        :returns: results of sent messages

        :Example:
        results = api.send_message([
            {'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'},
            {'from': '+1234567980', 'to': '+1234567982', 'text': 'SMS message2'}
        ])
        """
        results = self._make_request('post', '/users/%s/messages' % self.user_id, json=messages_data)[0]
        for i in range(0, len(messages_data)):
            item = results[i]
            item['id'] = item.get('location', '').split('/')[-1]
            item['message'] = messages_data[i]
        return results

    def get_message(self, id):
        """
        Get information about a message

        :type id: str
        :param id: id of a message

        :rtype: dict
        :returns: message information

        :Example:
        data = api.get_message('messageId')
        """
        return self._make_request('get', '/users/%s/messages/%s' % (self.user_id, id))[0]
