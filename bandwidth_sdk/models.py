# Object models for SDK
import six
from functools import partial
from .client import Client
from .utils import to_api, from_api, enum, get_location_id
from.generics import AudioMixin

# Sentinel value to mark that some of properties have been not synced.
UNEVALUATED = object()


class Gettable(object):
    client = None
    _fields = None

    @classmethod
    def get(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented

    def set_up(self, data):
        for k, v in six.iteritems(data):
            if k in self._fields:
                setattr(self, k, v)


class Resource(Gettable):
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


class Call(AudioMixin, Resource):
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
        super(Call, self).set_up(data)

    @classmethod
    def create(cls, caller, callee, bridge_id=None, recording_enabled=None, callback_url=None, timeout=30, **kwargs):
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
            'recording_enabled': recording_enabled,
            'callback_url': callback_url
        }

        data.update(kwargs)
        json_data = to_api(data)
        r = client.post(cls.path, data=json_data)
        call_id = get_location_id(r)
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

    def get_audio_url(self):
        return '{}/{}/audio'.format(self.path, self.call_id)

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
        r = self.client.post(url, data=json_data)
        call_id = get_location_id(r)
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
            # todo: drop data
            self.set_up(data)
        else:
            raise TypeError('Accepted only application-id or application data as dictionary')

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
        p_data = to_api(data)
        resp = client.post(cls._path, data=p_data)
        application_id = get_location_id(resp)
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
        return [cls(application_id=v['id'], data=from_api(v)) for v in data_as_list]

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
        application = cls(application_id=data_as_dict['id'], data=from_api(data_as_dict))
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
        client.post(url, data=to_api(cleaned_data))
        if cleaned_data:
            self.data = cleaned_data
            self.set_up(self.data)
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
        self.set_up(from_api(data))


class Bridge(AudioMixin, Resource):
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
        bridge_id = get_location_id(r)
        return cls(bridge_id, *calls, data=data)

    @property
    def call_ids(self):
        '''
        :return: list of call-ids for local version
        '''
        return [c.call_id for c in self.calls]

    def call_party(self, caller, callee, **kwargs):
        new_call = Call.create(caller, callee, bridge_id=self.id, **kwargs)
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

    def get_audio_url(self):
        return '{}/{}/audio'.format(self.path, self.id)

    def refresh(self):
        '''
        Updates bridge fields internally for this bridge instance
        :return: None
        '''
        url = '{}/{}'.format(self.path, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))


class Account(Gettable):
    balance = None
    account_type = None
    _path = 'account/'
    _fields = frozenset(('balance', 'account_type'))

    def __init__(self, data=None):
        self.client = Client()
        if data:
            self.set_up(data)

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
        self.path = 'calls/{}/gather'.format(call_id)

    def get(self, gather_id):
        """
        Get the gather DTMF parameters and results

        :param gather_id:

        :return: Gather instance
        """
        url = '{}/{}'.format(self.path, gather_id)
        data_as_dict = self.client.get(url).json()
        self.set_up(from_api(data_as_dict))
        return self

    def create(self, **kwargs):
        """
        Collects a series of DTMF digits from a phone call with an optional prompt.
        This request returns immediately. When gather finishes, an event with
        the results will be posted to the callback URL.

        :param max_digits: The maximum number of digits to collect, not including terminating digits (maximum 30)

        :param inter_digit_timeout: Stop gathering if a DTMF digit is not detected in this many seconds
            (default 5.0; maximum 30.0)

        :param terminating_digits: A string of DTMF digits that end the gather operation immediately if any one of
            them is detected (default "#"; an empty string means collect all DTMF until maxDigits or the timeout)

            Example:
                # : The gather ends if # is detected (this is the default behavior if the terminatingDigits property
                    is not specified)
                0#* : The gather ends if either 0, #, or * is detected

            Don't forget to encode keypad digits that have special meaning in a URL, like #.

        :param suppress_dtmf: Suppress DTMF callback events to be triggered (default true)

        :param tag A string you choose that will be included with the response and events for this gather operation

        :param prompt.sentence: The text to speak for the prompt (uses the call audio resource defaults)
            Don't forget to encode special characters in the sentence.

        :param prompt.gender: The gender to use for the voice reading the prompt sentence
            (uses the call audio resource defaults)

        :param prompt.locale: The language and region to use for the voice reading the prompt sentence
            (uses the call audio resource defaults)

        :param prompt.file_url: The URL for an audio file to play as the prompt (uses the call audio resource defaults)

        :param prompt.loop_enabled: When value is true, the audio will keep playing in a loop. Default: false

        :param prompt.bargeable: Make the prompt (audio or sentence) bargeable (will be interrupted at first digit
            gathered) Default: true

        >>> Gather.create(max_digits='5', terminating_digits='*', inter_digit_timeout='7',
                          prompt={'sentence': 'Please enter your 5 digit code', 'loop_enabled': True})
        :return new Gather instance
        """
        client = self.client
        data = to_api(kwargs)
        r = client.post(self.path, data=data)
        self.id = get_location_id(r)
        return self

    def stop(self):
        """
        Update the gather DTMF. The only update allowed is state:completed to stop the gather.
        """
        assert self.id is not None
        url = '{}/{}'.format(self.path, self.id)
        data = to_api({'state': 'completed'})
        self.client.post(url, data=data)


