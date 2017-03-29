import unittest
import six
import requests
from tests.bandwidth.helpers import get_voice_client as get_client
from tests.bandwidth.helpers import create_response, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.voice.lazy_enumerable import get_lazy_enumerator


class LazyEnumerableTests(unittest.TestCase):

    def test_get_lazy_enumerator(self):
        """
        get_lazy_enumerator() should return data on demand
        """
        with patch('requests.request', return_value=create_response(200, '[1, 2, 3]')) as p:
            client = get_client()
            results = get_lazy_enumerator(client, lambda: client._make_request(
                'get', 'https://api.catapult.inetwork.com/v1/users/userId/account/transactions?page=0&size=25'))
            p.assert_not_called()
            self.assertEqual([1, 2, 3], list(results))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/account/transactions?page=0&size=25',
                headers=headers,
                auth=AUTH)

    def test_get_lazy_enumerator_with_several_requests(self):
        """
        get_lazy_enumerator() should request new portion of data on demand
        """
        estimated_json1 = '[1, 2, 3]'
        estimated_json2 = '[4, 5, 6, 7]'
        response1 = create_response(200, estimated_json1)
        response1.headers['link'] = '<transactions?page=0&size=25>; rel="first", ' \
                                    '<transactions?page=1&size=25>; rel="next"'
        response2 = create_response(200, estimated_json2)
        client = get_client()
        with patch('requests.request', return_value=response2) as p:
            results = get_lazy_enumerator(client, lambda: ([1, 2, 3], response1, None))
            self.assertEqual([1, 2, 3, 4, 5, 6, 7], list(results))
            p.assert_called_with(
                'get',
                'transactions?page=1&size=25',
                headers=headers,
                auth=AUTH)
