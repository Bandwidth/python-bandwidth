import requests
import six
import urllib
import json
import itertools
from bandwidth.voice.lazy_enumerable import get_lazy_enumerator
from bandwidth.convert_camel import convert_object_to_snake_case
from bandwidth.voice.decorators import play_audio
from bandwidth.version import __version__ as version

quote = urllib.parse.quote if six.PY3 else urllib.quote
lazy_map = map if six.PY3 else itertools.imap


def _set_media_name(recording):
    recording['mediaName'] = recording.get('media', '').split('/')[-1]
    return recording


@play_audio('call')
@play_audio('bridge')
@play_audio('conference')
class Client:

    """
    Catapult client
    """

    def __init__(self, user_id=None, api_token=None, api_secret=None, **other_options):
        """
        Initialize the catatpult client.
        :type user_id: str
        :param user_id: catapult user id
        :type api_token: str
        :param api_token: catapult api token
        :type api_secret: str
        :param api_secret: catapult api secret
        :type api_endpoint: str
        :param api_endpoint: catapult api endpoint (optional, default value is https://api.catapult.inetwork.com)
        :type api_version: str
        :param api_version: catapult api version (optional, default value is v1)

        :rtype: bandwidth.catapult.Client
        :returns: bandwidth client

        Init the catapult client::

            api = bandwidth.catapult.Client('YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
            # or
            api = bandwidth.client('catapult', 'YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
        """
        if not all((user_id, api_token, api_secret)):
            raise ValueError('Arguments user_id, api_token and api_secret are required. '
                             'Use bandwidth.client("catapult", "YOUR-USER-ID", "YOUR-API-TOKEN", "YOUR-API-SECRET")')
        self.user_id = user_id
        self.api_endpoint = other_options.get(
            'api_endpoint', 'https://api.catapult.inetwork.com')
        self.api_version = other_options.get('api_version', 'v1')
        self.auth = (api_token, api_secret)

    def _request(self, method, url, *args, **kwargs):
        user_agent = 'PythonSDK_' + version
        headers = kwargs.pop('headers', None)
        if headers:
            headers['User-Agent'] = user_agent
        else:
            headers = {
                'User-Agent': user_agent
            }
        if url.startswith('/'):
            # relative url
            url = '%s/%s%s' % (self.api_endpoint, self.api_version, url)
        return requests.request(method, url, auth=self.auth, headers=headers, *args, **kwargs)

    def _check_response(self, response):
        if response.status_code >= 400:
            if response.headers.get('content-type') == 'application/json':
                data = response.json()
                raise CatapultException(
                    response.status_code, data['message'], code=data.get('code'))
            else:
                raise CatapultException(
                    response.status_code, response.content.decode('utf-8')[:79])

    def _make_request(self, method, url, *args, **kwargs):
        response = self._request(method, url, *args, **kwargs)
        self._check_response(response)
        data = None
        id = None
        if response.headers.get('content-type') == 'application/json':
            data = convert_object_to_snake_case(response.json())
        location = response.headers.get('location')
        if location is not None:
            id = location.split('/')[-1]
        return (data, response, id)

    def build_sentence(self, sentence, gender=None, locale=None, voice=None, loop_enabled=None, **kwargs):
        """
        Create a dictionary to speak sentence to live call, bridge, or conference

        :param str sentence: The sentence to speak.
        :param str gender: The gender of the voice used to synthesize the sentence.
        :param str locale: The locale used to get the accent of the voice used to synthesize the sentence.
        :param str voice: The voice to speak the sentence.<br>
            - English US: Susan (Default), Kate, Julie, Dave, Paul
            - English UK: Bridget
            - Spanish: Esperanza, Violeta, Jorge
            - French: Jolie, Bernard
            - German: Katrin, Stefan
            - Italian: Paola, Luca
        :param bool loop_enabled: When value is true, the sentence will keep repeating until stopped.

        :rtype: dict
        :returns: dictionary to be passed to audio playback methods

        :Example:

            my_sentence = api.build_sentence(sentence = "Hello from Bandwidth",
                                             gender="Female",
                                             locale="en_UK",
                                             voice="Bridget",
                                             loop_enabled=True
                                             )

            api.play_audio_to_call(call_id, my_sentence)
        """
        kwargs["sentence"] = sentence
        kwargs["gender"] = gender
        kwargs["locale"] = locale
        kwargs["voice"] = voice
        kwargs["loopEnabled"] = loop_enabled
        return kwargs

    def build_audio_playback(self, file_url, loop_enabled=None, **kwargs):
        """
        Create a dictionary to playback audio file
        :param str file_url: The location of an audio file to play (WAV and MP3 supported).
        :param bool loop_enabled: When value is true, the audio will keep playing in a loop.

        :Example:

            my_audio = api.build_audio_playback('http://my_site.com/file.mp3, loop_enabled=True)
        """
        kwargs["fileUrl"] = file_url
        kwargs["loopEnabled"] = loop_enabled
        return kwargs

    """
    Account API
    """

    def get_account(self):
        """
        Get an Account object

        :rtype: dict
        :returns: account data

        Example::

            data = api.get_account()
        """
        return self._make_request('get', '/users/%s/account' % self.user_id)[0]

    def list_account_transactions(self,
                                  max_items=None,
                                  to_date=None,
                                  from_date=None,
                                  trans_type=None,
                                  size=None,
                                  number=None,
                                  **kwargs):
        """
        Get the transactions from the user's account

        :param str max_items: Limit the number of transactions that will be returned.
        :param str to_date: Return only transactions that are newer than the parameter. \
            Format: "yyyy-MM-dd'T'HH:mm:ssZ"
        :param str from_date: Return only transactions that are older than the parameter. \
            Format: "yyyy-MM-dd'T'HH:mm:ssZ"
        :param str trans_type: Return only transactions that are this type.
        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items. \
            If no value is specified the default value is 25. (Maximum value 1000)
        :param str number: Search transactions by phone number
        :rtype: types.GeneratorType
        :returns: list of transactions

        Example: Get transactions::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions by date::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions filtering by date::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions limiting result::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions of payment type::

            list = api.get_account_transactions(type = 'charge')
        """
        kwargs["maxItems"] = max_items
        kwargs["toDate"] = to_date
        kwargs["fromDate"] = from_date
        kwargs["type"] = trans_type
        kwargs["size"] = size
        kwargs["number"] = number

        path = '/users/%s/account/transactions' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def list_calls(self, bridge_id=None, conference_id=None, from_=None, to=None, size=None, sort_order=None, **kwargs):
        """
        Get a list of calls

        :param str bridge_id: The id of the bridge for querying a list of calls history
        :param str conference_id: The id of the conference for querying a list of calls history
        :param str ``from_``: The number to filter calls that came from
        :param str to: The number to filter calls that was called to
        :param str sort_order: How to sort the calls. \
            Values are asc or desc If no value is specified the default value is desc
        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items. \
            If no value is specified the default value is 25. (Maximum value 1000)

        :rtype: types.GeneratorType
        :returns: list of calls

        Example: Fetch calls from specific telephone number::

            call_list = api.list_calls(from_ = '+19192223333', size = 1000)

            total_chargeable_duration = 0

            for call in call_list:
                total_chargeable_duration += call['chargeableDuration']

            print(total_chargeable_duration)
            ## 240

        Example: List Calls::

            call_list = api.list_calls(to = '+19192223333', size = 2)
            print(list(call_list))
            ## [
            ##   {
            ##     'activeTime'          : '2017-01-26T16:10:23Z',
            ##     'callbackUrl'         : 'http://yoursite.com/calls',
            ##     'chargeableDuration'  : 60,
            ##     'direction'           : 'out',
            ##     'endTime'             : '2017-01-26T16:10:33Z',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/events',
            ##     'from'                : '+17079311113',
            ##     'id'                  : 'c-abc123',
            ##     'recordingEnabled'    : False,
            ##     'recordingFileFormat' : 'wav',
            ##     'recordings'          : 'https://api.../v1/users/u-abc123/calls/c-abc123/recordings',
            ##     'startTime'           : '2017-01-26T16:10:11Z',
            ##     'state'               : 'completed',
            ##     'to'                  : '+19192223333',
            ##     'transcriptionEnabled': False,
            ##     'transcriptions'      : 'https://api.../v1/users/u-abc123/calls/c-abc123/transcriptions'
            ##   },
            ##   {
            ##     'activeTime'          : '2016-12-29T23:50:35Z',
            ##     'chargeableDuration'  : 60,
            ##     'direction'           : 'out',
            ##     'endTime'             : '2016-12-29T23:50:41Z',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/events',
            ##     'from'                : '+19194443333',
            ##     'id'                  : 'c-xyz987',
            ##     'recordingEnabled'    : False,
            ##     'recordingFileFormat' : 'wav',
            ##     'recordings'          : 'https://api.../v1/users/u-abc123/calls/c-xyz987/recordings',
            ##     'startTime'           : '2016-12-29T23:50:15Z',
            ##     'state'               : 'completed',
            ##     'to'                  : '+19192223333',
            ##     'transcriptionEnabled': False,
            ##     'transcriptions'      : 'https://api.../v1/users/u-abc123/calls/c-xyz987/transcriptions'
            ##   }
            ## ]

        """

        kwargs["bridgeId"] = bridge_id
        kwargs["conferenceId"] = conference_id
        kwargs["from"] = from_
        kwargs["to"] = to
        kwargs["size"] = size
        kwargs["sortOrder"] = sort_order

        path = '/users/%s/calls' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_call(self,
                    from_,
                    to,
                    call_timeout=None,
                    callback_url=None,
                    callback_timeout=None,
                    callback_http_method=None,
                    fallback_url=None,
                    bridge_id=None,
                    conference_id=None,
                    recording_enabled=False,
                    recording_file_format=None,
                    recording_max_duration=None,
                    transcription_enabled=False,
                    tag=None,
                    sip_headers=None,
                    **kwargs):
        """
        Create a call

        :param str ``from_``: A Bandwidth phone number on your account the call should come from (required)
        :param str to: The number to call (required)
        :param str call_timeout: Determine how long should the platform wait for call answer before timing out
                in seconds.
        :param str callback_url: The full server URL where the call events related to the Call will be sent to.
        :param str callback_timeout: Determine how long should the platform wait for callbackUrl's response before
                timing out in milliseconds.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are "GET" or "POST" (if not set the default is POST).
        :param str fallback_url: The full server URL used to send the callback event if the request to
                callbackUrl fails.
        :param str bridge_id: The id of the bridge where the call will be added.
        :param str conference_id: Id of the conference where the call will be added. This property is required
                if you want to add this call to a conference.
        :param bool recording_enabled: Indicates if the call should be recorded after being created. Set to "true"
                to enable. Default is "false".
        :param str recording_file_format: The file format of the recorded call. \
            Supported values are wav (default) and mp3.
        :param str recording_max_duration: Indicates the maximum duration of call recording in seconds. \
            Default value is 1 hour.
        :param bool transcription_enabled: Recordings for this call is going to be automatically transcribed.
        :param str tag: A string that will be included in the callback events of the call.
        :param str sip_headers: Map of Sip headers prefixed by "X-". Up to 5 headers can be sent per call.
        :rtype: str
        :returns: id of created call

        Example: Create an outbound phone call::

            call_id = api.create_call(from_='+1234567890',
                                      to='+1234567891',
                                      callback_url='http://yoursite.com/calls')

            print(call_id)
            ## c-abc123

            my_call = api.get_call(call_id)
            print(my_call)
            ## {   'callbackUrl'         : 'http://yoursite.com/calls',
            ##     'direction'           : 'out',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
            ##     'from'                : '+1234567890',
            ##     'id'                  : 'c-abc123',
            ##     'recordingEnabled'    : False,
            ##     'recordingFileFormat' : 'wav',
            ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
            ##     'startTime'           : '2017-01-26T16:10:11Z',
            ##     'state'               : 'started',
            ##     'to'                  : '+1234567891',
            ##     'transcriptionEnabled': False,
            ##     'transcriptions'      : 'https://api.../v1/users/u-abc/calls/c-abc123/transcriptions'}
        """
        kwargs["from"] = from_
        kwargs["to"] = to
        kwargs["callTimeout"] = call_timeout
        kwargs["callbackUrl"] = callback_url
        kwargs["callbackTimeout"] = callback_timeout
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["fallbackUrl"] = fallback_url
        kwargs["bridgeId"] = bridge_id
        kwargs["conferenceId"] = conference_id
        kwargs["recordingEnabled"] = recording_enabled
        kwargs["recordingFileFormat"] = recording_file_format
        kwargs["recordingMaxDuration"] = recording_max_duration
        kwargs["transcriptionEnabled"] = transcription_enabled
        kwargs["tag"] = tag
        kwargs["sipHeaders"] = sip_headers
        return self._make_request('post', '/users/%s/calls' % self.user_id, json=kwargs)[2]

    def get_call(self, call_id):
        """
        Get information about a call

        :type call_id: str
        :param call_id: id of a call

        :rtype: dict
        :returns: call information

        Fetch and Print Call::

            my_call = api.get_call(call_id)
            print(my_call)
            ## {   'callbackUrl'         : 'http://yoursite.com/calls',
            ##     'direction'           : 'out',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
            ##     'from'                : '+1234567890',
            ##     'id'                  : 'c-abc123',
            ##     'recordingEnabled'    : False,
            ##     'recordingFileFormat' : 'wav',
            ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
            ##     'startTime'           : '2017-01-26T16:10:11Z',
            ##     'state'               : 'started',
            ##     'to'                  : '+1234567891',
            ##     'transcriptionEnabled': False,
            ##     'transcriptions'      : 'https://api..../v1/users/u-abc/calls/c-abc123/transcriptions'}
        """
        return self._make_request('get', '/users/%s/calls/%s' % (self.user_id, call_id))[0]

    def update_call(self,
                    call_id,
                    state=None,
                    recording_enabled=None,
                    recording_file_format=None,
                    transfer_to=None,
                    transfer_caller_id=None,
                    whisper_audio=None,
                    callback_url=None,
                    **kwargs):
        """

        Update a call

        :type call_id: str
        :param call_id: id of a call

        :param str state: The call state. Possible values: rejected to reject not answer, active to answer the call,
            completed to hangup the call, transferring to start and connect call to a new outbound call.
        :param bool recording_enabled: Indicates if the call should be recorded. \
            Values true or false. You can turn recording on/off and have multiple recordings on a single call.
        :param str recording_file_format: The file format of the recorded call. \
            Supported values are wav (default) and mp3.
        :param str transfer_to: Phone number or SIP address that the call is going to be transferred to.
        :param str transfer_caller_id: This is the caller id that will be used when the call is transferred.
        :param dict whisper_audio: Audio to be played to the caller that the call will be transferred to.
        :param str callback_url: The server URL where the call events for the new call will be sent upon transferring.


        Update call with state = completed. (Hang up the call)::

            my_call = api.get_call(call_id)
            my_call_state = my_call['state']
            print(my_call_state)
            ## started

            api.update_call(my_call['id'], state='completed')

            my_call = api.get_call(my_call['id'])
            print(my_call['state'])
            ## completed

        """

        kwargs["state"] = state
        kwargs["recordingEnabled"] = recording_enabled
        kwargs["recordingFileFormat"] = recording_file_format
        kwargs["transferTo"] = transfer_to
        kwargs["transferCallerId"] = transfer_caller_id
        kwargs["whisperAudio"] = whisper_audio
        kwargs["callbackUrl"] = callback_url
        return self._make_request('post', '/users/%s/calls/%s' % (self.user_id, call_id), json=kwargs)[2]

    def play_audio_to_call(self,
                           call_id,
                           file_url=None,
                           sentence=None,
                           gender=None,
                           locale=None,
                           voice=None,
                           loop_enabled=None,
                           **kwargs):
        """
        Play audio to a call

        :param str call_id: id of a call
        :param str file_url: The location of an audio file to play (WAV and MP3 supported).
        :param str sentence: The sentence to speak.
        :param str gender: The gender of the voice used to synthesize the sentence.
        :param str locale: The locale used to get the accent of the voice used to synthesize the sentence.
        :param str voice: The voice to speak the sentence.
        :param bool loop_enabled: When value is true, the audio will keep playing in a loop.


        Play audio in file::

            api.play_audio_to_call('callId', fileUrl= 'http://host/path/file.mp3')
            api.play_audio_to_call('callId', sentence='Press 0 to complete call', gender='female')
            # or with extension methods
            api.play_audio_file_to_call('callId', 'http://host/path/file.mp3')
            api.speak_sentence_to_call('callId', 'Hello')

        """
        kwargs["fileUrl"] = file_url
        kwargs["sentence"] = sentence
        kwargs["gender"] = gender
        kwargs["locale"] = locale
        kwargs["voice"] = voice
        kwargs["loopEnabled"] = loop_enabled
        self._make_request(
            'post', '/users/%s/calls/%s/audio' % (self.user_id, call_id), json=kwargs)

    def send_dtmf_to_call(self, call_id, dtmf_out, **kwargs):
        """
        Send DTMF (phone keypad digit presses).

        :param str call_id: id of a call
        :param str dtmf_out: String containing the DTMF characters to be sent in a call.

        Example: Send Digits to call::

            api.send_dtmf_to_cal('c-callId', '1234')
        """
        kwargs["dtmfOut"] = dtmf_out
        self._make_request('post', '/users/%s/calls/%s/dtmf' %
                           (self.user_id, call_id), json=kwargs)

    def list_call_recordings(self, call_id):
        """
        Get a list of recordings of a call

        :type call_id: str
        :param call_id: id of a call

        :rtype: types.GeneratorType
        :returns: list of recordings

        Fetch all call recordings for a call::

            list = api.get_call_recordings('callId')
        """
        path = '/users/%s/calls/%s/recordings' % (self.user_id, call_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def list_call_transcriptions(self, call_id):
        """
        Get a list of transcriptions of a call

        :type call_id: str
        :param call_id: id of a call

        :rtype: types.GeneratorType
        :returns: list of transcriptions

        Get all transcriptions for calls::

            list = api.get_call_transcriptions('callId')
        """
        path = '/users/%s/calls/%s/transcriptions' % (self.user_id, call_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def list_call_events(self, call_id):
        """
        Get a list of events of a call

        :param str call_id: id of a call

        :rtype: types.GeneratorType
        :returns: list of events

        Fetch all events for calls::

            list = api.get_call_events('callId')
        """
        path = '/users/%s/calls/%s/events' % (self.user_id, call_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def get_call_event(self, call_id, event_id):
        """
        Get an event of a call

        :type call_id: str
        :param call_id: id of a call

        :type event_id: str
        :param event_id: id of an event

        :rtype: dict
        :returns: data of event

        Fetch information on a specific event::

            data = api.get_call_event('callId', 'eventId')
        """
        return self._make_request('get', '/users/%s/calls/%s/events/%s' % (self.user_id, call_id, event_id))[0]

    def create_call_gather(self, call_id,
                           max_digits=None,
                           inter_digit_timeout=None,
                           terminating_digits=None,
                           tag=None,
                           **kwargs):
        """
        Create a gather for a call

        :type call_id: str
        :param call_id: id of a call

        :param int max_digits: The maximum number of digits to collect, not including terminating digits (maximum 30).
        :param int inter_digit_timeout: Stop gathering if a DTMF digit is not detected in this many seconds
                (default 5.0; maximum 30.0).
        :param str terminating_digits: A string of DTMF digits that end the gather operation immediately
                if any one of them is detected
        :param str tag: A string you choose that will be included with the response and events for
                this gather operation.

        :rtype: str
        :returns: id of create of gather

        Create gather for only single digit::

            gather_id = api.create_call_gather('callId', max_digits = 1)
        """

        kwargs['maxDigits'] = max_digits
        kwargs['interDigitTimeout'] = inter_digit_timeout
        kwargs['terminatingDigits'] = terminating_digits
        kwargs['tag'] = tag

        return self._make_request('post', '/users/%s/calls/%s/gather' % (self.user_id, call_id), json=kwargs)[2]

    def get_call_gather(self, call_id, gather_id):
        """
        Get a gather of a call

        :type call_id: str
        :param call_id: id of a call

        :type gather_id: str
        :param gather_id: id of a gather

        :rtype: dict
        :returns: data of gather

        Get Gather information for a previously created gather::

            data = api.get_call_gather('callId', 'gatherId')
        """
        return self._make_request('get', '/users/%s/calls/%s/gather/%s' % (self.user_id, call_id, gather_id))[0]

    def update_call_gather(self, call_id, gather_id, state=None, **kwargs):
        """
        Update a gather of a call

        :type call_id: str
        :param call_id: id of a call
        :type gather_id: str
        :param gather_id: id of a gather
        :param str state: The only update allowed is state:completed to stop the gather.

        End gather::

            api.update_call_gather('callId', 'gatherId', state = 'completed')
        """
        kwargs['state'] = state
        return self._make_request('post', '/users/%s/calls/%s/gather/%s' % (self.user_id, call_id, gather_id),
                                  json=kwargs)

    # extensions

    def answer_call(self, call_id):
        """
        Answer incoming call

        :type call_id: str
        :param call_id: id of a call

        Example: Answer incoming call::

            api.answer_call('callId')
        """
        return self.update_call(call_id, state='active')

    def reject_call(self, call_id):
        """
        Reject incoming call

        :type call_id: str
        :param call_id: id of a call

        Example: Reject incoming call::

            api.reject_call('callId')
        """
        return self.update_call(call_id, state='rejected')

    def hangup_call(self, call_id):
        """
        Complete active call

        :type call_id: str
        :param call_id: id of a call

        Example: Hangup call::

            api.hangup_call('callId')
        """
        return self.update_call(call_id, state='completed')

    def enable_call_recording(self, call_id):
        """
        Turn on call recording

        :type call_id: str
        :param call_id: id of a call

        Example: Enable Call Recording::

            api.enable_call_recording('c-callId')
        """
        return self.update_call(call_id, recording_enabled=True)

    def disable_call_recording(self, call_id):
        """
        Turn off call recording

        :type call_id: str
        :param call_id: id of a call

        Example: Disable Call Recording::

            api.disable_call_recording('c-callId')
        """
        return self.update_call(call_id, recording_enabled=False)

    def toggle_call_recording(self, call_id):
        """
        Fetches the current call state and either toggles recording on or off

        :param str call_id: id of the call to toggle

        Example: Toggle the call recording::

            my_call_id = api.create_call(to='+19192223333', from_='+18281114444')
            my_call = api.get_call(my_call_id)
            print(my_call['recordingEnabled'])
            ## False

            api.toggle_call_recording(my_call_id)
            my_call = api.get_call(my_call_id)
            print(my_call['recordingEnabled'])
            ## True

            api.toggle_call_recording(my_call_id)
            my_call = api.get_call(my_call_id)
            print(my_call['recordingEnabled'])
            ## False

        """
        call_status = self.get_call(call_id)
        recording_enabled = call_status['recordingEnabled']

        if recording_enabled is True:
            return self.disable_call_recording(call_id)
        elif recording_enabled is False:
            return self.enable_call_recording(call_id)
        else:
            return call_status

    def transfer_call(self, call_id, to, caller_id=None, whisper_audio=None, callback_url=None, **kwargs):
        """
        Transfer a call

        :type call_id: str
        :param call_id: id of a call

        :type to: str
        :param to: number that the call is going to be transferred to.

        :type caller_id: str
        :param caller_id: caller id that will be used when the call is transferred

        :type whisper_audio: dict
        :param whisper_audio: audio to be played to the caller that the call will be transferred to

        :type callback_url: str
        :param callback_url: URL where the call events for the new call will be sent upon transferring

        :returns str: id of created call

        Example: Transfer with whisper::

            my_sentence = api.build_sentence(sentence = "Hello from Bandwidth",
                                 gender="Female",
                                 locale="en_UK",
                                 voice="Bridget",
                                 loop_enabled=True
                                )
            my_call = api.get_call('c-callId')
            api.transfer_call('c-callId', to = '+1234564890', caller_id = my_call['from'], whisper_audio = my_sentence )

        Example: Transfer with whisper audio playback::

            my_audio = api.build_audio_playback('http://my_site.com/file.mp3', loop_enabled=True)
            my_call = api.get_call('c-callId')
            api.transfer_call('c-callId', to = '+1234564890', whisper_audio = my_audio )

        """

        return self.update_call(call_id,
                                state='transferring',
                                transfer_caller_id=caller_id,
                                transfer_to=to,
                                callback_url=callback_url,
                                whisper_audio=whisper_audio,
                                **kwargs)

    def list_applications(self, size=None, **kwargs):
        """
        Get a list of user's applications

        :param int size: Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of applications

        Example: Fetch and print all applications::

            apps = api.list_applications()
            print(list(apps))

        Example: Iterate over all applications to find specific name::

            apps = api.list_applications(size=20)

            app_name = ""
            while app_name != "MyAppName":
                my_app = next(apps)
                app_name = my_app["name"]

            print(my_app)


            ## {   'autoAnswer': True,
            ##     'callbackHttpMethod': 'get',
            ##     'id': 'a-asdf',
            ##     'incomingCallUrl': 'https://test.com/callcallback/',
            ##     'incomingMessageUrl': 'https://test.com/msgcallback/',
            ##     'name': 'MyAppName'
            ## }

        """
        kwargs["size"] = size
        path = '/users/%s/applications' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_application(self,
                           name,
                           incoming_call_url=None,
                           incoming_call_url_callback_timeout=None,
                           incoming_call_fallback_url=None,
                           incoming_message_url=None,
                           incoming_message_url_callback_timeout=None,
                           incoming_message_fallback_url=None,
                           callback_http_method=None,
                           auto_answer=None,
                           **kwargs):
        """
        Creates an application that can handle calls and messages for one of your phone number.

        :param str name: A name you choose for this application (required).
        :param str incoming_call_url: A URL where call events will be sent for an inbound call.
        :param str incoming_call_url_callback_timeout: Determine how long should the platform wait for
            inconmingCallUrl's response before timing out in milliseconds.
        :param str incoming_call_fallback_url: The URL used to send the callback event
            if the request to incomingCallUrl fails.
        :param str incoming_message_url: A URL where message events will be sent for an inbound SMS message
        :param str incoming_message_url_callback_timeout: Determine how long should the platform wait for
            incomingMessageUrl's response before timing out in milliseconds.
        :param str incoming_message_fallback_url: The URL used to send the callback event if the request to
            incomingMessageUrl fails.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.\
            (If not set the default is HTTP POST)
        :param str auto_answer: Determines whether or not an incoming call should be automatically answered. \
            Default value is 'true'.

        :rtype: str
        :returns: id of created application

        Example: Create Application::

            my_app_id = api.create_application( name                 = "MyFirstApp",
                                                incoming_call_url    = "http://callback.com/calls",
                                                incoming_message_url  = "http://callback.com/messages",
                                                callback_http_method = "GET")

            print(my_app_id)
            ## a-1232asf123

            my_app = api.get_application(my_app_id)
            print(my_app)
            ## {   'autoAnswer'        : True,
            ##     'callbackHttpMethod': 'get',
            ##     'id'                : 'a-1232asf123',
            ##     'incomingCallUrl'   : 'http://callback.com/calls',
            ##     'incomingMessageUrl': 'http://callback.com/messages',
            ##     'incomingSmsUrl'    : 'http://callback.com/messages',
            ##     'name'              : 'MyFirstApp2'
            ## }

            print(my_app["id"])
            ## a-1232asf123

        """
        kwargs["name"] = name
        kwargs["incomingCallUrl"] = incoming_call_url
        kwargs[
            "incomingCallUrlCallbackTimeout"] = incoming_call_url_callback_timeout
        kwargs["incomingCallFallbackUrl"] = incoming_call_fallback_url
        kwargs["incomingMessageUrl"] = incoming_message_url
        kwargs[
            "incomingMessageUrlCallbackTimeout"] = incoming_message_url_callback_timeout
        kwargs["incomingMessageFallbackUrl"] = incoming_message_fallback_url
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["autoAnswer"] = auto_answer

        return self._make_request('post', '/users/%s/applications' % self.user_id, json=kwargs)[2]

    def get_application(self, app_id):
        """
        Gets information about an application

        :type app_id: str
        :param app_id: id of an application

        :rtype: dict
        :returns: application information

        Example: Fetch single application::

            my_app = api.get_application(my_app_id)
            print(my_app)
            ## {   'autoAnswer': True,
            ##     'callbackHttpMethod': 'get',
            ##     'id': 'a-1232asf123',
            ##     'incomingCallUrl': 'http://callback.com/calls',
            ##     'incomingMessageUrl': 'http://callback.com/messages',
            ##     'incomingSmsUrl': 'http://callback.com/messages',
            ##     'name': 'MyFirstApp2'
            ## }

            print(my_app["id"])
            ## a-1232asf123
        """
        return self._make_request('get', '/users/%s/applications/%s' % (self.user_id, app_id))[0]

    def update_application(self, app_id,
                           name=None,
                           incoming_call_url=None,
                           incoming_call_url_callback_timeout=None,
                           incoming_call_fallback_url=None,
                           incoming_message_url=None,
                           incoming_message_url_callback_timeout=None,
                           incoming_message_fallback_url=None,
                           callback_http_method=None,
                           auto_answer=None,
                           **kwargs):
        """
        Updates an application that can handle calls and messages for one of your phone number.

        :param str app_id: The Id of the application to upate (a-123)
        :param str name: A name you choose for this application (required).
        :param str incoming_call_url: A URL where call events will be sent for an inbound call.
        :param str incoming_call_url_callback_timeout: Determine how long should the platform wait for
            inconmingCallUrl's response before timing out in milliseconds.
        :param str incoming_call_fallback_url: The URL used to send the callback event
            if the request to incomingCallUrl fails.
        :param str incoming_message_url: A URL where message events will be sent for an inbound SMS message
        :param str incoming_message_url_callback_timeout: Determine how long should the platform wait for
            incomingMessageUrl's response before timing out in milliseconds.
        :param str incoming_message_fallback_url: The URL used to send the callback event if the request to
            incomingMessageUrl fails.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.\
            (If not set the default is HTTP POST)
        :param str auto_answer: Determines whether or not an incoming call should be automatically answered. \
            Default value is 'true'.

        :rtype: str
        :returns: id of created application

        Example: Update Existing Application::

            my_app_id = api.create_application( name                 = "MyFirstApp",
                                                incoming_call_url    = "http://callback.com/calls",
                                                incoming_message_url  = "http://callback.com/messages",
                                                callback_http_method = "GET")

            print(my_app_id)
            ## a-1232asf123

            my_app = api.get_application(my_app_id)
            print(my_app)
            {   'autoAnswer'        : True,
                'callbackHttpMethod': 'get',
                'id'                : 'a-1232asf123',
                'incomingCallUrl'   : 'http://callback.com/calls',
                'incomingMessageUrl': 'http://callback.com/messages',
                'incomingSmsUrl'    : 'http://callback.com/messages',
                'name'              : 'MyFirstApp'
            }

            api.update_application(my_app_id, name = "My Updated App")

            my_app = api.get_application(my_app_id)
            print(my_app)
            {   'autoAnswer'        : True,
                'callbackHttpMethod': 'get',
                'id'                : 'a-1232asf123',
                'incomingCallUrl'   : 'http://callback.com/calls',
                'incomingMessageUrl': 'http://callback.com/messages',
                'incomingSmsUrl'    : 'http://callback.com/messages',
                'name'              : 'My Updated App'
            }

        """
        kwargs["name"] = name
        kwargs["incomingCallUrl"] = incoming_call_url
        kwargs[
            "incomingCallUrlCallbackTimeout"] = incoming_call_url_callback_timeout
        kwargs["incomingCallFallbackUrl"] = incoming_call_fallback_url
        kwargs["incomingMessageUrl"] = incoming_message_url
        kwargs[
            "incomingMessageUrlCallbackTimeout"] = incoming_message_url_callback_timeout
        kwargs["incomingMessageFallbackUrl"] = incoming_message_fallback_url
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["autoAnswer"] = auto_answer

        self._make_request('post', '/users/%s/applications/%s' % (self.user_id, app_id), json=kwargs)

    def delete_application(self, app_id):
        """
        Remove an application

        :type app_id: str
        :param app_id: id of an application

        Example: Delete single application::

            api.delete_application('a-appId')

            try :
                api.get_application('a-appId')
            except CatapultException as err:
                print(err.message)
            ## The application a-appId could not be found

        """
        self._make_request(
            'delete', '/users/%s/applications/%s' % (self.user_id, app_id))

    def search_available_local_numbers(self,
                                       city=None,
                                       state=None,
                                       zip_code=None,
                                       area_code=None,
                                       local_number=None,
                                       in_local_calling_area=None,
                                       quantity=None,
                                       pattern=None,
                                       **kwargs):
        """
        Searches for available local or toll free numbers.

        :param str city: A city name
        :param str state: A two-letter US state abbreviation
        :param str zip_code: A 5-digit US ZIP code
        :param str area_code: A 3-digit telephone area code
        :param str local_number: It is defined as the first digits of a telephone number inside an area code for
            filtering the results. It must have at least 3 digits and the areaCode field must be filled.
        :param str in_local_calling_area: Boolean value to indicate that the search for available numbers
            must consider overlayed areas.
        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)
        :param str pattern: A number pattern that may include letters, digits, and the wildcard characters

        :rtype: list
        :returns: list of numbers

        Example: Search for 3 910 numbers::

            numbers = api.search_available_local_numbers(area_code = '910', quantity = 3)

            print(numbers)

            ## [   {   'city'          : 'WILMINGTON',
            ##         'nationalNumber': '(910) 444-0230',
            ##         'number'        : '+19104440230',
            ##         'price'         : '0.35',
            ##         'rateCenter'    : 'WILMINGTON',
            ##         'state'         : 'NC'},
            ##     {   'city'          : 'WILMINGTON',
            ##         'nationalNumber': '(910) 444-0263',
            ##         'number'        : '+19104440263',
            ##         'price'         : '0.35',
            ##         'rateCenter'    : 'WILMINGTON',
            ##         'state'         : 'NC'},
            ##     {   'city'          : 'WILMINGTON',
            ##         'nationalNumber': '(910) 444-0268',
            ##         'number'        : '+19104440268',
            ##         'price'         : '0.35',
            ##         'rateCenter'    : 'WILMINGTON',
            ##         'state'         : 'NC'}
            ## ]

            print(numbers[0]["number"])
            ## +19104440230

        """
        kwargs["city"] = city
        kwargs["state"] = state
        kwargs["zip"] = zip_code
        kwargs["areaCode"] = area_code
        kwargs["localNumber"] = local_number
        kwargs["inLocalCallingArea"] = in_local_calling_area
        kwargs["quantity"] = quantity
        kwargs["pattern"] = pattern
        return self._make_request('get', '/availableNumbers/local', params=kwargs)[0]

    def search_available_toll_free_numbers(self, quantity=None, pattern=None, **kwargs):
        """
        Searches for available local or toll free numbers.

        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)
        :param str pattern:  A number pattern that may include letters, digits, and the wildcard characters

        :rtype: list
        :returns: list of numbers

        Example: Search for 3 toll free numbers with pattern 456::

            numbers = api.search_available_toll_free_numbers(pattern = '*456', quantity = 3)

            print(numbers)

            ## [   {   'nationalNumber': '(844) 489-0456',
            ##         'number'        : '+18444890456',
            ##         'patternMatch'  : '           456',
            ##         'price'         : '0.75'},
            ##     {   'nationalNumber': '(844) 498-2456',
            ##         'number'        : '+18444982456',
            ##         'patternMatch'  : '           456',
            ##         'price'         : '0.75'},
            ##     {   'nationalNumber': '(844) 509-4566',
            ##         'number'        : '+18445094566',
            ##         'patternMatch'  : '          456 ',
            ##         'price'         : '0.75'}]

            print(numbers[0]["number"])
            ## +18444890456


        """
        kwargs["quantity"] = quantity
        kwargs["pattern"] = pattern
        return self._make_request('get', '/availableNumbers/tollFree', params=kwargs)[0]

    def search_and_order_local_numbers(self,
                                       city=None,
                                       state=None,
                                       zip_code=None,
                                       area_code=None,
                                       local_number=None,
                                       in_local_calling_area=None,
                                       quantity=None,
                                       **kwargs):
        """
        Searches and orders for available local numbers.

        :param str city: A city name
        :param str state: A two-letter US state abbreviation
        :param str zip_code: A 5-digit US ZIP code
        :param str area_code: A 3-digit telephone area code
        :param str local_number: It is defined as the first digits of a telephone number inside an area code for
            filtering the results. It must have at least 3 digits and the areaCode field must be filled.
        :param str in_local_calling_area: Boolean value to indicate that the search for available numbers
            must consider overlayed areas.
        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)

        :rtype: list
        :returns: list of ordered numbers

        Example: Search _and_ order a single number::

            ordered_numbers = api.search_and_order_available_numbers(zip = '27606', quantity = 1)

            print(ordered_number)

            ## [   {   'city'          : 'RALEIGH',
            ##         'id'            : 'n-abc',
            ##         'location'      : 'https://api.catapult.inetwork.com/v1/users/u-12/phoneNumbers/n-abc',
            ##         'nationalNumber': '(919) 222-4444',
            ##         'number'        : '+19192224444',
            ##         'price'         : '0.35',
            ##         'state'         : 'NC'}]


        """
        kwargs["city"] = city
        kwargs["state"] = state
        kwargs["zip"] = zip_code
        kwargs["areaCode"] = area_code
        kwargs["localNumber"] = local_number
        kwargs["inLocalCallingArea"] = in_local_calling_area
        kwargs["quantity"] = quantity
        number_list = self._make_request(
            'post', '/availableNumbers/local', params=kwargs)[0]
        for item in number_list:
            item['id'] = item.get('location', '').split('/')[-1]
        return number_list

    def search_and_order_toll_free_numbers(self, quantity, **kwargs):
        """
        Searches for available local or toll free numbers.

        Query parameters for toll free numbers
        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)

        :rtype: list
        :returns: list of numbers

        Example: Search then order a single toll-free number::

            numbers = api.search_and_order_toll_free_numbers(quantity = 1)

            print(numbers)

            ## [   {   'location'      : 'https://api.catapult.inetwork.com/v1/users/u-123/phoneNumbers/n-abc',
            ##         'nationalNumber': '(844) 484-1048',
            ##         'number'        : '+18444841048',
            ##         'price'         : '0.75'}]

            print(numbers[0]["number"])
            ## +18444841048

        """
        kwargs["quantity"] = quantity
        list = self._make_request(
            'post', '/availableNumbers/tollFree', params=kwargs)[0]
        for item in list:
            item['id'] = item.get('location', '').split('/')[-1]
        return list

    def list_bridges(self, size=None, **kwargs):
        """
        Get a list of bridges

        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items.
            If no value is specified the default value is 25. (Maximum value 1000)

        :rtype: types.GeneratorType
        :returns: list of bridges

        Example: List bridges 1000 at a time::

            bridges = api.list_bridges(size=1000)

            for bridge in bridges:
                print(bridge["id"])

            ## brg-6mv7pi22i
            ## brg-3emq7olua
            ## brg-bbufdc7yq
            ## brg-dvpvd7cuy
            ## brg-5ws2buzmq
        """
        kwargs["size"] = size
        path = '/users/%s/bridges' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_bridge(self, call_ids=None, bridge_audio=None, **kwargs):
        """
        Create a bridge

        :param bool bridge_audio: Enable/Disable two way audio path (default = true)
        :param str call_ids: The first of the call ids in the bridge. If either of the call ids is not provided the
            bridge is logically created and it can be used to place calls later.

        :rtype: str
        :returns: id of created bridge

        Example: Create bridge with 2 calls and audio::

            bridge_id = api.create_bridge(call_ids = ['callId1', 'callId2'], bridge_audio = True)

            print(bridge_id)
            # brg-123
        """
        kwargs["callIds"] = call_ids
        kwargs["bridgeAudio"] = bridge_audio
        return self._make_request('post', '/users/%s/bridges' % self.user_id, json=kwargs)[2]

    def get_bridge(self, bridge_id):
        """
        Gets information about a bridge

        :type bridge_id: str
        :param bridge_id: id of a bridge

        :rtype: dict
        :returns: bridge information

        Example: Fetch single bridge by ID::

            my_bridge = api.get_bridge('brg-bridgeId')
            print(my_bridge)

            ## {   'bridgeAudio': True,
            ##     'calls'      : 'https://api.catapult.inetwork.com/v1/users/u-123/bridges/brg-bridgeId/calls',
            ##     'createdTime': '2017-01-26T01:15:09Z',
            ##     'id'         : 'brg-bridgeId',
            ##     'state'      : 'created'}

            print(my_bridge["state"])
            ## created
        """
        return self._make_request('get', '/users/%s/bridges/%s' % (self.user_id, bridge_id))[0]

    def update_bridge(self, bridge_id, call_ids=None, bridge_audio=None, **kwargs):
        """
        Update a bridge

        :type bridge_id: str
        :param bridge_id: id of a bridge

        :param bool bridge_audio: Enable/Disable two way audio path (default = true)
        :param str call_ids: The first of the call ids in the bridge. If either of the call ids
                is not provided the bridge is logically created and it can be
                used to place calls later.

        Example: stop bridging audio::

            my_bridge = api.get_bridge('brg-bridgeId')

            print(my_bridge["bridgeAudio"])
            ## True

            api.update_bridge(my_bridge['id'], call_ids = ['callId1', 'callId2'], bridge_audio = False)
            my_bridge = api.get_bridge(my_bridge['id'])

            print(my_bridge["bridgeAudio"])
            ## False

        """
        kwargs["callIds"] = call_ids
        kwargs["bridgeAudio"] = bridge_audio
        self._make_request('post', '/users/%s/bridges/%s' %
                           (self.user_id, bridge_id), json=kwargs)

    def list_bridge_calls(self, bridge_id):
        """
        Get a list of calls of a bridge

        :type bridge_id: str
        :param bridge_id: id of a bridge

        :rtype: types.GeneratorType
        :returns: list of calls

        Example: Fetch all calls that were in a bridge::

            call_list = api.get_bridge_calls('bridgeId')

            print(list(call_list))
            ## [
            ##     {
            ##         "activeTime"      : "2013-05-22T19:49:39Z",
            ##         "direction"       : "out",
            ##         "from"            : "{fromNumber}",
            ##         "id"              : "{callId1}",
            ##         "bridgeId"        : "{bridgeId}",
            ##         "startTime"       : "2013-05-22T19:49:35Z",
            ##         "state"           : "active",
            ##         "to"              : "{toNumber1}",
            ##         "recordingEnabled": false,
            ##         "events"          : "https://api.catapult.inetwork.com/v1/users/{userId}/calls/{callId1}/events",
            ##         "bridge"          : "https://api.catapult.inetwork.com/v1/users/{userId}/bridges/{bridgeId}"
            ##     },
            ##     {
            ##         "activeTime"      : "2013-05-22T19:50:16Z",
            ##         "direction"       : "out",
            ##         "from"            : "{fromNumber}",
            ##         "id"              : "{callId2}",
            ##         "bridgeId"        : "{bridgeId}",
            ##         "startTime"       : "2013-05-22T19:50:16Z",
            ##         "state"           : "active",
            ##         "to"              : "{toNumber2}",
            ##         "recordingEnabled": false,
            ##         "events"          : "https://api.catapult.inetwork.com/v1/users/{userId}/calls/{callId2}/events",
            ##         "bridge"          : "https://api.catapult.inetwork.com/v1/users/{userId}/bridges/{bridgeId}"
            ##     }
            ## ]
        """
        path = '/users/%s/bridges/%s/calls' % (self.user_id, bridge_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def play_audio_to_bridge(self, bridge_id,
                             file_url=None,
                             sentence=None,
                             gender=None,
                             locale=None,
                             voice=None,
                             loop_enabled=None,
                             **kwargs):
        """
        Play audio to a bridge

        :param str bridge_id: id of a bridge
        :param str file_url: The location of an audio file to play (WAV and MP3 supported).
        :param str sentence: The sentence to speak.
        :param str gender: The gender of the voice used to synthesize the sentence.
        :param str locale: The locale used to get the accent of the voice used to synthesize the sentence.
        :param str voice: The voice to speak the sentence.
        :param bool loop_enabled: When value is true, the audio will keep playing in a loop.


        Examples: Play either file for speak sentence::

            api.play_audio_to_bridge('bridgeId', fileUrl='http://host/path/file.mp3')
            api.play_audio_to_bridge('bridgeId', sentence='Press 0 to complete call', gender='female')

            # or with extension methods
            api.play_audio_file_to_bridge('bridgeId', 'http://host/path/file.mp3')
            api.speak_sentence_to_bridge('bridgeId', 'Hello')
        """
        kwargs["fileUrl"] = file_url
        kwargs["sentence"] = sentence
        kwargs["gender"] = gender
        kwargs["locale"] = locale
        kwargs["voice"] = voice
        kwargs["loopEnabled"] = loop_enabled
        self._make_request(
            'post', '/users/%s/bridges/%s/audio' % (self.user_id, bridge_id), json=kwargs)

    def create_conference(self,
                          from_,
                          callback_url=None,
                          callback_timeout=None,
                          callback_http_method=None,
                          fallback_url=None,
                          tag=None,
                          **kwargs):
        """
        Create a conference

        :param str ``from_``: The phone number that will host the conference (required)
        :param str callback_url: The full server URL where the conference events related to the Conference will be sent
        :param str callback_timeout: Determine how long should the
            platform wait for callbackUrl's response before timing out in milliseconds.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST. \
            Values are "GET" or "POST" (if not set the default is POST).
        :param str fallback_url: The full server URL used to send the callback event if the request to callbackUrl
            fails or timesout
        :param str tag: A string that will be included in the callback events of the conference.

        :rtype: str
        :returns: id of created conference

        Example: create simple conference::

            conference_id = api.create_conference('+12018994444')

            print(conference_id)
            ## conf-ixaagbn5wcyskisiy

        Example: create conference with extra parameters::

            conference_id = api.create_conference(from_ = "+12018994444", callback_url = "http://google.com",
                                                  callback_timeout= 2000, fallback_url = "http://yahoo.com")

            print(conference_id)
            ## conf-ixaagbn5wcyskisiy

            my_conf = api.get_conference(conference_id)

            print(my_conf)
            ## {   'activeMembers'     : 0,
            ##     'callbackHttpMethod': 'post',
            ##     'callbackTimeout'   : 2000,
            ##     'callbackUrl'       : 'http://google.com',
            ##     'createdTime'       : '2017-01-26T01:58:59Z',
            ##     'fallbackUrl'       : 'http://yahoo.com',
            ##     'from'              : '+12018994444',
            ##     'hold'              : False,
            ##     'id'                : 'conf-ixaagbn5wcyskisiy',
            ##     'mute'              : False,
            ##     'state'             : 'created'}
        """

        kwargs["from"] = from_
        kwargs["callbackUrl"] = callback_url
        kwargs["callbackTimeout"] = callback_timeout
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["fallbackUrl"] = fallback_url
        kwargs["tag"] = tag

        return self._make_request('post', '/users/%s/conferences' % self.user_id, json=kwargs)[2]

    def get_conference(self, conference_id):
        """
        Get information about a conference

        :type conference_id: str
        :param conference_id: id of a conference

        :rtype: dict
        :returns: conference information

        Example: Create then fetch conference::

            conference_id = api.create_conference(from_ = "+12018994444", callback_url = "http://google.com",
                                                  callback_timeout= 2000, fallback_url = "http://yahoo.com")

            print(conference_id)
            ## conf-ixaagbn5wcyskisiy

            my_conf = api.get_conference(conference_id)

            print(my_conf)
            ## {   'activeMembers'     : 0,
            ##     'callbackHttpMethod': 'post',
            ##     'callbackTimeout'   : 2000,
            ##     'callbackUrl'       : 'http://google.com',
            ##     'createdTime'       : '2017-01-26T01:58:59Z',
            ##     'fallbackUrl'       : 'http://yahoo.com',
            ##     'from'              : '+12018994444',
            ##     'hold'              : False,
            ##     'id'                : 'conf-ixaagbn5wcyskisiy',
            ##     'mute'              : False,
            ##     'state'             : 'created'}
        """
        return self._make_request('get', '/users/%s/conferences/%s' % (self.user_id, conference_id))[0]

    def update_conference(self,
                          conference_id,
                          state=None,
                          mute=None,
                          hold=None,
                          callback_url=None,
                          callback_timeout=None,
                          callback_http_method=None,
                          fallback_url=None,
                          tag=None,
                          **kwargs):
        """
        Update a conference

        :param str conference_id: id of a conference
        :param str state: Conference state. Possible state values are: "completed" to terminate the conference.
        :param str mute: If "true", all member can't speak in the conference.\
            If "false", all members can speak in the conference
        :param str hold: If "true", all member can't hear or speak in the conference. \
            If "false", all members can hear and speak in the conference
        :param str callback_url: The full server URL where the conference events related to the conference will be sent
        :param str callback_timeout: Determine how long should the platform wait for callbackUrl's response before
            timing out in milliseconds.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST. \
            Values are "GET" or "POST" (if not set the default is POST).
        :param str fallback_url: The full server URL used to send the callback event
            if the request to callbackUrl fails.
        :param str tag: A string that will be included in the callback events of the conference.

        Example: End conference::

            api.update_conference('conferenceId', state='completed')

        """

        kwargs["state"] = state
        kwargs["mute"] = mute
        kwargs["hold"] = hold
        kwargs["callbackUrl"] = callback_url
        kwargs["callbackTimeout"] = callback_timeout
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["fallbackUrl"] = fallback_url
        kwargs["tag"] = tag

        self._make_request('post', '/users/%s/conferences/%s' %
                           (self.user_id, conference_id), json=kwargs)

    def play_audio_to_conference(self,
                                 conference_id,
                                 file_url=None,
                                 sentence=None,
                                 gender=None,
                                 locale=None,
                                 voice=None,
                                 loop_enabled=None,
                                 **kwargs):
        """
        Play audio to a conference

        :type conference_id: str
        :param conference_id: id of a conference

        :param str file_url: The location of an audio file to play (WAV and MP3 supported).
        :param str sentence: The sentence to speak.
        :param str gender: The gender of the voice used to synthesize the sentence.
        :param str locale: The locale used to get the accent of the voice used to synthesize the sentence.
        :param str voice: The voice to speak the sentence.
        :param str loop_enabled: When value is true, the audio will keep playing in a loop.


        Example: Play audio file to conference::

            api.play_audio_to_conference('conferenceId', fileUrl = 'http://host/path/file.mp3')

        Example: Speak Sentence to conference::

            api.play_audio_to_conference('conferenceId', sentence='Press 0 to complete call', gender='female')

        Example: Use Extensions methods::

            # or with extension methods
            api.play_audio_file_to_conference('conferenceId', 'http://host/path/file.mp3')
            api.speak_sentence_to_conference('conferenceId', 'Hello')
        """
        kwargs['fileUrl'] = file_url
        kwargs['sentence'] = sentence
        kwargs['gender'] = gender
        kwargs['locale'] = locale
        kwargs['voice'] = voice
        kwargs['loopEnabled'] = loop_enabled

        self._make_request('post', '/users/%s/conferences/%s/audio' %
                           (self.user_id, conference_id), json=kwargs)

    def list_conference_members(self, conference_id):
        """
        Get a list of members of a conference

        :type conference_id: str
        :param conference_id: id of a conference

        :rtype: types.GeneratorType
        :returns: list of recordings

        Example: Fetch and list conference members::

            my_conf_id = api.create_conference(from_='+19192223333')
            print(my_conf)
            # conf-confId

            my_call_id = api.create_call(from_='+19192223333', to='+19192223334', conference_id= 'conf-confId')
            print(my_call_id)
            # c-callId

            my_conf_member_id = api.create_conference_member(my_conf_id, call_id=my_call_id)
            print(my_conf_member_id)
            # member-memberId

            my_conference_members = list_conference_members(my_conf_id)

            print(list(my_conference_members))

            ## [
            ##    {
            ##       'addedTime'  :'2017-01-30T22:01:11Z',
            ##       'call'       :'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##       'hold'       :False,
            ##       'id'         :'member-memberId',
            ##       'joinTone'   :False,
            ##       'leavingTone':False,
            ##       'mute'       :False,
            ##       'removedTime':'2017-01-30T22:01:21Z',
            ##       'state'      :'completed'
            ##    }
            ## ]



        """
        path = '/users/%s/conferences/%s/members' % (
            self.user_id, conference_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def create_conference_member(self,
                                 conference_id,
                                 call_id=None,
                                 join_tone=None,
                                 leaving_tone=None,
                                 mute=None,
                                 hold=None,
                                 **kwargs):
        """
        Create a conference member for a conference

        :type conference_id: str
        :param conference_id: id of a conference

        :param str call_id: The callId must refer to an active call that was created using this conferenceId (required)
        :param bool join_tone: If "true", will play a tone when the member joins the conference. \
            If "false", no tone is played when the member joins the conference.
        :param bool leaving_tone: If "true", will play a tone when the member leaves the conference.\
            If "false", no tone is played when the member leaves the conference.
        :param bool mute: If "true", member can't speak in the conference.\
            If "false", this members can speak in the conference (unless set at the conference level).
        :param bool hold: If "true", member can't hear or speak in the conference.\
            If "false", member can hear and speak in the conference (unless set at the conference level).

        :rtype: str
        :returns: id of create of conference member

        Example: Create Conference and add member::

            my_conf_id = api.create_conference(from_='+19192223333')
            print(my_conf)
            # conf-confId

            my_call_id = api.create_call(from_='+19192223333', to='+19192223334', conference_id= 'conf-confId')
            print(my_call_id)
            # c-callId

            my_conf_member_id = api.create_conference_member(my_conf_id, call_id=my_call_id, join_tone=True)
            print(my_conf_member_id)
            # member-memberId

            my_conf_member = api.get_conference_member(my_conf_id, my_member_id)
            print(my_conf_member)

            ## {
            ##     'addedTime': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : False,
            ##     'id'           : 'member-memberId',
            ##     'joinTone'     : False,
            ##     'leavingTone'  : False,
            ##     'mute'         : False,
            ##     'removedTime'  : '2017-01-30T22:01:21Z',
            ##     'state'        : 'completed'
            ## }

        """
        kwargs['callId'] = call_id
        kwargs['joinTone'] = join_tone
        kwargs['leavingTone'] = leaving_tone
        kwargs['mute'] = mute
        kwargs['hold'] = hold

        path = '/users/%s/conferences/%s/members' % (
            self.user_id, conference_id)
        return self._make_request('post', path, json=kwargs)[2]

    def get_conference_member(self, conference_id, member_id):
        """
        Get a conference member

        :type conference_id: str
        :param conference_id: id of a conference

        :type member_id: str
        :param member_id: id of a member

        :rtype: dict
        :returns: data of conference member

        Example: Create Conference and add member::

            my_conf_id = api.create_conference(from_='+19192223333')
            print(my_conf)
            # conf-confId

            my_call_id = api.create_call(from_='+19192223333', to='+19192223334', conference_id= 'conf-confId')
            print(my_call_id)
            # c-callId

            my_conf_member_id = api.create_conference_member(my_conf_id, call_id=my_call_id, join_tone=True)
            print(my_conf_member_id)
            # member-memberId

            my_conf_member = api.get_conference_member(my_conf_id, my_member_id)
            print(my_conf_member)

            ## {
            ##     'addedTime': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : False,
            ##     'id'           : 'member-memberId',
            ##     'joinTone'     : True,
            ##     'leavingTone'  : False,
            ##     'mute'         : False,
            ##     'removedTime'  : '2017-01-30T22:01:21Z',
            ##     'state'        : 'active'
            ## }
        """
        path = '/users/%s/conferences/%s/members/%s' % (
            self.user_id, conference_id, member_id)
        return self._make_request('get', path)[0]

    def update_conference_member(self,
                                 conference_id,
                                 member_id,
                                 join_tone=None,
                                 leaving_tone=None,
                                 mute=None,
                                 hold=None,
                                 **kwargs):
        """
        Update a conference member

        :param str conference_id: id of a conference
        :param str member_id: id of a conference member
        :param bool join_tone: If "true", will play a tone when the member joins the conference. \
            If "false", no tone is played when the member joins the conference.
        :param bool leaving_tone: If "true", will play a tone when the member leaves the conference. \
            If "false", no tone is played when the member leaves the conference.
        :param bool mute: If "true", member can't speak in the conference. \
            If "false", this members can speak in the conference (unless set at the conference level).
        :param bool hold: If "true", member can't hear or speak in the conference. \
            If "false", member can hear and speak in the conference (unless set at the conference level).

        Example: update conference member::

            my_conf_id = api.create_conference(from_='+19192223333')
            print(my_conf)
            # conf-confId

            my_call_id = api.create_call(from_='+19192223333', to='+19192223334', conference_id= 'conf-confId')
            print(my_call_id)
            # c-callId

            my_conf_member_id = api.create_conference_member(my_conf_id, call_id=my_call_id, join_tone=True)
            print(my_conf_member_id)
            # member-memberId

            my_conf_member = api.get_conference_member(my_conf_id, my_member_id)
            print(my_conf_member)

            ## {
            ##     'addedTime': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : False,
            ##     'id'           : 'member-memberId',
            ##     'joinTone'     : True,
            ##     'leavingTone'  : False,
            ##     'mute'         : False,
            ##     'removedTime'  : '2017-01-30T22:01:21Z',
            ##     'state'        : 'active'
            ## }

            api.update_conference_member(my_conf_id, my_member_id, mute=True, hold=True)

            my_conf = api.get_conference_member(my_member_id)

            ## {
            ##     'addedTime': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : True,
            ##     'id'           : 'member-memberId',
            ##     'joinTone'     : True,
            ##     'leavingTone'  : False,
            ##     'mute'         : True,
            ##     'removedTime'  : '2017-01-30T22:01:21Z',
            ##     'state'        : 'active'
            ## }
        """
        kwargs['joinTone'] = join_tone
        kwargs['leavingTone'] = leaving_tone
        kwargs['mute'] = mute
        kwargs['hold'] = hold

        path = '/users/%s/conferences/%s/members/%s' % (
            self.user_id, conference_id, member_id)
        self._make_request('post', path, json=kwargs)

    def play_audio_to_conference_member(self,
                                        conference_id,
                                        member_id,
                                        file_url=None,
                                        sentence=None,
                                        gender=None,
                                        locale=None,
                                        voice=None,
                                        loop_enabled=None,
                                        **kwargs):
        """
        Play audio to a conference member

        :param str conference_id: id of a conference
        :param str member_id: id of a conference member
        :param str file_url: The location of an audio file to play (WAV and MP3 supported).
        :param str sentence: The sentence to speak.
        :param str gender: The gender of the voice used to synthesize the sentence.
        :param str locale: The locale used to get the accent of the voice used to synthesize the sentence.
        :param str voice: The voice to speak the sentence.
        :param str loop_enabled: When value is true, the audio will keep playing in a loop.

        Example: Play audio to specific conference member::

            api.play_audio_to_conference_member('conferenceId', 'memberId', fileUrl=http://host/path/file.mp3)
            api.play_audio_to_conference_member('conferenceId', 'memberId',
                                                sentence='Press 0 to complete call', gender='female')

            # or with extension methods
            api.play_audio_file_to_conference_member('conferenceId', 'memberId', 'http://host/path/file.mp3')
            api.speak_sentence_to_conference_member('conferenceId', 'memberId', 'Hello')
        """

        kwargs['fileUrl'] = file_url
        kwargs['sentence'] = sentence
        kwargs['gender'] = gender
        kwargs['locale'] = locale
        kwargs['voice'] = voice
        kwargs['loopEnabled'] = loop_enabled

        path = '/users/%s/conferences/%s/members/%s/audio' % (
            self.user_id, conference_id, member_id)
        self._make_request('post', path, json=kwargs)

    # extensions

    def speak_sentence_to_conference_member(self,
                                            conference_id,
                                            member_id,
                                            sentence,
                                            gender='female',
                                            voice='susan',
                                            locale='en_US',
                                            tag=None):
        """
        Speak sentence to a conference member

        :type conference_id: str
        :param conference_id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type sentence: str
        :param sentence: sentence to say

        :type gender: str
        :param gender: gender of voice

        :type voice: str
        :param voice: voice name

        :type locale: str
        :param locale: locale name

        :type tag: str
        :param tag: A string that will be included in the callback events of the call.

        Example: Speak sentence to specific conference member::

            api.speak_sentence_to_conference_member('conferenceId', 'memberId', 'Hello')
        """
        self.play_audio_to_conference_member(conference_id, member_id,
                                             sentence=sentence,
                                             gender=gender,
                                             voice=voice,
                                             locale=locale,
                                             tag=tag
                                             )

    def play_audio_file_to_conference_member(self, conference_id, member_id, file_url, tag=None):
        """
        Play audio file to a conference member

        :type conference_id: str
        :param conference_id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type file_url: str
        :param file_url: URL to remote file to play

        :type tag: str
        :param tag: A string that will be included in the callback events of the call.

        Example: Play an audio file to specific member::

            api.play_audio_file_to_conference_member('conferenceId', 'memberId', 'http://host/path/file.mp3')
        """

        self.play_audio_to_conference_member(conference_id, member_id,
                                             file_url=file_url,
                                             tag=tag
                                             )

    def remove_conference_member(self, conference_id, member_id):
        """
        Remove a conference member

        :type conference_id: str
        :param conference_id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        Example: Remove Member from Conference::

            my_conf = api.get_conference('conferenceId')
            my_conf_members = list(api.list_conference_members(my_conf['id']))
            print(my_conf_members)

            ## [{ 'addedTime'  : '2017-01-30T23:17:11Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId',
            ##    'joinTone'   : False,
            ##    'leavingTone': False,
            ##    'mute'       : False,
            ##    'state'      : 'active'},
            ##  { 'addedTime'  : '2017-01-30T23:17:14Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId2',
            ##    'joinTone'   : False,
            ##    'leavingTone': False,
            ##    'mute'       : False,
            ##    'state'      : 'active'}]

            api.remove_conference_member(my_conf['id'], my_conf_members[1]['id'])

            my_conf_members = list(api.list_conference_members(my_conf['id']))
            print(my_conf_members)

            ## [{ 'addedTime'  : '2017-01-30T23:17:11Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId',
            ##    'joinTone'   : False,
            ##    'leavingTone': False,
            ##    'mute'       : False,
            ##    'state'      : 'active'},
            ##  { 'addedTime'  : '2017-01-30T23:17:14Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId2',
            ##    'joinTone'   : False,
            ##    'leavingTone': False,
            ##    'mute'       : False,
            ##    'state'      : 'completed'}]

        """
        self.update_conference_member(
            conference_id, member_id, state='completed')

    def hold_conference_member(self, conference_id, member_id, hold):
        """
        Hold or unhold a conference member

        :type conference_id: str
        :param conference_id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type hold: bool
        :param hold: hold (if true) or unhold (if false) a member

        Example: Put specific conference member on hold::

            api.hold_conference_member('conferenceId', 'memberId', True)
        """
        self.update_conference_member(conference_id, member_id, hold=hold)

    def mute_conference_member(self, conference_id, member_id, mute):
        """
        Mute or unmute a conference member

        :type conference_id: str
        :param conference_id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type mute: bool
        :param mute: mute (if true) or unmute (if false) a member

        Example: Mute specific conference member::

            api.mute_conference_member('conferenceId', 'memberId', True)
        """
        self.update_conference_member(conference_id, member_id, mute=mute)

    def terminate_conference(self, conference_id):
        """
        Terminate of current conference

        :type conference_id: str
        :param conference_id: id of a conference

        Example: End the Conference::

            api.terminate_conference('conferenceId')

        """
        self.update_conference(conference_id, state='completed')

    def hold_conference(self, conference_id, hold):
        """
        Hold or unhold a conference

        :type conference_id: str
        :param conference_id: id of a conference

        :type hold: bool
        :param hold: hold (if true) or unhold (if false) a conference

        Example: Put entire confernce on hold, where no one can hear::

            api.hold_conference('conferenceId', True)
        """
        self.update_conference(conference_id, hold=hold)

    def mute_conference(self, conference_id, mute):
        """
        Mute or unmute a conference

        :type conference_id: str
        :param conference_id: id of a conference

        :type mute: bool
        :param mute: mute (if true) or unmute (if false) a conference

        Example: Mute the entire Conference, where no one can speak::

            api.mute_conference('conferenceId', True)
        """
        self.update_conference(conference_id, mute=mute)

    def list_domains(self, size=None, **kwargs):
        """
        Get a list of domains

        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items. \
            If no value is specified the default value is 25. (Maximum value 100)
        :rtype: types.GeneratorType
        :returns: list of domains

        Example: Fetch domains and print::

            domain_list = api.list_domains(size=10)
            print(list(domain_list))

            ## [{   'endpointsUrl': 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/endpoints',
            ##     'id'           : 'rd-domainId',
            ##     'name'         : 'siplearn1'},
            ## {   'endpointsUrl' : 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/endpoints',
            ##     'id'           : 'rd-domainId2',
            ##     'name'         : 'siplearn2'}]

        Example: Search for domain based on name::

            domain_list = api.list_domains(size=100)

            domain_name = ''

            while domain_name != 'My Prod Site':
                my_domain = next(domain_list)
                domain_name = my_domain['name']

            print(my_domain)
            ## {   'description' : 'Python Docs Example',
            ##     'endpointsUrl': 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/rd-domainId/endpoints',
            ##     'id'          : 'rd-domainId',
            ##     'name'        : 'My Prod Site'}


        """
        kwargs['size'] = size
        path = '/users/%s/domains' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_domain(self, name, description=None, **kwargs):
        """
        Create a domain

        :param str name: The name is a unique URI to be used in DNS lookups
        :param str description: String to describe the domain

        :rtype: str
        :returns: id of created domain

        Example: Create Domain::

            domain_id = api.create_domain(name='qwerty', description='Python Docs Example')

            print(domain_id)
            # rd-domainId
        """
        kwargs['name'] = name
        kwargs['description'] = description
        return self._make_request('post', '/users/%s/domains' % self.user_id, json=kwargs)[2]

    def get_domain(self, domain_id):
        """
        Get information about a domain

        :type domain_id: str
        :param domain_id: id of the domain

        :rtype: dict
        :returns: domain information

        Example: Create then fetch domain::

            domain_id = api.create_domain(name='qwerty', description='Python Docs Example')

            print(domain_id)
            # rd-domainId

            my_domain = api.get_domain(domain_id)

            print(my_domain)
            ## {   'description' : 'Python Docs Example',
            ##     'endpointsUrl': 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/rd-domainId/endpoints',
            ##     'id'          : 'rd-domainId',
            ##     'name'        : 'qwerty'}
        """
        return self._make_request('get', '/users/%s/domains/%s' % (self.user_id, domain_id))[0]

    def delete_domain(self, domain_id):
        """
        Delete a domain

        :type domain_id: str
        :param domain_id: id of a domain

        Example: Delete domain 'domainId'::

            api.delete_domain('domainId')
        """
        self._make_request('delete', '/users/%s/domains/%s' %
                           (self.user_id, domain_id))

    def list_domain_endpoints(self, domain_id, size=None, **kwargs):
        """
        Get a list of domain's endpoints

        :type domain_id: str
        :param domain_id: id of a domain
        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items.\
            If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of endpoints

        Example: List and iterate over::

            endpoint_list = api.list_domain_endpoints('rd-domainId', size=1000)

            for endpoint in endpoint_list:
                print(endpoint['id'])
            ##re-endpointId1
            ##re-endpointId2

        Example: List and print all::

            endpoint_list = api.list_domain_endpoints('rd-domainId', size=1000)

            print(list(endpoint_list))

            ## [
            ##     {
            ##         'applicationId':'a-appId',
            ##         'credentials'  :{
            ##             'realm'    :'creds.bwapp.bwsip.io',
            ##             'username' :'user1'
            ##         },
            ##         'description'  :"Your SIP Account",
            ##         'domainId'     :'rd-domainId',
            ##         'enabled'      :True,
            ##         'id'           :'re-endpointId1',
            ##         'name'         :'User1_endpoint',
            ##         'sipUri'       :'sip:user1@creds.bwapp.bwsip.io'
            ##     },
            ##     {
            ##         'applicationId':'a-appId',
            ##         'credentials'  :{
            ##             'realm'    :'creds1.bwapp.bwsip.io',
            ##             'username' :'user2'
            ##         },
            ##         'description'  :"Your SIP Account",
            ##         'domainId'     :'rd-domainId',
            ##         'enabled'      :True,
            ##         'id'           :'re-endpointId2',
            ##         'name'         :'User2_endpoint',
            ##         'sipUri'       :'sip:user2@creds.bwapp.bwsip.io'
            ##     }
            ## ]

        """
        kwargs['size'] = size
        path = '/users/%s/domains/%s/endpoints' % (self.user_id, domain_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_domain_endpoint(
            self,
            domain_id,
            name,
            password,
            description=None,
            application_id=None,
            enabled=True,
            **kwargs):
        """
        Create a domain endpoint

        :param str domain_id: id of a domain
        :param str name: The name of endpoint
        :param str description: String to describe the endpoint
        :param str application_id: Id of application which will handle calls and messages of this endpoint
        :param bool enabled: When set to true, SIP clients can register as this device to receive and make calls. \
            When set to false, registration, inbound, and outbound calling will not succeed.
        :param str password: Password of created SIP account

        :rtype: str
        :returns: id of endpoint

        Example: Create Endpoint on Domain 'rd-domainId'::

            endpoint_id = api.create_domain_endpoint('rd-domainId',
                                                     endpoint_name='User3_endpoint',
                                                     password='AtLeast6Chars')
            print(endpoint_id)
            # re-endpointId3

            my_endpoint = api.get_domain_endpoint(endpoint_id)
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'User3_endpoint'
            ##     },
            ##     'domainId'    :'rd-domainId',
            ##     'enabled'     :True,
            ##     'id'          :'re-endpointId3',
            ##     'name'        :'User3_endpoint',
            ##     'sipUri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }

        """
        kwargs['name'] = name
        kwargs['description'] = description
        kwargs['applicationId'] = application_id
        kwargs['enabled'] = enabled
        kwargs['credentials'] = dict(password=password)
        return self._make_request('post', '/users/%s/domains/%s/endpoints' % (self.user_id, domain_id), json=kwargs)[2]

    def get_domain_endpoint(self, domain_id, endpoint_id):
        """
        Get information about an endpoint

        :type domain_id: str
        :param domain_id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :rtype: dict
        :returns: call information

        Example: Create Endpoint on Domain 'rd-domainId' then fetch the endpoint::

            endpoint_id = api.create_domain_endpoint('rd-domainId',
                                                     endpoint_name='User3_endpoint',
                                                     password='AtLeast6Chars')
            print(endpoint_id)
            # re-endpointId3

            my_endpoint = api.get_domain_endpoint(endpoint_id)
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'User3_endpoint'
            ##     },
            ##     'domainId'    :'rd-domainId',
            ##     'enabled'     :True,
            ##     'id'          :'re-endpointId3',
            ##     'name'        :'User3_endpoint',
            ##     'sipUri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }
        """
        return self._make_request('get', '/users/%s/domains/%s/endpoints/%s' % (self.user_id,
                                                                                domain_id, endpoint_id))[0]

    def update_domain_endpoint(self,
                               domain_id,
                               endpoint_id,
                               password=None,
                               description=None,
                               application_id=None,
                               enabled=None,
                               **kwargs):
        """
        Update information about an endpoint

        :param str domain_id: id of a domain
        :param str endpoint_id: id of a endpoint
        :param str description: String to describe the endpoint
        :param str application_id: Id of application which will handle calls and messages of this endpoint
        :param bool enabled: When set to true, SIP clients can register as this device to receive and make calls. \
            When set to false, registration, inbound, and outbound calling will not succeed.
        :param str password: Password of created SIP account

        Example: Update password and disable the endpoint::


            my_endpoint = api.get_domain_endpoint('rd-domainId', 're-endpointId')
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'user5'
            ##     },
            ##     'domainId'    :'rd-domainId',
            ##     'enabled'     :True,
            ##     'id'          :'re-endpointId',
            ##     'name'        :'user3',
            ##     'sipUri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }

            api.update_domain_endpoint('rd-domainId', 're-endpointId', enabled=False, password='abc123')
            my_endpoint = api.get_domain_endpoint('rd-domainId', 're-endpointId')
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'user5'
            ##     },
            ##     'domainId'    :'rd-domainId',
            ##     'enabled'     :False,
            ##     'id'          :'re-endpointId',
            ##     'name'        :'user3',
            ##     'sipUri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }
        """

        kwargs['description'] = description
        kwargs['applicationId'] = application_id
        kwargs['enabled'] = enabled
        kwargs['credentials'] = dict(password=password)

        self._make_request('post', '/users/%s/domains/%s/endpoints/%s' %
                           (self.user_id, domain_id, endpoint_id), json=kwargs)

    def delete_domain_endpoint(self, domain_id, endpoint_id):
        """
        Remove an endpoint

        :param str domain_id: id of a domain
        :param str endpoint_id: id of a endpoint

        Example: Delete and try to fetch endpoint::

            my_endpoint = api.get_domain_endpoint('rd-domainId', 're-endpointId')
            print(my_endpoint)
            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'user5'
            ##     },
            ##     'domainId'    :'rd-domainId',
            ##     'enabled'     :False,
            ##     'id'          :'re-endpointId3ndpointId',
            ##     'name'        :'user3',
            ##     'sipUri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }
            api.delete_domain_endpoint(d, e)

            try:
                my_endpoint = api.get_domain_endpoint(d, e)
            except Exception as e:
                print(e)
            ## CatapultException(404, "The endpoint 're-endpointId' could not be found")

        """
        self._make_request(
            'delete', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, domain_id, endpoint_id))

    def create_domain_endpoint_auth_token(self, domain_id, endpoint_id, expires=3600, **kwargs):
        """
        Create auth token for an endpoint

        :param str domain_id: id of a domain
        :param str endpoint_id: id of a endpoint
        :param int expires: Duration of valid token.

        Example: Create token::

            token = api.create_domain_endpoint_auth_token('domainId', 'endpointId', 5000)
        """
        kwargs['expires'] = expires
        path = '/users/%s/domains/%s/endpoints/%s/tokens' % (
            self.user_id, domain_id, endpoint_id)
        return self._make_request('post', path, json=kwargs)[0]

    def list_errors(self, size=None, **kwargs):
        """
        Get a list of errors

        :param int size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of calls

        Example: List all errors::

            error_list = api.list_errors()

            print(list(error_list))

            # [{
            #     'category':'unavailable',
            #     'code'    :'number-allocator-unavailable',
            #     'details':[
            #         {
            #             'id'   :'ued-eh3zn3dxgiin4y',
            #             'name' :'requestPath',
            #             'value':'availableNumbers/local'
            #         },
            #         {
            #             'id'   :'ued-3fsdqiq',
            #             'name' :'remoteAddress',
            #             'value':'216.82.234.65'
            #         },
            #         {
            #             'id'   :'ued-2r4t47bwi',
            #             'name' :'requestMethod',
            #             'value':'GET'
            #         }
            #     ],
            #     'id'     :'ue-upvfv53xzca',
            #     'message':'Cannot connect to the number allocator',
            #     'time'   :'2016-03-28T18:31:33Z'
            # },
            # {
            #     'category':'unavailable',
            #     'code':'number-allocator-unavailable',
            #     'details':[
            #         {
            #             'id':'ued-kntwx7vyotalci',
            #             'name':'requestPath',
            #             'value':'availableNumbers/local'
            #         },
            #         {
            #             'id':'ued-b24vxpfskldq',
            #             'name':'remoteAddress',
            #             'value':'216.82.234.65'
            #         },
            #         {
            #             'id':'ued-ww5rcgl7zm2ydi',
            #             'name':'requestMethod',
            #             'value':'GET'
            #         }
            #     ],
            #     'id':'ue-pok2vg7kyuzaqq',
            #     'message':'Cannot connect to the number allocator',
            #     'time':'2016-03-28T18:31:33Z'
            # }]
        """
        kwargs['size'] = size
        path = '/users/%s/errors' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def get_error(self, error_id):
        """
        Get information about an error

        :type error_id: str
        :param id: id of an error
        :rtype: dict
        :returns: error information

        Example: Get information of specific error::

            error = api.get_error('ue-errorId')
            print(error)

            ## {
            ##     'category':'unavailable',
            ##     'code'    :'number-allocator-unavailable',
            ##     'details' :[
            ##         {
            ##            'id'      :'ued-kntvyotalci',
            ##            'name'    :'requestPath',
            ##            'value'   :'availableNumbers/local'
            ##         },
            ##         {
            ##            'id'      :'ued-b2dq',
            ##            'name'    :'remoteAddress',
            ##            'value'   :'216.82.234.65'
            ##         },
            ##         {
            ##            'id'      :'ued-wzm2ydi',
            ##            'name'    :'requestMethod',
            ##            'value'   :'GET'
            ##         }
            ##     ],
            ##     'id'      :'ue-errorId',
            ##     'message' :'Cannot connect to the number allocator',
            ##     'time'    :'2016-03-28T18:31:33Z'
            ## }
        """
        return self._make_request('get', '/users/%s/errors/%s' % (self.user_id, error_id))[0]

    def list_media_files(self):
        """
        Gets a list of user's media files.

        :rtype: types.GeneratorType
        :returns: list of media files

        Example: list media files and save any with the name `dog` in file name::

            media_list = api.list_media_files()
            for media in media_list:
                if 'dog' in media['mediaName'].lower():
                    stream, content_type = api.download_media_file(media['mediaName'])
                    with io.open(media['mediaName'], 'wb') as file:
                        file.write(stream.read())

        """
        path = '/users/%s/media' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def upload_media_file(self, media_name, content=None, content_type='application/octet-stream', file_path=None):
        """
        Upload a file

        :type media_name: str
        :param media_name: name of file on bandwidth server

        :type content: str|buffer|bytearray|stream|file
        :param content: content of file to upload (file object, string or buffer).
            Don't use together with file_path

        :type content_type: str
        :param content_type: mime type of file

        :type file_path: str
        :param file_path: path to file to upload. Don't use together with content

        Example: Upload text file::

            api.upload_media_file('file1.txt', 'content of file', 'text/plain')

            # with file path
            api.upload_media_file('file1.txt', file_path='/path/to/file1.txt')

        """
        is_file_path = False
        if file_path is not None and content is None:
            content = open(file_path, 'rb')
            is_file_path = True
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        try:
            return self._make_request('put', path, data=content, headers={'content-type': content_type})
        finally:
            if is_file_path:
                content.close()

    def download_media_file(self, media_name):
        """
        Download a file

        :type media_name: str
        :param media_name: name of file on bandwidth server

        :rtype (stream, str)
        :returns stream to file to download and mime type

        Example: list media files and save any with the name `dog` in file name::

            media_list = api.get_media_files()
            for media in media_list:
                if 'dog' in media['mediaName'].lower():
                    stream, content_type = api.download_media_file(media['mediaName'])
                    with io.open(media['mediaName'], 'wb') as file:
                        file.write(stream.read())
        """
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        response = self._request('get', path, stream=True)
        response.raise_for_status()
        return response.raw, response.headers['content-type']

    def delete_media_file(self, media_name):
        """
        Remove a file from the server

        :type media_name: str
        :param media_name: name of file on bandwidth server

        Example: Delete a file from server::

            api.delete_media_file('file1.txt')
        """
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        self._make_request('delete', path)

    def list_messages(self,
                      from_=None,
                      to=None,
                      from_date_time=None,
                      to_date_time=None,
                      direction=None,
                      state=None,
                      delivery_state=None,
                      sort_order=None,
                      size=None,
                      **kwargs):
        """
        Get a list of user's messages

        :param str ``from_``: The phone number to filter the messages that came from
        :param str to: The phone number to filter the messages that was sent to
        :param str from_date_time: The starting date time to filter the messages
            (must be in yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
        :param str to_date_time: The ending date time to filter the messages (must be in
            yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
        :param str direction: Filter by direction of message, in - a message that came from the telephone
            network to one of your numbers (an "inbound" message) or out - a message
            that was sent from one of your numbers to the telephone network (an "outbound"
            message)
        :param str state: The message state to filter. Values are 'received', 'queued', 'sending',
            'sent', 'error'
        :param str delivery_state: The message delivery state to filter. Values are 'waiting', 'delivered',
            'not-delivered'
        :param str sort_order: How to sort the messages. Values are 'asc' or 'desc'
        :param str size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of messages

        Example: Search for all messages and are in error::

            message_list = api.list_messages()

            for message in message_list:
                if message['state'] == 'error':
                    print(message['id'])
            ## m-it6ewpyiyadfe
            ## m-pjnqofcjyadfe
            ## m-t2gspvs6iadfe
            ## m-shuh6d6pyadfe
        """

        kwargs['from'] = from_
        kwargs['to'] = to
        kwargs['fromDateTime'] = from_date_time
        kwargs['toDateTime'] = to_date_time
        kwargs['direction'] = direction
        kwargs['state'] = state
        kwargs['deliveryState'] = delivery_state
        kwargs['sortOrder'] = sort_order
        kwargs['size'] = size

        path = '/users/%s/messages' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def send_message(self, from_, to,
                     text=None,
                     media=None,
                     receipt_requested=None,
                     callback_url=None,
                     callback_http_method=None,
                     callback_timeout=None,
                     fallback_url=None,
                     tag=None,
                     **kwargs):
        """
        Send a message (SMS or MMS)

        :param str ``from_``: One of your telephone numbers the message should come from
        :param str to: The phone number the message should be sent to
        :param str text: The contents of the text message
        :param list media: For MMS messages, a media url to the location of the media or
            list of medias to be sent send with the message.
        :param str receipt_requested: Requested receipt option for outbound messages: 'none', 'all', 'error'
        :param str callback_url: The server URL where the events related to the outgoing message will be sent to
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.
            Values are get or post Default is post
        :param str callback_timeout: Determine how long should the platform wait for
            callbackUrl's response before timing out (milliseconds).
        :param str fallback_url: The server URL used to send the message events if the request to callbackUrl fails.
        :param str tag: Any string, it will be included in the callback events of the message.
        :rtype: str
        :returns: id of created message

        Example: Send Text Message::

            id = api.send_message(
                from_ = '+1234567980',
                to = '+1234567981',
                text = 'SMS message'
                )

        Example: Send Picture Message::

            id = api.send_message(
                from_ = '+1234567980',
                to = '+1234567981',
                media = ['http://host/path/to/file']
                )
        """
        kwargs['from'] = from_
        kwargs['to'] = to
        kwargs['text'] = text
        kwargs['media'] = media
        kwargs['receiptRequested'] = receipt_requested
        kwargs['callbackUrl'] = callback_url
        kwargs['callbackHttpMethod'] = callback_http_method
        kwargs['callbackTimeout'] = callback_timeout
        kwargs['fallbackUrl'] = fallback_url
        kwargs['tag'] = tag

        return self._make_request('post', '/users/%s/messages' % self.user_id, json=kwargs)[2]

    def send_messages(self, messages_data):
        """
        Send some messages by one request

        :type messages_data: list
        :param messages_data: List of messages to send

        Parameters of each message
            from
                One of your telephone numbers the message should come from
            to
                The phone number the message should be sent to
            text
                The contents of the text message
            media
                For MMS messages, a media url to the location of the media or list of medias to
                be sent send with the message.
            receiptRequested
                Requested receipt option for outbound messages: 'none', 'all', 'error'
            callbackUrl
                The server URL where the events related to the outgoing message will
                be sent to
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are get or post Default is post
            callbackTimeout
                Determine how long should the platform wait for callbackUrl's response
                before timing out (milliseconds).
            fallbackUrl
                The server URL used to send the message events if the request to callbackUrl fails.
            tag
                Any string, it will be included in the callback events of the message.
        :rtype: list
        :returns: results of sent messages

        Example: Bulk Send Picture or Text messages (or both)::

            results = api.send_messages([
                {'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'},
                {'from': '+1234567980', 'to': '+1234567982', 'text': 'SMS message2'}
            ])
        """
        results = self._make_request(
            'post', '/users/%s/messages' % self.user_id, json=messages_data)[0]
        for i in range(0, len(messages_data)):
            item = results[i]
            item['id'] = item.get('location', '').split('/')[-1]
            item['message'] = messages_data[i]
        return results

    def get_message(self, id):
        """
        Get information about a message

        :type id: str
        :param id: id of a message

        :rtype: dict
        :returns: message information

        Example: Fetch information about single message::

            my_message = api.get_message('m-na6cpyjf2qcpz6l3drhcx7y')
            print(my_message)

            ## {
            ##     'callbackUrl'             :'https://yoursite.com/message',
            ##     'direction'               :'in',
            ##     'from'                    :'+19193047864',
            ##     'id'                      :'m-messageId',
            ##     'media'                   :[],
            ##     'messageId'               :'m-messageId',
            ##     'skipMMSCarrierValidation':True,
            ##     'state'                   :'received',
            ##     'text'                    :'Hey there',
            ##     'time'                    :'2017-02-01T21:10:32Z',
            ##     'to'                      :'+19191234567'
            ## }
        """
        return self._make_request('get', '/users/%s/messages/%s' % (self.user_id, id))[0]

    def get_number_info(self, number):
        """
        Gets CNAM information about phone number

        :type number: str
        :param number: phone number to get information

        :rtype: dict
        :returns: CNAM information

        Example: Get Number information::

            data = api.get_number_info('+1234567890')
            print(data)
            ## {   'created': '2017-02-10T09:11:50Z',
            ##     'name'       : 'RALEIGH, NC',
            ##     'number'     : '+1234567890',
            ##     'updated'    : '2017-02-10T09:11:50Z'}

        """
        path = '/phoneNumbers/numberInfo/%s' % quote(number)
        return self._make_request('get', path)[0]

    def list_phone_numbers(
            self,
            application_id=None,
            state=None,
            name=None,
            city=None,
            number_state=None,
            size=None,
            **kwargs):
        """
        Get a list of user's phone numbers

        :param str application_id: Used to filter the retrieved list of numbers by an associated application ID.
        :param str state: Used to filter the retrieved list of numbers allocated for the authenticated
            user by a US state.
        :param str name: Used to filter the retrieved list of numbers allocated for the authenticated
            user by it's name.
        :param str city: Used to filter the retrieved list of numbers allocated for the authenticated user
            by it's city.
        :param str number_state: Used to filter the retrieved list of numbers allocated for the authenticated user
            by the number state.
        :param str size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of phone numbers

        Example: List all phone numbers::

            number_list = api.list_phone_numbers(size=1000)
            print(list(number_list))
            ## [
            ##     {
            ##         'city'          :'RALEIGH',
            ##         'createdTime'   :'2017-02-06T18:41:37Z',
            ##         'id'            :'n-n123',
            ##         'name'          :'demo name',
            ##         'nationalNumber':'(919) 555-5346',
            ##         'number'        :'+19195555346',
            ##         'numberState'   :'enabled',
            ##         'price'         :'0.35',
            ##         'state'         :'NC'
            ##     },
            ##     {
            ##         'city'          :'RALEIGH',
            ##         'createdTime'   :'2017-02-06T18:41:56Z',
            ##         'id'            :'n-n1234',
            ##         'name'          :'demo name',
            ##         'nationalNumber':'(919) 555-5378',
            ##         'number'        :'+19195555378',
            ##         'numberState'   :'enabled',
            ##         'price'         :'0.35',
            ##         'state'         :'NC'
            ##     }
            ## ]
        """

        kwargs['applicationId'] = application_id
        kwargs['state'] = state
        kwargs['name'] = name
        kwargs['city'] = city
        kwargs['numberState'] = number_state
        kwargs['size'] = size

        path = '/users/%s/phoneNumbers' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def order_phone_number(self,
                           number=None,
                           name=None,
                           application_id=None,
                           fallback_number=None,
                           **kwargs):
        """
        Allocates a number so user can use it to make and receive calls and send
        and receive messages.

        :param str number: An available telephone number you want to use
        :param str name: A name you choose for this number.
        :param str application_id: The unique id of an Application you want to associate with this number.
        :param str fallback_number: Number to transfer an incoming call when the callback/fallback events can't
            be delivered.

        :rtype: str
        :returns: id of created phone number

        Example: Order Number::

            number_id = api.create_phone_number(number='+1234567890')
            print(number_id)
            # n-asdf123
        """

        kwargs['number'] = number
        kwargs['name'] = name
        kwargs['applicationId'] = application_id
        kwargs['fallbackNumber'] = fallback_number

        return self._make_request('post', '/users/%s/phoneNumbers' % self.user_id, json=kwargs)[2]

    def get_phone_number(self, number_id):
        """
        Get information about a phone number

        :type number_id: str
        :param number_id: id of a phone number

        :rtype: dict
        :returns: number information

        Example: Search, order, and fetch Number information::

            available_numbers = api.search_available_local_numbers(city='Raleigh', state='NC')

            number_id = api.order_phone_number(available_numbers[0]['number'])
            print(number_id)
            # n-123

            my_number = api.get_phone_number(number_id)
            print(my_number)
            ## {
            ##     'city'          :'RALEIGH',
            ##     'createdTime'   :'2017-02-06T18:27:14Z',
            ##     'id'            :'n-123',
            ##     'nationalNumber':'(919) 561-5039',
            ##     'number'        :'+19195615039',
            ##     'numberState'   :'enabled',
            ##     'price'         :'0.35',
            ##     'state'         :'NC'
            ## }

        """
        return self._make_request('get', '/users/%s/phoneNumbers/%s' % (self.user_id, number_id))[0]

    def update_phone_number(self, number_id,
                            name=None,
                            application_id=None,
                            fallback_number=None,
                            **kwargs):
        """
        Update information about a phone number

        :param str number_id: id of a phone number
        :param str name: A name you choose for this number.
        :param str application_id: The unique id of an Application you want to associate with this number.
        :param str fallback_number: Number to transfer an incoming call when the callback/fallback events can't
            be delivered.

        Example: Update number information::

            my_number = api.get_phone_number(number_id)
            print(my_number)
            ## {
            ##     'city'          :'RALEIGH',
            ##     'createdTime'   :'2017-02-06T18:27:14Z',
            ##     'id'            :'n-123',
            ##     'nationalNumber':'(919) 561-5039',
            ##     'number'        :'+19195615039',
            ##     'numberState'   :'enabled',
            ##     'price'         :'0.35',
            ##     'state'         :'NC'
            ## }

            api.update_phone_number(number_id, name='demo name')

            my_number = api.get_phone_number(number_id)
            print(my_number)
            ## {
            ##     'id'            :'n-123',
            ##     'number'        :'+19195615039',
            ##     'nationalNumber':'(919) 561-5039',
            ##     'name'          :'demo name',
            ##     'createdTime'   :'2017-02-06T18:41:56Z',
            ##     'city'          :'RALEIGH',
            ##     'state'         :'NC',
            ##     'price'         :'0.35',
            ##     'numberState'   :'enabled'
            ## }
        """
        kwargs['name'] = name
        kwargs['applicationId'] = application_id
        kwargs['fallbackNumber'] = fallback_number

        self._make_request(
            'post', '/users/%s/phoneNumbers/%s' % (self.user_id, number_id), json=kwargs)

    def delete_phone_number(self, number_id):
        """
        Remove a phone number

        :type number_id: str
        :param number_id: id of a phone number

        Example: Delete phone number (release) from account::

            api.delete_phone_number('numberId')
        """
        self._make_request(
            'delete', '/users/%s/phoneNumbers/%s' % (self.user_id, number_id))

    def list_recordings(self, size=None, **kwargs):
        """
        Get a list of call recordings

        :param int size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of recordings

        Example: List all recordings::

            recording_list = api.list_recordings(size=1000)
            print(recording_list)
            ## [
            ##     {
            ##         'call'     :'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##         'endTime'  :'2017-01-30T17:58:45Z',
            ##         'id'       :'rec-recordingId',
            ##         'media'    :'https://api.catapult.inetwork.com/v1/users/u-abc123/media/c-callId-1.wav',
            ##         'mediaName':'c-callId-1.wav',
            ##         'startTime':'2017-01-30T17:58:34Z',
            ##         'state'    :'complete'
            ##     },
            ##     {
            ##         'call'     :'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##         'endTime'  :'2017-01-30T17:53:30Z',
            ##         'id'       :'rec-recordingId2',
            ##         'media'    :'https://api.catapult.inetwork.com/v1/users/u-abc123/media/c-callId2-1.wav',
            ##         'mediaName':'c-callId2-1.wav',
            ##         'startTime':'2017-01-30T17:53:20Z',
            ##         'state'    :'complete'
            ##     }
            ## ]
        """
        kwargs['size'] = size
        path = '/users/%s/recordings' % self.user_id
        return lazy_map(_set_media_name,
                        get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs)))

    def get_recording(self, recording_id):
        """
        Gets information about a recording

        :type recording_id: str
        :param recording_id: id of a recording

        :rtype: dict
        :returns: recording information

        Example: Fetch recording information::

            my_recording = api.get_recording('recordingId2')
            print(my_recording)

            ## {
            ##     'call'     :'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##     'endTime'  :'2017-01-30T17:53:30Z',
            ##     'id'       :'rec-recordingId2',
            ##     'media'    :'https://api.catapult.inetwork.com/v1/users/u-abc123/media/c-callId2-1.wav',
            ##     'mediaName':'c-callId2-1.wav',
            ##     'startTime':'2017-01-30T17:53:20Z',
            ##     'state'    :'complete'
            ## }
        """
        path = '/users/%s/recordings/%s' % (self.user_id, recording_id)
        return _set_media_name(self._make_request('get', path)[0])

    def list_transcriptions(self, recording_id, size=None, **kwargs):
        """
        Get a list of transcriptions

        :type recording_id: str
        :param recording_id: id of a recording
        :param int size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of transcriptions

        Example: Print off all transcriptions for a recording::

            transcriptions_list = api.list_transcriptions('recordingId')
            print(list(transcriptions_list))
            ## [
            ##     {
            ##         'chargeableDuration': 60,
            ##         'id': '{transcription-id}',
            ##         'state': 'completed',
            ##         'time': '2014-10-09T12:09:16Z',
            ##         'text': '{transcription-text}',
            ##         'textSize': 3627,
            ##         'textUrl': '{url-to-full-text}'
            ##     },
            ##     {
            ##         'chargeableDuration': 60,
            ##         'id': '{transcription-id}',
            ##         'state': 'completed',
            ##         'text': '{transcription-text}',
            ##         'time': '2014-10-09T14:04:44Z',
            ##         'textSize': 72,
            ##         'textUrl': '{url-to-full-text}'
            ##     }
            ## ]
        """
        kwargs['size'] = size
        path = '/users/%s/recordings/%s/transcriptions' % (
            self.user_id, recording_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_transcription(self, recording_id):
        """
        Create a transcirption for given recording

        :type recording_id: str
        :param recording_id: id of a recording

        :rtype: str
        :returns: id of created transcription

        Example: Create new transcription from existing recording::

            transcription_id = api.create_transcirption('recordingId')
        """
        path = '/users/%s/recordings/%s/transcriptions' % (
            self.user_id, recording_id)
        return self._make_request('post', path, json={})[2]

    def get_transcription(self, recording_id, transcription_id):
        """
        Get information about a transcription

        :type recording_id: str
        :param recording_id: id of a recording

        :type id: str
        :param id: id of a transcription

        :rtype: dict
        :returns: application information

        Example: Fetch a single transcription on a recording::

            my_transcription = api.get_transcription('recordingId', 'transcriptionId')
            print(my_transcription)
            ## {
            ##     'chargeableDuration': 11,
            ##     'id'                : '{transcriptionId}',
            ##     'state'             : 'completed',
            ##     'text'              : 'Hey there, I was calling to talk about plans for this saturday. ',
            ##     'textSize'          : 63,
            ##     'textUrl'           : 'https://api.catapult.inetwork.com/.../media/{transcriptionId}',
            ##     'time'              : '2014-12-23T23:08:59Z'
            ## }
        """
        path = '/users/%s/recordings/%s/transcriptions/%s' % (
            self.user_id, recording_id, transcription_id)
        return self._make_request('get', path)[0]


class CatapultException(Exception):

    """
    Catapult API request exception
    """

    def __init__(self, status_code, message, **kwargs):
        """
        Initialize the catapult exception.
        :type status_code: str
        :param status_code: http status code
        :type message: str
        :param message: error message
        :type code: str
        :param code: optional error code

        :rtype: bandwidth.catapult.CatapultException
        :returns: instance of exception
        """
        self.status_code = status_code
        self.message = message
        self.code = kwargs.get('code')
        if self.code is None:
            self.code = str(status_code)

    def __str__(self):
        return 'Error %s: %s' % (self.code, self.message)
