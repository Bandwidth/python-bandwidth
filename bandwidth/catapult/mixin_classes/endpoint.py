from .lazy_enumerable import get_lazy_enumerator


class EndpointMixin:
    """
    Endpoint API
    """
    def get_domain_endpoints(self, id, query=None):
        """
        Get a list of domain's endpoints

        :type id: str
        :param id: id of a domain

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of endpoints

        :Example:
        list = api.get_domain_endpoints()
        """
        path = '/users/%s/domains/%s/endpoints' % (self.user_id, id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_domain_endpoint(self, id, data):
        """
        Create a domain endpoint

        :type id: str
        :param id: id of a domain

        Parameters
            name
                The name of endpoint
            description
                String to describe the endpoint
            applicationId
                Id of application which will handle calls and messages of this endpoint
            enabled
                When set to true, SIP clients can register as this device to receive and
                make calls. When set to false, registration, inbound, and outbound
                calling will not succeed.
            credentials.password
                Password of created SIP account


        :rtype: str
        :returns: id of endpoint

        :Example:
        id = api.create_domain_endpoint({'name': 'my-sip'})
        """
        data['domainId'] = id
        return self._make_request('post', '/users/%s/domains/%s/endpoints' % (self.user_id, id), json=data)[2]

    def get_domain_endpoint(self, id, endpoint_id):
        """
        Get information about an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :rtype: dict
        :returns: call information

        :Example:
        data = api.get_domain_endpoint('domainId', 'endpointId')
        """
        return self._make_request('get', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id))[0]

    def update_domain_endpoint(self, id, endpoint_id, data):
        """
        Update information about an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        Parameters
            description
                String to describe the endpoint
            applicationId
                Id of application which will handle calls and messages of this endpoint
            enabled
                When set to true, SIP clients can register as this device to receive and
                make calls. When set to false, registration, inbound, and outbound
                calling will not succeed.
            credentials.password
                Password of created SIP account

        :Example:
        api.update_domain_endpoint('domainId', 'endpointId', {'enabled': False})
        """
        self._make_request('post', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id), json=data)

    def delete_domain_endpoint(self, id, endpoint_id):
        """
        Remove an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :Example:
        api.delete_domain_endpoint('domainId', 'endpointId')
        """
        self._make_request('delete', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, id, endpoint_id))

    def create_domain_endpoint_auth_token(self, id, endpoint_id, data={'expires': 3600}):
        """
        Create auth token for an endpoint

        :type id: str
        :param id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :Example:
        token = api.create_domain_endpoint_auth_token('domainId', 'endpointId')
        """
        path = '/users/%s/domains/%s/endpoints/%s/tokens' % (self.user_id, id, endpoint_id)
        return self._make_request('post', path, json=data)[0]
