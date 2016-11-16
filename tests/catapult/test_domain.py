import unittest
import six
import requests
from  tests.catapult.helpers import create_response, get_client, AUTH
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

class DomainTests(unittest.TestCase):
    def test_get_domains(self):
        """
        get_domains() should return domains
        """
        estimated_json="""
        [{
            "id": "domainId",
            "name": "domainName"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.get_domains())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/domains', auth=AUTH, params=None)
            self.assertEqual('domainId', data[0]['id'])

    def test_create_domain(self):
        """
        create_domain() should create a domain and return id
        """
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/domainId'
        with patch('requests.request', return_value = estimated_response) as p:
            client = get_client()
            data = {'name': 'myDomain'}
            id = client.create_domain(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/domains', auth=AUTH, json=data)
            self.assertEqual('domainId', id)


    def test_delete_domain(self):
        """
        delete_domain() should remove an domain
        """
        with patch('requests.request', return_value = create_response(200)) as p:
            client = get_client()
            client.delete_domain('domainId')
            p.assert_called_with('delete', 'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId', auth=AUTH)

