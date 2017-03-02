import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class CallTests(unittest.TestCase):

    def test_list_calls(self):
        """
        list_calls() should return calls
        """
        estimated_resquest = {
            'bridgeId': None,
            'conferenceId': None,
            'from': None,
            'to': None,
            'size': None,
            'sortOrder': None
        }
        estimated_json = """
        [{
            "id": "callId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_calls())
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls',
                auth=AUTH,
                headers=headers,
                params=estimated_resquest)
            self.assertEqual('callId', data[0]['id'])

    def test_create_call(self):
        """
        create_call() should create a call and return id
        """
        estimated_resquest = {
            'from': '+1234567890',
            'to': '+1234567891',
            'callTimeout': None,
            'callbackUrl': None,
            'callbackTimeout': None,
            'callbackHttpMethod': None,
            'fallbackUrl': None,
            'bridgeId': None,
            'conferenceId': None,
            'recordingEnabled': False,
            'recordingFileFormat': None,
            'recordingMaxDuration': None,
            'transcriptionEnabled': False,
            'tag': None,
            'sipHeaders': None
        }
        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/callId'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            from_ = '+1234567890'
            to = '+1234567891'
            id = client.create_call(from_, to)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/calls',
                auth=AUTH,
                headers=headers,
                json=estimated_resquest)
            self.assertEqual('callId', id)

    def test_get_call(self):
        """
        get_call() should return a call
        """
        estimated_json = """
        {
            "id": "callId"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_call('callId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('callId', data['id'])

    def test_update_call(self):
        """
        update_call() should update a call
        """
        estimated_resquest = {
            'state': 'completed',
            'recordingEnabled': None,
            'recordingFileFormat': None,
            'transferTo': None,
            'transferCallerId': None,
            'whisperAudio': None,
            'callbackUrl': None
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.update_call('callId', state='completed')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId',
                auth=AUTH,
                headers=headers,
                json=estimated_resquest)

    def test_play_audio_to_call(self):
        """
        play_audio_to_call() should play audio to a call
        """
        estimated_resquest = {
            'fileUrl': 'url',
            'sentence': None,
            'gender': None,
            'locale': None,
            'voice': None,
            'loopEnabled': None
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.play_audio_to_call('callId', file_url='url')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/audio',
                auth=AUTH,
                headers=headers,
                json=estimated_resquest)

    def test_send_dtmf_to_call(self):
        """
        send_dtmf_to_call() should send dtmf data to a call
        """
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.send_dtmf_to_call('callId', 12)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/dtmf',
                auth=AUTH,
                headers=headers,
                json={
                    'dtmfOut': 12})

    def test_list_call_recordings(self):
        """
        list_call_recordings() should return recordings
        """
        estimated_json = """
        [{
            "id": "recordingId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_call_recordings('callId'))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/recordings',
                headers=headers,
                auth=AUTH)
            self.assertEqual('recordingId', data[0]['id'])

    def test_list_call_transcriptions(self):
        """
        get_call_transcriptions() should return transcriptions
        """
        estimated_json = """
        [{
            "id": "transcriptionId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_call_transcriptions('callId'))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/transcriptions',
                headers=headers,
                auth=AUTH)
            self.assertEqual('transcriptionId', data[0]['id'])

    def test_list_call_events(self):
        """
        list_call_events() should return events
        """
        estimated_json = """
        [{
            "id": "eventId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_call_events('callId'))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/events',
                headers=headers,
                auth=AUTH)
            self.assertEqual('eventId', data[0]['id'])

    def test_get_call_event(self):
        """
        get_call_event() should return an event
        """
        estimated_json = """
        [{
            "id": "eventId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_call_event('callId', 'eventId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/events/eventId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('eventId', data[0]['id'])

    def test_create_call_gather(self):
        """
        create_call_gather() should create a gather
        """
        estimated_resquest = {
            'maxDigits': 1,
            'interDigitTimeout': None,
            'terminatingDigits': None,
            'tag': None
        }
        response = create_response(201)
        response.headers['location'] = 'http://.../gatherId'
        with patch('requests.request', return_value=response) as p:
            client = get_client()
            id = client.create_call_gather('callId', max_digits=1)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/gather',
                headers=headers,
                auth=AUTH,
                json=estimated_resquest)
            self.assertEqual('gatherId', id)

    def test_get_call_gather(self):
        """
        get_call_gather() should return a gather
        """
        estimated_json = """
        [{
            "id": "gatherId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_call_gather('callId', 'gatherId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/gather/gatherId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('gatherId', data[0]['id'])

    def test_update_call_gather(self):
        """
        update_call_gather() should update a gather
        """
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            data = {'state': 'completed'}
            client.update_call_gather('callId', 'gatherId', state='completed')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/calls/callId/gather/gatherId',
                headers=headers,
                auth=AUTH,
                json=data)

    def test_answer_call(self):
        """
        answer_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.answer_call('callId')
            p.assert_called_with('callId', state='active')

    def test_reject_call(self):
        """
        reject_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.reject_call('callId')
            p.assert_called_with('callId', state='rejected')

    def test_hangup_call(self):
        """
        hangup_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.hangup_call('callId')
            p.assert_called_with('callId', state='completed')

    def test_enable_call_recording(self):
        """
        enable_call_recording() should call update_call with recording_enabled=True
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.enable_call_recording('callId')
            p.assert_called_with('callId', recording_enabled=True)

    def test_disable_call_recording(self):
        """
        disable_call_recording() should call update_call with recording_enabled=False
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.disable_call_recording('callId')
            p.assert_called_with('callId', recording_enabled=False)

    def test_toggle_call_recording_on(self):
        """
        toggle_call_recording() should call get_call with the id
        """
        """
        create_call() should create a call and return id
        """
        estimated_response_json = {
            'recordingEnabled': False,
        }
        client = get_client()
        with patch.object(client, 'get_call', return_value=estimated_response_json) as get_mock:
            with patch.object(client, 'enable_call_recording') as p:
                client.toggle_call_recording('callId')
                get_mock.assert_called_with('callId')
                p.assert_called_with('callId')

    def test_toggle_call_recording_off(self):
        """
        toggle_call_recording() should call get_call with the id
        """
        """
        create_call() should create a call and return id
        """
        estimated_response_json = {
            'recordingEnabled': True,
        }
        client = get_client()
        with patch.object(client, 'get_call', return_value=estimated_response_json) as get_mock:
            with patch.object(client, 'disable_call_recording') as p:
                client.toggle_call_recording('callId')
                get_mock.assert_called_with('callId')
                p.assert_called_with('callId')

    def test_toggle_call_recording_neutral(self):
        """
        toggle_call_recording() should call get_call with the id
        """
        estimated_response_json = {
            'recordingEnabled': 'wildcard',
        }
        client = get_client()
        with patch.object(client, 'get_call', return_value=estimated_response_json) as get_mock:
            client.toggle_call_recording('callId')
            get_mock.assert_called_with('callId')

    def test_transfer_call(self):
        """
        transfer_call() should call update_call with right data
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.transfer_call('callId', '+1234567890')
            p.assert_called_with('callId', state='transferring', transfer_to='+1234567890', callback_url=None,
                                 transfer_caller_id=None, whisper_audio=None)

    def test_transfer_call_with_caller_id(self):
        """
        transfer_call() should call update_call with right data (with caller id)
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            client.transfer_call('callId', '+1234567890', '+1234567891')
            p.assert_called_with(
                'callId',
                state='transferring',
                transfer_to='+1234567890',
                transfer_caller_id='+1234567891',
                callback_url=None,
                whisper_audio=None)

    def test_transfer_call_with_whisper_audio(self):
        """
        transfer_call() should call update_call with right data (with whisper audio)
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            my_sentence = client.build_sentence(sentence="Hello from Bandwidth",
                                                gender="Female",
                                                locale="en_UK",
                                                voice="Bridget",
                                                loop_enabled=True
                                                )
            client.transfer_call('callId', '+1234567890', '+1234567891', whisper_audio=my_sentence)
            p.assert_called_with('callId',
                                 state='transferring',
                                 transfer_to='+1234567890',
                                 transfer_caller_id='+1234567891',
                                 whisper_audio=my_sentence,
                                 callback_url=None
                                 )

    def test_transfer_call_with_callback_url(self):
        """
        transfer_call() should call update_call with right data (with callback url)
        """
        client = get_client()
        with patch.object(client, 'update_call') as p:
            my_audio = client.build_audio_playback('url')
            client.transfer_call(
                'callId',
                to='+1234567890',
                caller_id='+1234567891',
                whisper_audio=my_audio,
                callback_url='curl')
            p.assert_called_with('callId',
                                 state='transferring',
                                 transfer_to='+1234567890',
                                 transfer_caller_id='+1234567891',
                                 callback_url='curl',
                                 whisper_audio=my_audio
                                 )
