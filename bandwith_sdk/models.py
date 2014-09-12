# Object models for SDK
from .client import Client
from .utils import prepare_json

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


class Call(Resource):
    path = 'calls'
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
        """
        Makes a phone call.

        :param caller: One of your telephone numbers the call should come from (must be in E.164 format,
            like +19195551212)

        :param callee: The number to call (must be either an E.164 formated number, like +19195551212, or a
            valid SIP URI, like sip:someone@somewhere.com)

        :param kwargs:
            recordingEnabled -Indicates if the call should be recorded after being created.
            bridgeId - Create a call in a bridge

        :return: new Call instance with @call_id and @from_, @to fields.
        """
        client = cls.client or Client()

        json_data = {
            'from': caller,
            'to': callee,
            'callTimeout': 30,  # seconds
        }

        json_data.update(kwargs)
        data = client._post(cls.path, data=json_data)
        location = data.headers['Location']
        call_id = location.split('/')[-1]
        call = cls(call_id)
        call.from_ = caller
        call.to = callee
        return call

    @classmethod
    def get(cls, call_id):
        """
        Gets information about an active or completed call.

        :param call_id:

        :return: new Call instance with all provided fields.
        """
        client = cls.client or Client()
        url = '{}/{}'.format(cls.path, call_id)
        data_as_dict = client._get(url).json()
        return cls(data_as_dict)

    @classmethod
    def list(cls, **query):
        """
        Gets a list of active and historic calls you made or received.

        :param page: Used for pagination to indicate the page requested for querying a list of calls.
                    If no value is specified the default is 0.

        :param size: Used for pagination to indicate the size of each page requested for querying a list of calls.
                    If no value is specified the default value is 25. (Maximum value 1000)

        :param bridgeId: Id of the bridge for querying a list of calls history. (Pagination do not apply).

        :param conferenceId: Id of the conference for querying a list of calls history. (Pagination do not apply).

        :param from: Telephone number to filter the calls that came from (must be in E.164 format, like +19195551212).

        :param to: The number to filter calls that was called to (must be either an E.164 formated number,
                like +19195551212, or a valid SIP URI, like sip:someone@somewhere.com).

        :return: list of Call instances
        """
        client = cls.client or Client()
        data_as_list = client._get(cls.path, params=query).json()
        return [cls(v) for v in data_as_list]

    def __repr__(self):
        return 'Call({})'.format(repr(self.data) if self.data is not UNEVALUATED else self.call_id)

    # Audio part
    def play_audio(self, file_name):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = '{}/{}/audio'.format(self.path, self.call_id)
        self.client._post(url, data={'fileUrl': file_name})

    def stop_audio(self):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = '{}/{}/audio'.format(self.path, self.call_id)
        self.client._post(url, data={'fileUrl': ''})

    def speak_sentence(self, sentence, gender='female', locale=None, voice=None):
        url = '{}/{}/audio'.format(self.path, self.call_id)
        json_data = {'sentence': sentence, 'gender': gender}
        if locale:
            json_data['locale'] = locale
        if voice:
            json_data['voice'] = voice
        self.client._post(url, data=json_data)

    def stop_sentence(self):
        url = '{}/{}/audio'.format(self.path, self.call_id)
        self.client._post(url, data={'sentence': ''})

    def transfer(self, phone, callback_url=None):
        url = '{}/{}'.format(self.path, self.call_id)
        json_data = {"transferTo": phone,
                     "state": "transferring"
                     }
        if callback_url:
            json_data['callbackUrl'] = callback_url

        return self.client._post(url, data=json_data)

    def set_call_property(self, **kwargs):
        url = '{}/{}'.format(self.path, self.call_id)
        return self.client._post(url, data=kwargs)

    def bridge(self, *calls, bridge_audio=True):
        _calls = (self,) + calls
        return Bridge.create(*_calls, bridge_audio=bridge_audio)

    def refresh(self):
        url = '{}/{}'.format(self.path, self.call_id)
        data = self.client._get(url).json()
        self.data.update(data)
        self.set_up()

    def send_dtmf(self, dtmf, timeout=None):
        '''
        Sends a string of characters as DTMF on the given call_id
        Valid chars are '0123456789*#ABCD'
        '''
        url = '{}/{}/dtmf'.format(self.path, self.call_id)

        json_data = {'dtmfOut': dtmf}

        self.client._post(url, data=json_data, timeout=timeout)

    def receive_dtmf(self, max_digits, terminating_digits,
                     inter_digit_timeout='1', timeout=None):
        url = '{}/{}/gather'.format(self.path, self.call_id)

        http_get_params = {
            'maxDigits': max_digits,
            'terminatingDigits': terminating_digits,
            'interDigitTimeout': inter_digit_timeout}

        return self.client._get(url, params=http_get_params, timeout=timeout)

    def hangup(self):
        '''
        Hangs up a call with the given call_id
        '''
        url = '{}/{}/'.format(self.path, self.call_id)

        return self.client._post(url, data={}, timeout=None)

    def activate_gathering(self, maxDigits, interDigitTimeout, terminatingDigits, timeout=None, **kwargs):
        url = '{}/{}/gather'.format(self.path, self.call_id)
        data = {'maxDigits': maxDigits,
                'interDigitTimeout': interDigitTimeout,
                'terminatingDigits': terminatingDigits,
                'prompt': kwargs.get('prompt')}
        # deleting keys with None values
        data = {k: v for k, v in data.items() if v is not None}
        return self.client._post(url, data=data, timeout=timeout)

    def get_gather_info(self, gather_id, timeout=None):
        url = '{}/{}/gather/{}'.format(self.path, self.call_id, gather_id)
        return self.client._get(url, timeout=timeout)

    def get_recordings(self, timeout=None):
        '''
        Retrieves an array with all the recordings of the call_id
        '''
        url = '{}/{}/recordings'.format(self.path, self.call_id)

        return self.client._get(url, timeout=timeout).json()


