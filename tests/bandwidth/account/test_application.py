import unittest
import six
import requests
import json
from tests.bandwidth.helpers import get_account_client as get_client
from tests.bandwidth.helpers import create_response, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.voice import Client


class ApplicationTests(unittest.TestCase):

    def test_list_applications(self):
        """
        get_applications() should return applications
        """
        estimated_json = """
        [{
            "id": "a-111",
            "name": "MyFirstApp",
            "incomingCallUrl": "http://example.com/calls.php",
            "incomingMessageUrl": "http://example.com/messages.php",
            "incomingMessageUrlCallbackTimeout": 1000,
            "incomingCallUrlCallbackTimeout": 1000,
            "incomingCallFallbackUrl" : "http://fallback.com/",
            "incomingMessageFallbackUrl": "http://fallback.com/",
            "callbackHttpMethod": "GET",
            "autoAnswer": true
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_applications())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/applications',
                auth=AUTH,
                headers=headers,
                params={
                    "size": None})
            self.assertEqual(json.loads(estimated_json)[0]['id'], data[0]['id'])

    def test_create_application(self):
        """
        create_application() should create an application and return id
        """
        estimated_json_request = {
            'name': 'MyFirstApp',
            'incomingCallUrl': None,
            'incomingCallUrlCallbackTimeout': None,
            'incomingCallFallbackUrl': None,
            'incomingMessageUrl': None,
            'incomingMessageUrlCallbackTimeout': None,
            'incomingMessageFallbackUrl': None,
            'callbackHttpMethod': None,
            'autoAnswer': None
        }
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/applicationId'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            id = client.create_application(name='MyFirstApp')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/applications',
                auth=AUTH,
                headers=headers,
                json=estimated_json_request)
            self.assertEqual('applicationId', id)

    def test_get_application(self):
        """
        get_application() should return an application
        """
        estimated_json = """
        {
            "id": "applicationId",
            "name": "MyFirstApp",
            "incomingCallUrl": "http://example.com/calls.php",
            "incomingMessageUrl": "http://example.com/messages.php",
            "autoAnswer": true
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_application('applicationId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/applications/applicationId',
                auth=AUTH,
                headers=headers)
            self.assertEqual('applicationId', data['id'])

    def test_update_application(self):
        """
        update_application() should update an application
        """
        estimated_json_request = {
            'name': 'MyUpdatedApplication',
            'incomingCallUrl': None,
            'incomingCallUrlCallbackTimeout': None,
            'incomingCallFallbackUrl': None,
            'incomingMessageUrl': None,
            'incomingMessageUrlCallbackTimeout': None,
            'incomingMessageFallbackUrl': None,
            'callbackHttpMethod': None,
            'autoAnswer': None
        }
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/applicationId'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            id = client.update_application(app_id='a-123', name='MyUpdatedApplication')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/applications/a-123',
                auth=AUTH,
                headers=headers,
                json=estimated_json_request)

    def test_delete_application(self):
        """
        delete_application() should remove an application
        """
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.delete_application('applicationId')
            p.assert_called_with(
                'delete',
                'https://api.catapult.inetwork.com/v1/users/userId/applications/applicationId',
                headers=headers,
                auth=AUTH)
