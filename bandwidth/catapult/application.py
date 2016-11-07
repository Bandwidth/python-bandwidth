from .lazy_enumerable import get_lazy_enumerator


class ApplicationMixin:
    def get_applications(self, query=None):
        return get_lazy_enumerator(self, lambda: self._make_request('get', '/users/%s/applications' % self.user_id, params=query))

    def create_application(self, data):
        return self._make_request('post', '/users/%s/applications' % self.user_id, json=data)[2]

    def get_application(self, id):
        return self._make_request('get', '/users/%s/applications/%s' % (self.user_id, id))[0]

    def delete_application(self, id):
        self._make_request('delete', '/users/%s/applications/%s' % (self.user_id, id))
