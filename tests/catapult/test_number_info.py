import unittest
import six
import requests
import helpers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class NumberInfoTests(unittest.TestCase):
    def test_get_number_info(self):
        """
        get_number_info() should return recordings
        """
        estimated_json="""
        {
        "created": "2013-09-23T16:31:15Z",
        "name": "Name",
        "number": "{number}",
        "updated": "2013-09-23T16:42:18Z"
        }
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.get_number_info('1234567890')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/phoneNumbers/numberInfo/1234567890', auth=helpers.AUTH)
            self.assertEqual('Name', data['name'])
