import json
import logging
import requests
from .errors import AppPlatformError


logger = logging.getLogger(__package__)

ENDPOINT = 'https://api.catapult.inetwork.com'


class RESTClientObject(object):
    """
    Parameters
        default_timeout
            timeout for http request and connection
        headers
            headers for outgoing requests
        log_hook
            optional callback for received request.Response
        log
            optional client logger
    """

    default_timeout = 60
    headers = {'content-type': 'application/json'}

    def __init__(self, user_id, auth, endpoint=ENDPOINT,
                 log=None, log_hook=None):
        self.endpoint = endpoint
        self.log_hook = log_hook
        self.uid = user_id
        self.auth = auth
        self.log = log or logger

    def _log_response(self, response):
        """
        Perform logging actions with the response object returned
        by Client using self.log_hook.
        """
        if callable(self.log_hook):
            self.log_hook(response)  # pragma: no cover

    def _join_endpoint(self, url):
        return '{}/v1/users/{}/{}'.format(self.endpoint, self.uid, url)

    def request(self, method, *args, **kwargs):
        assert method in ('get', 'post', 'delete', 'patch', 'put')
        try:
            response = requests.request(method, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError:
            self.log.exception('Error from bandwidth api.')
            template = '{} client error: {}' if response.status_code < 500 else '{} server error: {}'
            if response.headers.get('content-type') == 'application/json':
                message = template.format(response.status_code, response.json()['message'])
            else:
                message = template.format(response.status_code, response.content.decode('ascii')[:79])
            raise AppPlatformError(message)
        except Exception as e:
            raise AppPlatformError(e)

    def delete(self, url, timeout=None, **kwargs):
        url = self._join_endpoint(url)

        if timeout is not None:
            kwargs['timeout'] = timeout  # pragma: no cover

        response = self.request('delete', url, auth=self.auth, headers=self.headers, **kwargs)

        self._log_response(response)

        return response

    def get(self, url, params=None, timeout=None, join_endpoint=True, **kwargs):
        if join_endpoint:
            url = self._join_endpoint(url)
        kwargs['timeout'] = timeout or self.default_timeout
        response = self.request('get', url, auth=self.auth, headers=self.headers, params=params, **kwargs)

        self._log_response(response)

        return response

    def post(self, url, data=None, timeout=None, **kwargs):
        url = self._join_endpoint(url)
        kwargs['timeout'] = timeout or self.default_timeout
        if data:
            data = json.dumps(data)
        response = self.request('post', url, auth=self.auth, headers=self.headers, data=data, **kwargs)

        self._log_response(response)

        return response

    def build_request(self, method, url, headers={}, join_endpoint=True, **kwargs):
        if join_endpoint:
            url = self._join_endpoint(url)
        response = self.request(method, url, auth=self.auth, headers=headers, **kwargs)
        self._log_response(response)
        return response
