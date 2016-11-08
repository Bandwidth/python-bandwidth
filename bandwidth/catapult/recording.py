import six
from .lazy_enumerable import get_lazy_enumerator
if six.PY2:
    from itertools import imap
    map = imap  # to use lazy map on python 2


def _set_media_name(recording):
    recording['mediaName'] = recording.get('media', '').split('/')[-1]
    return recording


class RecordingMixin:
    def get_recordings(self, query=None):
        path = '/users/%s/recordings' % self.user_id
        return map(_set_media_name, get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query)))

    def get_recording(self, id):
        path = '/users/%s/recordings/%s' % (self.user_id, id)
        return _set_media_name(self._make_request('get', path)[0])
