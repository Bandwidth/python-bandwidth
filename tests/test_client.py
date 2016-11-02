import unittest
import six

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from python-bandwidth import client, client_classes

class ClientTests(unittest.TestCase):
    def test_call_with_supported_client(self):
        """
        Call of client() should return client instance for supported client name
        """
        self.assertIsNotNone(client('catapult'))

    def test_call_with_supported_client_different_case(self):
        """
        Call of client() should return client instance for supported client name (case insensitive)
        """
        self.assertIsNotNone(client('CAtapult'))

    @unittest.expectedFailure
    def test_call_with_unsupported_client(self):
        """
        Call of client() should raise error for unsupported client name
        """
        client('Non existing client')

    def test_call_with_caching_client_class_name(self):
        """
        Call of client() should cache client class name
        """
        client_classes = {}
        orig_import = __import__
        call_count = 0
        import_mock = lambda *args:
            call_count += 1
            return orig_import(*args)
        with mock.patch('__builtin__.__import__', side_effect=import_mock):
            client('catapult')
            self.assertIs(1, call_count)
            client('catapult')
            self.assertIs(1, call_count)

