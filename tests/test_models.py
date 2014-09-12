import responses
import unittest

from bandwith_sdk import Call, Bridge, BandwithError


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

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Call.get('by-call-id')
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body='',
                      status=404,
                      content_type='application/json')
        with self.assertRaises(BandwithError) as be:
            Call.get('c-call-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 Client Error: None')

    @responses.activate
    def test_list(self):
        """
        Call.list()
        """
        raw = """
        [{
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
        },
        {
        "id": "c-call-id-1",
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
        ]
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls',
                      body=raw,
                      status=200,
                      content_type='application/json')
        calls = Call.list()

        self.assertEqual(calls[0].call_id, 'c-call-id')
        self.assertEqual(calls[1].call_id, 'c-call-id-1')

    @responses.activate
    def test_create(self):
        """
        Call.create("+1919000001", "+1919000002")
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Call.create("+1919000001", "+1919000002")

        self.assertEqual(call.call_id, 'new-call-id')


class BridgesTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Bridge.get('by-bridge-id')
        """
        raw = """
        {
        "id": "by-bridge-id",
        "state": "completed",
        "bridgeAudio": "true",
        "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
        "createdTime": "2013-04-22T13:55:30.279Z",
        "activatedTime": "2013-04-22T13:55:30.280Z",
        "completedTime": "2013-04-22T13:59:30.122Z"
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/by-bridge-id',
                      body=raw,
                      status=201,
                      content_type='application/json')
        bridge = Bridge.get('by-bridge-id')

        self.assertIsInstance(bridge, Bridge)

        self.assertEqual(bridge.id, 'by-bridge-id')

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Bridge.get('by-bridge-id')
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/by-bridge-id',
                      body='',
                      status=404,
                      content_type='application/json')
        with self.assertRaises(BandwithError) as be:
            Bridge.get('by-bridge-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 Client Error: None')

    @responses.activate
    def test_list(self):
        """
        Bridge.list()
        """
        raw = """
        [
          {
            "id": "bridge-1",
            "state": "completed",
            "bridgeAudio": "true",
            "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
            "createdTime": "2013-04-22T13:55:30.279Z",
            "activatedTime": "2013-04-22T13:55:30.280Z",
            "completedTime": "2013-04-22T13:56:30.122Z"
          },
          {
            "id": "bridge-2",
            "state": "completed",
            "bridgeAudio": "true",
            "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
            "createdTime": "2013-04-22T13:58:30.121Z",
            "activatedTime": "2013-04-22T13:58:30.122Z",
            "completedTime": "2013-04-22T13:59:30.122Z"
          }
        ]

        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body=raw,
                      status=200,
                      content_type='application/json')
        bridges = Bridge.list()

        self.assertEqual(bridges[0].id, 'bridge-1')
        self.assertEqual(bridges[1].id, 'bridge-2')

    @responses.activate
    def test_create(self):
        """
        Bridge.create()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/bridges/new-bridge-id'})

        bridge = Bridge.create()
        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'new-bridge-id')

    @responses.activate
    def test_create_form_call(self):
        """
        Bridge.create(Call('c-foo'), Call('c-bar')))
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/bridges/new-bridge-id'})

        bridge = Bridge.create(Call('c-foo'), Call('c-bar'))
        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'new-bridge-id')

        request_message = responses.calls[0].request.body

        self.assertEqual(sorted(request_message), sorted('{"callIds": ["c-foo", "c-bar"], "bridgeAudio": true}'))

    def test_calls_property(self):
        """
        Bridge('bridge-id').calls
        """

        bridge = Bridge('bridge-id', Call('c-foo'), Call('c-bar'))

        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'bridge-id')

        calls = bridge.calls

        self.assertEqual(calls[0].call_id, 'c-foo')
        self.assertEqual(calls[1].call_id, 'c-bar')
