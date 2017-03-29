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


class EndpointTests(unittest.TestCase):

    def test_list_domain_endpoints(self):
        """
        list_domain_endpoints() should return endpoints
        """
        estimated_json = """
        [{
            "id": "endpointId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_domain_endpoints('domainId'))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId/endpoints',
                auth=AUTH,
                headers=headers,
                params={'size': None})
            self.assertEqual('endpointId', data[0]['id'])

    def test_create_domain_endpoint(self):
        """
        create_domain_endpoint() should create an endpoint and return id
        """
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/endpointId'
        estimated_request = {
            'name': 'mysip',
            'description': None,
            'applicationId': None,
            'enabled': True,
            'credentials': {
                'password': 'abc123'
            }
        }
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            data = {'name': 'mysip', 'password': 'abc123'}
            id = client.create_domain_endpoint('domainId', **data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId/endpoints',
                auth=AUTH,
                headers=headers,
                json=estimated_request)
            self.assertEqual('endpointId', id)

    def test_get_domain_endpoint(self):
        """
        get_domain_endpoint() should return an endpoint
        """
        estimated_json = """
        {
            "id": "endpointId",
            "name": "mysip"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_domain_endpoint('domainId', 'endpointId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId/endpoints/endpointId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('endpointId', data['id'])

    def test_update_domain_endpoint(self):
        """update
        delete_domain_endpoint() should update an endpoint
        """
        estimated_request = {
            'description': 'My SIP',
            'applicationId': None,
            'enabled': None,
            'credentials': {
                'password': None
            }
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            data = {'description': 'My SIP'}
            client.update_domain_endpoint('domainId', 'endpointId', **data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId/endpoints/endpointId',
                auth=AUTH,
                headers=headers,
                json=estimated_request)

    def test_delete_domain_endpoint(self):
        """
        delete_domain_endpoint() should remove an endpoint
        """
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.delete_domain_endpoint('domainId', 'endpointId')
            p.assert_called_with(
                'delete',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId/endpoints/endpointId',
                headers=headers,
                auth=AUTH)

    def test_create_domain_endpoint_auth_token(self):
        """
        create_domain_endpoint_auth_token() should create auth token
        """
        estimated_json = """
        {
            "token": "tokenValue",
            "expires": 3600
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            t = client.create_domain_endpoint_auth_token('domainId', 'endpointId')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/domains/domainId/endpoints/endpointId/tokens',
                auth=AUTH,
                headers=headers,
                json={
                    'expires': 3600})
            self.assertEqual('tokenValue', t['token'])
