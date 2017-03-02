import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class RecordingTests(unittest.TestCase):

    def test_list_recordings(self):
        """
        list_recordings() should return recordings
        """
        estimated_json = """
        [{
            "endTime": "2013-02-08T13:17:12.181Z",
            "id": "{recordingId1}",
            "media": "https://.../v1/users/.../media/{callId1}-1.wav",
            "call": "https://.../v1/users/.../calls/{callId1}",
            "startTime": "2013-02-08T13:15:47.587Z",
            "state": "complete"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_recordings())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/recordings',
                auth=AUTH,
                headers=headers,
                params={'size': None})
            self.assertEqual('{recordingId1}', data[0]['id'])
            self.assertEqual('{callId1}-1.wav', data[0]['mediaName'])

    def test_get_recording(self):
        """
        get_recording() should return a recording
        """
        estimated_json = """
        {
            "endTime": "2013-02-08T13:17:12.181Z",
            "id": "{recordingId1}",
            "media": "https://.../v1/users/.../media/{callId1}-1.wav",
            "call": "https://.../v1/users/.../calls/{callId1}",
            "startTime": "2013-02-08T13:15:47.587Z",
            "state": "complete"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_recording('recordingId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/recordings/recordingId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('{callId1}-1.wav', data['mediaName'])
