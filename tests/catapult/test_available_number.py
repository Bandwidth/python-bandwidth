import unittest
import six
import requests
import helpers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

class AvailableNumberTests(unittest.TestCase):
    def test_search_available_numbers(self):
        """
        search_available_numbers() should return available numbers
        """
        estimated_json="""
        [{
            "number": "{number1}",
            "nationalNumber": "{national_number1}",
            "patternMatch": "          2 9 ",
            "city": "CARY",
            "lata": "426",
            "rateCenter": "CARY",
            "state": "NC",
            "price": "0.60"
        }]
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.search_available_numbers('local', {'quantity': 1})
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/availableNumbers/local', auth=helpers.AUTH, params={'quantity': 1})
            self.assertEqual('CARY', data[0]['city'])

    def test_search_and_order_available_numbers(self):
        """
        search_and_order_available_numbers() should search, order and return available numbers
        """
        estimated_json="""
        [{
        "number": "{number1}",
        "nationalNumber": "{national_number1}",
        "price": "0.60",
        "location": "https://.../v1/users/.../phoneNumbers/{numberId1}"
        }]
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.search_and_order_available_numbers('local', {'quantity': 1})
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/availableNumbers/local', auth=helpers.AUTH, params={'quantity': 1})
            self.assertEqual('{national_number1}', data[0]['nationalNumber'])
            self.assertEqual('{numberId1}', data[0]['id'])
