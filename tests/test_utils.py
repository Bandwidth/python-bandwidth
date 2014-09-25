import json
import datetime
import unittest
import responses
import requests

from dateutil.tz import tzutc
from bandwidth_sdk.utils import (camelize, underscorize, drop_empty,
                                 from_api, to_api, get_location_id, enum)


class UtilsTestCase(unittest.TestCase):

    def test_camelize(self):
        """
        test_camelize_ > testCamelize
        """
        self.assertEqual(camelize('test_camelize_'), 'testCamelize')
        self.assertEqual(camelize('from_'), 'from')

    def test_underscorize(self):
        """
        testUnderscorize > test_underscorize
        """
        self.assertEqual(underscorize('testUnderscorize'), 'test_underscorize')
        self.assertEqual(underscorize('TestUnderscorizeThisTest'),
                         'test_underscorize_this_test')

    def test_drop_empty(self):
        """
        Drop empty keys from dicts
        """
        d = dict(a='test', auto=False, b=None, prompt={}, w=0, j='')
        self.assertEqual(drop_empty(d),
                         {'a': 'test',
                          'auto': False,
                          'prompt': {},
                          'w': 0,
                          'j': ''})

    def test_from_api(self):
        """
        Convert incoming data to python native dicts
        include converting case of keys and
        parsing datetimes string to python objects
        """
        raw = """
        {
           "eventType":"incomingcall",
           "from":"+13233326955",
           "to":"+13865245000",
           "callId":"c-oexifypjlh5ygjr7qi4nesq",
           "callState":"active",
           "applicationId":"a-25nh2lj6qrxznkfu4b732jy",
           "time":"2012-11-14T16:21:59.616Z"
        }
        """
        self.assertEqual(from_api(json.loads(raw)),
                         {'event_type': 'incomingcall',
                          'from': '+13233326955',
                          'to': '+13865245000',
                          'call_id': 'c-oexifypjlh5ygjr7qi4nesq',
                          'call_state': 'active',
                          'application_id': 'a-25nh2lj6qrxznkfu4b732jy',
                          'time': datetime.datetime(year=2012,
                                                    month=11,
                                                    day=14,
                                                    hour=16,
                                                    minute=21,
                                                    second=59,
                                                    microsecond=616000,
                                                    tzinfo=tzutc())})
        with self.assertRaises(AssertionError):
            from_api('not_dict')

    def test_to_api(self):
        """
        Test outcoming data to catapult
        (convert to camelcase,
         stringify datetime objects etc, kick none objects)
        """
        with self.assertRaises(AssertionError):
            to_api('not_dict')
        d = {'event_type': 'incomingcall',
             'from': '+13233326955',
             'to': '+13865245000',
             'call_id': 'c-oexifypjlh5ygjr7qi4nesq',
             'call_state': 'active',
             'call_uri': None,
             'application_id': 'a-25nh2lj6qrxznkfu4b732jy',
             'time': datetime.datetime(year=2012,
                                       month=11,
                                       day=14,
                                       hour=16,
                                       minute=21,
                                       second=59,
                                       microsecond=616000,
                                       tzinfo=tzutc())}
        self.assertEquals(to_api(d), {
                          'eventType': 'incomingcall',
                          'from': '+13233326955',
                          'to': '+13865245000',
                          'callId': 'c-oexifypjlh5ygjr7qi4nesq',
                          'callState': 'active',
                          'applicationId': 'a-25nh2lj6qrxznkfu4b732jy',
                          'time': '2012-11-14T16:21:59.616000+00:00'
                          })

    @responses.activate
    def test_get_location(self):
        """
        Test getting id of new object from location header
        """
        responses.add(
            responses.POST,
            'https://api.catapult.inetwork.com/users/u-user/calls',
            body='',
            status=201,
            content_type='application/json',
            adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})
        resp = requests.post(
            'https://api.catapult.inetwork.com/users/u-user/calls')
        self.assertEquals(get_location_id(resp), 'new-call-id')

    def test_enum(self):
        Seasons = enum('winter', 'spring', 'summer', 'autumn')
        self.assertTrue(hasattr(Seasons, 'winter'))
        self.assertTrue(hasattr(Seasons, 'spring'))
        self.assertTrue(hasattr(Seasons, 'summer'))
        self.assertTrue(hasattr(Seasons, 'autumn'))
        self.assertEquals(Seasons.winter, 'winter')
        self.assertEquals(Seasons.spring, 'spring')
        self.assertEquals(Seasons.summer, 'summer')
        self.assertEquals(Seasons.autumn, 'autumn')
