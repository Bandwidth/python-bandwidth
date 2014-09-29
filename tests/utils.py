import unittest
from bandwidth_sdk import Client, set_client


class SdkTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_client(Client('u-user', 't-token', 's-secret'))

    @classmethod
    def tearDownClass(cls):
        set_client(None)
