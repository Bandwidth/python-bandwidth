import unittest
import six

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth import client, client_classes

class ClientTests(unittest.TestCase):
    def test_call_with_supported_client(self):
        """
        Call of client() should return client instance for supported client name
        """
        self.assertIsNotNone(client('catapult', 'userId', 'token', 'secret'))

    def test_call_with_supported_client_different_case(self):
        """
        Call of client() should return client instance for supported client name (case insensitive)
        """
        self.assertIsNotNone(client('CAtapult', 'userId', 'token', 'secret'))

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
        def import_mock(name, *args):
            if name == 'bandwidth.catapult':
                import_mock.call_count += 1
            return orig_import(name, *args)
        import_mock.call_count = 0
        with patch('__builtin__.__import__', side_effect=import_mock):
            client('catapult', 'userId', 'token', 'secret')
            self.assertIs(1, import_mock.call_count)
            client('catapult', 'userId', 'token', 'secret')
            self.assertIs(1, import_mock.call_count)

