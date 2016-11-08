import unittest
import six
import requests
import helpers
if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

from bandwidth.catapult import Client

class BridgesTests(unittest.TestCase):
    def test_get_bridges(self):
        """
        get_bridges() should return bridges
        """
        estimated_json="""
        [{
            "id": "bridgeId",
            "state": "completed",
            "bridgeAudio": "true",
            "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
            "createdTime": "2013-04-22T13:55:30.279Z",
            "activatedTime": "2013-04-22T13:55:30.280Z",
            "completedTime": "2013-04-22T13:59:30.122Z"
        }]
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = list(client.get_bridges())
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/bridges', auth=helpers.AUTH, params=None)
            self.assertEqual('bridgeId', data[0]['id'])

    def test_create_bridge(self):
        """
        create_bridge() should create a bridge and return id
        """
        estimated_response = helpers.create_response(201)
        estimated_response.headers['Location'] = 'http://localhost/bridgeId'
        with patch('requests.request', return_value = estimated_response) as p:
            client = helpers.get_client()
            data = {'callIds': ['callId']}
            id = client.create_bridge(data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/bridges', auth=helpers.AUTH, json=data)
            self.assertEqual('bridgeId', id)


    def test_get_bridge(self):
        """
        get_bridge() should return a bridge
        """
        estimated_json="""
        {
            "id": "bridgeId",
            "state": "completed",
            "bridgeAudio": "true",
            "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
            "createdTime": "2013-04-22T13:55:30.279Z",
            "activatedTime": "2013-04-22T13:55:30.280Z",
            "completedTime": "2013-04-22T13:59:30.122Z"
        }
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            data = client.get_bridge('bridgeId')
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/bridges/bridgeId', auth=helpers.AUTH)
            self.assertEqual('bridgeId', data['id'])

    def test_update_bridge(self):
        """
        update_bridge() should update a bridge
        """
        with patch('requests.request', return_value = helpers.create_response(200)) as p:
            client = helpers.get_client()
            data = {'bridgeAudio': False}
            client.update_bridge('bridgeId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/bridges/bridgeId', auth=helpers.AUTH, json=data)

    def test_get_bridge_calls(self):
        """
        get_bridge_calls() should return calls of a bridge
        """
        estimated_json="""
        [{
            "activeTime": "2013-05-22T19:49:39Z",
            "direction": "out",
            "from": "{fromNumber}",
            "id": "{callId1}",
            "bridgeId": "{bridgeId}",
            "startTime": "2013-05-22T19:49:35Z",
            "state": "active",
            "to": "{toNumber1}",
            "recordingEnabled": false,
            "events": "https://api.catapult.inetwork.com/v1/users/{userId}/calls/{callId1}/events",
            "bridge": "https://api.catapult.inetwork.com/v1/users/{userId}/bridges/{bridgeId}"
        }]
        """
        with patch('requests.request', return_value = helpers.create_response(200, estimated_json)) as p:
            client = helpers.get_client()
            calls = list(client.get_bridge_calls('bridgeId'))
            p.assert_called_with('get', 'https://api.catapult.inetwork.com/v1/users/userId/bridges/bridgeId/calls', auth=helpers.AUTH)
            self.assertEqual('{callId1}', calls[0]['id'])

    def test_play_audio_to_bridge(self):
        """
        play_audio_to_bridge() should play audio to a bridge
        """
        with patch('requests.request', return_value = helpers.create_response(200)) as p:
            client = helpers.get_client()
            data = {'fileUrl': 'url'}
            client.play_audio_to_bridge('bridgeId', data)
            p.assert_called_with('post', 'https://api.catapult.inetwork.com/v1/users/userId/bridges/bridgeId/audio', auth=helpers.AUTH, json=data)
