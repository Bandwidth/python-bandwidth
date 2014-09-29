import unittest

from bandwidth_sdk import Client, get_client, set_client, _Client


class ClientTest(unittest.TestCase):

    def setUp(self):
        set_client(None)

    def tearDown(self):
        set_client(None)

    def test_instantiation(self):
        """
        Basic client installation.
        """
        client = Client('u-user', 't-token', 's-secret')
        restored_client = get_client()
        self.assertIs(client, restored_client)

    @unittest.expectedFailure
    def test_instantiation_bad_args(self):
        """
        Not enough args in client constructor.
        """
        Client('u-**********', 't-******')

    def test_re_instantiation(self):
        """
        Client re installation.
        """
        previous = Client('u-**********', 't-******', 's-********')
        old_client = set_client(_Client('u-**********', 't-******', 's-********'))
        self.assertIs(previous, old_client)
