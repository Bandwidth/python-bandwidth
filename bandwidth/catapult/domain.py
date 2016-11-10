from .lazy_enumerable import get_lazy_enumerator


class DomainMixin:
    def get_domains(self, query=None):
        path = '/users/%s/domains' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_domain(self, data):
        return self._make_request('post', '/users/%s/domains' % self.user_id, json=data)[2]

    def delete_domain(self, id):
        self._make_request('delete', '/users/%s/domains/%s' % (self.user_id, id))
