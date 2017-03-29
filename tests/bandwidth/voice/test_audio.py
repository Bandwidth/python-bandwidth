import unittest
import six
import requests
from tests.bandwidth.helpers import get_voice_client as get_client
from tests.bandwidth.helpers import AUTH
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.voice import Client


class AudioBuilderTests(unittest.TestCase):

    def test_build_sentence(self):
        """
        Should return dict of values
        """
        estimated_json = {
            'gender': 'Female',
            'locale': 'en_UK',
            'loopEnabled': True,
            'sentence': 'Hello from Bandwidth',
            'voice': 'Bridget'
        }
        client = get_client()
        my_sentence = client.build_sentence(sentence="Hello from Bandwidth",
                                            gender="Female",
                                            locale="en_UK",
                                            voice="Bridget",
                                            loop_enabled=True
                                            )
        self.assertEqual(estimated_json, my_sentence)

    def test_build_audio_playback(self):
        """
        Should return dict of values
        """
        estimated_json = {
            'fileUrl': 'http://sound.com/test.mp3',
            'loopEnabled': True,
        }
        client = get_client()
        my_audio = client.build_audio_playback(file_url="http://sound.com/test.mp3",
                                               loop_enabled=True)
        self.assertEqual(estimated_json, my_audio)
