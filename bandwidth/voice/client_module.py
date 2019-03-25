import requests
import six
import urllib
import json
import itertools
from bandwidth.voice.lazy_enumerable import get_lazy_enumerator
from bandwidth.convert_camel import convert_object_to_snake_case
from bandwidth.voice.decorators import play_audio
from bandwidth.version import __version__ as version

from .api_exception_module import BandwidthVoiceAPIException

quote = urllib.parse.quote if six.PY3 else urllib.quote
lazy_map = map if six.PY3 else itertools.imap


def _set_media_name(recording):
    recording['media_name'] = recording.get('media', '').split('/')[-1]
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
            if response.headers.get('content-type') is not None and \
                    response.headers.get('content-type').startswith("application/json"):
                data = response.json()
                raise BandwidthVoiceAPIException(
                    response.status_code, data['message'], code=data.get('code'))
            else:
                raise BandwidthVoiceAPIException(
                    response.status_code, response.content.decode('utf-8')[:79])

    def _make_request(self, method, url, *args, **kwargs):
        response = self._request(method, url, *args, **kwargs)
        self._check_response(response)
        data = None
        id = None
        if response.headers.get('content-type') is not None and \
                response.headers.get('content-type').startswith("application/json"):
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
                total_chargeable_duration += call['chargeable_duration']

            print(total_chargeable_duration)
            ## 240

        Example: List Calls::

            call_list = api.list_calls(to = '+19192223333', size = 2)
            print(list(call_list))
            ## [
            ##   {
            ##     'active_time'          : '2017-01-26T16:10:23Z',
            ##     'callback_url'         : 'http://yoursite.com/calls',
            ##     'chargeable_duration'  : 60,
            ##     'direction'           : 'out',
            ##     'end_time'             : '2017-01-26T16:10:33Z',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/events',
            ##     'from'                : '+17079311113',
            ##     'id'                  : 'c-abc123',
            ##     'recording_enabled'    : False,
            ##     'recording_file_format' : 'wav',
            ##     'recordings'          : 'https://api.../v1/users/u-abc123/calls/c-abc123/recordings',
            ##     'start_time'           : '2017-01-26T16:10:11Z',
            ##     'state'               : 'completed',
            ##     'to'                  : '+19192223333',
            ##     'transcription_enabled': False,
            ##     'transcriptions'      : 'https://api.../v1/users/u-abc123/calls/c-abc123/transcriptions'
            ##   },
            ##   {
            ##     'active_time'          : '2016-12-29T23:50:35Z',
            ##     'chargeable_duration'  : 60,
            ##     'direction'           : 'out',
            ##     'end_time'             : '2016-12-29T23:50:41Z',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/events',
            ##     'from'                : '+19194443333',
            ##     'id'                  : 'c-xyz987',
            ##     'recording_enabled'    : False,
            ##     'recording_file_format' : 'wav',
            ##     'recordings'          : 'https://api.../v1/users/u-abc123/calls/c-xyz987/recordings',
            ##     'start_time'           : '2016-12-29T23:50:15Z',
            ##     'state'               : 'completed',
            ##     'to'                  : '+19192223333',
            ##     'transcription_enabled': False,
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
            ## {   'callback_url'         : 'http://yoursite.com/calls',
            ##     'direction'           : 'out',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
            ##     'from'                : '+1234567890',
            ##     'id'                  : 'c-abc123',
            ##     'recording_enabled'    : False,
            ##     'recording_file_format' : 'wav',
            ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
            ##     'start_time'           : '2017-01-26T16:10:11Z',
            ##     'state'               : 'started',
            ##     'to'                  : '+1234567891',
            ##     'transcription_enabled': False,
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
            ## {   'callback_url'         : 'http://yoursite.com/calls',
            ##     'direction'           : 'out',
            ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
            ##     'from'                : '+1234567890',
            ##     'id'                  : 'c-abc123',
            ##     'recording_enabled'    : False,
            ##     'recording_file_format' : 'wav',
            ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
            ##     'start_time'           : '2017-01-26T16:10:11Z',
            ##     'state'               : 'started',
            ##     'to'                  : '+1234567891',
            ##     'transcription_enabled': False,
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

            api.play_audio_to_call('call_id', file_url='http://host/path/file.mp3')
            api.play_audio_to_call('call_id', sentence='Press 0 to complete call', gender='female')
            # or with extension methods
            api.play_audio_file_to_call('call_id', 'http://host/path/file.mp3')
            api.speak_sentence_to_call('call_id', 'Hello')

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
            print(my_call['recording_enabled'])
            ## False

            api.toggle_call_recording(my_call_id)
            my_call = api.get_call(my_call_id)
            print(my_call['recording_enabled'])
            ## True

            api.toggle_call_recording(my_call_id)
            my_call = api.get_call(my_call_id)
            print(my_call['recording_enabled'])
            ## False

        """
        call_status = self.get_call(call_id)
        recording_enabled = call_status['recording_enabled']

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

            ## {   'bridge_audio': True,
            ##     'calls'      : 'https://api.catapult.inetwork.com/v1/users/u-123/bridges/brg-bridgeId/calls',
            ##     'created_time': '2017-01-26T01:15:09Z',
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

            print(my_bridge["bridge_audio"])
            ## True

            api.update_bridge(my_bridge['id'], call_ids = ['callId1', 'callId2'], bridge_audio = False)
            my_bridge = api.get_bridge(my_bridge['id'])

            print(my_bridge["bridge_audio"])
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
            ##         "active_time"      : "2013-05-22T19:49:39Z",
            ##         "direction"       : "out",
            ##         "from"            : "{fromNumber}",
            ##         "id"              : "{callId1}",
            ##         "bridge_id"        : "{bridgeId}",
            ##         "start_time"       : "2013-05-22T19:49:35Z",
            ##         "state"           : "active",
            ##         "to"              : "{toNumber1}",
            ##         "recording_enabled": false,
            ##         "events"          : "https://api.catapult.inetwork.com/v1/users/{userId}/calls/{callId1}/events",
            ##         "bridge"          : "https://api.catapult.inetwork.com/v1/users/{userId}/bridges/{bridgeId}"
            ##     },
            ##     {
            ##         "active_time"      : "2013-05-22T19:50:16Z",
            ##         "direction"       : "out",
            ##         "from"            : "{fromNumber}",
            ##         "id"              : "{callId2}",
            ##         "bridge_id"        : "{bridgeId}",
            ##         "start_time"       : "2013-05-22T19:50:16Z",
            ##         "state"           : "active",
            ##         "to"              : "{toNumber2}",
            ##         "recording_enabled": false,
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

            api.play_audio_to_bridge('bridgeId', file_url='http://host/path/file.mp3')
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
            ## {   'active_members'     : 0,
            ##     'callback_http_method': 'post',
            ##     'callback_timeout'   : 2000,
            ##     'callback_url'       : 'http://google.com',
            ##     'created_time'       : '2017-01-26T01:58:59Z',
            ##     'fallback_url'       : 'http://yahoo.com',
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
            ## {   'active_members'     : 0,
            ##     'callback_http_method': 'post',
            ##     'callback_timeout'   : 2000,
            ##     'callback_url'       : 'http://google.com',
            ##     'created_time'       : '2017-01-26T01:58:59Z',
            ##     'fallback_url'       : 'http://yahoo.com',
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

            api.play_audio_to_conference('conferenceId', file_url='http://host/path/file.mp3')

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
            ##       'added_time'  :'2017-01-30T22:01:11Z',
            ##       'call'       :'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##       'hold'       :False,
            ##       'id'         :'member-memberId',
            ##       'join_tone'   :False,
            ##       'leaving_tone':False,
            ##       'mute'       :False,
            ##       'removed_time':'2017-01-30T22:01:21Z',
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
            ##     'added_time': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : False,
            ##     'id'           : 'member-memberId',
            ##     'join_tone'     : False,
            ##     'leaving_tone'  : False,
            ##     'mute'         : False,
            ##     'removed_time'  : '2017-01-30T22:01:21Z',
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
            ##     'added_time': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : False,
            ##     'id'           : 'member-memberId',
            ##     'join_tone'     : True,
            ##     'leaving_tone'  : False,
            ##     'mute'         : False,
            ##     'removed_time'  : '2017-01-30T22:01:21Z',
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
            ##     'added_time': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : False,
            ##     'id'           : 'member-memberId',
            ##     'join_tone'     : True,
            ##     'leaving_tone'  : False,
            ##     'mute'         : False,
            ##     'removed_time'  : '2017-01-30T22:01:21Z',
            ##     'state'        : 'active'
            ## }

            api.update_conference_member(my_conf_id, my_member_id, mute=True, hold=True)

            my_conf = api.get_conference_member(my_member_id)

            ## {
            ##     'added_time': '2017-01-30T22:01:11Z',
            ##     'call'         : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##     'hold'         : True,
            ##     'id'           : 'member-memberId',
            ##     'join_tone'     : True,
            ##     'leaving_tone'  : False,
            ##     'mute'         : True,
            ##     'removed_time'  : '2017-01-30T22:01:21Z',
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

            api.play_audio_to_conference_member('conferenceId', 'memberId', file_url='http://host/path/file.mp3')
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

            ## [{ 'added_time'  : '2017-01-30T23:17:11Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId',
            ##    'join_tone'   : False,
            ##    'leaving_tone': False,
            ##    'mute'       : False,
            ##    'state'      : 'active'},
            ##  { 'added_time'  : '2017-01-30T23:17:14Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId2',
            ##    'join_tone'   : False,
            ##    'leaving_tone': False,
            ##    'mute'       : False,
            ##    'state'      : 'active'}]

            api.remove_conference_member(my_conf['id'], my_conf_members[1]['id'])

            my_conf_members = list(api.list_conference_members(my_conf['id']))
            print(my_conf_members)

            ## [{ 'added_time'  : '2017-01-30T23:17:11Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId',
            ##    'join_tone'   : False,
            ##    'leaving_tone': False,
            ##    'mute'       : False,
            ##    'state'      : 'active'},
            ##  { 'added_time'  : '2017-01-30T23:17:14Z',
            ##    'call'       : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##    'hold'       : False,
            ##    'id'         : 'member-memberId2',
            ##    'join_tone'   : False,
            ##    'leaving_tone': False,
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
            ##         'end_time'  :'2017-01-30T17:58:45Z',
            ##         'id'       :'rec-recordingId',
            ##         'media'    :'https://api.catapult.inetwork.com/v1/users/u-abc123/media/c-callId-1.wav',
            ##         'media_name':'c-callId-1.wav',
            ##         'start_time':'2017-01-30T17:58:34Z',
            ##         'state'    :'complete'
            ##     },
            ##     {
            ##         'call'     :'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-callId2',
            ##         'end_time'  :'2017-01-30T17:53:30Z',
            ##         'id'       :'rec-recordingId2',
            ##         'media'    :'https://api.catapult.inetwork.com/v1/users/u-abc123/media/c-callId2-1.wav',
            ##         'media_name':'c-callId2-1.wav',
            ##         'start_time':'2017-01-30T17:53:20Z',
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
            ##     'end_time'  :'2017-01-30T17:53:30Z',
            ##     'id'       :'rec-recordingId2',
            ##     'media'    :'https://api.catapult.inetwork.com/v1/users/u-abc123/media/c-callId2-1.wav',
            ##     'media_name':'c-callId2-1.wav',
            ##     'start_time':'2017-01-30T17:53:20Z',
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
            ##         'chargeable_duration': 60,
            ##         'id': '{transcription-id}',
            ##         'state': 'completed',
            ##         'time': '2014-10-09T12:09:16Z',
            ##         'text': '{transcription-text}',
            ##         'text_size': 3627,
            ##         'text_url': '{url-to-full-text}'
            ##     },
            ##     {
            ##         'chargeable_duration': 60,
            ##         'id': '{transcription-id}',
            ##         'state': 'completed',
            ##         'text': '{transcription-text}',
            ##         'time': '2014-10-09T14:04:44Z',
            ##         'text_size': 72,
            ##         'text_url': '{url-to-full-text}'
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
            ##     'chargeable_duration': 11,
            ##     'id'                : '{transcriptionId}',
            ##     'state'             : 'completed',
            ##     'text'              : 'Hey there, I was calling to talk about plans for this saturday. ',
            ##     'text_size'          : 63,
            ##     'text_url'           : 'https://api.catapult.inetwork.com/.../media/{transcriptionId}',
            ##     'time'              : '2014-12-23T23:08:59Z'
            ## }
        """
        path = '/users/%s/recordings/%s/transcriptions/%s' % (
            self.user_id, recording_id, transcription_id)
        return self._make_request('get', path)[0]
