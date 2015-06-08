import unittest
import six
import os

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

import responses

from bandwidth_sdk import Client, get_client, set_client, RESTClientObject, AppPlatformError
from .utils import SdkTestCase

import sys
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stderr)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

class ClientTest(SdkTestCase):

    def setUp(self):
        """
        These tests check client creation with different ways of passing in credentials.
        If you have the Catapult credentials set in env vars in the shell you're running make from,
        some of these test will fail.
        Before running make, run:
            $ unset BANDWIDTH_API_SECRET BANDWIDTH_API_TOKEN BANDWIDTH_USER_ID
        """
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

    def test_instantiation_without_env(self):
        """
        Basic client installation by get_client without configuration.
        """
        with self.assertRaises(ValueError):
            get_client()

    def test_instantiation_from_env(self):
        with patch.dict('os.environ', {'BANDWIDTH_USER_ID': 'venv_uid',
                                       'BANDWIDTH_API_TOKEN': 'venv_token',
                                       'BANDWIDTH_API_SECRET': 'venv_secret'}):
            rest_client = get_client()
            self.assertEqual(rest_client.uid, 'venv_uid')
            self.assertEqual(rest_client.auth, ('venv_token', 'venv_secret'))

    def test_instantiation_from_file_with_env_path(self):
        raw_data = """[catapult]
user_id=file_uid
token=file_token
secret=file_secret"""
        with open('./tests/fixtures/.bndsdkrc', 'w+') as test_file:
            test_file.write(raw_data)
        self.assertTrue(test_file.closed)
        with patch.dict('os.environ', {'BANDWIDTH_CONFIG_FILE': './tests/fixtures/.bndsdkrc'}):
            rest_client = get_client()
            self.assertEqual(rest_client.uid, 'file_uid')
            self.assertEqual(rest_client.auth, ('file_token', 'file_secret'))

        os.remove('./tests/fixtures/.bndsdkrc')

    def test_instantiation_from_file_with_wrong_path(self):
        with patch.dict('os.environ', {'BANDWIDTH_CONFIG_FILE': './tests/fixtures/.bndsdkrc'}):
            with self.assertRaises(ValueError):
                get_client()

    def test_instantiation_from_file_default_path(self):
        raw_data = """[catapult]
user_id=file_uid
token=file_token
secret=file_secret"""
        with open('.bndsdkrc', 'w+') as test_file:
            test_file.write(raw_data)
        self.assertTrue(test_file.closed)
        rest_client = get_client()
        self.assertEqual(rest_client.uid, 'file_uid')
        self.assertEqual(rest_client.auth, ('file_token', 'file_secret'))
        os.remove('.bndsdkrc')

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
        old_client = set_client(RESTClientObject('u-**********', 't-******', 's-********'))
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
                                                   'GET https://api.catapult.inetwork.com/v1/users/u-user/calls/c')