class Application(Resource):

    application_id = None
    name = None
    incoming_call_url = None
    incoming_call_url_callback_timeout = None
    incoming_call_fallback_url = None
    incoming_sms_url = None
    incoming_sms_url_callback_timeout = None
    incoming_sms_fallback_url = None
    callback_http_method = 'post'
    auto_answer = True
    _fields = ('application_id', 'name',
               'incoming_call_url',
               'incoming_call_url_callback_timeout',
               'incoming_call_fallback_url',
               'incoming_sms_url',
               'incoming_sms_url_callback_timeout',
               'incoming_sms_fallback_url', 'callback_http_method', 'auto_answer')

    def __init__(self, data: dict):
        self.client = Client()
        if isinstance(data, dict):
            self.data = data
            self.set_up()
        elif isinstance(data, str):
            self.data = UNEVALUATED
            self.application_id = data
        else:
            raise TypeError('Accepted only call-id or call data as dictionary')

    def set_up(self):
        [setattr(self, k, v) for k, v in self.data.items() if k in self._fields and v]

    @classmethod
    def create(cls, **kwargs):
        """
        :name: A name you choose for this application
        :incoming_call_url: A URL where call events will be sent for an inbound call
        :incoming_call_url_callback_timeout: Determine how long should the platform wait for incomingCallUrl's response before
        timing out in milliseconds.
        :incoming_call_fallback_url: The URL used to send the callback event if the request to incomingCallUrl fails.
        :incoming_sms_url:  A URL where message events will be sent for an inbound SMS message.
        :incoming_sms_url_callback_timeout: Determine how long should the platform wait for incomingSmsUrl's response before
        timing out in milliseconds.
        :incoming_sms_fallback_url: The URL used to send the callback event if the request to incomingSmsUrl fails.
        :callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.
        (If not set the default is HTTP POST).
        :auto_answer: Determines whether or not an incoming call should be automatically answered. Default value is 'true'.
        :return: Application instance
        """
        client = cls.client or Client()
        url = 'applications/'
        data = prepare_json(
            {k: v for k, v in kwargs.items() if v and k in cls._fields})
        resp = client._post(url, data=data)
        location = resp.headers['Location']
        application_id = location.split('/')[-1]
        kwargs.update({'application_id': application_id})
        return cls(data=kwargs)

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


class Bridge(Resource):
    path = 'bridges'
    id = None
    state = None
    call_ids = None
    calls = None
    bridge_audio = None
    completed_time = None
    created_time = None
    activated_time = None
    client = None

    def __init__(self, id, *calls, bridge_audio=True, data=None):
        self.calls = calls
        self.client = Client()
        self.bridge_audio = bridge_audio
        self.id = id
        if data:
            self.set_up(data)

    def set_up(self, data):
        self.state = data.get('state')
        self.bridge_audio = data.get('bridgeAudio')
        self.completed_time = data.get('completedTime')
        self.created_time = data.get('createdTime')
        self.activated_time = data.get('activatedTime')

    @classmethod
    def list(cls, page=1, size=20):
        client = cls.client or Client()
        data_as_list = client._get(cls.path, params=dict(page=page, size=size)).json()
        return [cls(v['id'], data=v) for v in data_as_list]

    @classmethod
    def get(cls, bridge_id):
        client = cls.client or Client()
        url = '{}/{}'.format(cls.path, bridge_id)
        data_as_dict = client._get(url).json()
        bridge = cls(data_as_dict['id'], data=data_as_dict)
        return bridge

    @classmethod
    def create(cls, *calls, bridge_audio=True):
        """
        :param calls:
        :param bridge_audio:
        :return:
        """
        client = cls.client or Client()
        data = {"bridgeAudio": bridge_audio, "callIds": [c.call_id for c in calls]}
        r = client._post(cls.path, data=data)
        location = r.headers['Location']
        bridge_id = location.split('/')[-1]
        return cls(bridge_id, *calls, bridge_audio=bridge_audio)

    @property
    def call_ids(self):
        return [c.call_id for c in self.calls]

    def call_party(self, caller, callee):
        new_call = Call.create(caller, callee, bridgeId=self.id)
        self.calls += (new_call,)
        return new_call

    def set_calls(self, *calls):
        data = {"bridgeAudio": "false",
                "callIds": [c.call_id for c in calls]
                }
        url = '{}/{}/audio'.format(self.path, self.id)

        self.client._post(url, data=data)
        self.calls = calls

    def fetch_calls(self):
        url = '{}/{}/calls'.format(self.path, self.id)
        r = self.client._get(url)
        self.calls = [Call(v) for v in r.json()]
        return self.calls

    def play_audio(self, file):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = '{}/{}/audio'.format(self.path, self.id)

        self.client._post(url, data={'fileUrl': file})

    def stop_audio(self):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = '{}/{}/audio'.format(self.path, self.id)

        self.client._post(url, data={'fileUrl': ''})

    def speak_sentence(self, sentence, gender='female', locale=None, voice=None):
        url = '{}/{}/audio'.format(self.path, self.id)
        json_data = {'sentence': sentence, 'gender': gender}
        if locale:
            json_data['locale'] = locale
        if voice:
            json_data['voice'] = voice
        self.client._post(url, data=json_data)

    def stop_sentence(self):
        url = '{}/{}/audio'.format(self.path, self.id)
        self.client._post(url, data={'sentence': ''})

    def refresh(self):
        url = '{}/{}'.format(self.path, self.id)
        data = self.client._get(url).json()
        self.set_up(data)
