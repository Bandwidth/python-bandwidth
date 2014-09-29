import unittest
import responses

from bandwidth_sdk import Client, get_client, set_client, _Client, AppPlatformError
from .utils import SdkTestCase


class ClientTest(SdkTestCase):

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
    def test_instantiation_without_env(self):
        """
        Basic client installation by get_client without configuration.
        """
        get_client()

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


class RestErrors(SdkTestCase):

    @responses.activate
    def test_404_plain_text(self):
        """
        Bad request in plain text
        """
        raw = "Not Found"

        responses.add(responses.GET, 'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw, status=404, content_type='text/plain')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'calls/c-call-id')

        self.assertEqual(str(app_error.exception), '404 client error: Not Found')

    @responses.activate
    def test_404_json(self):
        """
        Bad request with catapult reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(responses.GET, 'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw, status=404, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'calls/c-call-id')

        self.assertEqual(str(app_error.exception), '404 client error: Not Found')

    @responses.activate
    def test_other_errors(self):
        """
        Other errors
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(responses.GET, 'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw, status=404, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.build_request('get', 'calls/c')

        self.assertEqual(str(app_error.exception), 'Connection refused: '
                                                   'https://api.catapult.inetwork.com/v1/users/u-user/calls/c')
