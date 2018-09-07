from lxml import etree as ET
from lxml.builder import E


class Response:
    """
    BXML Response element

    :Example:
        from bandwidth.voice.bxml import Response
        response = Response(E.Call({'from': '+1234567890', 'to': '+1234567891'}), E.Hangup())
    """

    def __init__(self, *response_verbs):
        """
        Initialize Response element

        :type response_verbs: list
        :param response_verbs: on or several of BXML verbs

        :Example:
        response = bandwidth.catapult.bxml.Response(E.Hangup())
        response = bandwidth.catapult.bxml.Response(E.Call({'from': '+1234567890', 'to': '+1234567891'}), E.Hangup())
        response = bandwidth.catapult.bxml.Response(E.PlayAudio("Thank you"), E.Hangup())
        """
        self.response = E.xml(E.Response(*response_verbs))

    def to_xml(self):
        """
        Convert response object to XML presentation

        :rtype str
        :returns XML text

        :Example:
        xml = response.to_xml()
        """
        return ET.tostring(self.response)

    def __str__(self):
        """
        Convert response object to XML presentation implicitly

        :rtype str
        :returns XML text

        :Example:
        xml = str(response)
        """
        return self.to_xml().decode('utf-8')
