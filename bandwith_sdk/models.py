# Object models for SDK
import six
from .client import Client
from .utils import prepare_json, unpack_json_dct, to_api, from_api, enum

# Sentinel value to mark that some of properties have been not synced.
UNEVALUATED = object()


class Gettabble(object):
    client = None

    @classmethod
    def get(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented


class Resource(Gettabble):
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


class Call(Resource):
    path = 'calls'
    STATES = enum('started', 'rejected', 'active', 'completed', 'transferring')
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
    _fields = frozenset(('call_id', 'direction', 'from_', 'to', 'recording_enabled', 'callback_url',
                         'state', 'start_time', 'active_time'))

    def __init__(self, data):
        self.client = Client()
        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.call_id = data
        else:
            raise TypeError('Accepted only call-id or call data as dictionary')

    def set_up(self, data):
        self.from_ = self.from_ or data.get('from')
        self.call_id = self.call_id or data.get('id')
        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)

    @classmethod
    def create(cls, caller, callee, bridge_id=None, recording_enabled=None, timeout=30):
        """
        Makes a phone call.

        :param caller: One of your telephone numbers the call should come from (must be in E.164 format,
            like +19195551212)

        :param callee: The number to call (must be either an E.164 formated number, like +19195551212, or a
            valid SIP URI, like sip:someone@somewhere.com)

        :param bridge_id: Create a call in a bridge

        :param recording_enabled: Indicates if the call should be recorded after being created.

        :return: new Call instance with @call_id and @from_, @to fields.
        """
        client = cls.client or Client()

        data = {
            'from': caller,
            'to': callee,
            'call_timeout': timeout,  # seconds
            'bridge_id': bridge_id,
            'recording_enabled': recording_enabled
        }
        json_data = to_api(data)
        data = client.post(cls.path, data=json_data)
        location = data.headers['Location']
        call_id = location.split('/')[-1]
        call = cls(call_id)
        call.set_up(json_data)
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
        data_as_dict = client.get(url).json()
        return cls(data_as_dict)

    @classmethod
    def list(cls, **query):
        """
        Gets a list of active and historic calls you made or received.

        :param page: Used for pagination to indicate the page requested for querying a list of calls.
                    If no value is specified the default is 0.

        :param size: Used for pagination to indicate the size of each page requested for querying a list of calls.
                    If no value is specified the default value is 25. (Maximum value 1000)

        :param bridge_id: Id of the bridge for querying a list of calls history. (Pagination do not apply).

        :param conference_id: Id of the conference for querying a list of calls history. (Pagination do not apply).

        :param from_: Telephone number to filter the calls that came from (must be in E.164 format, like +19195551212).

        :param to: The number to filter calls that was called to (must be either an E.164 formated number,
                like +19195551212, or a valid SIP URI, like sip:someone@somewhere.com).

        :return: list of Call instances
        """
        client = cls.client or Client()
        query = to_api(query)
        data_as_list = client.get(cls.path, params=query).json()
        return [cls(v) for v in data_as_list]

    def __repr__(self):
        return 'Call(%r, state=%r)' % (self.call_id, self.state or 'Unknown')

    # Audio part
    def play_audio(self, file_url, **kwargs):
        '''
        Plays audio form the given url to the call associated with call_id

        :param file_url: The location of an audio file to play (WAV and MP3 supported).

        :param loop_enabled: When value is true, the audio will keep playing in a loop. Default: false.

        :param tag:	A string that will be included in the events delivered when the audio playback starts or finishes.

        :return: None
        '''

        url = '{}/{}/audio'.format(self.path, self.call_id)
        kwargs['file_url'] = file_url
        data = to_api(kwargs)
        self.client.post(url, data=data)

    def stop_audio(self):
        '''
        Stop an audio file playing
        '''
        url = '{}/{}/audio'.format(self.path, self.call_id)
        self.client.post(url, data=to_api({'file_url': ''}))

    def speak_sentence(self, sentence, **kwargs):
        '''
        :param sentence: The sentence to speak.

        :param gender: The gender of the voice used to synthesize the sentence. It will be considered only if sentence
                    is not null. The female gender will be used by default.

        :param locale: The locale used to get the accent of the voice used to synthesize the sentence. Currently
            Bandwidth API supports:

            en_US or en_UK (English)
            es or es_MX (Spanish)
            fr or fr_FR (French)
            de or de_DE (German)
            it or it_IT (Italian)

            It will be considered only if sentence is not null/empty. The en_US will be used by default.
        :param voice: The voice to speak the sentence. The API currently supports the following voices:

            English US: Kate, Susan, Julie, Dave, Paul
            English UK: Bridget
            Spanish: Esperanza, Violeta, Jorge
            French: Jolie, Bernard
            German: Katrin, Stefan
            Italian: Paola, Luca

            It will be considered only if sentence is not null/empty. Susan's voice will be used by default.

        :param loop_enabled: When value is true, the audio will keep playing in a loop. Default: false.

        :param tag:	A string that will be included in the events delivered when the audio playback starts or finishes.

        :return: None
        '''
        url = '{}/{}/audio'.format(self.path, self.call_id)
        kwargs['sentence'] = sentence
        data = to_api(kwargs)
        self.client.post(url, data=data)

    def stop_sentence(self):
        '''
        Stop a current sentence
        :return: None
        '''
        url = '{}/{}/audio'.format(self.path, self.call_id)
        self.client.post(url, data=to_api({'sentence': ''}))

    # Call manipulation
    def transfer(self, phone, **kwargs):
        '''
        :param phone:
        :param callback_url: A URL where call events will be sent for an inbound call
        :param transfer_caller_id: A phone number that will be shown
        :param whisper_audio: Say something before bridging the calls:
            {"sentence": "Hello {number}, thanks for calling"}
        :return: new Call instance
        '''
        url = '{}/{}'.format(self.path, self.call_id)
        json_data = {'transfer_to': phone,
                     'state': Call.STATES.transferring}
        json_data.update(kwargs)
        json_data = to_api(json_data)
        data = self.client.post(url, data=json_data)
        location = data.headers['Location']
        call_id = location.split('/')[-1]
        call = self.__class__(call_id)
        call.set_up(json_data)
        return call

    def set_call_property(self, **kwargs):
        url = '{}/{}'.format(self.path, self.call_id)
        return self.client.post(url, data=to_api(kwargs))

    def bridge(self, *calls, **kwargs):
        '''
        #todo: proper docstring
        :param calls:
        :param kwargs:
        :return:
        '''
        _calls = (self,) + calls
        return Bridge.create(*_calls, **kwargs)

    def refresh(self):
        '''
        Updates call fields internally for this call instance
        :return: None
        '''
        url = '{}/{}'.format(self.path, self.call_id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))

    def hangup(self):
        '''
        Hangs up a call with the given call_id
        '''
        url = '{}/{}'.format(self.path, self.call_id)

        json_data = {'state': Call.STATES.completed}
        self.client.post(url, data=to_api(json_data))
        self.set_up(json_data)

    def reject(self):
        '''
        Hangs up a call with the given call_id
        '''
        url = '{}/{}'.format(self.path, self.call_id)

        json_data = {'state': Call.STATES.rejected}
        self.client.post(url, data=to_api(json_data))
        self.set_up(json_data)

    # Dtmf section
    def send_dtmf(self, dtmf):
        '''
        Sends a string of characters as DTMF on the given call_id
        Valid chars are '0123456789*#ABCD'
        '''
        url = '{}/{}/dtmf'.format(self.path, self.call_id)

        json_data = to_api({'dtmf_out': dtmf})

        self.client.post(url, data=json_data)

    @property
    def gather(self):
        return Gather(self.call_id, client=self.client)

    def get_recordings(self, timeout=None):
        '''
        Retrieves an array with all the recordings of the call_id
        '''
        url = '{}/{}/recordings'.format(self.path, self.call_id)
        # todo: should be implement using Recording type
        return from_api(self.client.get(url, timeout=timeout).json())

    def get_events(self):
        '''
        Gets the events that occurred during the call. No query parameters are supported.
        '''
        url = '{}/{}/events'.format(self.path, self.call_id)
        data = self.client.get(url).json()
        return [from_api(e) for e in data]


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
    _path = 'applications/'
    _fields = ('application_id', 'name',
               'incoming_call_url',
               'incoming_call_url_callback_timeout',
               'incoming_call_fallback_url',
               'incoming_sms_url',
               'incoming_sms_url_callback_timeout',
               'incoming_sms_fallback_url', 'callback_http_method', 'auto_answer')

    def __init__(self, application_id, data):
        self.client = Client()
        self.application_id = application_id
        if data:
            self.data = data
            self.set_up()
        else:
            raise TypeError('Accepted only application-id or application data as dictionary')

    def set_up(self):
        [setattr(self, k, v) for k, v in self.data.items() if k in self._fields and v is not None]

    @classmethod
    def create(cls, **data):
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
        p_data = prepare_json(
            {k: v for k, v in data.items() if v is not None and k in cls._fields})
        resp = client.post(cls._path, data=p_data)
        location = resp.headers['Location']
        application_id = location.split('/')[-1]
        return cls(application_id=application_id, data=data)

    @classmethod
    def list(cls, page=0, size=25):
        """

        :page: Used for pagination to indicate the page requested for querying a list of applications.
        If no value is specified the default is 1.
        :size: Used for pagination to indicate the size of each page requested for querying a list of applications.
        If no value is specified the default value is 25. (Maximum value 1000).
        :return: List of Application instances
        """
        client = cls.client or Client()
        data_as_list = client.get(
            cls._path, params=dict(page=page, size=size)).json()
        return [cls(application_id=v['id'], data=unpack_json_dct(v)) for v in data_as_list]

    @classmethod
    def get(cls, application_id):
        """
        :application_id: application id that you want to retrieve.
        Gets information about one of your applications. No query parameters are supported.
        :return: Application instance
        """
        client = cls.client or Client()
        url = '{}{}'.format(cls._path, application_id)
        data_as_dict = client.get(url).json()
        application = cls(application_id=data_as_dict['id'], data=unpack_json_dct(data_as_dict))
        return application

    def patch(self, **data):
        """
        :incoming_call_url: A URL where call events will be sent for an inbound call
        :incoming_sms_url:  A URL where message events will be sent for an inbound SMS message
        :name:    A name you choose for this application
        :callback_http_method:  Determine if the callback event should be sent via HTTP GET or HTTP POST.
        (If not set the default is HTTP POST)
        :auto_answer:  Determines whether or not an incoming call should be automatically answered. Default value is 'true'.

        :return: True if it's patched
        """
        client = self.client or Client()
        url = '{}{}'.format(self._path, self.application_id)
        cleaned_data = {k: v for k, v in data.items() if v is not None and k in self._fields}
        client.post(url, data=prepare_json(cleaned_data))
        if cleaned_data:
            self.data = cleaned_data
            self.set_up()
        return True

    def delete(self):
        """
        Delete application instance on catapult side.
        :return: True if it's deleted
        """
        client = self.client or Client()
        url = '{}{}'.format(self._path, self.application_id)
        client.delete(url)
        return True

    def refresh(self):
        url = '{}{}'.format(self._path, self.application_id)
        data = self.client.get(url).json()
        self.data = from_api(data)
        self.set_up()


