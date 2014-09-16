import unittest
from datetime import datetime

from bandwith_sdk import (EventType,
                          Event,
                          IncomingCallEvent,
                          AnswerCallEvent,
                          HangupCallEvent,
                          PlaybackCallEvent,
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
