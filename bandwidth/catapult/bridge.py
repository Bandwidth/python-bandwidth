from .lazy_enumerable import get_lazy_enumerator
from .decorators import play_audio


@play_audio('bridge')
class BridgeMixin:
    """
    Bridge API
    """
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
