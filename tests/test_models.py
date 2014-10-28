import six

import responses
import unittest

from bandwidth_sdk import (Call, Bridge,
                           AppPlatformError, Application,
                           Account, Conference, Recording, ConferenceMember,
                           Gather, PhoneNumber, Media, Message, UserError)
from datetime import datetime

from .utils import SdkTestCase


def assertJsonEq(first, second, msg='Ouups'):
    assert sorted(first) == sorted(second), '%r != %r\n%s' % (first, second, msg)


def in_bytes(string):
    if isinstance(string, six.binary_type):
        return string
    elif isinstance(string, six.string_types):
        if six.PY3:
            return bytes(string, encoding='ascii')
        return string
    raise ValueError


class CallsTest(SdkTestCase):

    def test_bad_init(self):
        with self.assertRaises(TypeError):
            Call(['data'])

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
    def test_set_call_property(self):
        """
        Call(dict(id='new-call-id', recording_enabled=True)).set_call_property(recording_enabled=False)
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id',
                      body='',
                      status=200,
                      content_type='application/json',
                      )
        call = Call(dict(id='new-call-id', recording_enabled=True))
        self.assertEqual(call.call_id, 'new-call-id')
        self.assertTrue(call.recording_enabled)

        call = call.set_call_property(recording_enabled=False)
        self.assertFalse(call.recording_enabled)

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
    def test_get_recording(self):
        """
        Call('new-call-id').get_recordings()
        """
        raw = """
        [{
        "endTime": "2013-02-08T12:06:55.007Z",
        "id": "rec-1",
        "media": "https://.../v1/users/.../media/{callId}-1.wav",
        "call": "https://.../v1/users/.../calls/{callId}",
        "startTime": "2013-02-08T12:05:17.807Z",
        "state": "complete"
        },
        {
        "endTime": "2013-02-08T13:15:55.887Z",
        "id": "rec-2",
        "media": "https://.../v1/users/.../media/{callId}-2.wav",
        "call": "https://.../v1/users/.../calls/{callId}",
        "startTime": "2013-02-08T13:15:45.887Z",
        "state": "complete"
        }]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/recordings',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        recordings = Call('new-call-id').get_recordings()
        self.assertEqual(len(recordings), 2)

        record = recordings[0]

        self.assertEqual(record.id, 'rec-1')
        self.assertEqual(record.state, 'complete')

    @responses.activate
    def test_bridge_from_call(self):
        """
        Call('c-foo').bridge(Call('c-bar'))
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/bridges/new-bridge-id'})

        bridge = Call('c-foo').bridge(Call('c-bar'))
        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'new-bridge-id')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"callIds": ["c-foo", "c-bar"]}')

        self.assertEqual(bridge.call_ids, ["c-foo", "c-bar"])

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

    @responses.activate
    def test_gather_stop(self):
        """
        Gather(call_id='test_call_id').stop()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/test_call_id/gather/g-foo',
                      body='',
                      status=200,
                      content_type='application/json',
                      )
        gather = Gather(call_id='test_call_id')
        gather.id = 'g-foo'
        gather.stop()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"state": "completed"}')

    @responses.activate
    def test_gather_stop_failed(self):
        """
        Gather(call_id='test_call_id').stop()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/test_call_id/gather/g-foo',
                      body='',
                      status=200,
                      content_type='application/json',
                      )
        gather = Gather(call_id='test_call_id')
        with self.assertRaises(AssertionError):
            gather.stop()


class BridgesTest(SdkTestCase):

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
        self.assertEqual(bridge.call_ids, [])

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
    def test_fetch_calls(self):
        """
        Bridge('b-id').fetch_calls()
        """
        raw = """
        [
        {
        "activeTime": "2013-05-22T19:49:39Z",
        "direction": "out",
        "from": "+1919000001",
        "id": "c-xx",
        "bridgeId": "b-id",
        "startTime": "2013-05-22T19:49:35Z",
        "state": "active",
        "to": "+1919000002",
        "recordingEnabled": false,
        "events": "https://api.catapult.inetwork.com/v1/users/{userId}/calls/{callId1}/events",
        "bridge": "https://api.catapult.inetwork.com/v1/users/{userId}/bridges/{bridgeId}"
        },
        {
        "activeTime": "2013-05-22T19:50:16Z",
        "direction": "out",
        "from": "+1919000003",
        "id": "c-yy",
        "bridgeId": "b-id",
        "startTime": "2013-05-22T19:50:16Z",
        "state": "active",
        "to": "+1919000004",
        "recordingEnabled": false,
        "events": "https://api.catapult.inetwork.com/v1/users/{userId}/calls/{callId2}/events",
        "bridge": "https://api.catapult.inetwork.com/v1/users/{userId}/bridges/{bridgeId}"
        }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/b-id/calls',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        bridge = Bridge('b-id')
        calls = bridge.fetch_calls()

        call = calls[0]

        self.assertIsInstance(call, Call)
        self.assertEqual(call.call_id, 'c-xx')
        self.assertEqual(call.bridge_id, 'b-id')

        call = calls[1]
        self.assertIsInstance(call, Call)
        self.assertEqual(call.call_id, 'c-yy')
        self.assertEqual(call.bridge_id, 'b-id')

        self.assertEqual(bridge.call_ids, ['c-xx', 'c-yy'])

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


class ApplicationsTest(SdkTestCase):

    def test_bad_init(self):
        with self.assertRaises(TypeError):
            Application(['wrong_data'])

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

        self.assertEqual(application.id, 'a-application-id')
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

        self.assertEqual(applications[0].id, 'a-application-id')
        self.assertEqual(applications[0].incoming_call_url, 'http://callback.info')
        self.assertEqual(applications[0].callback_http_method, 'post')
        self.assertEqual(applications[0].name, 'test_application_name')
        self.assertEqual(applications[0].auto_answer, True)
        self.assertEqual(applications[1].id, 'a-application-id1')
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

        self.assertEqual(application.id, 'new-application-id')
        self.assertEqual(application.incoming_call_url, 'http://test.callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'new-application')
        self.assertEqual(application.auto_answer, True)

    @responses.activate
    def test_patch(self):
        """
        Application('new-application').patch(incoming_call_url='http://test.callback.info')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/new-application',
                      body='',
                      status=200,
                      content_type='application/json')

        application = Application('new-application')
        self.assertEqual(application.id, 'new-application')
        self.assertIsNone(application.incoming_call_url)
        self.assertEqual(application.callback_http_method, 'post')

        application.patch(incoming_call_url='http://test.callback.info',
                          callback_http_method='get')
        self.assertEqual(application.incoming_call_url, 'http://test.callback.info')
        self.assertEqual(application.callback_http_method, 'get')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"callbackHttpMethod": "get", "incomingCallUrl": "http://test.callback.info"}')

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

        self.assertEqual(application.id, 'new-application-id')
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
        self.assertEqual(application.id, 'new-application-id')
        self.assertEqual(application.incoming_call_url, 'http://callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'test_application_name')
        self.assertEqual(application.auto_answer, True)

    @responses.activate
    def test_delete_application(self):
        """
        Application('app-id').delete()
        """
        responses.add(responses.DELETE,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/app-id',
                      body='',
                      status=200,
                      content_type='application/json')
        app = Application('app-id')
        d_app = app.delete()
        self.assertTrue(d_app)
        self.assertEquals(responses.calls[0].request.method, 'DELETE')
        self.assertEquals(responses.calls[0].request.url.split('/')[-1], app.id)


class AccountTests(SdkTestCase):

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


class ConferenceTest(SdkTestCase):

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

    @responses.activate
    def test_update_member(self):
        """
        Conference('conf-id').member('m-id').update(mute=True, hold=True)
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

        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/conferences/conf-id/members/m-id',
                      body='',
                      status=200,
                      content_type='application/json')

        member.update(mute=True, hold=True)

        request_message = responses.calls[1].request.body
        assertJsonEq(request_message, '{"hold": true, "mute": true}')
        self.assertTrue(member.hold)
        self.assertTrue(member.mute)

    @responses.activate
    def test_conf_member_audio_url(self):
        """
        Conference('conf-id').member('m-id').get().get_audio_url()
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
        a_url = member.get_audio_url()
        self.assertEqual(a_url, 'conferences/conf-id/members/m-id/audio')


class RecordingTest(SdkTestCase):

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


class PhoneNumberTest(SdkTestCase):

    @responses.activate
    def test_phone_number_get(self):
        """
        PhoneNumber.get('numb-id')
        """
        raw = """
        {
           "id": "numb-id",
           "application": "https://catapult.inetwork.com/v1/users/u-user/applications/a-j321",
           "number":"+12323232",
           "nationalNumber":"(232) 3232",
           "name": "home phone",
           "createdTime": "2013-02-13T17:46:08.374Z",
           "state": "NC",
           "price": "0.60",
           "numberState": "enabled"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers/numb-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        number = PhoneNumber.get('numb-id')
        self.assertEqual(number.id, 'numb-id')
        self.assertIsInstance(number.application, Application)
        self.assertEqual(number.application.id, 'a-j321')
        self.assertEqual(number.number, '+12323232')
        self.assertEqual(number.national_number, '(232) 3232')
        self.assertEqual(number.name, 'home phone')
        self.assertEqual(number.state, 'NC')
        self.assertEqual(number.number_state, 'enabled')
        self.assertEqual(number.price, '0.60')
        self.assertIsInstance(number.created_time, datetime)

    @responses.activate
    def test_refresh_number(self):
        """
        number = PhoneNumber('numb-id')
        number.refresh()
        """
        raw = """
        {
           "id": "numb-id",
           "application": "https://catapult.inetwork.com/v1/users/u-user/applications/a-j321",
           "number":"+12323232",
           "nationalNumber":"(232) 3232",
           "name": "home phone",
           "createdTime": "2013-02-13T17:46:08.374Z",
           "state": "NC",
           "price": "0.60",
           "numberState": "enabled"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers/numb-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        number = PhoneNumber('numb-id')
        number.refresh()
        self.assertEqual(number.id, 'numb-id')
        self.assertIsInstance(number.application, Application)
        self.assertEqual(number.application.id, 'a-j321')
        self.assertEqual(number.number, '+12323232')
        self.assertEqual(number.national_number, '(232) 3232')
        self.assertEqual(number.name, 'home phone')
        self.assertEqual(number.state, 'NC')
        self.assertEqual(number.number_state, 'enabled')
        self.assertEqual(number.price, '0.60')
        self.assertIsInstance(number.created_time, datetime)

    @responses.activate
    def test_phone_number_list(self):
        """
        PhoneNumber.list()
        """
        raw = """
        [
        {
           "id": "numb-id",
           "application": "https://catapult.inetwork.com/v1/users/u-user/applications/a-j321",
           "number":"+123456789",
           "nationalNumber":"(234) 56789",
           "name": "home phone",
           "createdTime": "2013-02-13T17:46:08.374Z",
           "state": "NC",
           "price": "0.60",
           "numberState": "enabled"
        },
        {
           "id": "numb-id2",
           "application": "https://catapult.inetwork.com/v1/users/u-user/applications/a-j322",
           "number":"+1987654321",
           "nationalNumber":"(987) 7654321",
           "name": "work phone",
           "createdTime": "2013-02-13T18:32:05.223Z",
           "state": "NC",
           "price": "0.60",
           "numberState": "enabled"
        }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers',
                      body=raw,
                      status=200,
                      content_type='application/json')
        numbers = PhoneNumber.list()
        self.assertEqual(numbers[0].id, 'numb-id')
        self.assertIsInstance(numbers[0].application, Application)
        self.assertEqual(numbers[0].application.id, 'a-j321')
        self.assertEqual(numbers[0].number, '+123456789')
        self.assertEqual(numbers[0].national_number, '(234) 56789')
        self.assertEqual(numbers[0].name, 'home phone')
        self.assertEqual(numbers[0].number_state, 'enabled')
        self.assertEqual(numbers[0].price, '0.60')
        self.assertEqual(numbers[0].state, 'NC')
        self.assertIsInstance(numbers[0].created_time, datetime)
        self.assertEqual(numbers[1].id, 'numb-id2')
        self.assertIsInstance(numbers[1].application, Application)
        self.assertEqual(numbers[1].application.id, 'a-j322')
        self.assertEqual(numbers[1].number, '+1987654321')
        self.assertEqual(numbers[1].national_number, '(987) 7654321')
        self.assertEqual(numbers[1].name, 'work phone')
        self.assertEqual(numbers[1].number_state, 'enabled')
        self.assertEqual(numbers[1].price, '0.60')
        self.assertEqual(numbers[1].state, 'NC')
        self.assertIsInstance(numbers[1].created_time, datetime)

    @unittest.skip('as_iterator commented')
    @responses.activate
    def test_phone_number_as_iterator(self):
        """
        PhoneNumber.as_iterator()
        """
        page_1 = """
        [
        {
           "id": "numb-id-1",
           "number":"+1987000001"
        },
        {
           "id": "numb-id2",
           "number":"+1987000002"
        }
        ]
        """

        page_2 = """
        [
        {
           "id": "numb-id3",
           "number":"+1987000003"
        },
        {
           "id": "numb-id2",
           "number":"+1987000004"
        }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers?size=100&page=0',
                      body=page_1,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers?size=100&page=1',
                      body=page_2,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)

        numbers = PhoneNumber.as_iterator()
        numbers_list = list(numbers)

        self.assertEqual(len(numbers_list), 4)

        self.assertEqual(numbers_list[0].number, "+1987000001")
        self.assertEqual(numbers_list[1].number, "+1987000002")
        self.assertEqual(numbers_list[2].number, "+1987000003")
        self.assertEqual(numbers_list[3].number, "+1987000004")

    @responses.activate
    def test_get_number_info(self):
        """
        PhoneNumber.get_number_info('+19195551212')
        """
        raw = """
        {
        "id": "n-numb-id",
        "application": "https://catapult.inetwork.com/v1/users/u-user/applications/a-j322",
        "number":"+19195551212",
        "nationalNumber":"(919) 555-1212",
        "name": "home phone",
        "createdTime": "2013-02-13T17:46:08.374Z",
        "state": "NC",
        "price": "0.60",
        "numberState": "enabled"
         }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers/%2B19195551212',
                      body=raw,
                      status=200,
                      content_type='application/json')
        PhoneNumber.get_number_info('+19195551212')

    @responses.activate
    def test_patch_phone_number(self):
        """
        PhoneNumber('phone-id').patch(
            application=Application('app-id'), name='home phone')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers/phone-id',
                      body='',
                      status=200,
                      content_type='application/json')
        phone = PhoneNumber('phone-id')
        self.assertEqual(phone.id, 'phone-id')
        self.assertIsNone(phone.application)

        phone = phone.patch(application=Application('app-id'), name='home phone')

        self.assertEqual(phone.id, 'phone-id')
        self.assertIsInstance(phone.application, Application)
        self.assertEqual(phone.application.id, 'app-id')
        self.assertEqual(phone.name, 'home phone')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"name": "home phone", '
                                      '"applicationId": "app-id"}')

    @responses.activate
    def test_patch_phone_number_with_app_id(self):
        """
        PhoneNumber('phone-id').patch(
            application='app-id', name='home phone')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers/phone-id',
                      body='',
                      status=200,
                      content_type='application/json')
        phone = PhoneNumber('phone-id')
        self.assertEqual(phone.id, 'phone-id')
        self.assertIsNone(phone.application)

        phone = phone.patch(application='app-id', name='home phone')

        self.assertEqual(phone.id, 'phone-id')
        self.assertIsInstance(phone.application, Application)
        self.assertEqual(phone.application.id, 'app-id')
        self.assertEqual(phone.name, 'home phone')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"name": "home phone", '
                                      '"applicationId": "app-id"}')

    @responses.activate
    def test_delete_phone_number(self):
        """
        PhoneNumber('phone-id').delete()
        """
        responses.add(responses.DELETE,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers/phone-id',
                      body='',
                      status=200,
                      content_type='application/json')
        phone = PhoneNumber('phone-id')
        phone.delete()
        self.assertEquals(responses.calls[0].request.method, 'DELETE')
        self.assertEquals(responses.calls[0].request.url.split('/')[-1], phone.id)

    @responses.activate
    def test_allocate_phone_number_by_number_with_app_instance(self):
        """
        PhoneNumber.allocate(number='+19195551212', application=Application('app-id'))
        application as Application instance
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/phoneNumber/new-number-id'})
        application = Application({'id': 'app-id', 'incoming_call_url': 'http://callback.info'})
        number = PhoneNumber({'number': '+19195551212'}).allocate(application=application)
        self.assertEqual(number.id, 'new-number-id')
        self.assertEqual(number.number, '+19195551212')
        self.assertEqual(number.application.id, 'app-id')
        self.assertEqual(number.application.incoming_call_url, 'http://callback.info')

    @responses.activate
    def test_allocate_number_with_app_id_as_string(self):
        """
        PhoneNumber.allocate(number='+19195551212', application='app-id')
        id of application as string
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/phoneNumber/new-number-id'})
        application = 'app-id'
        number = PhoneNumber({'number': '+19195551212'}).allocate(application=application)
        self.assertEqual(number.id, 'new-number-id')
        self.assertEqual(number.number, '+19195551212')
        self.assertEqual(number.application.id, 'app-id')

    @responses.activate
    def test_list_local(self):
        """
        PhoneNumber.list_local(city='Cary', state='NC', pattern='*2%3F9*', quantity=2)
        """
        raw = """[
          {
            "number": "ava-1",
            "nationalNumber": "(919) 323-2393",
            "patternMatch": "          2 9 ",
            "city": "CARY",
            "lata": "426",
            "rateCenter": "CARY",
            "state": "NC",
            "price": "0.60"
          },
          {
            "number": "ava-2",
            "nationalNumber": "(919) 323-2394",
            "patternMatch": "          2 9 ",
            "city": "CARY",
            "lata": "426",
            "rateCenter": "CARY",
            "state": "NC",
            "price": "0.60"
          }
        ]
        """
        responses.add(responses.GET,
                      url='https://api.catapult.inetwork.com/v1/availableNumbers/local',
                      body=raw,
                      status=200,
                      content_type='application/json')
        a_numbers = PhoneNumber.list_local(city='Cary', state='NC', pattern='*2?9*', quantity=2)
        self.assertIsInstance(a_numbers[0], PhoneNumber)
        self.assertEqual(a_numbers[0].number, 'ava-1')
        self.assertEqual(a_numbers[0].national_number, '(919) 323-2393')
        self.assertEqual(a_numbers[0].pattern_match, '          2 9 ')
        self.assertEqual(a_numbers[0].city, 'CARY')
        self.assertEqual(a_numbers[0].lata, '426')
        self.assertEqual(a_numbers[0].rate_center, 'CARY')
        self.assertEqual(a_numbers[0].number_state, 'NC')
        self.assertEqual(a_numbers[0].price, '0.60')

        self.assertIsInstance(a_numbers[1], PhoneNumber)
        self.assertEqual(a_numbers[1].number, 'ava-2')
        self.assertEqual(a_numbers[1].national_number, '(919) 323-2394')
        self.assertEqual(a_numbers[1].pattern_match, '          2 9 ')
        self.assertEqual(a_numbers[1].city, 'CARY')
        self.assertEqual(a_numbers[1].lata, '426')
        self.assertEqual(a_numbers[1].rate_center, 'CARY')
        self.assertEqual(a_numbers[1].number_state, 'NC')
        self.assertEqual(a_numbers[1].price, '0.60')

    @responses.activate
    def test_list_toll_free(self):
        """
        PhoneNumber.list_tollfree(quantity=2, pattern='*2?9*')

        """
        raw = """
        [
          {
            "number":"toll-free-numb1",
            "nationalNumber":"(919) 323-2393",
            "patternMatch":"        2 9 ",
            "price":"2.00"
          },
          {
            "number":"toll-free-numb2",
            "nationalNumber":"(919) 323-2394",
            "patternMatch":"          2 9 ",
            "price":"2.00"
          }
        ]
        """
        responses.add(responses.GET,
                      url='https://api.catapult.inetwork.com/v1/availableNumbers/tollFree',
                      body=raw,
                      status=200,
                      content_type='application/json')
        t_free_numbers = PhoneNumber.list_tollfree(quantity=2, pattern='*2?9*')
        self.assertIsInstance(t_free_numbers[0], PhoneNumber)
        self.assertEqual(t_free_numbers[0].number, 'toll-free-numb1')
        self.assertEqual(t_free_numbers[0].national_number, '(919) 323-2393')
        self.assertEqual(t_free_numbers[0].pattern_match, '        2 9 ')
        self.assertEqual(t_free_numbers[0].price, '2.00')

        self.assertIsInstance(t_free_numbers[1], PhoneNumber)
        self.assertEqual(t_free_numbers[1].number, 'toll-free-numb2')
        self.assertEqual(t_free_numbers[1].national_number, '(919) 323-2394')
        self.assertEqual(t_free_numbers[1].pattern_match, '          2 9 ')
        self.assertEqual(t_free_numbers[1].price, '2.00')

    @responses.activate
    def test_batch_allocate_local(self):
        """
        PhoneNumber.batch_allocate_local(city='Cary', state='NC', quantity=2)
        """
        raw = """
        [
            {
                "number": "+19191919191",
                "nationalNumber": "(919) 191-9191",
                "price": "0.60",
                "location": "https://.../v1/users/u-user/phoneNumber/new-number-id"
            },
            {
                "number": "+19191919192",
                "nationalNumber": "(919) 191-9192",
                "price": "0.80",
                "location": "https://.../v1/users/u-user/phoneNumber/new-number-id2"
            }
        ]
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/availableNumbers/local',
                      body=raw,
                      status=201,
                      content_type='application/json')
        numbers = PhoneNumber.batch_allocate_local(city='Cary', state='NC', quantity=2)

        self.assertIsInstance(numbers[0], PhoneNumber)
        self.assertEqual(numbers[0].id, 'new-number-id')
        self.assertEqual(numbers[0].number, '+19191919191')
        self.assertEqual(numbers[0].national_number, '(919) 191-9191')
        self.assertEqual(numbers[0].price, '0.60')

        self.assertIsInstance(numbers[1], PhoneNumber)
        self.assertEqual(numbers[1].id, 'new-number-id2')
        self.assertEqual(numbers[1].number, '+19191919192')
        self.assertEqual(numbers[1].national_number, '(919) 191-9192')
        self.assertEqual(numbers[1].price, '0.80')

    @responses.activate
    def test_batch_allocate_tollfree(self):
        """
        PhoneNumber.batch_allocate_tollfree(quantity=2)
        """
        raw = """
        [
            {
                "number": "+19191919191",
                "nationalNumber": "(919) 191-9191",
                "price": "2.00",
                "location": "https://.../v1/users/u-user/phoneNumber/new-number-id"
            },
            {
                "number": "+19191919192",
                "nationalNumber": "(919) 191-9192",
                "price": "2.00",
                "location": "https://.../v1/users/u-user/phoneNumber/new-number-id2"
            }
        ]
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/availableNumbers/tollFree',
                      body=raw,
                      status=201,
                      content_type='application/json')
        numbers = PhoneNumber.batch_allocate_tollfree(quantity=2)

        self.assertIsInstance(numbers[0], PhoneNumber)
        self.assertEqual(numbers[0].id, 'new-number-id')
        self.assertEqual(numbers[0].number, '+19191919191')
        self.assertEqual(numbers[0].national_number, '(919) 191-9191')
        self.assertEqual(numbers[0].price, '2.00')

        self.assertIsInstance(numbers[1], PhoneNumber)
        self.assertEqual(numbers[1].id, 'new-number-id2')
        self.assertEqual(numbers[1].number, '+19191919192')
        self.assertEqual(numbers[1].national_number, '(919) 191-9192')
        self.assertEqual(numbers[1].price, '2.00')

    @responses.activate
    def test_allocate_available_number(self):
        """

        a_number = PhoneNumber.list_tollfree(quantity=2);
        a_number.allocate(application=Application('app-id'))
        """
        raw = """
        [
            {
                "number": "+19191919191",
                "nationalNumber": "(919) 191-9191",
                "price": "2.00",
                "location": "https://.../v1/users/u-user/phoneNumber/new-number-id"
            },
            {
                "number": "+19191919192",
                "nationalNumber": "(919) 191-9192",
                "price": "2.00",
                "location": "https://.../v1/users/u-user/phoneNumber/new-number-id2"
            }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/availableNumbers/tollFree',
                      body=raw,
                      status=200,
                      content_type='application/json')
        av_number = PhoneNumber.list_tollfree(quantity=2)[0]
        self.assertIsInstance(av_number, PhoneNumber)
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/phoneNumbers',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/phoneNumber/new-number-id'})
        application = Application({'id': 'app-id', 'incoming_call_url': 'http://callback.info'})
        number = av_number.allocate(application=application)
        self.assertIsInstance(number, PhoneNumber)
        self.assertEqual(number.id, 'new-number-id')
        self.assertEqual(number.number, '+19191919191')
        self.assertEqual(number.application.id, 'app-id')
        self.assertEqual(number.application.incoming_call_url, 'http://callback.info')


class CommonTest(SdkTestCase):
    """
    Account
    Application
    Bridge
    Call
    Conference
    ConferenceMember
    Gather
    Recording
    """

    def test_account_repr_not_failed(self):
        """
        Test Account representation
        """
        self.assertIsInstance(repr(Account()), six.string_types)

    def test_application_repr_not_failed(self):
        """
        Test Application representation
        """
        self.assertIsInstance(repr(Application('id')), six.string_types)

    def test_bridge_repr_not_failed(self):
        """
        Test Bridge representation
        """
        self.assertIsInstance(repr(Bridge('id')), six.string_types)

    def test_call_repr_not_failed(self):
        """
        Test Call representation
        """
        self.assertIsInstance(repr(Call('id')), six.string_types)

    def test_conference_repr_not_failed(self):
        """
        Test conference representation
        """
        self.assertIsInstance(repr(Conference('id')), six.string_types)

    def test_conferencemember_repr_not_failed(self):
        """
        Test ConferenceMember representation
        """
        self.assertIsInstance(repr(ConferenceMember('id', {'id': 'id'})), six.string_types)

    def test_gather_repr_not_failed(self):
        """
        Test Gather representation
        """
        self.assertIsInstance(repr(Gather('id')), six.string_types)

    def test_recording_repr_not_failed(self):
        """
        Test Recording representation
        """
        self.assertIsInstance(repr(Recording('id')), six.string_types)

    def test_message_repr_not_failed(self):
        """
        Test Message representation
        """
        self.assertIsInstance(repr(Message({'id': None, 'state': Message.STATES.error})), six.string_types)


class MediaTest(SdkTestCase):

    @responses.activate
    def test_list(self):
        """
        Media.list()
        """
        raw = """
        [
        {
         "contentLength": 561276,
         "mediaName": "one",
         "content": "https://catapult.inetwork.com/v1/users/users/{userId}/media/one"
        },
        {
         "contentLength": 2703360,
         "mediaName": "{mediaName2}",
         "content": "https://catapult.inetwork.com/v1/users/users/{userId}/media/two"
        },
        {
         "contentLength": 588,
         "mediaName": "{mediaName3}",
         "content": "https://catapult.inetwork.com/v1/users/users/{userId}/media/tree"
        }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media',
                      body=raw,
                      status=200,
                      content_type='application/json')

        medias = Media.list()

        media = medias[0]

        self.assertIsInstance(media, Media)
        self.assertEqual(media.media_name, 'one')
        self.assertEqual(media.content_length, 561276)

        self.assertEqual(str(media), 'Media(one)')

    @responses.activate
    def test_download(self):
        """
        Media('media-id').download()
        """
        raw = b'testrecordingcontent'
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/media-id',
                      body=raw,
                      status=200,
                      content_type='audio/wav')

        content, mime = Media('media-id').download()
        self.assertEqual(mime, 'audio/wav')
        self.assertIsInstance(content, six.binary_type)
        self.assertEqual(content, raw)

    @responses.activate
    def test_delete(self):
        """
        Media('media-id').delete()
        """
        responses.add(responses.DELETE,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/media-id',
                      body='',
                      status=200,
                      content_type='application/json')
        media = Media('media-id')
        media.delete()
        self.assertEquals(responses.calls[0].request.method, 'DELETE')
        self.assertEquals(responses.calls[0].request.url.split('/')[-1], media.media_name)

    @responses.activate
    def test_by_upload_file_name(self):
        """
        Media.upload('dolphin.mp3', file_path='./tests/fixtures/dolphin.mp3')
        """
        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/dolphin.mp3',
                      body='',
                      status=200,
                      )

        Media.upload('dolphin.mp3', file_path='./tests/fixtures/dolphin.mp3',
                     mime='application/octet-stream')
        request_message = responses.calls[0].request.body  # decoded to str implicitly
        self.assertEqual(request_message, in_bytes('thra\ntata\nrata'))

        self.assertEqual(Media('media-id').get_full_media_url(), 'https://api.catapult.inetwork.com/v1/users/'
                                                                 'u-user/media/media-id')

    @responses.activate
    def test_by_upload_file_name_unencoded(self):
        """
        Media.upload('chunk.mp3', file_path='./tests/fixtures/chunk.mp3')
        """
        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/chunk.mp3',
                      body='',
                      status=200,
                      )

        Media.upload('chunk.mp3', file_path='./tests/fixtures/chunk.mp3',
                     mime='application/octet-stream')
        request_message = responses.calls[0].request.body  # decoded to str implicitly
        self.assertEqual(len(request_message), 4546)

        self.assertEqual(Media('media-id').get_full_media_url(), 'https://api.catapult.inetwork.com/v1/users/'
                                                                 'u-user/media/media-id')

    @unittest.expectedFailure
    @responses.activate
    def test_by_upload_file_name_fail(self):
        """
        Bad file name: Media('media-id').upload('dolphin.mp3', file_path='./tests/fixtures/')
        """
        Media.upload('dolphin.mp3', file_path='./tests/fixtures/')

    @responses.activate
    def test_by_upload_content(self):
        """
        Media.upload('dolphin.mp3', content=b'lalalala')
        """
        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/dolphin.mp3',
                      body='',
                      status=200,
                      )
        content_line = in_bytes('lalalala')
        Media.upload('dolphin.mp3', content=content_line, mime='application/octet-stream')
        request_message = responses.calls[0].request.body  # decoded to str implicitly
        self.assertEqual(request_message, content_line)

        request_headers = responses.calls[0].request.headers
        self.assertEqual(request_headers['Content-Length'], '8')
        self.assertEqual(request_headers['Content-type'], 'application/octet-stream')

    @unittest.expectedFailure
    @responses.activate
    def test_by_upload_content_encoding(self):
        """
        Bad content encoding Media('media-id').upload('dolphin.mp3', content=u'lalalala')
        """
        content_line = u'lalalala'
        Media.upload('dolphin.mp3', content=content_line)

    @responses.activate
    def test_by_upload_from_fd(self):
        """
        Media.upload('dolphin.mp3', fd=open('./tests/fixtures/dolphin.mp3'))
        """
        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/dolphin.mp3',
                      body='',
                      status=200,
                      )

        with open('./tests/fixtures/dolphin.mp3') as fd:
            Media.upload('dolphin.mp3', fd=fd)

        request_message = responses.calls[0].request.body  # decoded to str implicitly
        self.assertEqual(request_message, 'thra\ntata\nrata')

        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/dolphin.mp3',
                      body='',
                      status=200,
                      )

        file_like = six.StringIO('thra\ntata\nrata')
        Media.upload('dolphin.mp3', fd=file_like, mime='application/octet-stream')

        request_message = responses.calls[1].request.body  # decoded to str implicitly
        self.assertEqual(request_message, 'thra\ntata\nrata')

        request_headers = responses.calls[1].request.headers
        self.assertEqual(request_headers['Content-Length'], '14')
        self.assertEqual(request_headers['Content-type'], 'application/octet-stream')

    @responses.activate
    def test_by_upload_file_seek(self):
        """
        Seek to EOF Media.upload('dolphin.mp3', fd=open('./tests/fixtures/dolphin.mp3'))
        """
        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/dolphin.mp3',
                      body='',
                      status=200,
                      )

        with open('./tests/fixtures/dolphin.mp3') as fd:
            fd.seek(14)
            Media('media-id').upload('dolphin.mp3', fd=fd)

        request_message = responses.calls[0].request.body  # decoded to str implicitly
        self.assertEqual(request_message, 'thra\ntata\nrata')

        request_headers = responses.calls[0].request.headers
        self.assertEqual(request_headers['Content-Length'], '14')

    @unittest.expectedFailure
    @responses.activate
    def test_by_upload_file_closed(self):
        """
        Closed fd Media.upload('dolphin.mp3', fd=open('./tests/fixtures/dolphin.mp3'))
        """
        responses.add(responses.PUT,
                      'https://api.catapult.inetwork.com/v1/users/u-user/media/dolphin.mp3',
                      body='',
                      status=200,
                      )

        fd = open('./tests/fixtures/dolphin.mp3')
        fd.close()
        Media.upload('dolphin.mp3', fd=fd)


