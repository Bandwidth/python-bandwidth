import unittest
import six
import requests
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult.decorators import play_audio


class DecoratorsTests(unittest.TestCase):
    def test_play_audio(self):
        """
        play_audio() should add methods speak_sentence and play_audio_file to class
        """
        @play_audio('test')
        class Test:
            def play_audio_to_test(self, id, data):
                pass
        t = Test()
        self.assertTrue(callable(getattr(t, 'speak_sentence_to_test', None)))
        self.assertTrue(callable(getattr(t, 'play_audio_file_to_test', None)))
        with patch.object(t, 'play_audio_to_test') as p:
            t.speak_sentence_to_test('id', 'Hello')
            p.assert_called_with('id', {
                'sentence': 'Hello',
                'gender': 'female',
                'voice': 'susan',
                'locale': 'en_US',
                'tag': None
            })
            t.play_audio_file_to_test('id', 'url')
            p.assert_called_with('id', {
                'fileUrl': 'url',
                'tag': None
            })



