import unittest
import six
import requests
import helpers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

class ErrorTests(unittest.TestCase):
    def test_get_errors(self):
        """
        get_errors() should return errors
        """
        estimated_json="""
        [{
            "time" : "2012-11-15T01:29:24.512Z",
            "category" : "unavailable",
            "id" : "{userErrorId}",
            "message" : "No application is configured for number +19195556666",
            "code" : "no-application-for-number"
        }]
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = list(client.get_errors())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/errors', auth=helpers.AUTH, params=None)
            self.assertEqual('{userErrorId}', data[0]['id'])

    def test_get_error(self):
        """
        get_errors() should return an error
        """
        estimated_json="""
        {
            "time" : "2012-11-15T01:29:24.512Z",
            "category" : "unavailable",
            "id" : "{userErrorId}",
            "message" : "No application is configured for number +19195556666",
            "code" : "no-application-for-number"
        }
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.get_error('errorId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/errors/errorId', auth=helpers.AUTH)
            self.assertEqual('{userErrorId}', data['id'])
