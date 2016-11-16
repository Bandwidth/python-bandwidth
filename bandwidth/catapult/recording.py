import six
import itertools
from .lazy_enumerable import get_lazy_enumerator

lazy_map = map if six.PY3 else itertools.imap


def _set_media_name(recording):
    recording['mediaName'] = recording.get('media', '').split('/')[-1]
    return recording


class RecordingMixin:
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
