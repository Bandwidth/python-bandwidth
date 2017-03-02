import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class ErrorTests(unittest.TestCase):

    def test_list_errors(self):
        """
        list_errors() should return errors
        """
        estimated_json = """
        [{
            "time" : "2012-11-15T01:29:24.512Z",
            "category" : "unavailable",
            "id" : "{userErrorId}",
            "message" : "No application is configured for number +19195556666",
            "code" : "no-application-for-number"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_errors())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/errors',
                auth=AUTH,
                headers=headers,
                params={'size': None})
            self.assertEqual('{userErrorId}', data[0]['id'])

    def test_get_error(self):
        """
        get_errors() should return an error
        """
        estimated_json = """
        {
            "time" : "2012-11-15T01:29:24.512Z",
            "category" : "unavailable",
            "id" : "{userErrorId}",
            "message" : "No application is configured for number +19195556666",
            "code" : "no-application-for-number"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_error('errorId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/errors/errorId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('{userErrorId}', data['id'])
