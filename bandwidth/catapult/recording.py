from itertools import imap
from .lazy_enumerable import get_lazy_enumerator


def _set_media_name(recording):
    recording['mediaName'] = recording.get('media', '').split('/')[-1]
    return recording


class RecordingMixin:
    def get_recordings(self, query=None):
        path = '/users/%s/recordings' % self.user_id
        return imap(_set_media_name, get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query)))

    def get_recording(self, id):
        path = '/users/%s/recordings/%s' % (self.user_id, id)
        return _set_media_name(self._make_request('get', path)[0])
