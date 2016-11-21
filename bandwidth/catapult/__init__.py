import requests
import six
import urllib
from .lazy_enumerable import get_lazy_enumerator


quote = urllib.parse.quote if six.PY3 else urllib.quote
lazy_map = map if six.PY3 else itertools.imap


def _set_media_name(recording):
    recording['mediaName'] = recording.get('media', '').split('/')[-1]
    return recording

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

        :Example:
        api = bandwidth.catapult.Client('YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
        # or
        api = bandwidth.client('catapult', 'YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
        """
        if not all((user_id, api_token, api_secret)):
            raise ValueError('Arguments user_id, api_token and api_secret are required. '
                             'Use bandwidth.client("catapult", "YOUR-USER-ID", "YOUR-API-TOKEN", "YOUR-API-SECRET")')
        self.user_id = user_id
        self.api_endpoint = other_options.get('api_endpoint', 'https://api.catapult.inetwork.com')
        self.api_version = other_options.get('api_version', 'v1')
        self.auth = (api_token, api_secret)

    def _request(self, method, url, *args, **kwargs):
        if url.startswith('/'):
            # relative url
            url = '%s/%s%s' % (self.api_endpoint, self.api_version, url)
        return requests.request(method, url, auth=self.auth, *args, **kwargs)

    def _check_response(self, response):
        if response.status_code >= 400:
            if response.headers.get('content-type') == 'application/json':
                data = response.json()
                raise CatapultException(response.status_code, data['message'], code=data.get('code'))
            else:
                raise CatapultException(response.status_code, response.content.decode('utf-8')[:79])

    def _make_request(self, method, url, *args, **kwargs):
        response = self._request(method, url, *args, **kwargs)
        self._check_response(response)
        data = None
        id = None
        if response.headers.get('content-type') == 'application/json':
            data = response.json()
        location = response.headers.get('location')
        if location is not None:
            id = location.split('/')[-1]
        return (data, response, id)

    """
    Account API
    """

    def get_account(self):
        """
        Get an Account object

        :rtype: dict
        :returns: account data

        :Example:
        data = api.get_account()
        """
        return self._make_request('get', '/users/%s/account' % self.user_id)[0]

    def get_account_transactions(self, query=None):
        """
        Get the transactions from the user's account

        Query parameters
            maxItems
                Limit the number of transactions that will be returned.
            toDate
                Return only transactions that are newer than the parameter. Format: "yyyy-MM-dd'T'HH:mm:ssZ"
            fromDate
                Return only transactions that are older than the parameter. Format: "yyyy-MM-dd'T'HH:mm:ssZ"
            type
                Return only transactions that are this type.
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)

        :rtype: types.GeneratorType
        :returns: list of transactions

        :Example:
        list = api.get_account_transactions({'type': 'charge'})
        """
        path = '/users/%s/account/transactions' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))



    def get_calls(self, query=None):
        """
        Get a list of calls

        Query parameters
            bridgeId
                The id of the bridge for querying a list of calls history
            conferenceId
                The id of the conference for querying a list of calls history
            from
                The number to filter calls that came from
            to
                The number to filter calls that was called to
            sortOrder
                How to sort the calls. Values are asc or desc
                If no value is specified the default value is desc
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of calls

        :Example:
        list = api.get_calls()
        """
        path = '/users/%s/calls' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_call(self, data):
        """
        Create a call

        Parameters
            from
                A Bandwidth phone number on your account the call should come from (required)
            to
                The number to call (required)
            callTimeout
                Determine how long should the platform wait for call answer before timing out
                in seconds.
            callbackUrl
                The full server URL where the call events related to the Call will be sent to.
            callbackTimeout
                Determine how long should the platform wait for callbackUrl's response before
                timing out in milliseconds.
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are "GET" or "POST" (if not set the default is POST).
            fallbackUrl
                The full server URL used to send the callback event if the request to
                callbackUrl fails.
            bridgeId
                The id of the bridge where the call will be added.
            conferenceId
                Id of the conference where the call will be added. This property is required
                if you want to add this call to a conference.
            recordingEnabled
                Indicates if the call should be recorded after being created. Set to "true"
                to enable. Default is "false".
            recordingFileFormat
                The file format of the recorded call. Supported values are wav (default) and mp3.
            recordingMaxDuration
                Indicates the maximum duration of call recording in seconds. Default value is 1 hour.
            transcriptionEnabled
                Whether all the recordings for this call is going to be automatically transcribed.
            tag
                A string that will be included in the callback events of the call.
            sipHeaders
                Map of Sip headers prefixed by "X-". Up to 5 headers can be sent per call.
        :rtype: str
        :returns: id of created call

        :Example:
        id = api.create_call({'from': '+1234567890', 'to': '+1234567891'})
        """
        return self._make_request('post', '/users/%s/calls' % self.user_id, json=data)[2]

    def get_call(self, id):
        """
        Get information about a call

        :type id: str
        :param id: id of a call

        :rtype: dict
        :returns: call information

        :Example:
        data = api.get_call('callId')
        """
        return self._make_request('get', '/users/%s/calls/%s' % (self.user_id, id))[0]

    def update_call(self, id, data):
        """
        Update a call

        :type id: str
        :param id: id of a call

        Parameters
            state
                The call state. Possible values: rejected to reject not answer, active to answer the call,
                completed to hangup the call, transferring to start and connect call to a new outbound call.
            recordingEnabled
                Indicates if the call should be recorded. Values true or false. You can turn recording
                on/off and have multiple recordings on a single call.
            recordingFileFormat
                The file format of the recorded call. Supported values are wav (default) and mp3.
            transferTo
                Phone number or SIP address that the call is going to be transferred to.
            transferCallerId
                This is the caller id that will be used when the call is transferred.
            whisperAudio
                Audio to be played to the caller that the call will be transferred to.
            callbackUrl
                The server URL where the call events for the new call will be sent upon transferring.

        :Example:
        api.update_call('callId', {'state': 'completed'})
        """
        return self._make_request('post', '/users/%s/calls/%s' % (self.user_id, id), json=data)[2]

    def play_audio_to_call(self, id, data):
        """
        Play audio to a call

        :type id: str
        :param id: id of a call

        Parameters
            fileUrl
                The location of an audio file to play (WAV and MP3 supported).
            sentence
                The sentence to speak.
            gender
                The gender of the voice used to synthesize the sentence.
            locale
                The locale used to get the accent of the voice used to synthesize the sentence.
            voice
                The voice to speak the sentence.
            loopEnabled
                When value is true, the audio will keep playing in a loop.


        :Example:
        api.play_audio_to_call('callId', {'fileUrl': 'http://host/path/file.mp3'})
        api.play_audio_to_call('callId', {'sentence': 'Press 0 to complete call', 'gender': 'female'})

        # or with extension methods
        api.play_audio_file_to_call('callId', 'http://host/path/file.mp3')
        api.speak_sentence_to_call('callId', 'Hello')
        """
        self._make_request('post', '/users/%s/calls/%s/audio' % (self.user_id, id), json=data)

    def send_dtmf_to_call(self, id, data):
        """
        Send DTMF (phone keypad digit presses).

        :type id: str
        :param id: id of a call

        Parameters
            dtmfOut
                String containing the DTMF characters to be sent in a call.
        """
        self._make_request('post', '/users/%s/calls/%s/dtmf' % (self.user_id, id), json=data)

    def get_call_recordings(self, id):
        """
        Get a list of recordings of a call

        :type id: str
        :param id: id of a call

        :rtype: types.GeneratorType
        :returns: list of recordings

        :Example:
        list = api.get_call_recordings('callId')
        """
        path = '/users/%s/calls/%s/recordings' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda:  self._make_request('get', path))

    def get_call_transcriptions(self, id):
        """
        Get a list of transcriptions of a call

        :type id: str
        :param id: id of a call

        :rtype: types.GeneratorType
        :returns: list of transcriptions

        :Example:
        list = api.get_call_transcriptions('callId')
        """
        path = '/users/%s/calls/%s/transcriptions' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def get_call_events(self, id):
        """
        Get a list of events of a call

        :type id: str
        :param id: id of a call

        :rtype: types.GeneratorType
        :returns: list of events

        :Example:
        list = api.get_call_events('callId')
        """
        path = '/users/%s/calls/%s/events' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def get_call_event(self, id, event_id):
        """
        Get an event of a call

        :type id: str
        :param id: id of a call

        :type event_id: str
        :param event_id: id of an event

        :rtype: dict
        :returns: data of event

        :Example:
        data = api.get_call_event('callId', 'eventId')
        """
        return self._make_request('get', '/users/%s/calls/%s/events/%s' % (self.user_id, id, event_id))[0]

    def create_call_gather(self, id, data):
        """
        Create a gather for a call

        :type id: str
        :param id: id of a call

        Parameters
            maxDigits
                The maximum number of digits to collect, not including terminating digits (maximum 30).
            interDigitTimeout
                Stop gathering if a DTMF digit is not detected in this many seconds
                (default 5.0; maximum 30.0).
            terminatingDigits
                A string of DTMF digits that end the gather operation immediately
                if any one of them is detected
            tag
                A string you choose that will be included with the response and events for
                this gather operation.
            prompt.sentence
                The text to speak for the prompt
            prompt.gender
                The gender to use for the voice reading the prompt sentence
            prompt.locale
                The language and region to use for the voice reading the prompt sentence
            prompt.loopEnabled
                When value is true, the audio will keep playing in a loop.
            prompt.bargeable
                Make the prompt (audio or sentence) bargeable (will be interrupted
                at first digit gathered).
            prompt.fileUrl
                The location of an audio file to play (WAV and MP3 supported).


        :rtype: str
        :returns: id of create of gather

        :Example:
        gather_id = api.create_call_gather('callId', {'maxDigits': 1})
        """
        return self._make_request('post', '/users/%s/calls/%s/gather' % (self.user_id, id), json=data)[2]

    def get_call_gather(self, id, gather_id):
        """
        Get a gather of a call

        :type id: str
        :param id: id of a call

        :type gather_id: str
        :param gather_id: id of a gather

        :rtype: dict
        :returns: data of gather

        :Example:
        data = api.get_call_gather('callId', 'gatherId')
        """
        return self._make_request('get', '/users/%s/calls/%s/gather/%s' % (self.user_id, id, gather_id))[0]

    def update_call_gather(self, id, gather_id, data):
        """
        Update a gather of a call

        :type id: str
        :param id: id of a call

        :type gather_id: str
        :param gather_id: id of a gather

        Parameters
            state
                The only update allowed is state:completed to stop the gather.

        :Example:
        api.update_call_gather('callId', 'gatherId', {'state': 'completed'})
        """
        self._make_request('post', '/users/%s/calls/%s/gather/%s' % (self.user_id, id, gather_id), json=data)

    # extensions

    def answer_call(self, id):
        """
        Answer incoming call

        :type id: str
        :param id: id of a call

        :Example:
        api.answer_call('callId')
        """
        self.update_call(id, {'state': 'active'})

    def reject_call(self, id):
        """
        Reject incoming call

        :type id: str
        :param id: id of a call

        :Example:
        api.reject_call('callId')
        """
        self.update_call(id, {'state': 'rejected'})

    def hangup_call(self, id):
        """
        Complete active call

        :type id: str
        :param id: id of a call

        :Example:
        api.hangup_call('callId')
        """
        self.update_call(id, {'state': 'completed'})

    def tune_call_recording(self, id, enabled):
        """
        Tune on or tune off call recording

        :type id: str
        :param id: id of a call

        :Example:
        api.tune_call_recording('callId', True)
        """
        self.update_call(id, {'recordingEnabled': enabled})

    def transfer_call(self, id, to, caller_id=None, whisper_audio=None, callback_url=None):
        """
        Transfer a call

        :type id: str
        :param id: id of a call

        :type to: str
        :param to: number that the call is going to be transferred to.

        :type caller_id: str
        :param caller_id: caller id that will be used when the call is transferred

        :type whisper_audio: str
        :param whisper_audio: audio to be played to the caller that the call will be transferred to

        :type callback_url: str
        :param callback_url: URL where the call events for the new call will be sent upon transferring

        :rtype str
        :returns id of created call

        :Example:
        api.transfer_call('callId', '+1234564890')
        """
        data = {'state': 'transferring', 'transferTo': to}
        if caller_id is not None:
            data['transferCallerId'] = caller_id
        if whisper_audio is not None:
            data['whisperAudio'] = whisper_audio
        if callback_url is not None:
            data['callbackUrl'] = callback_url
        return self.update_call(id, data)

    """
    Application API
    """
    def get_applications(self, query=None):
        """
        Get a list of user's applications

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of applications

        :Example:
        list = api.get_applications()
        """
        path = '/users/%s/applications' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_application(self, data):
        """
        Creates an application that can handle calls and messages for one of your phone number.

        Parameters
            name
                A name you choose for this application (required).
            incomingCallUrl
                A URL where call events will be sent for an inbound call.
            incomingCallUrlCallbackTimeout
                Determine how long should the platform wait for inconmingCallUrl's response
                before timing out in milliseconds.
            incomingCallFallbackUrl
                The URL used to send the callback event if the request to incomingCallUrl fails.
            incomingMessageUrl
                A URL where message events will be sent for an inbound SMS message
            incomingMessageUrlCallbackTimeout
                Determine how long should the platform wait for incomingMessageUrl's response before
                timing out in milliseconds.
            incomingMessageFallbackUrl
                The URL used to send the callback event if the request to incomingMessageUrl fails.
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                (If not set the default is HTTP POST)
            autoAnswer
                Determines whether or not an incoming call should be automatically answered.
                Default value is 'true'.

        :rtype: str
        :returns: id of created application

        :Example:
        id = api.create_application({'name': 'MyApp'})
        """
        return self._make_request('post', '/users/%s/applications' % self.user_id, json=data)[2]

    def get_application(self, id):
        """
        Gets information about an application

        :type id: str
        :param id: id of an application

        :rtype: dict
        :returns: application information

        :Example:
        data = api.get_application('appId')
        """
        return self._make_request('get', '/users/%s/applications/%s' % (self.user_id, id))[0]

    def delete_application(self, id):
        """
        Remove an application

        :type id: str
        :param id: id of an application

        :Example:
        api.delete_application('appId')
        """
        self._make_request('delete', '/users/%s/applications/%s' % (self.user_id, id))

    """
    Available number API
    """
    def search_available_numbers(self, number_type='local', query=None):
        """
        Searches for available local or toll free numbers.

        :type number_type: str
        :param number_type: type of number to search ('local' or 'tollFree')

        Query parameters for local numbers
            city
                A city name
            state
                A two-letter US state abbreviation
            zip
                A 5-digit US ZIP code
            areaCode
                A 3-digit telephone area code
            localNumber
                It is defined as the first digits of a telephone number inside an area code
                for filtering the results. It must have at least 3 digits and the areaCode
                field must be filled.
            inLocalCallingArea
                Boolean value to indicate that the search for available numbers must consider
                overlayed areas.
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)
            pattern
                A number pattern that may include letters, digits, and the wildcard characters

        Query parameters for toll free numbers
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)
            pattern
                A number pattern that may include letters, digits, and the wildcard characters

        :rtype: list
        :returns: list of numbers

        :Example:
        numbers = api.search_available_numbers('local', {'areaCode': '910', 'quantity': 3})
        """
        return self._make_request('get', '/availableNumbers/%s' % number_type, params=query)[0]

    def search_and_order_available_numbers(self, number_type='local', query=None):
        """
        Searches and orders for available local or toll free numbers.

        :type number_type: str
        :param number_type: type of number to search ('local' or 'tollFree')

        Query parameters for local numbers
            city
                A city name
            state
                A two-letter US state abbreviation
            zip
                A 5-digit US ZIP code
            areaCode
                A 3-digit telephone area code
            localNumber
                It is defined as the first digits of a telephone number inside an area code
                for filtering the results. It must have at least 3 digits and the areaCode
                field must be filled.
            inLocalCallingArea
                Boolean value to indicate that the search for available numbers must consider
                overlayed areas.
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)

        Query parameters for toll free numbers
            quantity
                The maximum number of numbers to return (default 10, maximum 5000)

        :rtype: list
        :returns: list of ordered numbers

        :Example:
        ordered_numbers = api.search_and_order_available_numbers('local', {'areaCode': '910', 'quantity': 3})
        """
        list = self._make_request('post', '/availableNumbers/%s' % number_type, params=query)[0]
        for item in list:
            item['id'] = item.get('location', '').split('/')[-1]
        return list

    def get_bridges(self, query=None):
        """
        Get a list of bridges

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of bridges

        :Example:
        list = api.get_bridges()
        """
        path = '/users/%s/bridges' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_bridge(self, data):
        """
        Create a bridge

        Parameters
            bridgeAudio
                Enable/Disable two way audio path (default = true)
            callIds
                The list of call ids in the bridge. If the list of call ids
                is not provided the bridge is logically created and it can be
                used to place calls later.
        :rtype: str
        :returns: id of created bridge

        :Example:
        id = api.create_bridge({'callIds': ['callId1', 'callId2'], 'bridgeAudio': 'true'})
        """
        return self._make_request('post', '/users/%s/bridges' % self.user_id, json=data)[2]

    def get_bridge(self, id):
        """
        Gets information about a bridge

        :type id: str
        :param id: id of a bridge

        :rtype: dict
        :returns: bridge information

        :Example:
        data = api.get_bridge('bridgeId')
        """
        return self._make_request('get', '/users/%s/bridges/%s' % (self.user_id, id))[0]

    def update_bridge(self, id, data):
        """
        Update a bridge

        :type id: str
        :param id: id of a bridge

        Parameters
            bridgeAudio
                Enable/Disable two way audio path (default = true)
            callIds
                The list of call ids in the bridge

        :Example:
        api.update_bridge('bridgeId', {'callIds': ['callId3'], 'bridgeAudio': 'true'})
        """
        self._make_request('post', '/users/%s/bridges/%s' % (self.user_id, id), json=data)

    def get_bridge_calls(self, id):
        """
        Get a list of calls of a bridge

        :type id: str
        :param id: id of a bridge

        :rtype: types.GeneratorType
        :returns: list of calls

        :Example:
        list = api.get_bridge_calls('bridgeId')
        """
        path = '/users/%s/bridges/%s/calls' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def play_audio_to_bridge(self, id, data):
        """
        Play audio to a bridge

        :type id: str
        :param id: id of a bridge

        Parameters
            fileUrl
                The location of an audio file to play (WAV and MP3 supported).
            sentence
                The sentence to speak.
            gender
                The gender of the voice used to synthesize the sentence.
            locale
                The locale used to get the accent of the voice used to synthesize the sentence.
            voice
                The voice to speak the sentence.
            loopEnabled
                When value is true, the audio will keep playing in a loop.


        :Example:
        api.play_audio_to_bridge('bridgeId', {'fileUrl': 'http://host/path/file.mp3'})
        api.play_audio_to_bridge('bridgeId', {'sentence': 'Press 0 to complete call', 'gender': 'female'})

        # or with extension methods
        api.play_audio_file_to_bridge('bridgeId', 'http://host/path/file.mp3')
        api.speak_sentence_to_bridge('bridgeId', 'Hello')
        """
        self._make_request('post', '/users/%s/bridges/%s/audio' % (self.user_id, id), json=data)

    def create_conference(self, data):
        """
        Create a conference

        Parameters
            from
                The phone number that will host the conference (required)
            callbackUrl
                The full server URL where the conference events related
                to the Conerence will be sent to.
            callbackTimeout
                Determine how long should the platform wait for callbackUrl's response before
                timing out in milliseconds.
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are "GET" or "POST" (if not set the default is POST).
            fallbackUrl
                The full server URL used to send the callback event if the request to
                callbackUrl fails.
            tag
                A string that will be included in the callback events of the conference.

        :rtype: str
        :returns: id of created conference

        :Example:
        id = api.create_conference({'from': '+1234567890'})
        """
        return self._make_request('post', '/users/%s/conferences' % self.user_id, json=data)[2]

    def get_conference(self, id):
        """
        Get information about a conference

        :type id: str
        :param id: id of a conference

        :rtype: dict
        :returns: conference information

        :Example:
        data = api.get_conference('conferenceId')
        """
        return self._make_request('get', '/users/%s/conferences/%s' % (self.user_id, id))[0]

    def update_conference(self, id, data):
        """
        Update a conference

        :type id: str
        :param id: id of a conference

        Parameters
            state
                Conference state. Possible state values are: "completed"
                to terminate the conference.
            mute
                If "true", all member can't speak in the conference.
                If "false", all members can speak in the conference
            hold
                If "true", all member can't hear or speak in the conference.
                If "false", all members can hear and speak in the conference
            callbackUrl
                The full server URL where the conference events related
                to the Conerence will be sent to.
            callbackTimeout
                Determine how long should the platform wait for callbackUrl's response before
                timing out in milliseconds.
            callbackHttpMethod
                Determine if the callback event should be sent via HTTP GET or HTTP POST.
                Values are "GET" or "POST" (if not set the default is POST).
            fallbackUrl
                The full server URL used to send the callback event if the request to
                callbackUrl fails.
            tag
                A string that will be included in the callback events of the conference.

        :Example:
        api.update_conference('conferenceId', {'state': 'completed'})
        """
        self._make_request('post', '/users/%s/conferences/%s' % (self.user_id, id), json=data)

    def play_audio_to_conference(self, id, data):
        """
        Play audio to a conference

        :type id: str
        :param id: id of a conference

        Parameters
            fileUrl
                The location of an audio file to play (WAV and MP3 supported).
            sentence
                The sentence to speak.
            gender
                The gender of the voice used to synthesize the sentence.
            locale
                The locale used to get the accent of the voice used to synthesize the sentence.
            voice
                The voice to speak the sentence.
            loopEnabled
                When value is true, the audio will keep playing in a loop.


        :Example:
        api.play_audio_to_conference('conferenceId', {'fileUrl': 'http://host/path/file.mp3'})
        api.play_audio_to_conference('conferenceId', {'sentence': 'Press 0 to complete call', 'gender': 'female'})

        # or with extension methods
        api.play_audio_file_to_conference('conferenceId', 'http://host/path/file.mp3')
        api.speak_sentence_to_conference('conferenceId', 'Hello')
        """
        self._make_request('post', '/users/%s/conferences/%s/audio' % (self.user_id, id), json=data)

    def get_conference_members(self, id):
        """
        Get a list of members of a conference

        :type id: str
        :param id: id of a conference

        :rtype: types.GeneratorType
        :returns: list of recordings

        :Example:
        list = api.get_conference_members('conferenceId')
        """
        path = '/users/%s/conferences/%s/members' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def create_conference_member(self, id, data):
        """
        Create a conference member for a conference

        :type id: str
        :param id: id of a conference

        Parameters
            callId
                The callId must refer to an active call that was created
                using this conferenceId (required)
            joinTone
                If "true", will play a tone when the member joins the conference.
                If "false", no tone is played when the member joins the conference.
            leavingTone
                If "true", will play a tone when the member leaves the conference.
                If "false", no tone is played when the member leaves the conference.
            mute
                If "true", member can't speak in the conference.
                If "false", this members can speak in the conference
                (unless set at the conference level).
            hold
                If "true", member can't hear or speak in the conference.
                If "false", member can hear and speak in the conference
                (unless set at the conference level).
        :rtype: str
        :returns: id of create of conference member

        :Example:
        member_id = api.create_conference_member('conferenceId', {'callId': 'callId1'})
        """
        path = '/users/%s/conferences/%s/members' % (self.user_id, id)
        return self._make_request('post', path, json=data)[2]

    def get_conference_member(self, id, member_id):
        """
        Get a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a member

        :rtype: dict
        :returns: data of conference member

        :Example:
        data = api.get_conference_member('conferenceId', 'memberId')
        """
        path = '/users/%s/conferences/%s/members/%s' % (self.user_id, id, member_id)
        return self._make_request('get', path)[0]

    def update_conference_member(self, id, member_id, data):
        """
        Update a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        Parameters
            joinTone
                If "true", will play a tone when the member joins the conference.
                If "false", no tone is played when the member joins the conference.
            leavingTone
                If "true", will play a tone when the member leaves the conference.
                If "false", no tone is played when the member leaves the conference.
            mute
                If "true", member can't speak in the conference.
                If "false", this members can speak in the conference
                (unless set at the conference level).
            hold
                If "true", member can't hear or speak in the conference.
                If "false", member can hear and speak in the conference
                (unless set at the conference level).

        :Example:
        api.update_conference_member('conferenceId', 'memberId', {'hold': True})
        """
        path = '/users/%s/conferences/%s/members/%s' % (self.user_id, id, member_id)
        self._make_request('post', path, json=data)

    def play_audio_to_conference_member(self, id, member_id, data):
        """
        Play audio to a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        Parameters
            fileUrl
                The location of an audio file to play (WAV and MP3 supported).
            sentence
                The sentence to speak.
            gender
                The gender of the voice used to synthesize the sentence.
            locale
                The locale used to get the accent of the voice used to synthesize the sentence.
            voice
                The voice to speak the sentence.
            loopEnabled
                When value is true, the audio will keep playing in a loop.


        :Example:
        api.play_audio_to_conference_member('conferenceId', 'memberId', {'fileUrl': 'http://host/path/file.mp3'})
        api.play_audio_to_conference_member('conferenceId', 'memberId',
                                            {'sentence': 'Press 0 to complete call', 'gender': 'female'})

        # or with extension methods
        api.play_audio_file_to_conference_member('conferenceId', 'memberId', 'http://host/path/file.mp3')
        api.speak_sentence_to_conference_member('conferenceId', 'memberId', 'Hello')
        """
        path = '/users/%s/conferences/%s/members/%s/audio' % (self.user_id, id, member_id)
        self._make_request('post', path, json=data)

    # extensions

    def speak_sentence_to_conference_member(self, id, member_id, sentence,
                                            gender='female', voice='susan', locale='en_US', tag=None):
        """
        Speak sentence to a conference member

        :type id: str
        :param id: id of a conference

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

        :Example:
        api.speak_sentence_to_conference_member('conferenceId', 'memberId', 'Hello')
        """
        self.play_audio_to_conference_member(id, member_id, {
            'sentence': sentence,
            'gender': gender,
            'voice': voice,
            'locale': locale,
            'tag': tag
        })

    def play_audio_file_to_conference_member(self, id, member_id, file_url, tag=None):
        """
        Play audio file to a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type file_url: str
        :param file_url: URL to remote file to play

        :type tag: str
        :param tag: A string that will be included in the callback events of the call.

        :Example:
        api.play_audio_file_to_conference_member('conferenceId', 'memberId', 'http://host/path/file.mp3')
        """

        self.play_audio_to_conference_member(id, member_id, {
            'fileUrl': file_url,
            'tag': tag
        })

    def delete_conference_member(self, id, member_id):
        """
        Remove a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :Example:
        api.delete_conference_member('conferenceId', 'memberId')

        """
        self.update_conference_member(id, member_id, {'state': 'completed'})

    def hold_conference_member(self, id, member_id, hold):
        """
        Hold or unhold a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type hold: bool
        :param hold: hold (if true) or unhold (if false) a member

        :Example:
        api.hold_conference_member('conferenceId', 'memberId', True)
        """
        self.update_conference_member(id, member_id, {'hold': hold})

    def mute_conference_member(self, id, member_id, mute):
        """
        Mute or unmute a conference member

        :type id: str
        :param id: id of a conference

        :type member_id: str
        :param member_id: id of a conference member

        :type mute: bool
        :param mute: mute (if true) or unmute (if false) a member

        :Example:
        api.mute_conference_member('conferenceId', 'memberId', True)
        """
        self.update_conference_member(id, member_id, {'mute': mute})

    def terminate_conference(self, id):
        """
        Terminate of current conference

        :type id: str
        :param id: id of a conference

        :Example:
        api.terminate_conference('conferenceId')

        """
        self.update_conference(id, {'state': 'completed'})

    def hold_conference(self, id, hold):
        """
        Hold or unhold a conference

        :type id: str
        :param id: id of a conference

        :type hold: bool
        :param hold: hold (if true) or unhold (if false) a conference

        :Example:
        api.hold_conference('conferenceId', True)
        """
        self.update_conference(id, {'hold': hold})

    def mute_conference(self, id, mute):
        """
        Mute or unmute a conference

        :type id: str
        :param id: id of a conference

        :type mute: bool
        :param mute: mute (if true) or unmute (if false) a conference

        :Example:
        api.mute_conference('conferenceId', True)
        """
        self.update_conference(id, {'mute': mute})

    """
    Domain API
    """
    def get_domains(self, query=None):
        """
        Get a list of domains

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 100)
        :rtype: types.GeneratorType
        :returns: list of domains

        :Example:
        list = api.get_domains()
        """
        path = '/users/%s/domains' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_domain(self, data):
        """
        Create a domain

        Parameters
            name
                The name is a unique URI to be used in DNS lookups
            description
                String to describe the domain
        :rtype: str
        :returns: id of created domain

        :Example:
        id = api.create_domain({'name': 'qwerty'})
        """
        return self._make_request('post', '/users/%s/domains' % self.user_id, json=data)[2]

    def delete_domain(self, id):
        """
        Delete a domain

        :type id: str
        :param id: id of a domain

        :Example:
        api.delete_domain('domainId')
        """
        self._make_request('delete', '/users/%s/domains/%s' % (self.user_id, id))
    """
    Endpoint API
    """
    def get_domain_endpoints(self, id, query=None):
        """
        Get a list of domain's endpoints

        :type id: str
        :param id: id of a domain

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of endpoints

        :Example:
        list = api.get_domain_endpoints()
        """
        path = '/users/%s/domains/%s/endpoints' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_domain_endpoint(self, id, data):
        """
        Create a domain endpoint

        :type id: str
        :param id: id of a domain

        Parameters
            name
                The name of endpoint
            description
                String to describe the endpoint
            applicationId
                Id of application which will handle calls and messages of this endpoint
            enabled
                When set to true, SIP clients can register as this device to receive and
                make calls. When set to false, registration, inbound, and outbound
                calling will not succeed.
            credentials.password
                Password of created SIP account


        :rtype: str
        :returns: id of endpoint

        :Example:
        id = api.create_domain_endpoint({'name': 'my-sip'})
        """
        data['domainId'] = id
        return self._make_request('post', '/users/%s/domains/%s/endpoints' % (self.user_id, id), json=data)[2]

    def get_domain_endpoint(self, id, endpoint_id):
        """
        Get information about an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :rtype: dict
        :returns: call information

        :Example:
        data = api.get_domain_endpoint('domainId', 'endpointId')
        """
        return self._make_request('get', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id))[0]

    def update_domain_endpoint(self, id, endpoint_id, data):
        """
        Update information about an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        Parameters
            description
                String to describe the endpoint
            applicationId
                Id of application which will handle calls and messages of this endpoint
            enabled
                When set to true, SIP clients can register as this device to receive and
                make calls. When set to false, registration, inbound, and outbound
                calling will not succeed.
            credentials.password
                Password of created SIP account

        :Example:
        api.update_domain_endpoint('domainId', 'endpointId', {'enabled': False})
        """
        self._make_request('post', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id), json=data)

    def delete_domain_endpoint(self, id, endpoint_id):
        """
        Remove an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :Example:
        api.delete_domain_endpoint('domainId', 'endpointId')
        """
        self._make_request('delete', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id))

    def create_domain_endpoint_auth_token(self, id, endpoint_id, data={'expires': 3600}):
        """
        Create auth token for an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :Example:
        token = api.create_domain_endpoint_auth_token('domainId', 'endpointId')
        """
        path = '/users/%s/domains/%s/endpoints/%s/tokens' % (self.user_id, id, endpoint_id)
        return self._make_request('post', path, json=data)[0]

    """
    Error API
    """
    def get_errors(self, query=None):
        """
        Get a list of errors

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of calls

        :Example:
        list = api.get_errors()
        """

        path = '/users/%s/errors' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def get_error(self, id):
        """
        Get information about an error

        :type id: str
        :param id: id of an error

        :rtype: dict
        :returns: error information

        :Example:
        data = api.get_error('errorId')
        """
        return self._make_request('get', '/users/%s/errors/%s' % (self.user_id, id))[0]

    """
    Media API
    """
    def get_media_files(self):
        """
        Gets a list of user's media files.

        :rtype: types.GeneratorType
        :returns: list of media files

        :Example:
        list = api.get_media_files()

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

        :Example:
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

        :Example:
        stream, content_type = api.download_media_file('file1.txt')
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

        :Example:
        api.delete_media_file('file1.txt')
        """
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        self._make_request('delete', path)

    """
    Message API
    """

    """
    Message API
    """
    def get_messages(self, query=None):
        """
        Get a list of user's messages

        Query parameters
            from
                The phone number to filter the messages that came from
            to
                The phone number to filter the messages that was sent to
            fromDateTime
                The starting date time to filter the messages
                (must be in yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
            toDateTime
                The ending date time to filter the messages (must be in
                yyyy-MM-dd hh:mm:ss format, like 2014-05-25 12:00:00.)
            direction
                Filter by direction of message, in - a message that came from the telephone
                 network to one of your numbers (an "inbound" message) or out - a message
                 that was sent from one of your numbers to the telephone network (an "outbound"
                 message)
            state
                The message state to filter. Values are 'received', 'queued', 'sending',
                'sent', 'error'
            deliveryState
                The message delivery state to filter. Values are 'waiting', 'delivered',
                'not-delivered'
            sortOrder
                How to sort the messages. Values are 'asc' or 'desc'
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of messages

        :Example:
        list = api.get_messages()
        """
        path = '/users/%s/messages' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def send_message(self, data):
        """
        Send a message (SMS or MMS)

        Parameters
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
        :rtype: str
        :returns: id of created message

        :Example:
        # SMS
        id = api.send_message({'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'})
        # MMS
        id = api.send_message({'from': '+1234567980', 'to': '+1234567981', 'text': 'MMS message',
        'media': ['http://host/path/to/file']})
        """
        return self._make_request('post', '/users/%s/messages' % self.user_id, json=data)[2]

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

        :Example:
        results = api.send_message([
            {'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'},
            {'from': '+1234567980', 'to': '+1234567982', 'text': 'SMS message2'}
        ])
        """
        results = self._make_request('post', '/users/%s/messages' % self.user_id, json=messages_data)[0]
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

        :Example:
        data = api.get_message('messageId')
        """
        return self._make_request('get', '/users/%s/messages/%s' % (self.user_id, id))[0]

    """
    NumberInfo API
    """
    def get_number_info(self, number):
        """
        Gets CNAM information about phone number

        :type number: str
        :param number: phone number to get information

        :rtype: dict
        :returns: CNAM information

        :Example:
        data = api.get_number_info('+1234567890')

        """
        path = '/phoneNumbers/numberInfo/%s' % quote(number)
        return self._make_request('get', path)[0]

    """
    PhoneNumber API
    """
    def get_phone_numbers(self, query=None):
        """
        Get a list of user's phone numbers

        Query parameters
            applicationId
                Used to filter the retrieved list of numbers by an associated application ID.
            state
                Used to filter the retrieved list of numbers allocated for the authenticated
                user by a US state.
            name
                Used to filter the retrieved list of numbers allocated for the authenticated
                user by it's name.
            city
                Used to filter the retrieved list of numbers allocated for the authenticated user
                by it's city.
            numberState
                Used to filter the retrieved list of numbers allocated for the authenticated user
                by the number state.
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of phone numbers

        :Example:
        list = api.get_phone_numbers()
        """
        path = '/users/%s/phoneNumbers' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_phone_number(self, data):
        """
        Allocates a number so user can use it to make and receive calls and send
        and receive messages.

        Parameters
            number
                An available telephone number you want to use
            name
                A name you choose for this number.
            applicationId
                The unique id of an Application you want to associate with this number.
            fallbackNumber
                Number to transfer an incoming call when the callback/fallback events can't
                be delivered.

        :rtype: str
        :returns: id of created phone number

        :Example:
        id = api.create_phone_number({'number': '+1234567890'})
        """
        return self._make_request('post', '/users/%s/phoneNumbers' % self.user_id, json=data)[2]

    def get_phone_number(self, id):
        """
        Get information about a phone number

        :type id: str
        :param id: id of a phone number

        :rtype: dict
        :returns: number information

        :Example:
        data = api.get_phone_number('numberId')
        """
        return self._make_request('get', '/users/%s/phoneNumbers/%s' % (self.user_id, id))[0]

    def update_phone_number(self, id, data):
        """
        Update information about a phone number

        :type id: str
        :param id: id of a phone number

        Parameters
            name
                A name you choose for this number.
            applicationId
                The unique id of an Application you want to associate with this number.
            fallbackNumber
                Number to transfer an incoming call when the callback/fallback events can't
                be delivered.

        :Example:
        data = api.update_phone_number('numberId', {'applicationId': 'appId1'})
        """
        self._make_request('post', '/users/%s/phoneNumbers/%s' % (self.user_id, id), json=data)

    def delete_phone_number(self, id):
        """
        Remove a phone number

        :type id: str
        :param id: id of a phone number

        :Example:
        api.delete_phone_number('numberId')
        """
        self._make_request('delete', '/users/%s/phoneNumbers/%s' % (self.user_id, id))

    """
    Recording API
    """
    def get_recordings(self, query=None):
        """
        Get a list of call recordings

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of recordings

        :Example:
        list = api.get_recordings()
        """
        path = '/users/%s/recordings' % self.user_id
        return lazy_map(_set_media_name,
                        get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query)))

    def get_recording(self, id):
        """
        Gets information about a recording

        :type id: str
        :param id: id of a recording

        :rtype: dict
        :returns: recording information

        :Example:
        data = api.get_recording('recordingId')
        """
        path = '/users/%s/recordings/%s' % (self.user_id, id)
        return _set_media_name(self._make_request('get', path)[0])

    """
    Transcription API
    """
    def get_transcriptions(self, recording_id, query=None):
        """
        Get a list of transcriptions

        :type recording_id: str
        :param recording_id: id of a recording

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of transcriptions

        :Example:
        list = api.get_transcriptions('recordingId')
        """
        path = '/users/%s/recordings/%s/transcriptions' % (self.user_id, recording_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_transcription(self, recording_id):
        """
        Create a transcirption for given recording

        :type recording_id: str
        :param recording_id: id of a recording

        :rtype: str
        :returns: id of created transcription

        :Example:
        id = api.create_transcirption('recordingId')
        """
        path = '/users/%s/recordings/%s/transcriptions' % (self.user_id, recording_id)
        return self._make_request('post', path, json={})[2]

    def get_transcription(self, recording_id, id):
        """
        Get information about a transcription

        :type recording_id: str
        :param recording_id: id of a recording

        :type id: str
        :param id: id of a transcription

        :rtype: dict
        :returns: application information

        :Example:
        data = api.get_transcription('recordingId', 'transcriptionId')
        """
        path = '/users/%s/recordings/%s/transcriptions/%s' % (self.user_id, recording_id, id)
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
