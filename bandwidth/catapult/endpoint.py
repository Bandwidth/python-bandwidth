from .lazy_enumerable import get_lazy_enumerator


class EndpointMixin:
    def get_domain_endpoints(self, id, query=None):
        path = '/users/%s/domains/%s/endpoints' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_domain_endpoint(self, id, data):
        data['domainId'] = id
        return self._make_request('post', '/users/%s/domains/%s/endpoints' % (self.user_id, id), json=data)[2]

    def get_domain_endpoint(self, id, endpoint_id):
        return self._make_request('get', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id))[0]

    def update_domain_endpoint(self, id, endpoint_id, data):
        self._make_request('post', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id), json=data)

    def delete_domain_endpoint(self, id, endpoint_id):
        self._make_request('delete', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id))

    def create_domain_endpoint_auth_token(self, id, endpoint_id, data={'expires': 3600}):
        path = '/users/%s/domains/%s/endpoints/%s/tokens' % (self.user_id, id, endpoint_id)
        return self._make_request('post', path, json=data)[0]
