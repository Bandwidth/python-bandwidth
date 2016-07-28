from bandwidth_sdk import xml
from .utils import SdkTestCase


class XmlTest(SdkTestCase):
    def test_pause_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Pause duration=\"6\"></Pause>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        pause = xml.Pause(duration=6)
        xml_response.push(pause)
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_pause_direct_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Pause duration=\"6\"></Pause>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        pause = xml.Pause(6)
        xml_response.push(pause)
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_transfer_direct_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Transfer transferCallerId=\"+11234567891\" transferTo=\"+11234567892\"/>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Transfer(transfer_caller_id="+11234567891", transfer_to="+11234567892"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_hangup_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Hangup></Hangup>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Hangup())
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_transfer_empty_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Transfer/>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Transfer())
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_transfer_speak_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Transfer transferCallerId=\"+11234567891\" transferTo=\"+11234567892\">\n"
                                     "    <PhoneNumber>+9991112345</PhoneNumber>\n"
                                     "    <PhoneNumber>+8888811111</PhoneNumber>\n"
                                     "    <SpeakSentence gender=\"male\" locale=\"en_US\" voice=\"paul\">"
                                     "Inner speak sentence</SpeakSentence>\n"
                                     "  </Transfer>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Transfer(transfer_caller_id="+11234567891", transfer_to="+11234567892",
                                       phone_number=["+9991112345", "+8888811111"],
                                       speak_sentence=xml.SpeakSentence("Inner speak sentence", gender="male",
                                                                        voice="paul", locale="en_US")))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_speak_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <SpeakSentence gender=\"male\" locale=\"en_US\" voice=\"paul\">"
                                     "Text to speak</SpeakSentence>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.SpeakSentence("Text to speak", gender="male", voice="paul", locale="en_US"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_gather_minimum_xml(self):
        expected_result = str.encode("<?xml version='1.0' encoding='ASCII'?>\n"
                                     "<Response>\n"
                                     "  <Gather requestUrl=\"http://test.com\"/>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Gather(request_url="http://test.com"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_gather_speak_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Gather requestUrl=\"http://test.com\" requestUrlTimeout=\"5\" "
                                     "terminatingDigits=\"#\" interDigitTimeout=\"5\" bargeable=\"true\">\n"
                                     "    <SpeakSentence gender=\"male\" locale=\"en_US\" voice=\"paul\">"
                                     "Inner speak sentence</SpeakSentence>\n"
                                     "  </Gather>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Gather(request_url="http://test.com", request_url_timeout="5", terminating_digits="#",
                                     inter_digit_timeout="5", bargeable="true",
                                     speak_sentence=xml.SpeakSentence("Inner speak sentence", gender="male",
                                                                      voice="paul", locale="en_US")))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_play_audio_empty_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <PlayAudio/>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.PlayAudio())
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_play_audio_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <PlayAudio>http://test.com</PlayAudio>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.PlayAudio(url="http://test.com"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_media_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Media>\n"
                                     "    <Url>http://test1.com</Url>\n"
                                     "    <Url>http://test2.com</Url>\n"
                                     "  </Media>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Media(url_list=["http://test1.com", "http://test2.com"]))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_record_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Record requestUrl=\"/stepTransfer\" requestUrlTimeout=\"5\" "
                                     "terminatingDigits=\"#\"></Record>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Record(request_url="/stepTransfer", request_url_timeout="5", terminating_digits="#"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_redirect_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Redirect requestUrl=\"/stepTransfer\" requestUrlTimeout=\"5\"></Redirect>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Redirect(request_url="/stepTransfer", request_url_timeout="5"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_reject_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <Reject></Reject>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.Reject())
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)

    def test_send_message_xml(self):
        expected_result = str.encode("<?xml version=\'1.0\' encoding=\'ASCII\'?>\n"
                                     "<Response>\n"
                                     "  <SendMessage from=\"+19994444\" to=\"+144445555\">"
                                     "Message to send</SendMessage>\n"
                                     "</Response>\n")

        xml_response = xml.Response()
        xml_response.push(xml.SendMessage("Message to send", "+19994444", "+144445555"))
        actual_result = xml_response.to_xml()

        self.assertEqual(expected_result, actual_result)
