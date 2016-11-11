from .lazy_enumerable import get_lazy_enumerator


class DomainMixin:
    """
    Domain API
    """
    def get_domains(self, query=None):
        """
        Get a list of domains

        Query parameters
            size
                Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 100)
        :rtype: types.GeneratorType
        :returns: list of domains

        :Example:
        list = api.get_domains()
        """
        path = '/users/%s/domains' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=query))

    def create_domain(self, data):
        """
        Create a domain

        Parameters
            name
                The name is a unique URI to be used in DNS lookups
            description
                String to describe the domain
        :rtype: str
        :returns: id of created domain

        :Example:
        id = api.create_domain({'name': 'qwerty'})
        """
        return self._make_request('post', '/users/%s/domains' % self.user_id, json=data)[2]

    def delete_domain(self, id):
        """
        Delete a domain

        :type id: str
        :param id: id of a domain

        :Example:
        api.delete_domain('domainId')
        """
        self._make_request('delete', '/users/%s/domains/%s' % (self.user_id, id))
