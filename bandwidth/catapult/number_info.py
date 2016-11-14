import six
import urllib

quote = urllib.parse.quote if six.PY3 else urllib.quote


class NumberInfoMixin:
    """
    NumberInfo API
    """
    def get_number_info(self, number):
        """
        Gets CNAM information about phone number

        :type number: str
        :param number: phone number to get information

        :rtype: dict
        :returns: CNAM information

        :Example:
        data = api.get_number_info('+1234567890')

        """
        path = '/phoneNumbers/numberInfo/%s' % quote(number)
        return self._make_request('get', path)[0]
