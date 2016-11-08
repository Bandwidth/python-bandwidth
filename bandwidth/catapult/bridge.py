from .lazy_enumerable import get_lazy_enumerator
from .decorators import play_audio


@play_audio('bridge')
class BridgeMixin:
    def get_bridges(self, query=None):
        path = '/users/%s/bridges' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_bridge(self, data):
        return self._make_request('post', '/users/%s/bridges' % self.user_id, json=data)[2]

    def get_bridge(self, id):
        return self._make_request('get', '/users/%s/bridges/%s' % (self.user_id, id))[0]

    def update_bridge(self, id, data):
        self._make_request('post', '/users/%s/bridges/%s' % (self.user_id, id), json=data)

    def get_bridge_calls(self, id):
        path = '/users/%s/bridges/%s/calls' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def play_audio_to_bridge(self, id, data):
        self._make_request('post', '/users/%s/bridges/%s/audio' % (self.user_id, id), json=data)
