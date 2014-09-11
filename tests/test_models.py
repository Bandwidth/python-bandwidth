import responses
import unittest

from bandwith_sdk import Client, Call


class CallsTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Call.get('by-call-id')
        """
        raw = """
        {
        "id": "c-call-id",
        "direction": "out",
        "from": "+1919000001",
        "to": "+1919000002",
        "recordingEnabled": false,
        "callbackUrl": "",
        "state": "active",
        "startTime": "2013-02-08T13:15:47.587Z",
        "activeTime": "2013-02-08T13:15:52.347Z",
        "events": "https://.../calls/{callId}/events"
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw,
                      status=201,
                      content_type='application/json')
        call = Call.get('c-call-id')

        self.assertEqual(call.call_id, 'c-call-id')
