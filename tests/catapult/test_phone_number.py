import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class PhoneNumberTests(unittest.TestCase):

    def test_list_phone_numbers(self):
        """
        list_phone_numbers() should return numbers
        """
        estimated_request = {
            'applicationId': None,
            'state': None,
            'name': None,
            'city': None,
            'numberState': None,
            'size': None
        }
        estimated_json = """
        [{
        "id": "{numberId1}",
        "application": "https://catapult.inetwork.com/v1/users/users/u-ly123/applications/a-j321",
        "number":"{number1}",
        "nationalNumber":"{national_number1}",
        "name": "home phone",
        "createdTime": "2013-02-13T17:46:08.374Z",
        "state": "NC",
        "price": "0.60",
        "numberState": "enabled"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_phone_numbers())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers',
                auth=AUTH,
                headers=headers,
                params=estimated_request)
            self.assertEqual('{numberId1}', data[0]['id'])

    def test_order_phone_number(self):
        """
        order_phone_number() should create an number and return id
        """
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/numberId'
        estimated_request = {
            'number': '+1234567890',
            'name': 'MyFirstNumber',
            'applicationId': None,
            'fallbackNumber': None
        }
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            data = {'name': 'MyFirstNumber', 'number': '+1234567890'}
            id = client.order_phone_number(**data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers',
                auth=AUTH,
                headers=headers,
                json=estimated_request)
            self.assertEqual('numberId', id)

    def test_get_phone_number(self):
        """
        get_phone_number() should return a phone number
        """
        estimated_json = """
        {
        "id": "{numberId1}",
        "application": "https://catapult.inetwork.com/v1/users/users/u-ly123/applications/a-j321",
        "number":"{number1}",
        "nationalNumber":"{national_number1}",
        "name": "home phone",
        "createdTime": "2013-02-13T17:46:08.374Z",
        "state": "NC",
        "price": "0.60",
        "numberState": "enabled"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_phone_number('numberId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers/numberId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('{numberId1}', data['id'])

    def test_delete_phone_number(self):
        """
        delete_phone_number() should remove a number
        """
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.delete_phone_number('numberId')
            p.assert_called_with(
                'delete',
                'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers/numberId',
                headers=headers,
                auth=AUTH)

    def test_update_phone_number(self):
        """
        update_phone_number() should update a phone number
        """
        estimated_request = {
            'name': None,
            'applicationId': 'appId',
            'fallbackNumber': None
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            data = {'application_id': 'appId'}
            client.update_phone_number('numberId', **data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers/numberId',
                auth=AUTH,
                headers=headers,
                json=estimated_request)