class Bridge(Resource):
    path = 'bridges'
    STATES = enum('created', 'active', 'hold', 'completed', 'error')
    id = None
    state = None
    calls = None
    bridge_audio = None
    completed_time = None
    created_time = None
    activated_time = None
    client = None
    _fields = frozenset(('id', 'state', 'bridge_audio', 'completed_time', 'created_time',
                         'activated_time'))

    def __init__(self, id, *calls, **kwargs):
        self.calls = calls
        self.client = Client()
        self.bridge_audio = kwargs.pop('bridge_audio', None)
        self.id = id
        if 'data' in kwargs:
            self.set_up(from_api(kwargs['data']))

    def set_up(self, data):
        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)

    @classmethod
    def list(cls, page=1, size=20):
        """
        Get list of bridges for a given user.

        :param page: Used for pagination to indicate the page requested for querying a list of calls.
                    If no value is specified the default is 0.


        :param size: Used for pagination to indicate the size of each page requested for querying a list of calls.
                    If no value is specified the default value is 25. (Maximum value 1000)

        :return: list of Bridge instances
        """
        client = cls.client or Client()
        query = to_api({'page': page, 'size': size})
        data_as_list = client.get(cls.path, params=query).json()
        return [cls(v['id'], data=v) for v in data_as_list]

    @classmethod
    def get(cls, bridge_id):
        """
        Gets information about a specific bridge.

        :param bridge_id:

        :return: Bridge instance
        """
        client = cls.client or Client()
        url = '{}/{}'.format(cls.path, bridge_id)
        data_as_dict = client.get(url).json()
        bridge = cls(data_as_dict['id'], data=data_as_dict)
        return bridge

    @classmethod
    def create(cls, *calls, **kwargs):
        """
        Gets information about a specific bridge.

        :param calls: The list of call in the bridge.
                If the list of call ids is not provided the bridge is logically created and it can be used to place
                calls later

        :param bridge_audio: Enable/Disable two way audio path (default = true)

        :return: new Bridge instance
        """
        client = cls.client or Client()
        data = to_api(kwargs)
        data["call_ids"] = [c.call_id for c in calls]
        data = to_api(data)
        r = client.post(cls.path, data=data)
        location = r.headers['Location']
        bridge_id = location.split('/')[-1]
        return cls(bridge_id, *calls, data=data)

    @property
    def call_ids(self):
        '''
        :return: list of call-ids for local version
        '''
        return [c.call_id for c in self.calls]

    def call_party(self, caller, callee):
        new_call = Call.create(caller, callee, bridge_id=self.id)
        self.calls += (new_call,)
        return new_call

    def update(self, *calls, **kwargs):
        """
        Change calls in a bridge and bridge/unbridge the audio
        :return: None
        """
        kwargs['call_ids'] = [c.call_id for c in calls]
        data = to_api(kwargs)
        url = '{}/{}'.format(self.path, self.id)

        self.client.post(url, data=data)
        self.calls = calls

    def fetch_calls(self):
        """
        Get the list of calls that are on the bridge
        """
        url = '{}/{}/calls'.format(self.path, self.id)
        r = self.client.get(url)
        self.calls = [Call(v) for v in r.json()]
        return self.calls

    # Audio part
    def play_audio(self, file_url, **kwargs):
        '''
        Plays audio form the given url to the call associated with call_id

        :param file_url: The location of an audio file to play (WAV and MP3 supported).

        :param loop_enabled: When value is true, the audio will keep playing in a loop. Default: false.

        :param tag:	A string that will be included in the events delivered when the audio playback starts or finishes.

        :return: None
        '''

        url = '{}/{}/audio'.format(self.path, self.id)
        kwargs['file_url'] = file_url
        data = to_api(kwargs)
        self.client.post(url, data=data)

    def stop_audio(self):
        '''
        Stop an audio file playing
        '''
        url = '{}/{}/audio'.format(self.path, self.id)
        self.client.post(url, data=to_api({'file_url': ''}))

    def speak_sentence(self, sentence, **kwargs):
        '''
        :param sentence: The sentence to speak.

        :param gender: The gender of the voice used to synthesize the sentence. It will be considered only if sentence
                    is not null. The female gender will be used by default.

        :param locale: The locale used to get the accent of the voice used to synthesize the sentence. Currently
            Bandwidth API supports:

            en_US or en_UK (English)
            es or es_MX (Spanish)
            fr or fr_FR (French)
            de or de_DE (German)
            it or it_IT (Italian)

            It will be considered only if sentence is not null/empty. The en_US will be used by default.
        :param voice: The voice to speak the sentence. The API currently supports the following voices:

            English US: Kate, Susan, Julie, Dave, Paul
            English UK: Bridget
            Spanish: Esperanza, Violeta, Jorge
            French: Jolie, Bernard
            German: Katrin, Stefan
            Italian: Paola, Luca

            It will be considered only if sentence is not null/empty. Susan's voice will be used by default.

        :param loop_enabled: When value is true, the audio will keep playing in a loop. Default: false.

        :param tag:	A string that will be included in the events delivered when the audio playback starts or finishes.

        :return: None
        '''
        url = '{}/{}/audio'.format(self.path, self.id)
        kwargs['sentence'] = sentence
        data = to_api(kwargs)
        self.client.post(url, data=data)

    def stop_sentence(self):
        '''
        Stop a current sentence
        :return: None
        '''
        url = '{}/{}/audio'.format(self.path, self.id)
        self.client.post(url, data=to_api({'sentence': ''}))

    def refresh(self):
        '''
        Updates bridge fields internally for this bridge instance
        :return: None
        '''
        url = '{}/{}'.format(self.path, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))


