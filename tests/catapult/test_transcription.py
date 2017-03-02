import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class TranscriptionTests(unittest.TestCase):

    def test_list_transcriptions(self):
        """
        list_transcriptions() should return transcriptions
        """
        estimated_json = """
        [{
            "chargeableDuration": 60,
            "id": "{transcription-id}",
            "state": "completed",
            "time": "2014-10-09T12:09:16Z",
            "text": "{transcription-text}",
            "textSize": 3627,
            "textUrl": "{url-to-full-text}"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_transcriptions('recordingId'))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/recordings/recordingId/transcriptions',
                auth=AUTH,
                headers=headers,
                params={'size': None})
            self.assertEqual('{transcription-id}', data[0]['id'])

    def test_create_transcription(self):
        """
        create_transcription() should create a transcription and return id
        """
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/transcriptionId'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            id = client.create_transcription('recordingId')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/recordings/recordingId/transcriptions',
                auth=AUTH,
                headers=headers,
                json={})
            self.assertEqual('transcriptionId', id)

    def test_get_transcription(self):
        """
        get_transcription() should return a transcription
        """
        estimated_json = """
        {
            "chargeableDuration": 60,
            "id": "{transcription-id}",
            "state": "completed",
            "time": "2014-10-09T12:09:16Z",
            "text": "{transcription-text}",
            "textSize": 3627,
            "textUrl": "{url-to-full-text}"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_transcription('recId', 'transcriptionId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/recordings/recId/transcriptions/transcriptionId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('{transcription-id}', data['id'])
