import lxml.builder as lb
from lxml import etree
from collections import OrderedDict


class Response(object):
    """
        Root class for Bandwidth XML
    """
    def __init__(self):
        self.verbs = []

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        response = lb.E.Response(
            *self._create_body()
        )
        return etree.tostring(response, pretty_print=True, xml_declaration=True, )

    def _create_body(self):
        result = []
        for verb in self.verbs:
            result.append(verb.to_xml())
        return result

    def push(self, verb):
        self.verbs.append(verb)


class Pause(object):
    """
        Pause is a verb to specify the length of seconds to wait before executing the next verb
    """
    def __init__(self, duration):
        self._param = OrderedDict()
        self._param["duration"] = str(duration)

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.Pause("", self._param)


class Transfer(object):
    """
        The Transfer verb is used to transfer the call to another number
    """
    def __init__(self, transfer_caller_id=None, transfer_to=None, phone_number=None, speak_sentence=None,
                 play_audio=None, call_timeout=None, recording_enabled=None, recording_callback_url=None,
                 file_format=None, terminating_digits=None, max_duration=None, transcribe=None,
                 transcribe_callback_url=None):
        self._param = OrderedDict()
        self._subparam = OrderedDict()
        if transfer_caller_id is not None:
            self._param["transferCallerId"] = str(transfer_caller_id)
        if transfer_to is not None:
            self._param["transferTo"] = str(transfer_to)
        if call_timeout is not None:
            self._param["call_timeout"] = str(call_timeout)
        if recording_enabled is not None:
            self._param["recording_enabled"] = str(recording_enabled)
        if recording_callback_url is not None:
            self._param["recording_callback_url"] = str(recording_callback_url)
        if file_format is not None:
            self._param["file_format"] = str(file_format)
        if terminating_digits is not None:
            self._param["terminating_digits"] = str(terminating_digits)
        if max_duration is not None:
            self._param["max_duration"] = str(max_duration)
        if transcribe is not None:
            self._param["transcribe"] = str(transcribe)
        if transcribe_callback_url is not None:
            self._param["transcribe_callback_url"] = str(transcribe_callback_url)

        if phone_number is not None:
            assert isinstance(phone_number, list), 'Wrong type - expecting a list of phone numbers'
            self._subparam["phoneNumber"] = phone_number
        if speak_sentence is not None:
            assert isinstance(speak_sentence, SpeakSentence), 'Wrong type - expecting a SpeakSentence object'
            self._subparam["speakSentence"] = speak_sentence
        if play_audio is not None:
            assert isinstance(play_audio, PlayAudio), 'Wrong type - expecting a PlayAudio object'
            self._subparam["playAudio"] = play_audio

    def _get_sub_parameters(self):
        sub_parameters = []

        if len(self._subparam) == 0:
            return {}
        if "phoneNumber" in self._subparam and self._subparam["phoneNumber"] is not None:
            for number in self._subparam["phoneNumber"]:
                sub_parameters.append(lb.E.PhoneNumber(number))
        if "speakSentence" in self._subparam and self._subparam["speakSentence"] is not None:
            sub_parameters.append(self._subparam["speakSentence"].to_xml())
        if "playAudio" in self._subparam and self._subparam["playAudio"] is not None:
            sub_parameters.append(self._subparam["playAudio"].to_xml())

        return sub_parameters

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.Transfer(self._param, *self._get_sub_parameters())


class SpeakSentence(object):
    """
        The SpeakSentence verb is used to convert any text into speak
    """
    def __init__(self, text, gender=None, locale=None, voice=None):
        self._param = OrderedDict()
        self.text = text
        if gender is not None:
            self._param["gender"] = str(gender)
        if locale is not None:
            self._param["locale"] = str(locale)
        if voice is not None:
            self._param["voice"] = voice

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.SpeakSentence(self._param, self.text)


