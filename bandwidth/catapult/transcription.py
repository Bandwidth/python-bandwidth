from .lazy_enumerable import get_lazy_enumerator


class TranscriptionMixin:
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
