import urllib


class NumberInfoMixin:
    def get_number_info(self, number):
        path = '/phoneNumbers/numberInfo/%s' % urllib.quote(number)
        return self._make_request('get', path)[0]