class Gather(object):
    """
        The Gather verb is used to collect digits for some period of time
    """
    def __init__(self, request_url, request_url_timeout=None, terminating_digits=None, inter_digit_timeout=None,
                 bargeable=None, speak_sentence=None, play_audio=None, max_digits=None):
        self._param = OrderedDict()
        self._subparam = OrderedDict()
        if request_url is not None:
            self._param["requestUrl"] = str(request_url)
        if request_url_timeout is not None:
            self._param["requestUrlTimeout"] = str(request_url_timeout)
        if terminating_digits is not None:
            self._param["terminatingDigits"] = str(terminating_digits)
        if inter_digit_timeout is not None:
            self._param["interDigitTimeout"] = str(inter_digit_timeout)
        if bargeable is not None:
            self._param["bargeable"] = str(bargeable)
        if max_digits is not None:
            self._param["max_digits"] = str(max_digits)
        if speak_sentence is not None:
            assert isinstance(speak_sentence, SpeakSentence), 'Wrong type - expecting a SpeakSentence object'
            self._subparam["speakSentence"] = speak_sentence
        if play_audio is not None:
            assert isinstance(play_audio, PlayAudio), 'Wrong type - expecting a PlayAudio object'
            self._subparam["playAudio"] = play_audio

    def _get_sub_parameters(self):
        sub_parameters = []
        if len(self._subparam) == 0:
            return {}
        if "playAudio" in self._subparam and self._subparam["playAudio"] is not None:
            sub_parameters.append(self._subparam["playAudio"].to_xml())

        if "speakSentence" in self._subparam and self._subparam["speakSentence"] is not None:
            sub_parameters.append(self._subparam["speakSentence"].to_xml())
        return sub_parameters

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.Gather(self._param, *self._get_sub_parameters())


class PlayAudio(object):
    """
        The PlayAudio verb is used to play an audio file in the call
    """
    def __init__(self, url=None, digits=None):
        self._param = OrderedDict()
        self.url = url
        if digits is not None:
            self._param["digits"] = digits

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        if len(self._param) > 0:
            if self.url is not None:
                response = lb.E.PlayAudio(self._param, self.url)
            else:
                response = lb.E.PlayAudio("", self._param)
        elif self.url is not None:
            response = lb.E.PlayAudio(self.url)
        else:
            response = lb.E.PlayAudio()

        return response


class Media(object):
    """
         Media is a noun that is exclusively placed within <SendMessage> to provide the messages with attached
         media (MMS) capability
    """
    def __init__(self, url_list):
        assert isinstance(url_list, list), 'Wrong type - expecting a list of URLs'
        self._subparam = OrderedDict()
        self._subparam["url_list"] = url_list

    def _get_sub_parameters(self):
        sub_parameters = []
        for url in self._subparam["url_list"]:
            sub_parameters.append(lb.E.Url(url))
        return sub_parameters

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        if "url_list" in self._subparam and self._subparam["url_list"] is not None:
            return lb.E.Media(*self._get_sub_parameters())
        return lb.E.Media()


class Record(object):
    """
        The Record verb allow call recording
    """
    def __init__(self, request_url=None, request_url_timeout=None, terminating_digits=None, max_duration=None,
                 transcribe=None, transcribe_callback_url=None, file_format=None):
        self._param = OrderedDict()
        if request_url is not None:
            self._param["requestUrl"] = str(request_url)
        if request_url_timeout is not None:
            self._param["requestUrlTimeout"] = str(request_url_timeout)
        if terminating_digits is not None:
            self._param["terminatingDigits"] = str(terminating_digits)
        if max_duration is not None:
            self._param["maxDuration"] = str(max_duration)
        if transcribe is not None:
            self._param["transcribe"] = str(transcribe)
        if transcribe_callback_url is not None:
            self._param["transcribeCallbackUrl"] = str(transcribe_callback_url)
        if file_format is not None:
            self._param["file_format"] = str(file_format)

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.Record("", self._param)


class Redirect(object):
    """
        The Redirect verb is used to redirect the current XML execution to another URL
    """
    def __init__(self, request_url=None, request_url_timeout=None):
        self._param = OrderedDict()
        if request_url is not None:
            self._param["requestUrl"] = str(request_url)
        if request_url_timeout is not None:
            self._param["requestUrlTimeout"] = str(request_url_timeout)

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.Redirect("", self._param)


class Reject(object):
    """
        The Reject verb is used to reject incoming calls
    """
    @staticmethod
    # Turn a simple dict of key/value pairs into XML
    def to_xml():
        return lb.E.Reject("")


class SendMessage(object):
    """
        The SendMessage is used to send a text message
    """
    def __init__(self, text, from_number, to_number, status_callback_url=None, request_url=None,
                 request_url_timeout=None):
        self._param = OrderedDict()
        self.text = text
        if from_number is not None:
            self._param["from"] = str(from_number)
        if to_number is not None:
            self._param["to"] = str(to_number)
        if status_callback_url is not None:
            self._param["statusCallbackUrl"] = str(status_callback_url)
        if request_url is not None:
            self._param["requestUrl"] = str(request_url)
        if request_url_timeout is not None:
            self._param["requestUrlTimeout"] = str(request_url_timeout)

    # Turn a simple dict of key/value pairs into XML
    def to_xml(self):
        return lb.E.SendMessage(self._param, self.text)


class Hangup(object):
    """
        The Hangup verb is used to hangup current call
    """
    @staticmethod
    # Turn a simple dict of key/value pairs into XML
    def to_xml():
        return lb.E.Hangup("")