class MessageTestCase(SdkTestCase):

    @responses.activate
    def test_message_get(self):
        """
        Messages.get('message-id')
        """
        raw = """
            {
          "id": "message-id",
          "messageId": "message-id",
          "from": "+191912345678",
          "to": "+19199876543",
          "text": "Good morning, this is a test message",
          "time": "2012-10-05T20:37:38.048Z",
          "direction": "out",
          "state": "sent",
          "callbackUrl": "http://my.callback.url"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/messages/message-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        message = Message.get('message-id')
        self.assertIsInstance(message, Message)
        self.assertEqual(message.id, 'message-id')
        self.assertEqual(message.from_, '+191912345678')
        self.assertEqual(message.to, '+19199876543')
        self.assertEqual(message.text, 'Good morning, this is a test message')
        self.assertIsInstance(message.time, datetime)
        self.assertEqual(message.direction, 'out')
        self.assertEqual(message.state, Message.STATES.sent)
        self.assertEqual(message.callback_url, 'http://my.callback.url')

    @responses.activate
    def test_list_messages(self):
        """
        Messages.list(sender='+19796543211', receiver='+19796543212')
        """
        raw = """
        [
          {
            "id": "mess-id1",
            "messageId": "mess-id1",
            "from": "+19796543211",
            "to": "+19796543212",
            "text": "Good morning, this is a test message",
            "time": "2012-10-05T20:37:38.048Z",
            "direction": "out",
            "state": "sent"
          },
          {
            "id": "mess-id2",
            "messageId": "mess-id2",
            "from": "+19796543211",
            "to": "+19796543212",
            "text": "I received your test message",
            "time": "2012-10-05T20:38:11.023Z",
            "direction": "in",
            "state": "sent"
          }
        ]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/messages',
                      body=raw,
                      status=200,
                      content_type='application/json')
        messages = Message.list(sender='+19796543211', receiver='+19796543212')
        self.assertIsInstance(messages[0], Message)
        self.assertEqual(messages[0].id, 'mess-id1')
        self.assertEqual(messages[0].from_, '+19796543211')
        self.assertEqual(messages[0].to, '+19796543212')
        self.assertEqual(messages[0].text, 'Good morning, this is a test message')
        self.assertIsInstance(messages[0].time, datetime)
        self.assertEqual(messages[0].direction, 'out')
        self.assertEqual(messages[0].state, Message.STATES.sent)
        self.assertIsInstance(messages[1], Message)
        self.assertEqual(messages[1].id, 'mess-id2')
        self.assertEqual(messages[1].from_, '+19796543211')
        self.assertEqual(messages[1].to, '+19796543212')
        self.assertEqual(messages[1].text, 'I received your test message')
        self.assertIsInstance(messages[1].time, datetime)
        self.assertEqual(messages[1].direction, 'in')
        self.assertEqual(messages[1].state, Message.STATES.sent)

    @responses.activate
    def test_send_message(self):
        """
        Message.send(sender='+19796543211',
                     receiver='+19796543212',
                     text='Good morning,
                     this is a test message',
                     tag='test tag')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/messages',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/messages/new-mess-id'})
        number = PhoneNumber({'id': 'phone_id', 'number': '+19796543211'})
        message = Message.send(sender=number,
                               receiver='+19796543212',
                               text='Good morning, '
                                    'this is a test message',
                               tag='test tag')
        self.assertIsInstance(message, Message)
        self.assertEqual(message.id, 'new-mess-id')
        self.assertEqual(message.from_, '+19796543211')
        self.assertEqual(message.text, 'Good morning, this is a test message')
        self.assertEqual(message.tag, 'test tag')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"to": "+19796543212", "from": "+19796543211", '
                                      '"text": "Good morning, this is a test message", '
                                      '"tag": "test tag"}')

    @responses.activate
    def test_send_batch_messages(self):
        """
        sender = Message.send_batch()
        sender.push_message('+19195551212', '+19195551213', 'Hello this is test')
        sender.execute()
        """
        sender = Message.send_batch()
        self.assertIsInstance(sender, Message._Multi)
        self.assertEqual(len(responses.calls), 0)
        sender.push_message(sender='+1900000001',
                            receiver='+1900000002',
                            text='Good morning, '
                                 'this is a test message',
                            tag='test tag')
        self.assertEqual(len(responses.calls), 0)
        sender.push_message(sender='+1900000002',
                            receiver='+1900000003',
                            text='Good morning, '
                                 'this is a second test message',
                            tag='test tag2')
        self.assertEqual(len(responses.calls), 0)
        sender.push_message(sender='+1900000002',
                            receiver='+1900000003',
                            text='',
                            tag='test tag3')
        self.assertEqual(len(responses.calls), 0)

        raw = """
            [
              {
                "result": "accepted",
                "location": "https://.../v1/users/.../messages/mess-id-1"
              },
              {
                "result": "accepted",
                "location": "https://.../v1/users/.../messages/mess-id-2"
              },
              {
                "result": "error",
                "error": {
                  "category": "bad-request",
                  "code": "blank-property",
                  "message": "The 'message' resource property 'text' can't be blank",
                  "details": []
                 }
              }
            ]
            """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/messages',
                      body=raw,
                      status=202,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/messages/new-mess-id'})
        messages = sender.execute()
        self.assertEqual(len(responses.calls), 1)
        self.assertIsInstance(messages[0], Message)
        self.assertEqual(messages[0].id, 'mess-id-1')
        self.assertEqual(messages[0].from_, '+1900000001')
        self.assertEqual(messages[0].to, '+1900000002')
        self.assertEqual(messages[0].text, 'Good morning, '
                                           'this is a test message')
        self.assertEqual(messages[0].tag, 'test tag')
        self.assertIsInstance(messages[1], Message)
        self.assertEqual(messages[1].id, 'mess-id-2')
        self.assertEqual(messages[1].from_, '+1900000002')
        self.assertEqual(messages[1].to, '+1900000003')
        self.assertEqual(messages[1].text, 'Good morning, '
                                           'this is a second test message')
        self.assertEqual(messages[1].tag, 'test tag2')

        self.assertTrue(sender.errors)
        self.assertIsInstance(sender.errors, list)
        self.assertIsInstance(sender.errors[0], Message)
        self.assertEqual(sender.errors[0].tag, 'test tag3')
        self.assertEqual(sender.errors[0].from_, '+1900000002')
        self.assertEqual(sender.errors[0].to, '+1900000003')
        self.assertEqual(sender.errors[0].text, '')
        self.assertEqual(sender.errors[0].error_message, "The 'message' resource property 'text' can't be blank")

        with self.assertRaises(AppPlatformError):
            sender.execute()
        self.assertEqual(len(responses.calls), 1)


class UserErrorTest(SdkTestCase):

    @responses.activate
    def test_get(self):
        """
        UserError.get('e-id')
        """
        raw = """
        {
          "id": "e-id",
          "version": 0,
          "user": {
            "@id": 1,
            "accountNonExpired": true,
            "accountNonLocked": true,
            "companyName": "{companyName}",
            "credentialsNonExpired": true,
            "email": "{email}",
            "enabled": true,
            "firstName": "{firstName}",
            "id": "{userId}",
            "lastName": "{lastName}",
            "password": "{password}",
            "username": "{username}"
          },
          "time": "2012-10-05T20:38:11.023Z",
          "category": "bad-request",
          "code": "missing-property",
          "message": "The 'call' resource property 'transferTo' is required but was not specified",
          "details": [
            {
              "id": "{userErrorDetailId1}",
              "name": "requestPath",
              "value": "users/{userId}/calls/{callId}"
            },
            {
              "id": "{userErrorDetailId2}",
              "name": "remoteAddress",
              "value": "{remoteAddress}"
            },
            {
              "id": "{userErrorDetailId3}",
              "name": "requestMethod",
              "value": "POST"
            }
          ]
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/errors/e-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        error = UserError.get('e-id')
        self.assertEqual(error.id, 'e-id')
        self.assertEqual(error.code, 'missing-property')

        self.assertIsInstance(error.time, datetime)

        self.assertEqual(error.category, UserError.CATEGORIES.bad_request)
        self.assertEqual(error.message, "The 'call' resource property 'transferTo' is required but was not specified")

        self.assertIsInstance(error.details, list)

        self.assertEqual(len(error.details), 3)

        first_detail = error.details[0]

        self.assertIsInstance(first_detail, UserError.Detail)
        self.assertEqual(first_detail.id, "{userErrorDetailId1}")
        self.assertEqual(first_detail.name, "requestPath")
        self.assertEqual(first_detail.value, "users/{userId}/calls/{callId}")

        user = error.user

        self.assertIsInstance(user, UserError.User)

        self.assertEqual(user.id, "{userId}")
        self.assertEqual(user.enabled, True)
        self.assertEqual(user.first_name, "{firstName}")

        self.assertEqual(str(error), "UserError(e-id, message=The 'call' resource property 'transferTo' "
                                     "is required but was not specified)")

    @responses.activate
    def test_list(self):
        """
        UserError.list()
        """
        raw = """
        [{
            "time": "2012-11-15T01:30:16.208Z",
            "category": "unavailable",
            "id": "e-id",
            "details": [{
                "id": "{userErrorDetailId1}",
                "name": "applicationId",
                "value": "{applicationId}"
            }, {
                "id": "{userErrorDetailId2}",
                "name": "number",
                "value": "{number}"
            }, {
                "id": "{userErrorDetailId3}",
                "name": "callId",
                "value": "{callId}"
            }],
            "message": "Application {applicationId} for number{number} does not specify a URL for call events",
            "code": "no-callback-for-call"
        }, {
            "time": "2012-11-15T01:29:24.512Z",
            "category": "unavailable",
            "id": "{userErrorId2}",
            "message": "No application is configured for number +19195556666",
            "code": "no-application-for-number"
        }]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/errors',
                      body=raw,
                      status=200,
                      content_type='application/json')

        errors = UserError.list()

        self.assertEqual(len(errors), 2)

        error = errors[0]

        self.assertEqual(error.id, 'e-id')
        self.assertEqual(error.code, 'no-callback-for-call')

        self.assertIsInstance(error.time, datetime)

        self.assertEqual(error.category, UserError.CATEGORIES.unavailable)
        self.assertEqual(error.message, "Application {applicationId} for "
                                        "number{number} does not specify a URL for call events")

        self.assertIsInstance(error.details, list)

        self.assertEqual(len(error.details), 3)

        first_detail = error.details[0]

        self.assertIsInstance(first_detail, UserError.Detail)
        self.assertEqual(first_detail.id, "{userErrorDetailId1}")
        self.assertEqual(first_detail.name, "applicationId")
        self.assertEqual(first_detail.value, "{applicationId}")

        user = error.user

        self.assertIsNone(user)

        error = errors[1]

        self.assertEqual(error.id, '{userErrorId2}')
        self.assertEqual(error.code, 'no-application-for-number')

        self.assertIsInstance(error.time, datetime)

        self.assertEqual(error.category, UserError.CATEGORIES.unavailable)
        self.assertEqual(error.message, "No application is configured for number +19195556666")

        self.assertIsInstance(error.details, list)

        self.assertEqual(len(error.details), 0)

        user = error.user

        self.assertIsNone(user)
