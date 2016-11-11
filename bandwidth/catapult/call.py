from .lazy_enumerable import get_lazy_enumerator
from .decorators import play_audio


@play_audio('call')
class CallMixin:
    """
    Call API
    """
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
