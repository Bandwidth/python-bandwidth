import unittest
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
                           SmsEvent,
                           ConferenceEvent,
                           ConferenceMemberEvent,
                           ConferenceSpeakEvent,
                           ConferencePlaybackEvent,
                           Call
                           )


class EventsTest(unittest.TestCase):

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
        self.assertEqual(event.call_id, 'c-oexifypjlh5ygjr7qi4nesq')

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
        self.assertEqual(event.call_id, 'c-jjm3aiicnpngixjjelyomda')

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

        self.assertIsInstance(event.time, datetime)

        self.assertFalse(event.done)

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
                    "gatherId": "{gatherId}"
                    }

        event = Event.create(**data_inc)

        self.assertEqual(str(event), 'GatherCallEvent(c-z572ntgyy2vnffwpa5bwrcy)')

        self.assertIsInstance(event, EventType)
        self.assertIsInstance(event, GatherCallEvent)

        self.assertEqual(event.call_id, 'c-z572ntgyy2vnffwpa5bwrcy')

        self.assertIsInstance(event.time, datetime)

        self.assertEquals(event.digits, '1')
        self.assertIsInstance(event.call, Call)

        #todo: assert event gather

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
