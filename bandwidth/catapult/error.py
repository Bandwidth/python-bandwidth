from .lazy_enumerable import get_lazy_enumerator


class ErrorMixin:
    def get_errors(self, query=None):
        path = '/users/%s/errors' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def get_error(self, id):
        return self._make_request('get', '/users/%s/errors/%s' % (self.user_id, id))[0]
