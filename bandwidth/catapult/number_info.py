import six
import urllib

quote = urllib.parse.quote if six.PY3 else urllib.quote


class NumberInfoMixin:
    def get_number_info(self, number):
        path = '/phoneNumbers/numberInfo/%s' % quote(number)
        return self._make_request('get', path)[0]
