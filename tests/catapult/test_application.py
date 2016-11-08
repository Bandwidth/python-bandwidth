import unittest
import six
import requests
import helpers
if six.PY3:
    import .helpers
    from unittest.mock import patch
else:
    import helpers
    from mock import patch

from bandwidth.catapult import Client

class ApplicationTests(unittest.TestCase):
    def test_get_applications(self):
        """
        get_applications() should return applications
        """
        estimated_json="""
        [{
            "id": "applicationId",
            "name": "MyFirstApp",
            "incomingCallUrl": "http://example.com/calls.php",
            "incomingMessageUrl": "http://example.com/messages.php",
            "autoAnswer": true
        }]
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = list(client.get_applications())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/applications', auth=helpers.AUTH, params=None)
            self.assertEqual('applicationId', data[0]['id'])

    def test_create_application(self):
        """
        create_application() should create an application and return id
        """
        estimated_response = helpers.create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/applicationId'
        with patch('requests.request', return_value = estimated_response) as p:
            client = helpers.get_client()
            data = {'name': 'MyFirstApp'}
            id = client.create_application(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/applications', auth=helpers.AUTH, json=data)
            self.assertEqual('applicationId', id)


    def test_get_application(self):
        """
        get_application() should return an application
        """
        estimated_json="""
        {
            "id": "applicationId",
            "name": "MyFirstApp",
            "incomingCallUrl": "http://example.com/calls.php",
            "incomingMessageUrl": "http://example.com/messages.php",
            "autoAnswer": true
        }
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.get_application('applicationId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/applications/applicationId', auth=helpers.AUTH)
            self.assertEqual('applicationId', data['id'])

    def test_delete_application(self):
        """
        delete_application() should remove an application
        """
        with patch('requests.request', return_value = helpers.create_response(200)) as p:
            client = helpers.get_client()
            client.delete_application('applicationId')
            p.assert_called_with('delete', 'https://api.catapult.inetwork.com/v1/users/userId/applications/applicationId', auth=helpers.AUTH)

