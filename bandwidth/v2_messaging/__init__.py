import requests
import six
import urllib
import json
import itertools
from bandwidth.voice.lazy_enumerable import get_lazy_enumerator
from bandwidth.convert_camel import convert_object_to_snake_case
from bandwidth.version import __version__ as version

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
        self.api_version = other_options.get('api_version', 'v2')
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
            if response.headers.get('content-type') == 'application/json':
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
        if response.headers.get('content-type') == 'application/json':
            data = convert_object_to_snake_case(response.json())
        location = response.headers.get('location')
        if location is not None:
            id = location.split('/')[-1]
        return (data, response, id)

    def send_message(from_, to,
                     application_id,
                     text=None,
                     media=None,
                     tag=None,
                     **kwargs):
        """
        Send a message (SMS or MMS)
        :param str ``from_``: One of your telephone numbers the message should come from
        :param list to: The phone numbers the message should be sent to.
        :param str application_id: The ID of the Application your
            from number is associated with in the Bandwidth Phone Number Dashboard.
        :param str text: The contents of the text message
        :param list media: For MMS messages, a media url to the location of the media or
            list of medias to be sent send with the message.
        :param str tag: Any string, it will be included in the callback events of the message.
        :rtype: Dict
        :returns: object of created message
        Example: Send Text Message::
            id = api.send_message(
                from_ = '+1234567980',
                to = ['+1234567981'],
                text = 'SMS message',
                application_id = '93de2206-9669-4e07-948d-329f4b722ee2'
                )
        Example: Send Group Multi-Media Message::
            id = api.send_message(
                from_ = '+1234567980',
                to = ['+1234567981','+1234567999'],
                media = ['http://host/path/to/file'],
                text = 'Group MMS message',
                application_id = '93de2206-9669-4e07-948d-329f4b722ee2'
                )
        Example: Send Toll-free Message::
            id = api.send_message(
                from_ = '+18331231234',
                to = ['+1234567999'],
                text = 'Toll-free SMS',
                application_id = '93de2206-9669-4e07-948d-329f4b722ee2'
                )
        """
        kwargs['from'] = from_
        kwargs['to'] = to
        kwargs['text'] = text
        kwargs['media'] = media
        kwargs['applicationId'] = application_id
        kwargs['tag'] = tag

        return self._make_request('post', '/users/%s/messages' % self.user_id, json=kwargs)


class BandwidthMessageAPIException(Exception):

    """
    Catapult API request exception
    """

    def __init__(self, status_code, message, **kwargs):
        """
        Initialize the catapult exception.
        :type status_code: str
        :param status_code: http status code
        :type message: str
        :param message: error message
        :type code: str
        :param code: optional error code

        :rtype: bandwidth.catapult.CatapultException
        :returns: instance of exception
        """
        self.status_code = status_code
        self.message = message
        self.code = kwargs.get('code')
        if self.code is None:
            self.code = str(status_code)

    def __str__(self):
        return 'Error %s: %s' % (self.code, self.message)
