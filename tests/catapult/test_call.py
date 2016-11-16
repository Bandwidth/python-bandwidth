import unittest
import six
import requests
from  tests.catapult.helpers import create_response, get_client, AUTH
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

class CallTests(unittest.TestCase):
    def test_get_calls(self):
        """
        get_calls() should return calls
        """
        estimated_json="""
        [{
            "id": "callId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.get_calls())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls', auth=AUTH, params=None)
            self.assertEqual('callId', data[0]['id'])

    def test_create_call(self):
        """
        create_call() should create a call and return id
        """
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/callId'
        with patch('requests.request', return_value = estimated_response) as p:
            client = get_client()
            data = {'from': '+1234567890', 'to': '+1234567891'}
            id = client.create_call(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/calls', auth=AUTH, json=data)
            self.assertEqual('callId', id)


    def test_get_call(self):
        """
        get_call() should return a call
        """
        estimated_json="""
        {
            "id": "callId"
        }
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_call('callId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId', auth=AUTH)
            self.assertEqual('callId', data['id'])

    def test_update_call(self):
        """
        update_call() should update a call
        """
        with patch('requests.request', return_value = create_response(200)) as p:
            client = get_client()
            data = {'state': 'completed'}
            client.update_call('callId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId', auth=AUTH, json=data)

    def test_play_audio_to_call(self):
        """
        play_audio_to_call() should play audio to a call
        """
        with patch('requests.request', return_value = create_response(200)) as p:
            client = get_client()
            data = {'fileUrl': 'url'}
            client.play_audio_to_call('callId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/audio', auth=AUTH, json=data)

    def test_send_dtmf_to_call(self):
        """
        send_dtmf_to_call() should send dtmf data to a call
        """
        with patch('requests.request', return_value = create_response(200)) as p:
            client = get_client()
            data = {'dtmfOut': '12'}
            client.send_dtmf_to_call('callId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/dtmf', auth=AUTH, json=data)

    def test_get_call_recordings(self):
        """
        get_call_recordings() should return recordings
        """
        estimated_json="""
        [{
            "id": "recordingId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.get_call_recordings('callId'))
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/recordings', auth=AUTH)
            self.assertEqual('recordingId', data[0]['id'])

    def test_get_call_transcriptions(self):
        """
        get_call_transcriptions() should return transcriptions
        """
        estimated_json="""
        [{
            "id": "transcriptionId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.get_call_transcriptions('callId'))
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/transcriptions', auth=AUTH)
            self.assertEqual('transcriptionId', data[0]['id'])

    def test_get_call_events(self):
        """
        get_call_events() should return events
        """
        estimated_json="""
        [{
            "id": "eventId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.get_call_events('callId'))
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/events', auth=AUTH)
            self.assertEqual('eventId', data[0]['id'])

    def test_get_call_event(self):
        """
        get_call_event() should return an event
        """
        estimated_json="""
        [{
            "id": "eventId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_call_event('callId', 'eventId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/events/eventId', auth=AUTH)
            self.assertEqual('eventId', data[0]['id'])

    def test_create_call_gather(self):
        """
        create_call_gather() should create a gather
        """
        response = create_response(201)
        response.headers['location'] = 'http://.../gatherId'
        with patch('requests.request', return_value = response) as p:
            client = get_client()
            data = {'maxDigits': 1}
            id = client.create_call_gather('callId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/gather', auth=AUTH, json=data)
            self.assertEqual('gatherId', id)

    def test_get_call_gather(self):
        """
        get_call_gather() should return a gather
        """
        estimated_json="""
        [{
            "id": "gatherId"
        }]
        """
        with patch('requests.request', return_value = create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_call_gather('callId', 'gatherId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/gather/gatherId', auth=AUTH)
            self.assertEqual('gatherId', data[0]['id'])

    def test_update_call_gather(self):
        """
        update_call_gather() should update a gather
        """
        with patch('requests.request', return_value = create_response(200)) as p:
            client = get_client()
            data = {'state': 'completed'}
            client.update_call_gather('callId', 'gatherId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/gather/gatherId', auth=AUTH, json=data)

    def test_answer_call(self):
        """
        answer_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.answer_call('callId')
            p.assert_called_with('callId', {'state': 'active'})

    def test_reject_call(self):
        """
        reject_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.reject_call('callId')
            p.assert_called_with('callId', {'state': 'rejected'})

    def test_hangup_call(self):
        """
        hangup_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.hangup_call('callId')
            p.assert_called_with('callId', {'state': 'completed'})

    def test_tune_call_recording(self):
        """
        tune_call_recording() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.tune_call_recording('callId', True)
            p.assert_called_with('callId', {'recordingEnabled': True})

    def test_transfer_call(self):
        """
        transfer_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.transfer_call('callId', '+1234567890')
            p.assert_called_with('callId', {'state': 'transferring', 'transferTo': '+1234567890' })

    def test_transfer_call_with_caller_id(self):
        """
        transfer_call() should call update_call with right data (with caller id)
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.transfer_call('callId', '+1234567890', '+1234567891')
            p.assert_called_with('callId', {'state': 'transferring', 'transferTo': '+1234567890', 'transferCallerId': '+1234567891' })

    def test_transfer_call_with_whisper_audio(self):
        """
        transfer_call() should call update_call with right data (with whisper audio)
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.transfer_call('callId', '+1234567890', '+1234567891', {'fileUrl': 'url'})
            p.assert_called_with('callId', {
                'state': 'transferring',
                'transferTo': '+1234567890',
                'transferCallerId': '+1234567891',
                'whisperAudio': {'fileUrl': 'url'}
            })

    def test_transfer_call_with_callback_url(self):
        """
        transfer_call() should call update_call with right data (with callback url)
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.transfer_call('callId', '+1234567890', '+1234567891', {'fileUrl': 'url'}, 'curl')
            p.assert_called_with('callId', {
                'state': 'transferring',
                'transferTo': '+1234567890',
                'transferCallerId': '+1234567891',
                'whisperAudio': {'fileUrl': 'url'},
                'callbackUrl': 'curl'
            })
