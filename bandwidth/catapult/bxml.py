from lxml import etree as ET
from lxml.builder import E


class BXMLResponse:
    def __init__(self, *response_verbs):
        self.response = E.xml(E.Response(*response_verbs))

    def to_xml(self):
        return ET.tostring(self.response)

    def __str__(self):
        return self.to_xml().decode('utf-8')
