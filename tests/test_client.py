from __future__ import absolute_import
import unittest
import six

from bandwidth import client
from bandwidth import _client_classes

if six.PY3:
    from unittest.mock import patch
    builtins = 'builtins'
else:
    from mock import patch
    builtins = '__builtin__'


class ClientTests(unittest.TestCase):

    def test_call_with_supported_client(self):
        """
        Call of client() should return client instance for supported client name
        """
        self.assertIsNotNone(client('voice', 'userId', 'token', 'secret'))

    def test_call_with_supported_client_different_case(self):
        """
        Call of client() should return client instance for supported client name (case insensitive)
        """
        self.assertIsNotNone(client('VOIce', 'userId', 'token', 'secret'))

    def test_call_with_unsupported_client(self):
        """
        Call of client() should raise error for unsupported client name
        """
        with self.assertRaises(ValueError):
            client('Non existing client')

    def test_call_with_caching_client_class_name(self):
        """
        Call of client() should cache client class name
        """
        _client_classes = {}
        orig_import = __import__
        with patch('%s.__import__' % builtins, side_effect=orig_import) as p:
            client('voice', 'userId', 'token', 'secret')
            old = p.call_count
            client('voice', 'userId', 'token', 'secret')
            self.assertEqual(old, p.call_count)
