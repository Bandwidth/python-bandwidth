import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class AvailableNumberTests(unittest.TestCase):

    def test_search_available_local_numbers(self):
        """
        search_available_numbers() should return available numbers
        """
        estimated_json_request = {
            'city': None,
            'state': None,
            'zip': None,
            'areaCode': None,
            'localNumber': None,
            'inLocalCallingArea': None,
            'quantity': 1,
            'pattern': None
        }
        estimated_json = """
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
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.search_available_local_numbers(quantity=1)
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/availableNumbers/local',
                auth=AUTH,
                headers=headers,
                params=estimated_json_request)
            self.assertEqual('CARY', data[0]['city'])

    def test_search_available_toll_free_numbers(self):
        """
        search_available_numbers() should return available numbers
        """
        estimated_json_request = {
            'quantity': 1,
            'pattern': '*456'
        }
        estimated_json = """
        [{
        "nationalNumber": "(844) 489-0456",
        "number": "+18444890456",
        "patternMatch": "           456",
        "price": "0.75"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.search_available_toll_free_numbers(quantity=1, pattern='*456')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/availableNumbers/tollFree',
                auth=AUTH,
                headers=headers,
                params=estimated_json_request)
            self.assertEqual('+18444890456', data[0]['number'])

    def test_search_and_order_local_numbers(self):
        """
        search_and_order_available_numbers() should search, order and return available numbers
        """
        estimated_json_request = {
            'city': None,
            'state': None,
            'zip': '27606',
            'areaCode': None,
            'localNumber': None,
            'inLocalCallingArea': None,
            'quantity': 1
        }
        estimated_json = """
        [{
        "number": "{number1}",
        "nationalNumber": "{national_number1}",
        "price": "0.60",
        "location": "https://.../v1/users/.../phoneNumbers/{numberId1}"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.search_and_order_local_numbers(zip_code='27606', quantity=1)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/availableNumbers/local',
                auth=AUTH,
                headers=headers,
                params=estimated_json_request)
            self.assertEqual('{national_number1}', data[0]['nationalNumber'])
            self.assertEqual('{numberId1}', data[0]['id'])

    def test_search_and_order_toll_free_numbers(self):
        """
        search_and_order_available_numbers() should search, order and return available numbers
        """
        estimated_json_request = {'quantity': 1}
        estimated_json = """
        [{
        "number": "{number1}",
        "nationalNumber": "{national_number1}",
        "price": "0.60",
        "location": "https://.../v1/users/.../phoneNumbers/{numberId1}"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.search_and_order_toll_free_numbers(quantity=1)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/availableNumbers/tollFree',
                auth=AUTH,
                headers=headers,
                params=estimated_json_request)
            self.assertEqual('{national_number1}', data[0]['nationalNumber'])
            self.assertEqual('{numberId1}', data[0]['id'])
