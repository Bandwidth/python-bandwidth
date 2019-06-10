import unittest
import six
import copy
import requests
from tests.bandwidth.helpers import get_account_client as get_client
from tests.bandwidth.helpers import create_response, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.account import Client, BandwidthAccountAPIException


class ClientTests(unittest.TestCase):

    def test_init_with_right_auth_data(self):
        """
        Client() should return client instance with right auth data
        """
        client = Client('userId', 'apiToken', 'apiSecret')
        self.assertEqual('userId', client.user_id)
        self.assertTupleEqual(('apiToken', 'apiSecret'), client.auth)
        self.assertEqual('https://api.catapult.inetwork.com', client.api_endpoint)
        self.assertEqual('v1', client.api_version)

    def test_init_with_right_auth_data_and_another_endpoint_and_version(self):
        """
        Client() should return client instance with right auth data (different endpoint and version)
        """
        client = Client('userId', 'apiToken', 'apiSecret', api_endpoint='url', api_version='v2')
        self.assertEqual('userId', client.user_id)
        self.assertTupleEqual(('apiToken', 'apiSecret'), client.auth)
        self.assertEqual('url', client.api_endpoint)
        self.assertEqual('v2', client.api_version)

    def test_init_with_missing_auth_data(self):
        """
        Client() should raise error on missing auth data
        """
        with self.assertRaises(ValueError):
            Client('userId')

    def test_request_with_absolute_url(self):
        """
        _request() should make authorized request to absolute url
        """
        with patch('requests.request', return_value=create_response()) as p:
            client = get_client()
            response = client._request('get', 'http://localhost')
            p.assert_called_with('get', 'http://localhost', headers=headers, auth=('apiToken', 'apiSecret'))

    def test_request_with_relative_url(self):
        """
        _request() should make authorized request to relative url
        """
        with patch('requests.request', return_value=create_response()) as p:
            client = get_client()
            response = client._request('get', '/path')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path',
                                 headers=headers, auth=('apiToken', 'apiSecret'))

    def test_make_request_with_headers(self):
        """
        _request() should add the user agent to header
        """
        with patch('requests.request', return_value=create_response()) as p:
            client = get_client()
            req_headers = {
                'hello': 'world'
            }
            res_headers = copy.deepcopy(headers)
            res_headers['hello'] = 'world'
            response = client._request('get', '/path', headers=req_headers)
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path',
                                 headers=res_headers, auth=('apiToken', 'apiSecret'))

    def test_check_response_with_json_error(self):
        """
        _check_response() should extract error data from json
        """
        response = create_response(400, '{"message": "This is error", "code": "invalid-request"}')
        client = get_client()
        with self.assertRaises(BandwidthAccountAPIException) as r:
            client._check_response(response)
        err = r.exception
        self.assertEqual('invalid-request', err.code)
        self.assertEqual('This is error', err.message)
        self.assertEqual(400, err.status_code)
        self.assertEqual('Error invalid-request: This is error', str(err))

    def test_check_response_with_json_error_without_code(self):
        """
        _check_response() should extract error data from json (without code)
        """
        response = create_response(400, '{"message": "This is error"}')
        client = get_client()
        with self.assertRaises(BandwidthAccountAPIException) as r:
            client._check_response(response)
        err = r.exception
        self.assertEqual('400', err.code)
        self.assertEqual('This is error', err.message)
        self.assertEqual(400, err.status_code)
        self.assertEqual('Error 400: This is error', str(err))

    def test_check_response_with_plain_text_error(self):
        """
        _check_response() should extract error data from plain text
        """
        response = create_response(400, 'This is error', 'text/html')
        client = get_client()
        with self.assertRaises(BandwidthAccountAPIException) as r:
            client._check_response(response)
        err = r.exception
        self.assertEqual('400', err.code)
        self.assertEqual('This is error', err.message)
        self.assertEqual(400, err.status_code)
        self.assertEqual('Error 400: This is error', str(err))

    def test_make_request_with_json(self):
        """
        _make_request() should make request, check response and extract json data
        """
        estimated_response = create_response(200, '{"data": "data"}')
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            data, response, _ = client._make_request('get', '/path')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path',
                                 headers=headers, auth=('apiToken', 'apiSecret'))
            self.assertIs(estimated_response, response)
            self.assertDictEqual({'data': 'data'}, data)

    def test_make_request_with_location_header(self):
        """
        _make_request() should make request, check response and extract id from location header
        """
        estimated_response = create_response(201, '', 'text/html')
        estimated_response.headers['location'] = 'http://localhost/path/id'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            _, response, id = client._make_request('get', '/path')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/path',
                                 headers=headers, auth=('apiToken', 'apiSecret'))
            self.assertIs(estimated_response, response)
            self.assertEqual('id', id)

    def test_encode_if_not_encoded_encoded_string(self):
        """
        encode_if_not_encoded() should return the same string if it is already encoded
        """
        client = Client('userId', 'apiToken', 'apiSecret')
        encoded_string = "Home%281%29-m-m4dh5ym.jpg"
        self.assertEqual(encoded_string, client._encode_if_not_encoded(encoded_string))

    def test_encoded_if_not_encoded_non_encoded_string(self):
        """
        encoded_if_not_encoded() should encode the string if not already encoded
        """
        client = Client('userId', 'apiToken', 'apiSecret')
        encoded_string = "Home%281%29-m-m4dh5ym.jpg"
        non_encoded_string = "Home(1)-m-m4dh5ym.jpg"
        self.assertEqual(encoded_string, client._encode_if_not_encoded(non_encoded_string))
