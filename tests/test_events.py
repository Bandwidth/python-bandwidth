import responses
from datetime import datetime

from bandwidth_sdk import (EventType,
                           Event,
                           IncomingCallEvent,
                           AnswerCallEvent,
                           HangupCallEvent,
                           PlaybackCallEvent,
                           GatherCallEvent,
                           ErrorCallEvent,
                           TimeoutCallEvent,
                           RecordingCallEvent,
                           SpeakCallEvent,
                           DtmfCallEvent,
                           MessageEvent,
                           ConferenceEvent,
                           ConferenceMemberEvent,
                           ConferenceSpeakEvent,
                           ConferencePlaybackEvent,
                           RejectCallEvent,
                           Call,
                           Conference,
                           Gather,
                           Recording,
                           Message
                           )

from .utils import SdkTestCase


class EventsTest(SdkTestCase):

    def test_factory_incoming(self):
        """
        Event.create factory methods for incommingcall
        """
        data_inc = b'''
        {
        "eventType":"incomingcall",
        "from":"+13233326955",
        "to":"+13865245000",
        "callId":"c-oexifypjlh5ygjr7qi4nesq",
        "callUri": "https://api.catapult.inetwork.com/v1/users/u-ndh7ecxejswersdu5g8zngvca/calls/c-oexifypjlh5ygjr7qi4nesq",
        "callState":"active",
        "applicationId":"a-25nh2lj6qrxznkfu4b732jy",
        "time":"2012-11-14T16:21:59.616Z"
        }
        '''

        event = Event.create(data=data_inc)

        self.assertEqual(str(event), 'IncomingCallEvent(c-oexifypjlh5ygjr7qi4nesq)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, IncomingCallEvent)

        self.assertEqual(event.from_, '+13233326955')
        self.assertEqual(event.to, '+13865245000')
        self.assertEqual(event.call_id, 'c-oexifypjlh5ygjr7qi4nesq')
        self.assertEqual(event.call_state, 'active')
        self.assertEqual(event.application_id, 'a-25nh2lj6qrxznkfu4b732jy')

        self.assertIsInstance(event.time, datetime)

    def test_factory_answer(self):
        """
        Event.create factory methods for answer
        """
        data_inc = b'''
        {
        "eventType":"answer",
        "from":"+15753222083",
        "to":"+13865245000",
        "callId":"c-jjm3aiicnpngixjjelyomda",
        "callUri": "https://api.catapult.inetwork.com/v1/users/u-ndh7ecxejswersdu5g8zngvca/calls/c-jjm3aiicnpngixjjelyomda",
        "callState":"active",
        "applicationId":"a-25nh2lj6qrxznkfu4b732jy",
        "time":"2012-11-14T16:28:31.536Z"
        }
        '''

        event = Event.create(data=data_inc)

        self.assertEqual(str(event), 'AnswerCallEvent(c-jjm3aiicnpngixjjelyomda)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, AnswerCallEvent)

        self.assertEqual(event.from_, '+15753222083')
        self.assertEqual(event.to, '+13865245000')
        self.assertEqual(event.call_id, 'c-jjm3aiicnpngixjjelyomda')
        self.assertEqual(event.call_state, 'active')
        self.assertEqual(event.application_id, 'a-25nh2lj6qrxznkfu4b732jy')

        self.assertIsInstance(event.time, datetime)

    def test_factory_hangup(self):
        """
        Event.create factory methods for hangup
        """
        data_inc = b'''
        {
        "eventType":"hangup",
        "callId":"c-z572ntgyy2vnffwpa5bwrcy",
        "callUri": "https://api.catapult.inetwork.com/v1/users/u-ndh7ecxejswersdu5g8zngvca/calls/c-z572ntgyy2vnffwpa5bwrcy",
        "from":"+13233326955",
        "to":"+13233326955",
        "cause":"NORMAL_CLEARING",
        "time":"2012-11-14T15:56:12.636Z"
        }
        '''

        event = Event.create(data=data_inc)

        self.assertEqual(str(event), 'HangupCallEvent(c-z572ntgyy2vnffwpa5bwrcy)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, HangupCallEvent)

        self.assertEqual(event.from_, '+13233326955')
        self.assertEqual(event.to, '+13233326955')
        self.assertEqual(event.cause, 'NORMAL_CLEARING')
        self.assertEqual(event.call_id, 'c-z572ntgyy2vnffwpa5bwrcy')

        self.assertIsInstance(event.time, datetime)

    def test_factory_reject(self):
        """
        Event.create factory methods for reject event
        """
        data_inc = b'''
        {
        "eventType":"hangup",
        "callId":"c-z572ntgyy2vnffwpa5bwrcy",
        "callUri": "https://api.catapult.inetwork.com/v1/users/u-ndh7ecxejswersdu5g8zngvca/calls/c-z572ntgyy2vnffwpa5bwrcy",
        "from":"+13233326955",
        "to":"+13233326955",
        "cause":"CALL_REJECTED",
        "time":"2012-11-14T15:56:12.636Z"
        }
        '''

        event = Event.create(data=data_inc)

        self.assertEqual(str(event), 'RejectCallEvent(c-z572ntgyy2vnffwpa5bwrcy)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, RejectCallEvent)

        self.assertEqual(event.from_, '+13233326955')
        self.assertEqual(event.to, '+13233326955')
        self.assertEqual(event.cause, 'CALL_REJECTED')
        self.assertEqual(event.call_id, 'c-z572ntgyy2vnffwpa5bwrcy')

        self.assertIsInstance(event.time, datetime)

    def test_factory_playback(self):
        """
        Event.create factory methods for playback
        """
        data_inc = b'''
        {
        "eventType":"playback",
        "callId":"c-z572ntgyy2vnffwpa5bwrcy",
        "callUri": "https://api.catapult.inetwork.com/v1/users/u-ndh7ecxejswersdu5g8zngvca/calls/c-z572ntgyy2vnffwpa5bwrcy",
        "status":"started",
        "time":"2012-11-14T15:56:05.896Z"
        }
        '''

        event = Event.create(data=data_inc)

        self.assertEqual(str(event), 'PlaybackCallEvent(c-z572ntgyy2vnffwpa5bwrcy)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, PlaybackCallEvent)

        self.assertEqual(event.call_id, 'c-z572ntgyy2vnffwpa5bwrcy')
        self.assertEqual(event.status, 'started')

        self.assertIsInstance(event.time, datetime)

        self.assertFalse(event.done)

    @responses.activate
    def test_factory_gather(self):
        """
        Event.create factory methods for gather
        """
        data_inc = {"time": "2014-06-13T22:40:34Z",
                    "reason": "max-digits",
                    "state": "completed",
                    "digits": "1",
                    "eventType": "gather",
                    "callId": 'c-z572ntgyy2vnffwpa5bwrcy',
                    "gatherId": "gatherId"
                    }

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'GatherCallEvent(c-z572ntgyy2vnffwpa5bwrcy)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, GatherCallEvent)

        self.assertEqual(event.call_id, 'c-z572ntgyy2vnffwpa5bwrcy')
        self.assertEqual(event.gather_id, 'gatherId')
        self.assertEqual(event.reason, 'max-digits')
        self.assertEqual(event.state, 'completed')

        self.assertIsInstance(event.time, datetime)

        self.assertEquals(event.digits, '1')
        self.assertIsInstance(event.call, Call)

        raw = """
        {
        "id": "gatherId",
        "state": "completed",
        "reason": "max-digits",
        "createdTime": "2014-02-12T19:33:56Z",
        "completedTime": "2014-02-12T19:33:59Z",
        "call": "https://api.catapult.inetwork.com/v1/users/u-xa2n3oxk6it4efbglisna6a/calls/c-isw3qup6gvr3ywcsentygnq",
        "digits": "123"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-z572ntgyy2vnffwpa5bwrcy'
                      '/gather/gatherId',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )
        gather = event.gather
        self.assertIsInstance(gather, Gather)

        self.assertEqual(gather.reason, 'max-digits')

    def test_factory_error(self):
        """
        Event.create factory methods for error
        """
        data_inc = {'to': '+16263882600',
                    'callUri': 'https://api.catapult.inetwork.com/v1/users/u-2qep/calls/c-kmg',
                    'callState': 'error',
                    'eventType': 'error',
                    'from': '+17146143600',
                    'callId': 'c-kmg'}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'ErrorCallEvent(c-kmg)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, ErrorCallEvent)

        self.assertEqual(event.call_id, 'c-kmg')

        self.assertEquals(event.call_state, 'error')
        self.assertEquals(event.to, '+16263882600')
        self.assertEquals(event.from_, '+17146143600')

        self.assertIsInstance(event.call, Call)

    def test_factory_timeout(self):
        """
        Event.create factory methods for timeout
        """
        data_inc = {'time': '2014-09-23T06:30:39Z',
                    'from': '+16824595961',
                    'callId': 'c-5nq',
                    'to': '+12697047265',
                    'callUri': 'https://api.catapult.inetwork.com/v1/users/u-2qi/calls/c-5nq',
                    'tag': 'c-2mdp',
                    'eventType': 'timeout'}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'TimeoutCallEvent(c-5nq)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, TimeoutCallEvent)

        self.assertEqual(event.call_id, 'c-5nq')

        self.assertEquals(event.tag, 'c-2mdp')

        self.assertIsInstance(event.call, Call)
        self.assertIsInstance(event.time, datetime)

    def test_factory_recording(self):
        """
        Event.create factory methods for recording
        """
        data_inc = {'recordingUri': 'https://api.catapult.inetwork.com/v1/users/u-2q/recordings/rec-7k',
                    'recordingId': 'rec-7k',
                    'endTime': '2014-09-25T13:41:02Z',
                    'callId': 'c-c5zk',
                    'eventType': 'recording',
                    'startTime': '2014-09-25T13:38:28Z',
                    'status': 'complete',
                    'state': 'complete'}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'RecordingCallEvent(c-c5zk)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, RecordingCallEvent)

        self.assertEqual(event.call_id, 'c-c5zk')
        self.assertEqual(event.recording_id, 'rec-7k')

        self.assertIsInstance(event.call, Call)
        self.assertIsInstance(event.start_time, datetime)
        self.assertIsInstance(event.end_time, datetime)

        rec = event.recording
        self.assertIsInstance(rec, Recording)
        self.assertEqual(rec.id, event.recording_id)

    def test_factory_speak(self):
        """
        Event.create factory methods for speak
        """
        data_inc = {"callId": "c-xx",
                    "callUri": "https://api.catapult.inetwork.com/v1/users/u-ndh/calls/c-xx",
                    "eventType": "speak",
                    "state": "PLAYBACK_START",
                    "status": "started",
                    "time": "2013-06-26T17:55:45.748Z",
                    "type": "speak"}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'SpeakCallEvent(c-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, SpeakCallEvent)

        self.assertEqual(event.call_id, 'c-xx')
        self.assertEquals(event.state, 'PLAYBACK_START')
        self.assertIsInstance(event.call, Call)
        self.assertIsInstance(event.time, datetime)
        self.assertEqual(event.done, False)

    def test_factory_dtmf(self):
        """
        Event.create factory methods for dtmf
        """
        data_inc = {'dtmfDigit': '2',
                    'callId': 'c-xx',
                    'callUri': 'https://api.catapult.inetwork.com/v1/users/u-2q/calls/c-xx',
                    'dtmfDuration': '1400',
                    'time': '2014-09-25T13:35:49Z',
                    'eventType': 'dtmf'}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'DtmfCallEvent(c-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, DtmfCallEvent)

        self.assertEqual(event.call_id, 'c-xx')
        self.assertEqual(event.dtmf_digit, '2')
        self.assertEqual(event.dtmf_duration, '1400')

        self.assertIsInstance(event.call, Call)
        self.assertIsInstance(event.time, datetime)

    def test_factory_sms(self):
        """
        Event.create factory methods for sms
        """
        data_inc = {"eventType": "sms",
                    "direction": "in",
                    "messageId": "m-xx",
                    "messageUri": "https://api.catapult.inetwork.com/v1/"
                                  "users/u-ndh7ecxejswersdu5g8zngvca/messages/m-xx",
                    "from": "+13233326955",
                    "to": "+13865245000",
                    "text": "Example",
                    "applicationId": "a-25nh2lj6qrxznkfu4b732jy",
                    "time": "2012-11-14T16:13:06.076Z",
                    "state": "received"}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'MessageEvent(message_id=m-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, MessageEvent)

        self.assertEqual(event.direction, 'in')
        self.assertEqual(event.message_id, 'm-xx')
        self.assertEqual(event.from_, '+13233326955')
        self.assertEqual(event.to, '+13865245000')
        self.assertEqual(event.text, 'Example')
        self.assertEqual(event.state, 'received')
        self.assertIsInstance(event.time, datetime)

        self.assertIsInstance(event.message, Message)
        self.assertEqual(event.message.id, 'm-xx')
        self.assertEqual(event.state, 'received')

    def test_factory_conference(self):
        """
        Event.create factory methods for conference
        """
        data_inc = {"conferenceId": "conf-xx",
                    "conferenceUri": "https://api.catapult.inetwork.com/v1"
                                     "/users/u-ndh7ecxejswersdu5g8zngvca/conferences/conf-xx",
                    "eventType": "conference",
                    "status": "completed",
                    "createdTime": "2013-07-12T16:29:32.521-02:00",
                    "completedTime": "2013-07-12T16:45:10.103-02:00"}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'ConferenceEvent(conference_id=conf-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, ConferenceEvent)

        self.assertIsInstance(event.created_time, datetime)
        self.assertIsInstance(event.completed_time, datetime)
        self.assertIsInstance(event.conference, Conference)

        self.assertEqual(event.status, 'completed')
        self.assertEqual(event.conference_id, 'conf-xx')

    def test_factory_conference_member(self):
        """
        Event.create factory methods for conference member
        """
        data_inc = {"activeMembers": 1,
                    "callId": "c-xx",
                    "conferenceId": "conf-xx",
                    "eventType": "conference-member",
                    "hold": False,
                    "memberId": "member-yy",
                    "memberUri": "https://api.catapult.inetwork.com/v1/"
                                 "users/u-ndh7ecxejswersdu5g8zngvca/"
                                 "conferences/conf-xx/members/member-yy",
                    "mute": False,
                    "state": "active",
                    "time": "2013-07-12T20:53:11.646Z"}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'ConferenceMemberEvent(conference_id=conf-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, ConferenceMemberEvent)

        self.assertEqual(event.call_id, 'c-xx')
        self.assertEqual(event.conference_id, 'conf-xx')
        self.assertEqual(event.active_members, 1)
        self.assertEqual(event.hold, False)
        self.assertEqual(event.mute, False)
        self.assertEqual(event.state, 'active')

        self.assertIsInstance(event.conference, Conference)
        self.assertIsInstance(event.call, Call)
        self.assertIsInstance(event.time, datetime)

    def test_factory_conference_speak(self):
        """
        Event.create factory methods for conference speak
        """
        data_inc = {"eventType": "conference-speak",
                    "conferenceId": "conf-xx",
                    "conferenceUri": "https://api.catapult.inetwork.com/v1/"
                                     "users/u-ndh7ecxejswersdu5g8zngvca/conferences/conf-xx",
                    "status": "started",
                    "time": "2013-07-12T21:22:55.046Z"}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'ConferenceSpeakEvent(conference_id=conf-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, ConferenceSpeakEvent)

        self.assertEqual(event.conference_id, 'conf-xx')
        self.assertEqual(event.status, 'started')

        self.assertIsInstance(event.time, datetime)

    def test_factory_conference_playback(self):
        """
        Event.create factory methods for conference playback
        """
        data_inc = {"eventType": "conference-playback",
                    "conferenceId": "conf-xx",
                    "conferenceUri": "https://api.catapult.inetwork.com/v1/users"
                                     "/u-ndh7ecxejswersdu5g8zngvca/conferences/conf-xx",
                    "status": "started",
                    "time": "2013-07-12T21:18:19.966Z"}

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'ConferencePlaybackEvent(conference_id=conf-xx)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, ConferencePlaybackEvent)

        self.assertEqual(event.conference_id, 'conf-xx')
        self.assertEqual(event.status, 'started')

        self.assertIsInstance(event.time, datetime)

    def test_unknown_event(self):
        """
        Event.create for malformed event
        """
        data_inc = {"eventType": "unknown",
                    "status": "started",
                    "time": "2013-07-12T21:18:19.966Z"}

        with self.assertRaises(ValueError):
            Event.create(**data_inc)
