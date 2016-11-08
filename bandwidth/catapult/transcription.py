from .lazy_enumerable import get_lazy_enumerator


class TranscriptionMixin:
    def get_transcriptions(self, recording_id, query=None):
        path = '/users/%s/recordings/%s/transcriptions' % (self.user_id, recording_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_transcription(self, recording_id):
        path = '/users/%s/recordings/%s/transcriptions' % (self.user_id, recording_id)
        return self._make_request('post', path, json={})[2]

    def get_transcription(self, recording_id, id):
        path = '/users/%s/recordings/%s/transcriptions/%s' % (self.user_id, recording_id, id)
        return self._make_request('get', path)[0]
