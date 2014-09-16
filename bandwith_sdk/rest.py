import json
import requests
from .errors import BandwithError


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
    log_hook = None
    log = None

    def _log_response(self, response):
        '''
        Perform logging actions with the response object returned
        by Client using self.log_hook.
        '''
        if callable(self.log_hook):
            self.log_hook(response)

    def _join_endpoint(self, url):
        return '{}{}'.format(self.endpoint, url)

    def request(self, method, *args, **kwargs):
        assert method in ('get', 'post', 'delete', 'patch')
        try:
            response = requests.request(method, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            self.log.exception('Error from bandwith api.')
            if 400 <= response.status_code <= 500:
                if response.headers['content-type'] == 'json':
                    message = response.json()['message']
                else:
                    message = response.content.decode('ascii')[:79]
                raise BandwithError(message)
            else:
                raise BandwithError(e)
        except Exception as e:
            raise BandwithError(e)

    def delete(self, url, timeout=None, **kwargs):
        url = self._join_endpoint(url)

        if timeout is not None:
            kwargs['timeout'] = timeout

        response = self.request('delete', url, auth=self.auth, headers=self.headers, **kwargs)

        self._log_response(response)

        return response

    def get(self, url, params=None, timeout=None, **kwargs):
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
