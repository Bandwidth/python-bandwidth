from .lazy_enumerable import get_lazy_enumerator


class PhoneNumbersMixin:
    def get_phone_numbers(self, query=None):
        path = '/users/%s/phoneNumbers' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_phone_number(self, data):
        return self._make_request('post', '/users/%s/phoneNumbers' % self.user_id, json=data)[2]

    def get_phone_number(self, id):
        return self._make_request('get', '/users/%s/phoneNumbers/%s' % (self.user_id, id))[0]

    def update_phone_number(self, id, data):
        self._make_request('post', '/users/%s/phoneNumbers/%s' % (self.user_id, id), json=data)

    def delete_phone_number(self, id):
        self._make_request('delete', '/users/%s/phoneNumbers/%s' % (self.user_id, id))