class Account(Gettabble):
    balance = None
    account_type = None
    _path = 'account/'

    def __init__(self, data=None):
        self.client = Client()
        if data:
            self.set_up(data)

    def set_up(self, data):
        [setattr(self, k, v) for k, v in data.items() if v is not None]

    @classmethod
    def get(cls):
        """
        Get an Account object. No query parameters are supported
        :return: Account instance.
        """
        client = cls.client or Client()
        data = from_api(client.get(cls._path).json())
        return cls(data=data)

    @classmethod
    def get_transactions(cls, **query_params):
        """
        Get the transactions from Account.
        :max_items: Limit the number of transactions that will be returned
        :to_date: Return only transactions that are newer than the parameter. Format: "yyyy-MM-dd'T'HH:mm:ssZ"
        :from_date: Return only transactions that are older than the parameter. Format: "yyyy-MM-dd'T'HH:mm:ssZ"
        :type: Return only transactions that are this type
        :page: Used for pagination to indicate the page requested for querying a list of transactions.
               If no value is specified the default is 0.
        :size: Used for pagination to indicate the size of each page requested for querying a list of transactions.
               If no value is specified the default value is 25. (Maximum value 1000)

        :return: list of dictionaries that contains information about transaction
        """
        client = cls.client or Client()
        url = '{}{}'.format(cls._path, 'transactions')
        json_resp = client.get(url, params=to_api(query_params)).json()
        data = [from_api(d) for d in json_resp]
        return data


