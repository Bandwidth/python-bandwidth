import six

import responses
import unittest

from bandwidth_sdk import (Call, Bridge,
                           AppPlatformError, Application,
                           Account, Conference, Recording)
from datetime import datetime


def assertJsonEq(first, second, msg='Ouups'):
    assert sorted(first) == sorted(second), '%r != %r\n%s' % (first, second, msg)


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
        self.assertEqual(call.direction, 'out')
        self.assertEqual(call.from_, '+1919000001')
        self.assertEqual(call.to, '+1919000002')
        self.assertEqual(call.recording_enabled, False)
        self.assertEqual(call.state, 'active')

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Call.get('by-call-id')
        """
        raw = """
                {
            "category": "not-found",
            "code": "call-not-found",
            "message": "The call c-call-id could not be found",
            "details": [
                {
                    "name": "callId",
                    "value": "c-call-id"
                },
                {
                    "name": "requestMethod",
                    "value": "GET"
                },
                {
                    "name": "remoteAddress",
                    "value": "193.239.74.XXX"
                },
                {
                    "name": "requestPath",
                    "value": "users/u-user/calls/c-call-id"
                }
            ]
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw,
                      status=404,
                      content_type='application/json')
        with self.assertRaises(AppPlatformError) as be:
            Call.get('c-call-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 client error: The call c-call-id could not be found')

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

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"to": "+1919000002", "from": "+1919000001", '
                                      '"callTimeout": 30}')

    @responses.activate
    def test_play_audio(self):
        """
        Call('new-call-id').play_audio('Hello.mp3')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Call('new-call-id')
        call.play_audio('Hello.mp3', loop_enabled=True, tag='custom_tag')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"loopEnabled": true, "tag": "custom_tag", "fileUrl": "Hello.mp3"}')

    @responses.activate
    def test_stop_audio(self):
        """
        Call('new-call-id').stop_audio()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.stop_audio()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"fileUrl": ""}')

    @responses.activate
    def test_speak_sentence(self):
        """
        Call('new-call-id').speak_sentence('Hello', gender='female')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Call('new-call-id')
        call.speak_sentence('Hello', gender='female', voice='Jorge', loop_enabled=True)
        request_message = responses.calls[0].request.body
        assertJsonEq(
            request_message, '{"voice": "Jorge", "sentence": "Hello", "gender": "female", "loopEnabled": true}')

    @responses.activate
    def test_stop_sentence(self):
        """
        Call('new-call-id').stop_sentence()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.stop_sentence()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"sentence": ""}')

    @responses.activate
    def test_transfer(self):
        """
        Call('new-call-id').transfer('+1919000008', whisper_audio={"sentence": "Hello {number}, thanks for calling"})
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/tr-call-id'})

        call = Call('new-call-id')
        new_call = call.transfer('+1919000008', whisper_audio={"sentence": "Hello {number}, thanks for calling"})
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"transferTo": "+1919000008", "state": "transferring", '
                                      '"whisperAudio": {"sentence": "Hello {number}, thanks for calling"}}')

        self.assertIsInstance(new_call, Call)
        self.assertEqual(new_call.call_id, 'tr-call-id')

    @responses.activate
    def test_hangup(self):
        """
        Call('new-call-id').hangup()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.hangup()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"state": "completed"}')

        self.assertEqual(call.state, 'completed')

    @responses.activate
    def test_reject(self):
        """
        Call('new-call-id').reject()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.reject()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"state": "rejected"}')

        self.assertEqual(call.state, 'rejected')

    @responses.activate
    def test_send_dtmf(self):
        """
        Call('new-call-id').send_dtmf('121')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/dtmf',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.send_dtmf('121')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"dtmfOut": "121"}')

    @responses.activate
    def test_get_events(self):
        """
        Call('new-call-id').get_events()
        """
        raw = """
        [
        {
        "id": "{callEventId1}",
        "time": "2012-09-19T13:55:41.343Z",
        "name": "create"
        },
        {
        "id": "{callEventId2}",
        "time": "2012-09-19T13:55:45.583Z",
        "name": "answer"
        },
        {
        "id": "{callEventId3}",
        "time": "2012-09-19T13:55:45.583Z",
        "name": "hangup",
        "data": "foo"
        }]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/events',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        events = call.get_events()
        self.assertEqual(len(events), 3)

    @responses.activate
    def test_refresh(self):
        """
        Call('c-call-id').refresh()
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
                      status=200,
                      content_type='application/json',
                      )

        call = Call('c-call-id')
        call.refresh()
        self.assertEqual(call.call_id, 'c-call-id')
        self.assertEqual(call.direction, 'out')
        self.assertEqual(call.from_, '+1919000001')
        self.assertEqual(call.to, '+1919000002')
        self.assertEqual(call.recording_enabled, False)
        self.assertEqual(call.state, 'active')

    @responses.activate
    def test_gather_create(self):
        """
        gather = Call('new-call-id').gather;
        gather.create(max_digits='5', terminating_digits='*', inter_digit_timeout='7')
        """

        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/gather',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id/gather/g-foo'})

        gather = Call('new-call-id').gather
        gather.create(max_digits='5', terminating_digits='*', inter_digit_timeout='7',
                      prompt={"sentence": "Please enter your 5 digit code", 'loop_enabled': True})

        self.assertEqual(gather.id, 'g-foo')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"maxDigits": "5", "terminatingDigits": "*", '
                                      '"prompt": {"loopEnabled": true, "sentence": "Please enter your 5 digit code"}, '
                                      '"interDigitTimeout": "7"}')

    @responses.activate
    def test_gather_get(self):
        """
        gather = Call('new-call-id').gather;
        gather.get('g-foo')
        """
        raw = """
        {
        "id": "g-foo",
        "state": "completed",
        "reason": "max-digits",
        "createdTime": "2014-02-12T19:33:56Z",
        "completedTime": "2014-02-12T19:33:59Z",
        "call": "https://api.catapult.inetwork.com/v1/users/u-xa2n3oxk6it4efbglisna6a/calls/c-isw3qup6gvr3ywcsentygnq",
        "digits": "123"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/gather/g-foo',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        gather = Call('new-call-id').gather
        gather.get('g-foo')

        self.assertEqual(gather.id, 'g-foo')
        self.assertEqual(gather.reason, 'max-digits')
        self.assertEqual(gather.digits, '123')


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
        raw = """
                {
            "category": "not-found",
            "code": "bridge-not-found",
            "message": "The bridge by-bridge-id could not be found",
            "details": [
                {
                    "name": "bridgeId",
                    "value": "by-bridge-id"
                },
                {
                    "name": "requestMethod",
                    "value": "GET"
                },
                {
                    "name": "remoteAddress",
                    "value": "193.239.152.XXX"
                },
                {
                    "name": "requestPath",
                    "value": "users/u-user/bridges/by-bridge-id"
                }
            ]
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/by-bridge-id',
                      body=raw,
                      status=404,
                      content_type='application/json')
        with self.assertRaises(AppPlatformError) as be:
            Bridge.get('by-bridge-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 client error: The bridge by-bridge-id could not be found')

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
        assertJsonEq(request_message, '{"callIds": ["c-foo", "c-bar"]}')

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

    @responses.activate
    def test_play_audio(self):
        """
        Bridge('b-id').play_audio('Hello.mp3')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id/audio',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/b-id'})

        bridge = Bridge('b-id')
        bridge.play_audio('Hello.mp3', loop_enabled=True, tag='custom_tag')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"loopEnabled": true, "tag": "custom_tag", "fileUrl": "Hello.mp3"}')

    @responses.activate
    def test_stop_audio(self):
        """
        Bridge('b-id').stop_audio()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id/audio',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        bridge = Bridge('b-id')
        bridge.stop_audio()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"fileUrl": ""}')

    @responses.activate
    def test_speak_sentence(self):
        """
        Bridge('b-id').speak_sentence('Hello', gender='female')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id/audio',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/bridges/b-id'})

        bridge = Bridge('b-id')
        bridge.speak_sentence('Hello', gender='female', voice='Jorge', loop_enabled=True)
        request_message = responses.calls[0].request.body
        assertJsonEq(
            request_message, '{"voice": "Jorge", "sentence": "Hello", "gender": "female", "loopEnabled": true}')

    @responses.activate
    def test_stop_sentence(self):
        """
        Bridge('b-id').stop_sentence()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id/audio',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        Bridge('b-id').stop_sentence()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"sentence": ""}')

    @responses.activate
    def test_refresh(self):
        """
        Bridge('b-id').refresh()
        """
        raw = """
        {
        "id": "b-id",
        "state": "completed",
        "bridgeAudio": true,
        "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
        "createdTime": "2013-04-22T13:55:30.279Z",
        "activatedTime": "2013-04-22T13:55:30.280Z",
        "completedTime": "2013-04-22T13:59:30.122Z"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        bridge = Bridge('b-id')
        bridge.refresh()

        self.assertEqual(bridge.state, 'completed')
        self.assertEqual(bridge.bridge_audio, True)

    @responses.activate
    def test_call_party(self):
        """
        Bridge('b-id').call_party("+1919000001", "+1919000002")
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Bridge('b-id').call_party('+1919000001', '+1919000002')

        self.assertIsInstance(call, Call)
        self.assertEqual(call.call_id, 'new-call-id')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"to": "+1919000002", "from": "+1919000001", '
                                      '"callTimeout": 30, "bridgeId": "b-id"}')

    @responses.activate
    def test_update(self):
        """
        Bridge('b-id').update(Call('a-id'), Call('b-id'), bridge_audio=False)
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        Bridge('b-id').update(Call('a-id'), Call('b-id'), bridge_audio=False)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"bridgeAudio": false, "callIds": ["a-id", "b-id"]}')


class ApplicationsTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Application.get('by-application_id')
        """
        raw = """
        {
        "id": "a-application-id",
        "callbackHttpMethod": "post",
        "incomingCallUrl": "http://callback.info",
        "name": "test_application_name",
        "autoAnswer": true
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/a-application-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        application = Application.get('a-application-id')

        self.assertEqual(application.application_id, 'a-application-id')
        self.assertEqual(application.incoming_call_url, 'http://callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'test_application_name')
        self.assertEqual(application.auto_answer, True)

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Application.get('by-application_id')
        """
        raw = """
                {
            "category": "not-found",
            "code": "application-not-found",
            "message": "The application by-application_id could not be found",
            "details": [
                {
                    "name": "applicationId",
                    "value": "by-application_id"
                },
                {
                    "name": "requestMethod",
                    "value": "GET"
                },
                {
                    "name": "remoteAddress",
                    "value": "193.239.74.XXX"
                },
                {
                    "name": "requestPath",
                    "value": "users/u-user/applications/by-application_id"
                }
            ]
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/by-application_id',
                      body=raw,
                      status=404,
                      content_type='application/json')
        with self.assertRaises(AppPlatformError) as be:
            Application.get('by-application_id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 client error: The application by-application_id could not be found')

    @responses.activate
    def test_list(self):
        """
        Application.list()
        """
        raw = """
        [{
        "id": "a-application-id",
        "callbackHttpMethod": "post",
        "incomingCallUrl": "http://callback.info",
        "name": "test_application_name",
        "autoAnswer": true
        },
        {
        "id": "a-application-id1",
        "callbackHttpMethod": "get",
        "incomingCallUrl": "http://callback1.info",
        "name": "test_application_name1",
        "autoAnswer": false
        }
        ]
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/',
                      body=raw,
                      status=200,
                      content_type='application/json')
        applications = Application.list()

        self.assertEqual(applications[0].application_id, 'a-application-id')
        self.assertEqual(applications[0].incoming_call_url, 'http://callback.info')
        self.assertEqual(applications[0].callback_http_method, 'post')
        self.assertEqual(applications[0].name, 'test_application_name')
        self.assertEqual(applications[0].auto_answer, True)
        self.assertEqual(applications[1].application_id, 'a-application-id1')
        self.assertEqual(applications[1].incoming_call_url, 'http://callback1.info')
        self.assertEqual(applications[1].callback_http_method, 'get')
        self.assertEqual(applications[1].name, 'test_application_name1')
        self.assertEqual(applications[1].auto_answer, False)

    @responses.activate
    def test_create(self):
        """
        Application.create(name='new-application', incoming_call_url='http://test.callback.info')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/applications/new-application-id'})

        application = Application.create(name='new-application', incoming_call_url='http://test.callback.info')

        self.assertEqual(application.application_id, 'new-application-id')
        self.assertEqual(application.incoming_call_url, 'http://test.callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'new-application')
        self.assertEqual(application.auto_answer, True)

    @responses.activate
    def test_create_refresh(self):
        """
        Application.refresh()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/applications/new-application-id'})

        application = Application.create(name='new-application', incoming_call_url='http://test.callback.info')

        self.assertEqual(application.application_id, 'new-application-id')
        self.assertEqual(application.incoming_call_url, 'http://test.callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'new-application')
        self.assertEqual(application.auto_answer, True)

        raw = """
        {
        "id": "new-application-id",
        "callbackHttpMethod": "post",
        "incomingCallUrl": "http://callback.info",
        "name": "test_application_name",
        "autoAnswer": true
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/new-application-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        application.refresh()
        self.assertEqual(application.application_id, 'new-application-id')
        self.assertEqual(application.incoming_call_url, 'http://callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'test_application_name')
        self.assertEqual(application.auto_answer, True)


class AccountTests(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Account.get()
        """
        raw = """
        {
        "balance": "98.75800",
        "accountType": "pre-pay"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/account/',
                      body=raw,
                      status=200,
                      content_type='application/json')
        account = Account.get()
        self.assertEqual(account.balance, "98.75800")
        self.assertEqual(account.account_type, "pre-pay")

    @responses.activate
    def test_get_transactions(self):
        """
        Account.get_transactions()
        """
        raw = """
        [
            {
                "id": "transaction_1",
                "time": "2014-09-15T18:14:08Z",
                "amount": "0.00",
                "type": "charge",
                "units": 12,
                "productType": "toll-free-call-out",
                "number": "+1Number1"
            },
            {
                "id": "transaction_2",
                "time": "2014-09-15T18:14:08Z",
                "amount": "0.00",
                "type": "charge",
                "units": 12,
                "productType": "toll-free-call-in",
                "number": "+1Number2"
            }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/account/transactions',
                      body=raw,
                      status=200,
                      content_type='application/json')
        data = Account.get_transactions()
        self.assertEqual(data[0]['id'], 'transaction_1')
        self.assertIsInstance(data[0]['time'], datetime)
        self.assertEqual(data[1]['id'], 'transaction_2')
        self.assertIsInstance(data[1]['time'], datetime)


class ConferenceTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Conference.get('conf-id')
        """
        raw = """
        {
        "activeMembers": 0,
        "createdTime": "2013-07-12T15:22:47-02",
        "from": "+19703255647",
        "id": "conf-id",
        "state": "created"
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        conf = Conference.get('conf-id')

        self.assertEqual(conf.active_members, 0)
        self.assertEqual(conf.from_, "+19703255647")
        self.assertEqual(conf.id, 'conf-id')
        self.assertEqual(conf.state, 'created')
        self.assertIsInstance(conf.created_time, datetime)

    @responses.activate
    def test_get_members(self):
        """
        Conference('conf-id').get_members()
        """
        raw = """
        [
        {
        "addedTime": "2013-07-12T15:54:47-02",
        "hold": false,
        "id": "{memberId1}",
        "mute": false,
        "state": "active",
        "joinTone": false,
        "leavingTone": false,
        "call": "https://localhost:8444/v1/users/{userId}/calls/{callId1}"
        },
        {
        "addedTime": "2013-07-12T15:55:12-02",
        "hold": false,
        "id": "{memberId2}",
        "mute": false,
        "state": "active",
        "joinTone": false,
        "leavingTone": false,
        "call": "https://localhost:8444/v1/users/{userId}/calls/{callId2}"
        },
        {
        "addedTime": "2013-07-12T15:56:12-02",
        "hold": false,
        "id": "{memberId3}",
        "mute": false,
        "removedTime": "2013-07-12T15:56:59-02",
        "state": "completed",
        "joinTone": false,
        "leavingTone": false,
        "call": "https://localhost:8444/v1/users/{userId}/calls/{callId3}"
        }
        ]
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id/members',
                      body=raw,
                      status=200,
                      content_type='application/json')
        members = Conference('conf-id').get_members()

        self.assertEqual(members[0].id, "{memberId1}")
        self.assertEqual(members[1].id, "{memberId2}")

    @responses.activate
    def test_create(self):
        """
        Conference.create("+1919000001")
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/conferences/new-conf-id'})

        conference = Conference.create("+1919000001", callback_url="http://my.callback.url",
                                       callback_timeout="2000",
                                       fallback_url="http://my.fallback.url")

        self.assertEqual(conference.id, 'new-conf-id')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"callbackTimeout": "2000", "from": "+1919000001", '
                                      '"callbackUrl": "http://my.callback.url", '
                                      '"fallbackUrl": "http://my.fallback.url"}')

    @responses.activate
    def test_play_audio(self):
        """
        Conference('conf-id').play_audio('Hello.mp3')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id/audio',
                      body='',
                      content_type='application/json'
                      )

        Conference('conf-id').play_audio('Hello.mp3', loop_enabled=True, tag='custom_tag')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"loopEnabled": true, "tag": "custom_tag", "fileUrl": "Hello.mp3"}')

    @responses.activate
    def test_stop_audio(self):
        """
        Conference('conf-id').stop_audio()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id/audio',
                      body='',
                      content_type='application/json'
                      )

        Conference('conf-id').stop_audio()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"fileUrl": ""}')

    @responses.activate
    def test_update(self):
        """
        Conference('conf-id').update(state='completed')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id',
                      body='',
                      content_type='application/json'
                      )

        Conference('conf-id').update(state='completed')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"state": "completed"}')

    @responses.activate
    def test_add_member(self):
        """
        Conference('conf-id').add_member(call_id='foo', join_tone=False, leaving_tone=False)
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id/members',
                      body='',
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/conferences/new-conf-id/members/m-id'}
                      )
        member = Conference('conf-id').add_member(call_id='foo', join_tone=False, leaving_tone=False)
        self.assertEqual(member.id, 'm-id')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"joinTone": false, "leavingTone": false, "callId": "foo"}')

    @responses.activate
    def test_get_member(self):
        """
        Conference('conf-id').member('m-id').get()
        """
        raw = """
        {
        "addedTime": "2013-07-12T15:54:47-02",
        "hold": false,
        "id": "m-id",
        "mute": false,
        "state": "active",
        "joinTone": false,
        "leavingTone": false,
        "call": "https://localhost:8444/v1/users/{userId}/calls/{callId1}"
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id/members/m-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        member = Conference('conf-id').member('m-id').get()

        self.assertEqual(member.id, "m-id")
        self.assertEqual(member.hold, False)
        self.assertEqual(member.mute, False)
        self.assertEqual(member.state, "active")
        self.assertEqual(member.join_tone, False)
        self.assertEqual(member.leaving_tone, False)
        self.assertIsInstance(member.added_time, datetime)


class RecordingTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Recording.get('r-id')
        """
        raw = """
        {
          "endTime": "2013-02-08T13:17:12.181Z",
          "id": "r-id",
          "media": "https://api.catapult.inetwork.com/v1/users/u-user-id/media/c-bonay3r4mtwbplurq4nkt7q-1.wav",
          "call": "https://api.catapult.inetwork.com/v1/users/u-user-id/calls/c-call-id",
          "startTime": "2013-02-08T13:15:47.587Z",
          "state": "complete"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/recordings/r-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        recording = Recording.get('r-id')
        self.assertEqual(recording.state, 'complete')
        self.assertEqual(recording.id, 'r-id')
        self.assertEqual(recording.media,
                         'https://api.catapult.inetwork.com/v1/users/u-user-id/media/c-bonay3r4mtwbplurq4nkt7q-1.wav')
        self.assertIsInstance(recording.start_time, datetime)
        self.assertIsInstance(recording.end_time, datetime)
        self.assertIsInstance(recording.call, Call)
        self.assertEqual(recording.call.call_id, 'c-call-id')

    @responses.activate
    def test_list(self):
        """
        Recording.list()
        """
        raw = """
        [
        {
          "endTime": "2013-02-08T13:17:12.181Z",
          "id": "r-id",
          "media": "https://api.catapult.inetwork.com/v1/users/u-user-id/media/c-bonay3r4mtwbplurq4nkt7q-1.wav",
          "call": "https://api.catapult.inetwork.com/v1/users/u-user-id/calls/c-call-id",
          "startTime": "2013-02-08T13:15:47.587Z",
          "state": "complete"
        },
        {
          "id": "r-id2",
          "media": "https://api.catapult.inetwork.com/v1/users/u-user-id/media/c-bonay3r4mtwbplurq4nkt7q-2.wav",
          "call": "https://api.catapult.inetwork.com/v1/users/u-user-id/calls/c-call-id1",
          "startTime": "2013-02-08T13:15:47.587Z",
          "state": "recording"
        }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/recordings',
                      body=raw,
                      status=200,
                      content_type='application/json')
        recordings = Recording.list()
        self.assertEqual(recordings[0].state, 'complete')
        self.assertEqual(recordings[0].id, 'r-id')
        self.assertEqual(recordings[0].media,
                         'https://api.catapult.inetwork.com/v1/users/u-user-id/media/c-bonay3r4mtwbplurq4nkt7q-1.wav')
        self.assertIsInstance(recordings[0].start_time, datetime)
        self.assertIsInstance(recordings[0].end_time, datetime)
        self.assertIsInstance(recordings[0].call, Call)
        self.assertEqual(recordings[0].call.call_id, 'c-call-id')
        self.assertEqual(recordings[1].state, 'recording')
        self.assertEqual(recordings[1].id, 'r-id2')
        self.assertEqual(recordings[1].media,
                         'https://api.catapult.inetwork.com/v1/users/u-user-id/media/c-bonay3r4mtwbplurq4nkt7q-2.wav')
        self.assertIsInstance(recordings[1].start_time, datetime)
        self.assertIsNone(recordings[1].end_time)
        self.assertIsInstance(recordings[1].call, Call)
        self.assertEqual(recordings[1].call.call_id, 'c-call-id1')

    @responses.activate
    def test_get_media_url(self):
        """
        Recording.get('r-id').get_media_file()
        """
        raw = """
        {
          "endTime": "2013-02-08T13:17:12.181Z",
          "id": "r-id",
          "media": "https://api.catapult.inetwork.com/v1/users/u-user-id/media/file.wav",
          "call": "https://api.catapult.inetwork.com/v1/users/u-user-id/calls/c-call-id",
          "startTime": "2013-02-08T13:15:47.587Z",
          "state": "complete"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/recordings/r-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        recording = Recording.get('r-id')
        raw = b'testrecordingcontent'
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user-id/media/file.wav',
                      body=raw,
                      status=200,
                      content_type='audio/wav')
        getted_data = recording.get_media_file()
        self.assertEqual(getted_data[1], 'audio/wav')
        self.assertIsInstance(getted_data[0], six.binary_type)
