import requests
import six
import urllib
import json
import itertools
from bandwidth.voice.lazy_enumerable import get_lazy_enumerator
from bandwidth.convert_camel import convert_object_to_snake_case
from bandwidth.version import __version__ as version

from .api_exception_module import BandwidthMessageAPIException

quote = urllib.parse.quote if six.PY3 else urllib.quote
lazy_map = map if six.PY3 else itertools.imap


class Client:

    """
    Catapult client
    """

    def __init__(self, user_id=None, api_token=None, api_secret=None, **other_options):
        """
        Initialize the catatpult client.
        :type user_id: str
        :param user_id: catapult user id
        :type api_token: str
        :param api_token: catapult api token
        :type api_secret: str
        :param api_secret: catapult api secret
        :type api_endpoint: str
        :param api_endpoint: catapult api endpoint (optional, default value is https://api.catapult.inetwork.com)
        :type api_version: str
        :param api_version: catapult api version (optional, default value is v1)

        :rtype: bandwidth.catapult.Client
        :returns: bandwidth client

        Init the catapult client::

            api = bandwidth.catapult.Client('YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
            # or
            api = bandwidth.client('catapult', 'YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
        """
        if not all((user_id, api_token, api_secret)):
            raise ValueError('Arguments user_id, api_token and api_secret are required. '
                             'Use bandwidth.client("catapult", "YOUR-USER-ID", "YOUR-API-TOKEN", "YOUR-API-SECRET")')
        self.user_id = user_id
        self.api_endpoint = other_options.get(
            'api_endpoint', 'https://api.catapult.inetwork.com')
        self.api_version = other_options.get('api_version', 'v1')
        self.auth = (api_token, api_secret)

    def _request(self, method, url, *args, **kwargs):
        user_agent = 'PythonSDK_' + version
        headers = kwargs.pop('headers', None)
        if headers:
            headers['User-Agent'] = user_agent
        else:
            headers = {
                'User-Agent': user_agent
            }
        if url.startswith('/'):
            # relative url
            url = '%s/%s%s' % (self.api_endpoint, self.api_version, url)
        return requests.request(method, url, auth=self.auth, headers=headers, *args, **kwargs)

    def _check_response(self, response):
        if response.status_code >= 400:
            if response.headers.get('content-type') is not None and \
                    response.headers.get('content-type').startswith("application/json"):
                data = response.json()
                raise BandwidthMessageAPIException(
                    response.status_code, data['message'], code=data.get('code'))
            else:
                raise BandwidthMessageAPIException(
                    response.status_code, response.content.decode('utf-8')[:79])

    def _make_request(self, method, url, *args, **kwargs):
        response = self._request(method, url, *args, **kwargs)
        self._check_response(response)
        data = None
        id = None
        if response.headers.get('content-type') is not None and \
                response.headers.get('content-type').startswith("application/json"):
            data = convert_object_to_snake_case(response.json())
        location = response.headers.get('location')
        if location is not None:
            id = location.split('/')[-1]
        return (data, response, id)

    def list_messages(self,
                      from_=None,
                      to=None,
                      from_date_time=None,
                      to_date_time=None,
                      direction=None,
                      state=None,
                      delivery_state=None,
                      sort_order=None,
                      size=None,
                      **kwargs):
        """
        Get a list of user's messages

        :param str ``from_``: The phone number to filter the messages that came from
        :param str to: The phone number to filter the messages that was sent to
        :param str from_date_time: The starting date time to filter the messages
            (must be in yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
        :param str to_date_time: The ending date time to filter the messages (must be in
            yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
        :param str direction: Filter by direction of message, in - a message that came from the telephone
            network to one of your numbers (an "inbound" message) or out - a message
            that was sent from one of your numbers to the telephone network (an "outbound"
            message)
        :param str state: The message state to filter. Values are 'received', 'queued', 'sending',
            'sent', 'error'
        :param str delivery_state: The message delivery state to filter. Values are 'waiting', 'delivered',
            'not-delivered'
        :param str sort_order: How to sort the messages. Values are 'asc' or 'desc'
        :param str size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of messages

        Example: Search for all messages and are in error::

            message_list = api.list_messages()

            for message in message_list:
                if message['state'] == 'error':
                    print(message['id'])
            ## m-it6ewpyiyadfe
            ## m-pjnqofcjyadfe
            ## m-t2gspvs6iadfe
            ## m-shuh6d6pyadfe
        """

        kwargs['from'] = from_
        kwargs['to'] = to
        kwargs['fromDateTime'] = from_date_time
        kwargs['toDateTime'] = to_date_time
        kwargs['direction'] = direction
        kwargs['state'] = state
        kwargs['deliveryState'] = delivery_state
        kwargs['sortOrder'] = sort_order
        kwargs['size'] = size

        path = '/users/%s/messages' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def send_message(self, from_, to,
                     text=None,
                     media=None,
                     receipt_requested=None,
                     callback_url=None,
                     callback_http_method=None,
                     callback_timeout=None,
                     fallback_url=None,
                     tag=None,
                     **kwargs):
        """
        Send a message (SMS or MMS)

        :param str ``from_``: One of your telephone numbers the message should come from
        :param str to: The phone number the message should be sent to
        :param str text: The contents of the text message
        :param list media: For MMS messages, a media url to the location of the media or
            list of medias to be sent send with the message.
        :param str receipt_requested: Requested receipt option for outbound messages: 'none', 'all', 'error'
        :param str callback_url: The server URL where the events related to the outgoing message will be sent to
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.
            Values are get or post Default is post
        :param str callback_timeout: Determine how long should the platform wait for
            callbackUrl's response before timing out (milliseconds).
        :param str fallback_url: The server URL used to send the message events if the request to callbackUrl fails.
        :param str tag: Any string, it will be included in the callback events of the message.
        :rtype: str
        :returns: id of created message

        Example: Send Text Message::

            id = api.send_message(
                from_ = '+1234567980',
                to = '+1234567981',
                text = 'SMS message'
                )

        Example: Send Picture Message::

            id = api.send_message(
                from_ = '+1234567980',
                to = '+1234567981',
                media = ['http://host/path/to/file']
                )
        """
        kwargs['from'] = from_
        kwargs['to'] = to
        kwargs['text'] = text
        kwargs['media'] = media
        kwargs['receiptRequested'] = receipt_requested
        kwargs['callbackUrl'] = callback_url
        kwargs['callbackHttpMethod'] = callback_http_method
        kwargs['callbackTimeout'] = callback_timeout
        kwargs['fallbackUrl'] = fallback_url
        kwargs['tag'] = tag

        return self._make_request('post', '/users/%s/messages' % self.user_id, json=kwargs)[2]

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

        Example: Bulk Send Picture or Text messages (or both)::

            results = api.send_messages([
                {'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'},
                {'from': '+1234567980', 'to': '+1234567982', 'text': 'SMS message2'}
            ])

        """
        results = self._make_request(
            'post', '/users/%s/messages' % self.user_id, json=messages_data)[0]
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

        Example: Fetch information about single message::

            my_message = api.get_message('m-abc123')
            print(my_message)

            ## {
            ##     'callback_url'             :'https://yoursite.com/message',
            ##     'direction'               :'in',
            ##     'from'                    :'+19193047864',
            ##     'id'                      :'m-messageId',
            ##     'media'                   :[],
            ##     'message_id'               :'m-messageId',
            ##     'skip_mms_carrier_validation':True,
            ##     'state'                   :'received',
            ##     'text'                    :'Hey there',
            ##     'time'                    :'2017-02-01T21:10:32Z',
            ##     'to'                      :'+19191234567'
            ## }
        """
        return self._make_request('get', '/users/%s/messages/%s' % (self.user_id, id))[0]
