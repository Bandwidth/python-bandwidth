import unittest
import six
import requests
import helpers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class PhoneNumberTests(unittest.TestCase):
    def test_get_phone_numbers(self):
        """
        get_phone_numbers() should return numbers
        """
        estimated_json="""
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
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = list(client.get_phone_numbers())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers', auth=helpers.AUTH, params=None)
            self.assertEqual('{numberId1}', data[0]['id'])

    def test_create_phone_number(self):
        """
        create_phone_number() should create an number and return id
        """
        estimated_response = helpers.create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/numberId'
        with patch('requests.request', return_value = estimated_response) as p:
            client = helpers.get_client()
            data = {'name': 'MyFirstNumber', 'number': '+1234567890'}
            id = client.create_phone_number(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers', auth=helpers.AUTH, json=data)
            self.assertEqual('numberId', id)


    def test_get_phone_number(self):
        """
        get_phone_number() should return a phone number
        """
        estimated_json="""
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
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.get_phone_number('numberId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers/numberId', auth=helpers.AUTH)
            self.assertEqual('{numberId1}', data['id'])

    def test_delete_phone_number(self):
        """
        delete_phone_number() should remove a number
        """
        with patch('requests.request', return_value = helpers.create_response(200)) as p:
            client = helpers.get_client()
            client.delete_phone_number('numberId')
            p.assert_called_with('delete', 'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers/numberId', auth=helpers.AUTH)


    def test_update_phone_number(self):
        """
        update_phone_number() should update a phone number
        """
        with patch('requests.request', return_value = helpers.create_response(200)) as p:
            client = helpers.get_client()
            data = {'applicationId': 'appId'}
            client.update_phone_number('numberId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/phoneNumbers/numberId', auth=helpers.AUTH, json=data)
