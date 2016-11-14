from .lazy_enumerable import get_lazy_enumerator
from .decorators import play_audio


@play_audio('conference')
class ConferenceMixin:
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
