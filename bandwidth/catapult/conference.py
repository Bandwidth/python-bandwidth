from .lazy_enumerable import get_lazy_enumerator
from .decorators import play_audio


@play_audio('conference')
class ConferenceMixin:
    def create_conference(self, data):
        return self._make_request('post', '/users/%s/conferences' % self.user_id, json=data)[2]

    def get_conference(self, id):
        return self._make_request('get', '/users/%s/conferences/%s' % (self.user_id, id))[0]

    def update_conference(self, id, data):
        self._make_request('post', '/users/%s/conferences/%s' % (self.user_id, id), json=data)

    def play_audio_to_conference(self, id, data):
        self._make_request('post', '/users/%s/conferences/%s/audio' % (self.user_id, id), json=data)

    def get_conference_members(self, id):
        path = '/users/%s/conferences/%s/members' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def create_conference_member(self, id, data):
        path = '/users/%s/conferences/%s/members' % (self.user_id, id)
        return self._make_request('post', path, json=data)[2]

    def get_conference_member(self, id, member_id):
        path = '/users/%s/conferences/%s/members/%s' % (self.user_id, id, member_id)
        return self._make_request('get', path)[0]

    def update_conference_member(self, id, member_id, data):
        path = '/users/%s/conferences/%s/members/%s' % (self.user_id, id, member_id)
        self._make_request('post', path, json=data)

    def play_audio_to_conference_member(self, id, member_id, data):
        path = '/users/%s/conferences/%s/members/%s/audio' % (self.user_id, id, member_id)
        self._make_request('post', path, json=data)

    # extensions

    def speak_sentence_to_conference_member(self, id, member_id, sentence,
                                            gender='female', voice='susan', locale='en_US', tag=None):
        self.play_audio_to_conference_member(id, member_id, {
            'sentence': sentence,
            'gender': gender,
            'voice': voice,
            'locale': locale,
            'tag': tag
        })

    def play_audio_file_to_conference_member(self, id, member_id, file_url, tag=None):
        self.play_audio_to_conference_member(id, member_id, {
            'fileUrl': file_url,
            'tag': tag
        })

    def delete_conference_member(self, id, member_id):
        self.update_conference_member(id, member_id, {'state': 'completed'})

    def hold_conference_member(self, id, member_id, hold):
        self.update_conference_member(id, member_id, {'hold': hold})

    def mute_conference_member(self, id, member_id, mute):
        self.update_conference_member(id, member_id, {'mute': mute})

    def terminate_conference(self, id):
        self.update_conference(id, {'state': 'completed'})

    def hold_conference(self, id, hold):
        self.update_conference(id, {'hold': hold})

    def mute_conference(self, id, mute):
        self.update_conference(id, {'mute': mute})