class Gather(Resource):
    path = 'calls'
    id = None
    reason = None
    state = None
    created_time = None
    completed_time = None
    digits = None

    _fields = frozenset(('id', 'state', 'reason', 'created_time', 'completed_time',
                         'digits'))

    def __init__(self, call_id, client=None):
        self.client = client or Client()
        self.call_id = call_id

    def set_up(self, data):
        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)

    def get(self, gather_id):
        """
        Gets information about a specific bridge.

        :param gather_id:

        :return: Bridge instance
        """
        url = '{}/{}/gather/{}'.format(self.path, self.call_id, gather_id)
        data_as_dict = self.client.get(url).json()
        self.set_up(from_api(data_as_dict))
        return self

    def create(self, **kwargs):
        """
        Collects a series of DTMF digits from a phone call with an optional prompt.
        This request returns immediately. When gather finishes, an event with
        the results will be posted to the callback URL.
        """
        client = self.client
        data = to_api(kwargs)
        url = '{}/{}/gather'.format(self.path, self.call_id)
        r = client.post(url, data=data)
        location = r.headers['Location']
        self.id = location.split('/')[-1]
        return self

    def stop(self):
        assert self.id is not None
        url = '{}/{}/gather/{}'.format(self.path, self.call_id, self.id)
        data = to_api({'state': 'completed'})
        self.client.post(url, data=data)
