import unittest
import six
import requests
from tests.bandwidth.helpers import get_account_client as get_client
from tests.bandwidth.helpers import create_response, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.voice import Client


class DomainTests(unittest.TestCase):

    def test_list_domains(self):
        """
        list_domains() should return domains
        """
        estimated_json = """
        [{
            "id": "domainId",
            "name": "domainName"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_domains())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/domains',
                auth=AUTH,
                headers=headers,
                params={
                    'size': None})
            self.assertEqual('domainId', data[0]['id'])

    def test_create_domain(self):
        """
        create_domain() should create a domain and return id
        """
        estimated_request = {
            'name': 'myDomain',
            'description': None
        }
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/domainId'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            data = {'name': 'myDomain'}
            id = client.create_domain(**data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/domains',
                auth=AUTH,
                headers=headers,
                json=estimated_request)
            self.assertEqual('domainId', id)

    def test_get_domain(self):
        """
        get_domain('domain_id') should return a domain
        """
        estimated_json = """
            {   "description" : "Python Docs Example",
                "endpointsUrl": "https://api.catapult.inetwork.com/v1/users/u-abc123/domains/rd-domainId/endpoints",
                "id"          : "rd-domainId",
                "name"        : "qwerty"}
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_domain('rd-domainId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/rd-domainId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('rd-domainId', data['id'])

    def test_delete_domain(self):
        """
        delete_domain() should remove an domain
        """
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.delete_domain('domainId')
            p.assert_called_with(
                'delete',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId',
                headers=headers,
                auth=AUTH)
