# Object models for SDK
from .client import Client

# Sentinel value to mark that some of properties have been not synced.
UNEVALUATED = object()


class Resource(object):
    client = None

    @classmethod
    def create(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented

    @classmethod
    def list(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented

    @classmethod
    def get(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented


class Call(object):
    call_id = None
    direction = None
    from_ = None
    to = None
    recording_enabled = None
    callback_url = None
    state = None
    start_time = None
    active_time = None
    client = None

    def __init__(self, data: dict):
        self.client = Client()
        if isinstance(data, dict):
            self.data = data
            self.set_up()
        elif isinstance(data, str):
            self.data = UNEVALUATED
            self.call_id = data
        else:
            raise TypeError('Accepted only call-id or call data as dictionary')

    def set_up(self):
        self.call_id = self.data.get('id') or self.data.get('callId')
        self.direction = self.data.get('direction')
        self.from_ = self.data.get('from')
        self.to = self.data.get('to')
        self.recording_enabled = self.data.get('recordingEnabled')
        self.callback_url = self.data.get('callbackUrl')
        self.state = self.data.get('state')
        self.start_time = self.data.get('startTime')
        self.active_time = self.data.get('activeTime')

    @classmethod
    def create(cls, caller, callee, **kwargs):
        client = cls.client or Client()
        url = 'calls/'

        json_data = {
            'from': caller,
            'to': callee,
            'callTimeout': 30,  # seconds
        }

        json_data.update(kwargs)
        data = client._post(url, data=json_data)
        location = data.headers['Location']
        call_id = location.split('/')[-1]
        return cls(call_id)

    @classmethod
    def get(cls, *args, **kwargs):
        client = cls.client or Client()
        data_as_dict = client.get_call_info(*args, **kwargs)
        return cls(data_as_dict)

    @classmethod
    def list(cls, *args, **kwargs):
        client = cls.client or Client()
        data_as_list = client.get_calls(*args, **kwargs)
        return [cls(v) for v in data_as_list]

    def __repr__(self):
        return 'Call({})'.format(repr(self.data) if self.data is not UNEVALUATED else self.call_id)

    # Audio part
    def play_audio(self, file_name):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = 'calls/{}/audio'.format(self.call_id)
        self.client._post(url, data={'fileUrl': file_name})

    def stop_audio(self):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = 'calls/{}/audio'.format(self.call_id)
        self.client._post(url, data={'fileUrl': ''})

    def speak_sentence(self, sentence, gender='female', locale=None, voice=None):
        url = 'calls/{}/audio'.format(self.call_id)
        json_data = {'sentence': sentence, 'gender': gender}
        if locale:
            json_data['locale'] = locale
        if voice:
            json_data['voice'] = voice
        self.client._post(url, data=json_data)

    def stop_sentence(self):
        url = 'calls/{}/audio'.format(self.call_id)
        self.client._post(url, data={'sentence': ''})

    def transfer(self, phone, callback_url=None):
        url = 'calls/{}'.format(self.call_id)
        json_data = {"transferTo": phone,
                     "state": "transferring"
                     }
        if callback_url:
            json_data['callbackUrl'] = callback_url

        return self.client._post(url, data=json_data)

    def set_call_property(self, timeout=None, **kwargs):
        url = 'calls/{}'.format(self.call_id)
        return self.client._post(url, data=kwargs, timeout=timeout)

    def bridge(self, *calls, bridge_audio=True):
        _calls = (self,) + calls
        return Bridge.create(*_calls, bridge_audio=bridge_audio)

    def refresh(self):
        url = 'calls/{}'.format(self.call_id)
        data = self.client._get(url).json()
        self.data.update(data)
        self.set_up()

    def send_dtmf(self, dtmf, timeout=None):
        '''
        Sends a string of characters as DTMF on the given call_id
        Valid chars are '0123456789*#ABCD'
        '''
        url = 'calls/{}/dtmf'.format(self.call_id)

        json_data = {'dtmfOut': dtmf}

        self.client._post(url, data=json_data, timeout=timeout)

    def receive_dtmf(self, max_digits, terminating_digits,
                     inter_digit_timeout='1', timeout=None):
        url = 'calls/{}/gather'.format(self.call_id)

        http_get_params = {
            'maxDigits': max_digits,
            'terminatingDigits': terminating_digits,
            'interDigitTimeout': inter_digit_timeout}

        return self.client._get(url, params=http_get_params, timeout=timeout)

    def hangup(self):
        '''
        Hangs up a call with the given call_id
        '''
        url = 'calls/{}/'.format(self.call_id)

        return self.client._post(url, data={}, timeout=None)

    def activate_gathering(self, maxDigits, interDigitTimeout, terminatingDigits, timeout=None, **kwargs):
        url = 'calls/{}/gather'.format(self.call_id)
        data = {'maxDigits': maxDigits,
                'interDigitTimeout': interDigitTimeout,
                'terminatingDigits': terminatingDigits,
                'prompt': kwargs.get('prompt')}
        data = {k: v for k, v in data.items() if v is not None}  # deleting keys with None values
        return self.client._post(url, data=data, timeout=timeout)

    def get_gather_info(self, gather_id, timeout=None):
        url = 'calls/{}/gather/{}'.format(self.call_id, gather_id)
        return self.client._get(url, timeout=timeout)

    def get_recordings(self, timeout=None):
        '''
        Retrieves an array with all the recordings of the call_id
        '''
        url = 'calls/{}/recordings'.format(self.call_id)

        return self.client._get(url, timeout=timeout).json()