class Conference(AudioMixin, Gettable):

    """
    The Conference resource allows you create conferences, add members to it,
    play audio, speak text, mute/unmute members, hold/unhold members and other
    things related to conferencing.
    """
    path = 'conferences'
    STATES = enum('created', 'active', 'completed')
    client = None

    active_members = None
    callback_url = None
    callback_timeout = None
    fallback_url = None
    completed_time = None
    created_time = None
    from_ = None
    id = None
    state = None
    _fields = frozenset(('id', 'state', 'from_', 'created_time', 'completed_time', 'fallback_url',
                         'callback_timeout', 'callback_url', 'active_members'))

    def __init__(self, data):
        self.client = Client()
        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only id as string or data as dictionary')

    def set_up(self, data):
        self.from_ = self.from_ or data.get('from')
        super(Conference, self).set_up(data)

    def get_audio_url(self):
        return '{}/{}/audio'.format(self.path, self.id)

    @classmethod
    def create(cls, from_, **params):
        """
        todo: docstring
        """
        client = cls.client or Client()
        params['from'] = from_
        json_data = to_api(params)
        r = client.post(cls.path, data=json_data)
        cid = get_location_id(r)
        conference = cls(params)
        conference.id = cid
        return conference

    @classmethod
    def get(cls, conf_id):
        """
        Retrieve the conference information.

        :param conf_id:

        :return: new Conference instance with all provided fields.
        """
        client = cls.client or Client()
        url = '{}/{}'.format(cls.path, conf_id)
        data_as_dict = client.get(url).json()
        return cls(data_as_dict)

    def __repr__(self):
        return 'Conference(%r, state=%r)' % (self.id, self.state or 'Unknown')

    def update(self, **params):
        """
        Change the conference properties/status.
        :return: the instance with updated fields.
        """
        client = self.client
        url = '{}/{}'.format(self.path, self.id)
        data = to_api(params)
        client.post(url, data=data)
        self.set_up(params)
        return self

    def get_members(self):
        """
        List all members from a conference. If a member had already hung up or removed from conference it will be
        displayed as completed.
        """
        client = self.client
        url = '{}/{}/members'.format(self.path, self.id)
        member_list = client.get(url).json()
        return [self.member(member) for member in member_list]

    def add_member(self, call_id, **params):
        """
        Add members to a conference.
        Important:-- The callId must refer to an active call that was created using this conferenceId.
        """
        client = self.client
        url = '{}/{}/members'.format(self.path, self.id)
        params['call_id'] = call_id
        data = to_api(params)
        r = client.post(url, data=data)
        mid = get_location_id(r)
        return self.member(mid)

    @property
    def member(self):
        return partial(ConferenceMember, self.id)


class ConferenceMember(AudioMixin, Resource):

    """

    """
    sub_path = 'members'
    id = None
    added_time = None
    hold = None
    mute = None
    state = None
    join_tone = None
    leaving_tone = None
    conf_id = None

    _fields = frozenset(('id', 'state', 'added_time', 'hold', 'mute', 'join_tone', 'leaving_tone'))

    def __init__(self, conf_id, data):
        self.client = Client()
        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only id as string or data as dictionary')
        self.conf_id = conf_id

    def get(self):
        """
        Retrieve a conference member attributes/properties.
        :return: ConferenceMember instance.
        """
        client = self.client
        url = 'conferences/{}/members/{}'.format(self.conf_id, self.id)
        data = from_api(client.get(url).json())
        self.set_up(data)
        return self

    def update(self, **params):
        """
        Update a member status/properties.
        """
        client = self.client
        url = 'conferences/{}/members/{}'.format(self.conf_id, self.id)
        data = to_api(params)
        client.post(url, data=data).json()
        self.set_up(params)
        return self

    def __repr__(self):
        return 'ConferenceMember(%r, state=%r)' % (self.id, self.state or 'Unknown')

    def get_audio_url(self):
        return 'conferences/{}/members/{}/audio'.format(self.conf_id, self.id)


class Recording(Gettable):
    """
    Recording resource
    """
    id = None
    media = None
    call = None
    state = None
    start_time = None
    end_time = None
    _path = 'recordings'
    _fields = frozenset(['id', 'media', 'call', 'state', 'start_time', 'end_time'])

    def __init__(self, data):
        self.client = Client()
        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data

    def __repr__(self):
        return "Recording({}, state={})".format(self.id, self.state or "Unknown")

    def set_up(self, data):
        call = data.pop('call', None)
        if call:
            data['call'] = Call(call.split('/')[-1])
        super(Recording, self).set_up(data)

    @classmethod
    def list(cls, page=None, size=None):
        """
        List all call recordings.

        :param page: Used for pagination to indicate the page requested for querying a list of recordings.
                     If no value is specified the default is 0.
        :param size: Used for pagination to indicate the size of each page requested for querying a list of recordings.
                     If no value is specified the default value is 25. (Maximum value 1000).
        :return: List of recording instances.
        """
        client = cls.client or Client()
        data_as_list = client.get(
            cls._path, params=to_api(dict(page=page, size=size))).json()
        return [cls(data=v) for v in data_as_list]

    @classmethod
    def get(cls, recording_id):
        """
        Retrieve a specific call recording information instance by recording id

        :param recording_id: recording id of recording that you want to retriev
        :return: Recording instance
        """
        client = cls.client or Client()
        url = '{}/{}'.format(cls._path, recording_id)
        data_as_dict = client.get(url).json()
        recording = cls(data=data_as_dict)
        return recording

    def get_media_file(self):
        """
        Downloads a recording file

        :return: Tuple where first arg is content of media file in bytes,
                 and second is content-type of file.
        """
        client = self.client or Client()
        resp = client.get(self.media, join_endpoint=False)
        return resp.content, resp.headers['Content-Type']
