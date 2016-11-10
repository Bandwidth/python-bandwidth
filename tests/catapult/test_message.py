import unittest
import six
import requests
from  tests.catapult.helpers import create_response, get_client, AUTH
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

class MessageTests(unittest.TestCase):
    def test_get_messages(self):
        """
        get_messages() should return messages
        """
        estimated_json="""
        [{
            "id": "messageId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.get_messages())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/messages', auth=AUTH, params=None)
            self.assertEqual('messageId', data[0]['id'])

    def test_send_message(self):
        """
        send_message() should create an message and return id
        """
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/messageId'
        with patch('requests.request', return_value = estimated_response) as p:
            client = get_client()
            data = {'from': 'num1', 'to': 'num2', 'text': 'text'}
            id = client.send_message(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/messages', auth=AUTH, json=data)
            self.assertEqual('messageId', id)

    def test_send_messages(self):
        """
        send_messages() should send some messages
        """
        estimated_json = """
        [
            {"result": "accepted", "location": "http://localhost/messageId"}
        ]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = [{'from': 'num1', 'to': 'num2', 'text': 'text'}]
            results = client.send_messages(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/messages', auth=AUTH, json=data)
            self.assertEqual('messageId', results[0]['id'])


    def test_get_message(self):
        """
        get_message() should return a message
        """
        estimated_json="""
        {
            "id": "messageId"
        }
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_message('messageId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/messages/messageId', auth=AUTH)
            self.assertEqual('messageId', data['id'])

