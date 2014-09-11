import unittest

from bandwith_sdk import Client


class ClientTest(unittest.TestCase):

    def test_instantiation(self):
        """
        Basic client installation.
        """
        client = Client('u-**********', 't-******', 's-********')
        restored_client = Client()
        self.assertIs(client, restored_client)

    @unittest.expectedFailure
    def test_instantiation_bad_args(self):
        """
        Not enough args in client constructor.
        """
        Client('u-**********', 't-******')

    @unittest.expectedFailure
    def test_instantiation_again(self):
        """
        Client should be instantiated only once.
        """
        Client('u-**********', 't-******', 's-********')
        Client('u-**********', 't-******', 's-********')
