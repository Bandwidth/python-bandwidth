import unittest
import six
import requests
from tests.catapult.helpers import create_response, get_client, AUTH, headers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client


class ConferenceTests(unittest.TestCase):

    def test_create_conference(self):
        """
        create_conference() should create a conference and return id
        """

        estimated_request = {
            'callbackUrl': None,
            'from': '+1234567980',
            'callbackTimeout': None,
            'callbackHttpMethod': 'GET',
            'fallbackUrl': None,
            'tag': 'my_tag'
        }

        estimated_response = create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/conferenceId'
        with patch('requests.request', return_value=estimated_response) as p:
            client = get_client()
            id = client.create_conference(
                from_='+1234567980',
                callbackUrl='http://abc.com',
                tag='my_tag',
                callback_http_method='GET'
            )
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences',
                auth=AUTH,
                headers=headers,
                json=estimated_request)
            self.assertEqual('conferenceId', id)

    def test_get_conference(self):
        """
        get_conference() should return a conference
        """
        estimated_json = """
        {
            "id": "conferenceId"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_conference('conferenceId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('conferenceId', data['id'])

    def test_update_conference(self):
        """
        update_conference() should update a conference
        """
        estimated_request = {
            'state': 'completed',
            'mute': None,
            'hold': None,
            'callbackUrl': None,
            'callbackTimeout': None,
            'callbackHttpMethod': None,
            'fallbackUrl': None,
            'tag': None
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            client.update_conference('conferenceId', state='completed')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId',
                auth=AUTH,
                headers=headers,
                json=estimated_request)

    def test_play_audio_to_conference(self):
        """
        play_audio_to_conference() should play an audio to a conference
        """
        estimated_request = {
            'fileUrl': 'url',
            'sentence': None,
            'gender': None,
            'locale': None,
            'voice': None,
            'loopEnabled': None
        }

        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            data = {'file_url': 'url'}
            client.play_audio_to_conference('conferenceId', **data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId/audio',
                auth=AUTH,
                headers=headers,
                json=estimated_request)

    def test_create_conference_member(self):
        """
        create_conference_member() should create a conference member
        """
        estimated_request = {
            'callId': 'callId',
            'joinTone': None,
            'leavingTone': None,
            'mute': None,
            'hold': None
        }
        response = create_response(201)
        response.headers['location'] = 'http://.../memberId'
        with patch('requests.request', return_value=response) as p:
            client = get_client()
            data = {'call_id': 'callId'}
            id = client.create_conference_member('conferenceId', **data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId/members',
                auth=AUTH,
                headers=headers,
                json=estimated_request)
            self.assertEqual('memberId', id)

    def test_list_conference_members(self):
        """
        list_conference_members() should return members of a conference
        """
        estimated_json = """
        [{
            "id": "memberId"
        }]
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = list(client.list_conference_members('conferenceId'))
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId/members',
                headers=headers,
                auth=AUTH)
            self.assertEqual('memberId', data[0]['id'])

    def test_get_conference_member(self):
        """
        get_conference_member() should return a conference member
        """
        estimated_json = """
        {
            "id": "memberId"
        }
        """
        with patch('requests.request', return_value=create_response(200, estimated_json)) as p:
            client = get_client()
            data = client.get_conference_member('conferenceId', 'memberId')
            p.assert_called_with(
                'get',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId/members/memberId',
                headers=headers,
                auth=AUTH)
            self.assertEqual('memberId', data['id'])

    def test_update_conference_member(self):
        """
        update_conference_member() should update a conference member
        """
        estimated_request = {
            'state': 'completed',
            'joinTone': None,
            'leavingTone': None,
            'mute': None,
            'hold': None
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            data = {'state': 'completed'}
            client.update_conference_member('conferenceId', 'memberId', **data)
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId/members/memberId',
                auth=AUTH,
                headers=headers,
                json=estimated_request)

    def test_play_audio_to_conference_member(self):
        """
        play_audio_to_conference_member() should play audio to a conference member
        """
        estimated_request = {
            'fileUrl': 'url',
            'sentence': None,
            'gender': None,
            'locale': None,
            'voice': None,
            'loopEnabled': None
        }
        with patch('requests.request', return_value=create_response(200)) as p:
            client = get_client()
            data = {'file_url': 'url'}
            client.play_audio_to_conference_member('conferenceId', 'memberId', file_url='url')
            p.assert_called_with(
                'post',
                'https://api.catapult.inetwork.com/v1/users/userId/conferences/conferenceId/members/memberId/audio',
                auth=AUTH,
                headers=headers,
                json=estimated_request)

    def test_speak_sentence_to_conference_member(self):
        """
        speak_sentence_to_conference_member() should call play_audio_to_conference_member() with right params
        """
        client = get_client()
        with patch.object(client, 'play_audio_to_conference_member') as p:
            client.speak_sentence_to_conference_member('conferenceId', 'memberId', 'Hello')
            p.assert_called_with('conferenceId', 'memberId',
                                 sentence='Hello',
                                 gender='female',
                                 voice='susan',
                                 locale='en_US',
                                 tag=None
                                 )

    def test_play_audio_file_to_conference_member(self):
        """
        play_audio_file_to_conference_member() should call play_audio_to_conference_member() with right params
        """
        client = get_client()
        with patch.object(client, 'play_audio_to_conference_member') as p:
            client.play_audio_file_to_conference_member('conferenceId', 'memberId', 'url')
            p.assert_called_with('conferenceId', 'memberId',
                                 file_url='url',
                                 tag=None
                                 )

    def test_remove_conference_member(self):
        """
        delete_conference_member() should call update_conference_member() with right params
        """
        client = get_client()
        with patch.object(client, 'update_conference_member') as p:
            client.remove_conference_member('conferenceId', 'memberId')
            p.assert_called_with('conferenceId', 'memberId', state='completed')

    def test_hold_conference_member(self):
        """
        hold_conference_member() should call update_conference_member() with right params
        """
        client = get_client()
        with patch.object(client, 'update_conference_member') as p:
            client.hold_conference_member('conferenceId', 'memberId', True)
            p.assert_called_with('conferenceId', 'memberId', hold=True)

    def test_mute_conference_member(self):
        """
        mute_conference_member() should call update_conference_member() with right params
        """
        client = get_client()
        with patch.object(client, 'update_conference_member') as p:
            client.mute_conference_member('conferenceId', 'memberId', True)
            p.assert_called_with('conferenceId', 'memberId', mute=True)

    def test_terminate_conference(self):
        """
        terminate_conference() should call update_conference() with right params
        """
        client = get_client()
        with patch.object(client, 'update_conference') as p:
            client.terminate_conference('conferenceId')
            p.assert_called_with('conferenceId', state='completed')

    def test_hold_conference(self):
        """
        hold_conference() should call update_conference() with right params
        """
        client = get_client()
        with patch.object(client, 'update_conference') as p:
            client.hold_conference('conferenceId', True)
            p.assert_called_with('conferenceId', hold=True)

    def test_mute_conference(self):
        """
        mute_conference() should call update_conference() with right params
        """
        client = get_client()
        with patch.object(client, 'update_conference') as p:
            client.mute_conference('conferenceId', True)
            p.assert_called_with('conferenceId', mute=True)
