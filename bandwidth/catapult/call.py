from .lazy_enumerable import get_lazy_enumerator
from .decorators import play_audio


@play_audio('call')
class CallMixin:
    def get_calls(self, query=None):
        path = '/users/%s/calls' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_call(self, data):
        return self._make_request('post', '/users/%s/calls' % self.user_id, json=data)[2]

    def get_call(self, id):
        return self._make_request('get', '/users/%s/calls/%s' % (self.user_id, id))[0]

    def update_call(self, id, data):
        return self._make_request('post', '/users/%s/calls/%s' % (self.user_id, id), json=data)[2]

    def play_audio_to_call(self, id, data):
        self._make_request('post', '/users/%s/calls/%s/audio' % (self.user_id, id), json=data)

    def send_dtmf_to_call(self, id, data):
        self._make_request('post', '/users/%s/calls/%s/dtmf' % (self.user_id, id), json=data)

    def get_call_recordings(self, id):
        path = '/users/%s/calls/%s/recordings' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda:  self._make_request('get', path))

    def get_call_transcriptions(self, id):
        path = '/users/%s/calls/%s/transcriptions' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def get_call_events(self, id):
        path = '/users/%s/calls/%s/events' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def get_call_event(self, id, event_id):
        return self._make_request('get', '/users/%s/calls/%s/events/%s' % (self.user_id, id, event_id))[0]

    def create_call_gather(self, id, data):
        return self._make_request('post', '/users/%s/calls/%s/gather' % (self.user_id, id), json=data)[2]

    def get_call_gather(self, id, gather_id):
        return self._make_request('get', '/users/%s/calls/%s/gather/%s' % (self.user_id, id, gather_id))[0]

    def update_call_gather(self, id, gather_id, data):
        self._make_request('post', '/users/%s/calls/%s/gather/%s' % (self.user_id, id, gather_id), json=data)

    # extensions

    def answer_call(self, id):
        self.update_call(id, {'state': 'active'})

    def reject_call(self, id):
        self.update_call(id, {'state': 'rejected'})

    def hangup_call(self, id):
        self.update_call(id, {'state': 'completed'})

    def tune_call_recording(self, id, enabled):
        self.update_call(id, {'recordingEnabled': enabled})

    def transfer_call(self, id, to, caller_id=None, whisper_audio=None, callback_url=None):
        data = {'state': 'transferring', 'transferTo': to}
        if caller_id is not None:
            data['transferCallerId'] = caller_id
        if whisper_audio is not None:
            data['whisperAudio'] = whisper_audio
        if callback_url is not None:
            data['callbackUrl'] = callback_url
        return self.update_call(id, data)
