import unittest
import six

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

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
        client = Client('userId', 'apiToken', 'apiSecret', api_endpoint = 'url', api_version = 'v2')
        self.assertEqual('userId', client.user_id)
        self.assertTupleEqual(('apiToken', 'apiSecret'), client.auth)
        self.assertEqual('url', client.api_endpoint)
        self.assertEqual('v2', client.api_version)

    @unittest.expectedFailure
    def test_init_with_missing_auth_data(self):
        """
        Client() should raise error on missing auth data
        """
        Client('userId')

