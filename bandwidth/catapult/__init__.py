import requests
from .account import AccountMixin
from .application import ApplicationMixin
from .available_number import AvailableNumberMixin


class Client(AccountMixin, ApplicationMixin, AvailableNumberMixin):
    def __init__(self, user_id=None, api_token=None, api_secret=None, **other_options):
        if not all((user_id, api_token, api_secret)):
            raise ValueError('Arguments user_id, api_token and api_secret are required. '
                             'Use bandwidth.client("catapult", "YOUR-USER-ID", "YOUR-API-TOKEN", "YOUR-API-SECRET")')
        self.user_id = user_id
        self.api_endpoint = other_options.get('api_endpoint', 'https://api.catapult.inetwork.com')
        self.api_version = other_options.get('api_version', 'v1')
        self.auth = (api_token, api_secret)

    def _request(self, method, url, *args, **kwargs):
        if url.startswith('/'):
            # relative url
            url = '%s/%s%s' % (self.api_endpoint, self.api_version, url)
        return requests.request(method, url, auth=self.auth, *args, **kwargs)

    def _check_response(self, response):
        if response.status_code >= 400:
            if response.headers.get('content-type') == 'application/json':
                data = response.json()
                raise CatapultException(response.status_code, data['message'], code=data.get('code'))
            else:
                raise CatapultException(response.status_code, response.content.decode('utf-8')[:79])

    def _make_request(self, method, url, *args, **kwargs):
        response = self._request(method, url, *args, **kwargs)
        self._check_response(response)
        data = None
        id = None
        if response.headers.get('content-type') == 'application/json':
            data = response.json()
        location = response.headers.get('location')
        if location is not None:
            id = location.split('/')[-1]
        return (data, response, id)


class CatapultException(Exception):
    def __init__(self, status_code, message, **kwargs):
        self.status_code = status_code
        self.message = message
        self.code = kwargs.get('code')
        if self.code is None:
            self.code = str(status_code)

    def __str__(self):
        return 'Error %s: %s' % (self.code, self.message)
