# Object models for SDK
import six
from functools import partial
from collections import namedtuple
from .client import get_client
from .utils import to_api, from_api, enum, get_location_id, file_exists
from .errors import AppPlatformError
from .generics import AudioMixin


class BaseResource(object):
    client = None
    _fields = None

    @classmethod
    def get(cls, *args, **kwargs):  # pragma: no cover
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

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.id)


class CreateResource(BaseResource):
    """
    Supports create interface.
    """
    @classmethod
    def create(cls, *args, **kwargs):  # pragma: no cover
        """
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented


class ListResource(BaseResource):
    """
    Supports list interface.
    """
    @classmethod
    def list(cls, *args, **kwargs):  # pragma: no cover
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented

    @classmethod
    def page_iterator(cls, chunk_size=100, **query_params):
        """
        Makes a generator that returns paginated data from resource API.

        :param chunk_size: Size of chunk that you want to receive over one iteration.
                           Default is 100.
        :param query_params: Keyword arguments that can receive list() method
        """
        page = 0
        while True:
            results = cls.list(page=page, size=chunk_size, **query_params)

            if len(results) < chunk_size:
                yield results
                break
            else:
                yield results
                page += 1

    @classmethod
    def as_iterator(cls, chunk_size=100, **query_params):
        """
        Makes a generator for continuous iteration over very large API lists. This is essentially
         a chained and structured generator.

        :param chunk_size: Size of chunk that you are going to receive in one API request.
                           Default is 100.
        :param query_params: Other keyword arguments for `cls.list` method.
        """
        for page in cls.page_iterator(chunk_size, **query_params):
            for el in page:
                yield el


class GenericResource(ListResource, CreateResource):
    """
    General abstraction of API resource.
    """


class Call(AudioMixin, GenericResource):
    path = 'calls'
    STATES = enum('started', 'rejected', 'active', 'completed', 'transferring')
    _fields = frozenset(('call_id', 'direction', 'from_', 'to', 'recording_enabled', 'callback_url',
                         'state', 'start_time', 'active_time', 'end_time', 'bridge_id'))

    def __init__(self, data):
        self.client = get_client()

        self.call_id = None
        self.direction = None
        self.from_ = None
        self.to = None
        self.recording_enabled = None
        self.callback_url = None
        self.state = None
        self.start_time = None
        self.active_time = None
        self.end_time = None
        self.bridge_id = None

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
        bridge = data.get('bridge')
        if bridge is not None:
            self.bridge_id = bridge.split('/')[-1]

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
        client = cls.client or get_client()

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
        client = cls.client or get_client()
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
        client = cls.client or get_client()
        query = to_api(query)
        data_as_list = client.get(cls.path, params=query).json()
        return [cls(v) for v in data_as_list]

    def __repr__(self):
        return 'Call(%r, state=%r)' % (self.call_id, self.state or 'Unknown')

    def get_audio_url(self):
        return '{}/{}/audio'.format(self.path, self.call_id)

    # Call manipulation
    def transfer(self, phone, **kwargs):
        """
        :param phone:
        :param callback_url: A URL where call events will be sent for an inbound call
        :param transfer_caller_id: A phone number that will be shown
        :param whisper_audio: Say something before bridging the calls:
            {'sentence': 'Hello {number}, thanks for calling'}
        :return: new Call instance
        """
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
        self.client.post(url, data=to_api(kwargs))
        self.set_up(from_api(kwargs))
        return self

    def bridge(self, *calls, **kwargs):
        """
        Bridge calls with this call.
        :param calls: Call instances
        :param kwargs: bridge_audio - Enable/Disable two way audio path (default = true)
        :return: Bridge instance.
        """
        _calls = (self,) + calls
        return Bridge.create(*_calls, **kwargs)

    def refresh(self):
        """
        Updates call fields internally for this call instance
        :return: None
        """
        url = '{}/{}'.format(self.path, self.call_id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))

    def hangup(self):
        """
        Hangs up a call with the given call_id
        """
        url = '{}/{}'.format(self.path, self.call_id)

        json_data = {'state': Call.STATES.completed}
        self.client.post(url, data=to_api(json_data))
        self.set_up(json_data)

    def reject(self):
        """
        Hangs up a call with the given call_id
        """
        url = '{}/{}'.format(self.path, self.call_id)

        json_data = {'state': Call.STATES.rejected}
        self.client.post(url, data=to_api(json_data))
        self.set_up(json_data)

    # Dtmf section
    def send_dtmf(self, dtmf):
        """
        Sends a string of characters as DTMF on the given call_id
        Valid chars are '0123456789*#ABCD'
        """
        url = '{}/{}/dtmf'.format(self.path, self.call_id)

        json_data = to_api({'dtmf_out': dtmf})

        self.client.post(url, data=json_data)

    @property
    def gather(self):
        return Gather(self.call_id, client=self.client)

    def get_recordings(self):
        """
        Retrieves an array with all the recordings of the call_id
        """
        url = '{}/{}/recordings'.format(self.path, self.call_id)
        recordings = self.client.get(url).json()
        return [Recording(d) for d in recordings]

    def get_events(self):
        """
        Gets the events that occurred during the call. No query parameters are supported.
        """
        url = '{}/{}/events'.format(self.path, self.call_id)
        data = self.client.get(url).json()
        return [from_api(e) for e in data]


class Application(GenericResource):
    _path = 'applications/'
    _fields = ('id', 'name',
               'incoming_call_url',
               'incoming_call_url_callback_timeout',
               'incoming_call_fallback_url',
               'incoming_sms_url',
               'incoming_sms_url_callback_timeout',
               'incoming_sms_fallback_url',
               'callback_http_method', 'auto_answer')

    def __init__(self, data):
        self.client = get_client()

        self.id = None
        self.name = None
        self.incoming_call_url = None
        self.incoming_call_url_callback_timeout = None
        self.incoming_call_fallback_url = None
        self.incoming_sms_url = None
        self.incoming_sms_url_callback_timeout = None
        self.incoming_sms_fallback_url = None
        self.callback_http_method = 'post'
        self.auto_answer = True

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only application-id or application data as dictionary')

    @classmethod
    def create(cls, **data):
        """
        :name: A name you choose for this application
        :incoming_call_url: A URL where call events will be sent for an inbound call
        :incoming_call_url_callback_timeout: Determine how long should the platform wait for incomingCallUrl's response
        before timing out in milliseconds.
        :incoming_call_fallback_url: The URL used to send the callback event if the request to incomingCallUrl fails.
        :incoming_sms_url: A URL where message events will be sent for an inbound SMS message.
        :incoming_sms_url_callback_timeout: Determine how long should the platform wait for incomingSmsUrl's response
        before timing out in milliseconds.
        :incoming_sms_fallback_url: The URL used to send the callback event if the request to incomingSmsUrl fails.
        :callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.
            (If not set the default is HTTP POST).
        :auto_answer: Determines whether or not an incoming call should be automatically answered.
            Default value is 'true'.
        :return: Application instance
        """
        client = cls.client or get_client()
        p_data = to_api(data)
        resp = client.post(cls._path, data=p_data)
        application_id = get_location_id(resp)
        data.update({'id': application_id})
        return cls(data=data)

    @classmethod
    def list(cls, page=0, size=25):
        """

        :page: Used for pagination to indicate the page requested for querying a list of applications.
        If no value is specified the default is 1.
        :size: Used for pagination to indicate the size of each page requested for querying a list of applications.
        If no value is specified the default value is 25. (Maximum value 1000).
        :return: List of Application instances
        """
        client = cls.client or get_client()
        data_as_list = client.get(
            cls._path, params=dict(page=page, size=size)).json()
        return [cls(data=from_api(v)) for v in data_as_list]

    @classmethod
    def get(cls, application_id):
        """
        :application_id: application id that you want to retrieve.
        Gets information about one of your applications. No query parameters are supported.
        :return: Application instance
        """
        client = cls.client or get_client()
        url = '{}{}'.format(cls._path, application_id)
        data_as_dict = client.get(url).json()
        application = cls(data=from_api(data_as_dict))
        return application

    def patch(self, **data):
        """
        :incoming_call_url: A URL where call events will be sent for an inbound call
        :incoming_sms_url:  A URL where message events will be sent for an inbound SMS message
        :name:    A name you choose for this application
        :callback_http_method:  Determine if the callback event should be sent via HTTP GET or HTTP POST.
        (If not set the default is HTTP POST)
        :auto_answer:  Determines whether or not an incoming call should be automatically answered.
            Default value is 'true'.
        :return: self if it's patched
        """
        client = self.client or get_client()
        url = '{}{}'.format(self._path, self.id)
        cleaned_data = {k: v for k, v in data.items() if v is not None and k in self._fields}
        client.post(url, data=to_api(cleaned_data))
        if cleaned_data:
            self.data = cleaned_data
            self.set_up(self.data)
        return self

    def delete(self):
        """
        Delete application instance on catapult side.
        :return: True if it's deleted
        """
        client = self.client or get_client()
        url = '{}{}'.format(self._path, self.id)
        client.delete(url)
        return True

    def refresh(self):
        url = '{}{}'.format(self._path, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))


class Bridge(AudioMixin, GenericResource):
    path = 'bridges'
    STATES = enum('created', 'active', 'hold', 'completed', 'error')
    _fields = frozenset(('id', 'state', 'bridge_audio', 'completed_time', 'created_time',
                         'activated_time', 'calls'))

    def __init__(self, id, *calls, **kwargs):
        self.client = get_client()

        self.id = id
        self.state = None
        self.calls = calls
        self.bridge_audio = kwargs.pop('bridge_audio', None)
        self.completed_time = None
        self.created_time = None
        self.activated_time = None

        if 'data' in kwargs:
            self.set_up(from_api(kwargs['data']))
            self.fetch_calls()

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
        client = cls.client or get_client()
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
        client = cls.client or get_client()
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
        client = cls.client or get_client()
        data = to_api(kwargs)
        data['call_ids'] = [c.call_id for c in calls]
        data = to_api(data)
        r = client.post(cls.path, data=data)
        bridge_id = get_location_id(r)
        return cls(bridge_id, *calls, data=data)

    @property
    def call_ids(self):
        """
        :return: list of call-ids for local version
        """
        return [c.call_id for c in self.calls]

    def call_party(self, caller, callee, **kwargs):
        new_call = Call.create(caller, callee, bridge_id=self.id, **kwargs)
        self.calls += (new_call,)
        return new_call

    def update(self, *calls, **kwargs):
        """
        Change calls in a bridge and bridge/unbridge the audio.
        :return: None
        """
        kwargs['call_ids'] = [c.call_id for c in calls]
        data = to_api(kwargs)
        url = '{}/{}'.format(self.path, self.id)

        self.client.post(url, data=data)
        self.calls = calls

    def fetch_calls(self):
        """
        Get the list of calls that are on the bridge.
        """
        url = '{}/{}/calls'.format(self.path, self.id)
        r = self.client.get(url)
        self.calls = [Call(v) for v in r.json()]
        return self.calls

    def get_audio_url(self):
        return '{}/{}/audio'.format(self.path, self.id)

    def refresh(self):
        """
        Updates bridge fields internally for this bridge instance
        :return: None
        """
        url = '{}/{}'.format(self.path, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))


class Account(BaseResource):
    _path = 'account/'
    _fields = frozenset(('balance', 'account_type'))

    def __init__(self, data=None):
        self.client = get_client()

        self.balance = None
        self.account_type = None

        if data:
            self.set_up(data)

    def __repr__(self):
        return 'Account(user_id={})'.format(self.client.uid)

    @classmethod
    def get(cls):
        """
        Get an Account object. No query parameters are supported
        :return: Account instance.
        """
        client = cls.client or get_client()
        data = from_api(client.get(cls._path).json())
        return cls(data=data)

    @classmethod
    def get_transactions(cls, **query_params):
        """
        Get the transactions from Account.
        :max_items: Limit the number of transactions that will be returned
        :to_date: Return only transactions that are newer than the parameter. Format: 'yyyy-MM-dd'T'HH:mm:ssZ'
        :from_date: Return only transactions that are older than the parameter. Format: 'yyyy-MM-dd'T'HH:mm:ssZ'
        :type: Return only transactions that are this type
        :page: Used for pagination to indicate the page requested for querying a list of transactions.
        If no value is specified the default is 0.
        :size: Used for pagination to indicate the size of each page requested for querying a list of transactions.
        If no value is specified the default value is 25. (Maximum value 1000)
        :return: list of dictionaries that contains information about
        transactions.
        """
        client = cls.client or get_client()
        url = '{}{}'.format(cls._path, 'transactions')
        json_resp = client.get(url, params=to_api(query_params)).json()
        data = [from_api(d) for d in json_resp]
        return data


class Gather(CreateResource):
    path = 'calls'
    _fields = frozenset(('id', 'state', 'reason', 'created_time', 'completed_time',
                         'digits'))

    def __init__(self, call_id, client=None):
        self.client = client or get_client()

        self.id = None
        self.reason = None
        self.state = None
        self.created_time = None
        self.completed_time = None
        self.digits = None

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
            them is detected (default '#'; an empty string means collect all DTMF until maxDigits or the timeout)

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


class Conference(AudioMixin, CreateResource):

    """
    The Conference resource allows you create conferences, add members to it,
    play audio, speak text, mute/unmute members, hold/unhold members and other
    things related to conferencing.

    :param active_members : Number of active conference members
    :param callback_url : URL where the events related to the Conference will be posted to
    :param callback_timeout : Determine how long should the platform wait for callbackUrl's response before timing out
        in milliseconds.
    :param fallback_url : The URL used to send the callback event if the request to callbackUrl fails.
    :param completed_time : The time that the Conference was completed
    :param created_time : The time that the Conference was created
    :param from : The number that will host the conference
    :param id : Conference unique ID
    :param state : Conference state.
    """
    path = 'conferences'
    STATES = enum('created', 'active', 'completed')
    _fields = frozenset(('id', 'state', 'from_', 'created_time', 'completed_time', 'fallback_url',
                         'callback_timeout', 'callback_url', 'active_members'))

    def __init__(self, data):  # pragma: no cover
        self.client = get_client()

        self.active_members = None
        self.callback_url = None
        self.callback_timeout = None
        self.fallback_url = None
        self.completed_time = None
        self.created_time = None
        self.from_ = None
        self.id = None
        self.state = None

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
        Creates a new conference.

       :param from_: The number that will host the conference
       :param callback_url: URL where the events related to the Conference will be posted to
       :param callback_timeout: Determine how long should the platform wait for callbackUrl's response before
            timing out in milliseconds.
       :param fallback_url:  The URL used to send the callback event if the request to callbackUrl fails.
        """
        client = cls.client or get_client()
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
        client = cls.client or get_client()
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
        """
        Get member class closure.
        >>> Conference('conf-id').member('m-id').get()
        """
        return partial(ConferenceMember, self.id)


class ConferenceMember(AudioMixin, BaseResource):
    """
    Member of call conference.

    :param added_time: Date when the member was added to the conference
    :param call : The URL used to retrieve the call of the member
    :param hold : true - member can't hear the conference / false - member can hear the conference.
    :param id : Conference member ID
    :param mute : true - member can't speak in the conference / false - member can speak in the conference.
    :param removed_time : Date when member was removed from conference
    :param state : Member state: active, completed.
    :param join_tone: true - play a tone when the new member joins the conference / false - don't play a tone when
        the new member joins the conference
    :param leaving_tone : true - play a tone when the new member leaves the conference / false - don't play a tone
        when the new member leaves the conference
    """
    STATES = enum('created', 'active', 'completed')
    _fields = frozenset(('id', 'state', 'added_time', 'hold', 'mute', 'join_tone', 'leaving_tone'))

    def __init__(self, conf_id, data):  # pragma: no cover
        self.client = get_client()

        self.id = None
        self.added_time = None
        self.hold = None
        self.mute = None
        self.state = None
        self.join_tone = None
        self.leaving_tone = None

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
        Allowed params:
        :param mute: true - member can't speak in the conference / false - member can speak in the conference.
        :param hold: true - member can't hear the conference / false - member can hear the conference.
        :param state: Member state: active, completed.
        :return updated object
        """
        client = self.client
        url = 'conferences/{}/members/{}'.format(self.conf_id, self.id)
        data = to_api(params)
        client.post(url, data=data)
        self.set_up(params)
        return self

    def __repr__(self):  # pragma: no cover
        return 'ConferenceMember(%r, state=%r)' % (self.id, self.state or 'Unknown')

    def get_audio_url(self):
        return 'conferences/{}/members/{}/audio'.format(self.conf_id, self.id)


class Recording(ListResource):
    """
    Recording resource
    """
    STATES = enum('recording', 'complete', 'saving', 'error')
    _path = 'recordings'
    _fields = frozenset(('id', 'media', 'call', 'state', 'start_time', 'end_time'))

    def __init__(self, data):
        self.client = get_client()

        self.id = None
        self.media = None
        self.call = None
        self.state = None
        self.start_time = None
        self.end_time = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data

    def __repr__(self):
        return 'Recording({}, state={})'.format(self.id, self.state or 'Unknown')

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
        client = cls.client or get_client()
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
        client = cls.client or get_client()
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
        client = self.client or get_client()
        resp = client.get(self.media, join_endpoint=False)
        return resp.content, resp.headers['Content-Type']


class PhoneNumber(ListResource):
    _path = 'phoneNumbers'
    _available_numbers_path = 'availableNumbers'
    _fields = frozenset(('id', 'application', 'number', 'national_number',
                         'name', 'created_time', 'city', 'state', 'price',
                         'number_state', 'fallback_number', 'pattern_match', 'lata', 'rate_center'))
    NUMBER_STATES = enum('enabled', 'released', 'available')

    def __init__(self, data, available=False):
        self.client = get_client()

        self.id = None
        self.application = None
        self.number = None
        self.national_number = None
        self.name = None
        self.created_time = None
        self.city = None
        self.state = None
        self.price = None
        self.number_state = None
        self.fallback_number = None

        # Available number attributes
        self.pattern_match = None
        self.lata = None
        self.rate_center = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        if available:
            self.number_state = self.state
            self.state = self.NUMBER_STATES.available

    def __repr__(self):  # pragma: no cover
        return 'PhoneNumber(number={})'.format(self.number or 'Unknown')

    def set_up(self, data):
        app_id = data.pop('application', None) or data.pop('application_id', None)
        if isinstance(app_id, six.string_types):
            data['application'] = Application(data=app_id.split('/')[-1])
        elif isinstance(app_id, Application):
            data['application'] = app_id
        # option for creating phonenumber instance from available numbers
        # batch allocate
        self_id = data.pop('location', None)
        if self_id:
            data['id'] = self_id.split('/')[-1]
        super(PhoneNumber, self).set_up(data)

    @classmethod
    def list(cls, page=None, size=None, application_id=None, state=None,
             name=None, city=None, number_state=None, **kwargs):
        """
        Gets a list of your numbers.

        :param page: Used for pagination to indicate the page requested for
          querying a list of phone numbers. If no value is specified the
          default is 0.
        :param size: Used for pagination to indicate the size of each list
          requested for querying a list of phone numbers. If no value is
          specified the default value is 25. (Maximum value 1000)
        :param application_id: Used to filter the retrieved list of numbers by
          an associated application ID.
        :param state: Used to filter the retrieved list of numbers allocated
          for the authenticated user by a US state.
        :param name: Used to filter the retrieved list of numbers allocated for
          the authenticated user by it's name.
        :param city: Used to filter the retrieved list of numbers allocated for
          the authenticated user by it's city.
        :param number_state: Used to filter the retrieved list of numbers
          allocated for the authenticated user by the number state.
        :return: list of your numbers
        :rtype: list of PhoneNumber
        """
        client = get_client()
        params = to_api(dict(
            page=page, size=size, application_id=application_id, state=state,
            name=name, city=city, number_state=number_state, **kwargs))
        data = client.get(cls._path, params=params).json()
        return [cls(number) for number in data]

    @classmethod
    def get(cls, number_id):
        """
        Gets information about one of your numbers using the number's ID.
        No query parameters are supported.
        :return: PhoneNumber instance.
        """
        client = get_client()
        url = '{}/{}'.format(cls._path, number_id)
        data = client.get(url).json()
        return cls(data=data)

    @classmethod
    def get_number_info(cls, number):
        """
        Gets information about one of your numbers
        using the E.164 number string, like "+19195551212".
        No query parameters are supported.
        :return: PhoneNumber instance.
        """

        number = six.moves.urllib.parse.quote(number)
        return cls.get(number)

    def patch(self, **data):
        """
        Makes changes to a number instance on catapult side.
        :param application: Application instance you want to
                            associate with this number
                            or The ID of an Application.
        :param name: A name you choose for this number.
        :param fallback_number: Number to transfer an incoming call when the
                                callback/fallback events can't be delivered
        :return: PhoneNumber instance
        """
        client = get_client()
        url = '{}/{}'.format(self._path, self.id)
        app = data.pop('application', None)
        if isinstance(app, Application):
            app_id = app.id
            data['application_id'] = app_id
        elif isinstance(app, six.string_types):
            data['application_id'] = app

        client.post(url, data=to_api(data))
        data.pop('application_id')
        data['application'] = app or None
        self.set_up(data)
        return self

    def delete(self):
        """
        Removes a number from your account so you can no longer make or
        receive calls, or send or receive messages with it.
        When you remove a number from your account,
        it will not immediately become available for re-use, so be careful.

        :return: None.
        """
        client = get_client()
        url = '{}/{}'.format(self._path, self.id)
        client.delete(url)

    def refresh(self):
        url = '{}/{}'.format(self._path, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))

    def allocate(self, application=None, name=None, fallback_number=None):
        """
        Allocates a number so you can use it to make and receive calls and
        send and receive messages.
        :param number:  An available telephone number you want to use
                (must be in E.164 format, like +19195551212). Mandatory field.
        :param application: Application instance you want to
                            associate with this number
                            or The ID of an Application.
        :param name: A name you choose for this number.
        :param fallback_number:  Number to transfer an incoming call when the
                                 callback/fallback events can't be delivered

        :return: PhoneNumber instance.
        """
        client = get_client()
        url = self._path
        data = {'number': self.number,
                'name': name,
                'fallback_number': fallback_number}
        to_update = data.copy()
        if isinstance(application, Application):
            app_id = application.id
            data['application_id'] = app_id
        elif isinstance(application, six.string_types):
            data['application_id'] = application
        resp = client.post(url, data=to_api(data))
        number_id = get_location_id(resp)
        self.id = number_id
        to_update['application'] = application
        self.set_up(to_update)
        return self

    # Avaible number resource section

    @classmethod
    def validate_search_query(cls, params):
        """
        Validating params for available local numbers search.
        Rules:
        1) state, zip and areaCode are mutually exclusive, you may use only one of them per request.
        2) localNumber and inLocalCallingArea only applies for searching and order numbers in specific areaCode.
        """
        mandatory_params = sum(('area_code' in params, 'zip' in params, 'state' in params))
        if mandatory_params > 1:
            raise ValueError('state, zip and areaCode are mutually exclusive, you may use only one of them per request')
        elif mandatory_params == 0:
            raise ValueError('Specify a State, ZIP Code, or Area Code with your query')
        if 'area_code' not in params and ('in_local_calling_area' in params or 'local_number' in params):
            raise ValueError('localNumber and inLocalCallingArea only applies '
                             'for searching numbers in specific areaCode')

    @classmethod
    def list_local(cls, **params):
        """
        :param city: A city name
        :param state: A two-letter US state abbreviation ("CA" for California)
        :param zip: A 5-digit US ZIP code
        :param area_code: A 3-digit telephone area code.
        :param local_number: It is defined as the first digits of a telephone
                             number inside an area code for filtering
                             the results.
                             It must have at least 3 digits and the area_code
                             param must be not None.
        :param in_local_calling_area: Boolean value to indicate that the search
                                      for available numbers must consider
                                      overlayed areas. Only applied for
                                      local_number searching.
        :param quantity: The maximum number of numbers to return
                         (default 10, maximum 5000).

        :param pattern: A number pattern that may include
                        letters, digits, and the following
                        wildcard characters:
                            ? : matches any single digit
                            * : matches zero or more digits
        !Note:
        1. state, zip and area_code are mutually exclusive,
           you may use only one of them per calling list_local.
        2. local_number and in_local_calling_area only applies
           for searching numbers in specific area_code.

        :return: List of AvailableNumber instances.
        """
        cls.validate_search_query(params)
        client = get_client()
        url = client.endpoint + '/v1/{}/local'.format(cls._available_numbers_path)
        data = client.build_request('get', url, params=to_api(params), join_endpoint=False).json()
        return [cls(number, available=True) for number in data]

    @classmethod
    def list_tollfree(cls, **params):
        """
        Searches for available Toll Free numbers.
        :param quantity: The maximum number of numbers to return
                         (default 10, maximum 5000)
        :param pattern: A number pattern that may include
                        letters, digits, and the following wildcard characters:
                            ? : matches any single digit
                            * : matches zero or more digits
        :return: List of AvailableNumber instances.
        """
        client = get_client()
        url = client.endpoint + '/v1/{}/tollFree'.format(cls._available_numbers_path)
        data = client.build_request('get', url, params=to_api(params), join_endpoint=False).json()
        return [cls(number, available=True) for number in data]

    @classmethod
    def batch_allocate_local(cls, **params):
        """
        :param city: A city name
        :param state: A two-letter US state abbreviation ("CA" for California)
        :param zip: A 5-digit US ZIP code
        :param area_code: A 3-digit telephone area code
        :param local_number: It is defined as the first digits of a telephone
                             number inside an area code for filtering
                             the results.
                             It must contain from 3 to 4 digits.
        :param in_local_calling_area: Boolean value to indicate that the search
                                      for available numbers must consider
                                      overlayed areas.
                                      Only applied for local_number searching.
        :param quantity: The maximum quantity of numbers to search and order
                         (default 1, maximum 10).
        !Note:
        1. state, zip and area_code are mutually exclusive,
           you may use only one of them per calling list_local.
        2. local_number and in_local_calling_area only applies
           for searching numbers in specific area_code.

        :return: List of PhoneNumber instances.
        """
        cls.validate_search_query(params)
        client = get_client()
        url = client.endpoint + '/v1/{}/local'.format(cls._available_numbers_path)
        data = client.build_request('post', url, params=to_api(params), join_endpoint=False).json()
        return [cls(number) for number in data]

    @classmethod
    def batch_allocate_tollfree(cls, quantity=1):
        """
        Searches and order available Toll Free numbers.
        :param quantity: The maximum quantity of numbers for seaching and order
                         (default 1, maximum 10).
        :return: List of PhoneNumber instances.
        """
        client = get_client()
        url = client.endpoint + '/v1/{}/tollFree'.format(cls._available_numbers_path)
        data = client.build_request('post', url,
                                    data=to_api(dict(quantity=quantity)), join_endpoint=False).json()
        return [cls(number) for number in data]


class NumberInfo(BaseResource):
    """
    This resource provides a CNAM number info. CNAM is an acronym which stands for Caller ID Name.
    CNAM can be used to display the calling party's name alongside the phone number, to help users easily
    identify a caller. CNAM API allows the user to get the CNAM information of a particular number

    :param name:  The Caller ID name information
    :param number:  The full phone number, specified in E.164 format
    :param created:  The time this Caller ID information was first queried
    :param updated:  The time this Caller ID information was last updated
    """
    _path = 'phoneNumbers/numberInfo'
    _fields = frozenset(('name', 'number', 'created', 'updated'))

    def __init__(self, data):  # pragma: no cover
        self.client = get_client()

        self.name = None
        self.number = None
        self.created = None
        self.updated = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        else:
            raise ValueError('Invalid data')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name or self.number)

    @classmethod
    def get(cls, number):
        """
        Get the CNAM of the number.
        :return: NumberInfo instance.
        """
        client = get_client()
        number = six.moves.urllib.parse.quote(number)
        url = '{}/v1/{}/{}'.format(client.endpoint, cls._path, number)
        data = client.get(url, join_endpoint=False).json()
        return cls(data=data)


class Media(ListResource):
    """
    The Media resource lets you upload your media files to Bandwidth API servers so they can be used in
    application scripts without requiring a separate hosting provider. You can upload files up to 65 MB and
    file storage is free for an unlimited number of files.
    Files you upload can only be accessed by you when you supply your API access token and secret.
    They are not available to anonymous users.
    """

    _path = 'media'
    _fields = frozenset(('media_name', 'content_length'))

    def __init__(self, data):  # pragma: no cover
        self.client = get_client()

        self.content_length = None
        self.media_name = None
        self.media_url = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.media_name = data
            self.media_url = '{}/{}'.format(self._path, self.media_name)
        else:
            raise TypeError('Accepted only id or media data as dictionary')

    def set_up(self, data):
        content = data.pop('content', None)
        if content:
            data['id'] = content.split('/')[-1]
        return super(Media, self).set_up(data)

    def get_full_media_url(self):
        return self.client._join_endpoint(self.media_url)

    @classmethod
    def list(cls):
        """
        Gets a list of your media files. No query parameters are supported.
        :return: List of recording instances.
        """
        client = cls.client or get_client()
        data_as_list = client.get(cls._path).json()
        return [cls(data=v) for v in data_as_list]

    @classmethod
    def page_iterator(cls, chunk_size=100, chunks_amount=5, **query_params):
        raise NotImplementedError('Media does not support this operation')

    def delete(self):
        """
        Deletes a media file from Bandwidth API server. Make sure you don't have any application scripts still
        using the media before you delete it. If you acccidentally delete a media file, you can immediately
        upload a new file with the same name.
        :return: None
        """
        assert self.media_name is not None, 'Id field is required for this action'
        url = '{}/{}'.format(self._path, self.media_name)
        self.client.delete(url)

    def download(self):
        """
        Downloads a media file you previously uploaded.
        :return: Tuple where first arg is content of media file in bytes,
                and second is content-type of file.
        """
        r = self.client.get(self.media_url)
        return r.content, r.headers['Content-Type']

    @classmethod
    def upload(cls, media_name, content=None, file_path=None, fd=None, mime='audio/mpeg'):
        """
        Uploads a file the normal HTTP way. You may add headers to the request in order
        to provide some control to your media-file.
        :return: None
        """
        assert sum((bool(content), bool(file_path), bool(fd))) == 1, 'Upload should be used either ' \
                                                                     'with content buffer ' \
                                                                     'or with path to file on local filesystem ' \
                                                                     'or with open file descriptor'
        if file_path:
            if not file_exists(file_path):
                raise AppPlatformError('Provided file does not exists {}'.format(file_path))
            with open(file_path, 'rb') as fd:
                content = fd.read()
        elif fd:
            fd.seek(0)
            content = fd.read()
        else:
            assert isinstance(content, six.binary_type), 'Only bytes accepted in content'
        url = '{}/{}'.format(cls._path, media_name)
        client = get_client()
        client.build_request('put', url, data=content, headers={'content-type': mime})
        return cls(media_name)

    def __repr__(self):
        return 'Media({})'.format(self.media_name)


class Message(GenericResource):
    _path = 'messages'
    STATES = enum('received', 'queued', 'sending', 'sent', 'error')
    RECEIPT_REQUEST = ['all', 'error', 'none']
    _fields = frozenset(('id', 'direction', 'callback_url', 'callback_timeout',
                         'fallback_url', 'from_', 'to', 'state', 'time', 'text',
                         'error_message', 'tag', 'receipt_requested', 'delivery_state',
                         'delivery_code', 'delivery_description', 'media_list'))

    class _Multi(object):

        def __init__(self):
            self.messages = []
            self.errors = []
            self.done = False

        def _post_messages(self):
            post_data = self.messages
            client = get_client()
            url = Message._path
            r = client.post(url, data=post_data).json()
            return r

        def push_message(self, sender, receiver, text=None, media_list=None, callback_url=None, tag=None, receipt_requested=None):
            message = Message._prepare_message(sender=sender, receiver=receiver, text=text,
                                               callback_url=callback_url, tag=tag,
                                               receipt_requested=receipt_requested,
                                               media_list=media_list)
            self.messages.append(message)

        def execute(self):
            if self.done:
                raise AppPlatformError('You have already executed this queue')
            self.done = True
            val = self._post_messages()
            self.messages.reverse()
            messages = []
            for answer in val:
                data = self.messages.pop()
                if 'location' in answer:
                    data.update({'id': answer['location'].split('/')[-1]})
                    messages.append(Message(data))
                elif 'error' in answer:
                    data.update({'error_message': answer['error']['message'],
                                 'state': Message.STATES.error})
                    self.errors.append(Message(data))
            return messages

    def __init__(self, data):  # pragma: no cover
        self.client = get_client()

        self.id = None
        self.direction = None
        self.callback_url = None
        self.callback_timeout = None
        self.fallback_url = None
        self.from_ = None
        self.to = None
        self.state = None
        self.time = None
        self.text = None
        self.media_list = None
        self.tag = None
        self.receipt_requested = None
        self.delivery_state = None
        self.delivery_code = None
        self.delivery_description = None
        self.error_message = None

        self._multi = False
        self._batch_messages = None

        if isinstance(data, dict):
            self.set_up(from_api(data))

            if self.receipt_requested is not None and self.receipt_requested not in self.RECEIPT_REQUEST:
                raise TypeError('Accepted only all, error or none as receipt_request')

        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only message-id or message data as dictionary')

    def __repr__(self):
        return 'Message({}, state={}, delivery_state={})'.format(self.id, self.state, self.delivery_state)

    def set_up(self, data):
        self.from_ = self.from_ or data.get('from')
        self.media_list = data.get("media")
        super(Message, self).set_up(data)

    @classmethod
    def _prepare_message(cls, sender, receiver, text=None, media_list=None, callback_url=None, tag=None, receipt_requested=None):
        if isinstance(sender, PhoneNumber):
            sender = sender.number

        if receipt_requested is not None and receipt_requested not in cls.RECEIPT_REQUEST:
            raise TypeError('Accepted only all, error or none as receipt_requested')

        data = {
            'from': sender,
            'to': receiver,
            'text': text,
            'callback_url': callback_url,
            'receipt_requested': receipt_requested,
            'tag': tag
        }

        if (media_list is not None):
            data['media'] = [m.get_full_media_url() for m in media_list]

        return to_api(data)

    @classmethod
    def list(cls, **query):
        """
        :param sender: The phone number to filter the messages that came from
                     (must be in E.164 format, like +19195551212).
        :param receiver: The phone number to filter the messages that was sent to
                   (must be in E.164 format, like +19195551212).
        :param page: Used for pagination to indicate the page requested for
                     querying a list of messages.
                     If no value is specified the default is 0.
        :param size: Used for pagination to indicate the size of each page
                     requested for querying a list of messages.
                     If no value is specified the default value is 25. (Maximum value 1000)
        """
        client = cls.client or get_client()
        if 'sender' in query:
            query['from'] = query.pop('sender')
        if 'receiver' in query:
            query['to'] = query.pop('receiver')
        query = to_api(query)
        data_as_list = client.get(cls._path, params=query).json()
        return [cls(v) for v in data_as_list]

    @classmethod
    def get(cls, message_id):
        """
        Gets information about a previously sent or received message
        :param message_id: id of message that you want to retrieve
        :return: new Message instance with all provided fields.
        """
        client = cls.client or get_client()
        url = '{}/{}'.format(cls._path, message_id)
        data_as_dict = client.get(url).json()
        return cls(data_as_dict)

    @classmethod
    def send(cls, sender, receiver, text=None, media_list=None, callback_url=None, tag=None, receipt_requested=None):
        """
        :param sender: One of your telephone numbers the message should come from.
                       Must be PhoneNumber instance or in E.164 format, like +19195551212.
        :param receiver: The phone number the message should be sent to
                         (must be in E.164 format, like +19195551212)
        :param text: The contents of the text message.
        :param media_list: A list of catapult media objects to be included into the message
        :param callback_url: URL where the events related to the outgoing message will be posted to.
        :param tag: A string that will be included in the callback events of the message.
        :param receipt_requested: A enum option specifying if the message wants receipt.
        :return: New message instance with filled data.
        """
        data = cls._prepare_message(sender=sender, receiver=receiver, text=text,
                                    callback_url=callback_url, tag=tag, receipt_requested=receipt_requested,
                                    media_list=media_list)

        client = cls.client or get_client()
        r = client.post(cls._path, data=data)

        message_id = get_location_id(r)
        message = cls(message_id)
        message.set_up(data)
        return message

    @classmethod
    def send_batch(cls):
        """
        Method that return sender instance for sending batch of messages
        with different params.

        sender instance have 2 methods:
         1. push_message(), that is similar to method send of Message class, and
                           takes same arguments
            :return: None
         2. execute(), that execute request to catapult with pushed messages, returns
            list of Messages instance.
            :return: [Message('some-id', state='sent'), Message('some-id2', state='sent')]


        sender have attribute "errors" that can contains list Messages with state=error and with
        error_messages attribute (what actually went wrong in batch creation)

        Usage:
        sender = Message.send_batch()
        sender.push_message('+19195551212', '+19195551213', 'Hello this is test')
        sender.push_message('+19195551213', '+19195551214', 'Hello this is test1')
        sender.push_message('+19195551214', '+19195551215', '')
        sender.execute()
        if sender.errors:
            ...

        """
        return cls._Multi()


class Domain(GenericResource):
    _path = 'domains'
    _fields = ('id', 'name', 'description', 'endpoints')

    def __init__(self, data):
        self.client = get_client()

        self.id = None
        self.name = None
        self.description = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only domain-id or domain data as dictionary')

    @classmethod
    def create(cls, **data):
        """
        :param name: A name you choose for this domain
        :param description: A description you choose for this domain
        :return: Domain instance
        """
        client = cls.client or get_client()
        p_data = to_api(data)
        resp = client.post(cls._path, data=p_data)
        domain_id = get_location_id(resp)
        data.update({'id': domain_id})
        return cls(data=data)

    @classmethod
    def list(cls, page=0, size=25):
        """
        :param page: Used for pagination to indicate the page requested for querying a list of domains.
        If no value is specified the default is 1.
        :param size: Used for pagination to indicate the size of each page requested for querying a list of domains.
        If no value is specified the default value is 25. (Maximum value 1000).
        :return: List of Domain instances
        """
        client = cls.client or get_client()
        data_as_list = client.get(
            cls._path, params=dict(page=page, size=size)).json()
        return [cls(data=from_api(v)) for v in data_as_list]

    @classmethod
    def get(cls, domain_id):
        """
        :param domain_id: domain id that you want to retrieve.
        Gets information about one of your domains. No query parameters are supported.
        :return: Domain instance
        """
        client = cls.client or get_client()
        url = '{}/{}'.format(cls._path, domain_id)
        data_as_dict = client.get(url).json()
        domain = cls(data=from_api(data_as_dict))
        return domain

    def patch(self, **data):
        """
        :param description:    A description you choose for this application
        :return: self if it's patched
        """
        client = self.client or get_client()
        url = '{}/{}'.format(self._path, self.id)
        cleaned_data = {k: v for k, v in data.items() if v is not None and k in self._fields}
        client.post(url, data=to_api(cleaned_data))
        if cleaned_data:
            self.data = cleaned_data
            self.set_up(self.data)
        return self

    def delete(self):
        """
        Delete domain instance on catapult side.
        :return: True if it's deleted
        """
        client = self.client or get_client()
        url = '{}/{}'.format(self._path, self.id)
        client.delete(url)
        return True

    def refresh(self):
        url = '{}/{}'.format(self._path, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))

    def get_endpoints(self):
        """
        List all endpoints from a domain.
        """
        client = self.client
        url = '{}/{}/endpoints'.format(self._path, self.id)
        endpoint_list = client.get(url).json()
        return [Endpoint(self.id, data) for data in endpoint_list]

    def add_endpoint(self, **params):
        """
        Add endpoints to a domain.
        :param name: A name you choose for this endpoint
        :param description: A description you choose for this endpoint
        :param application_id: A application_id in which the endpoint will be related
        :param enabled: Used to indicate if this endpoing is enabled
        :param credentials: A set of credentials for this endpoints
        :return: Endpoint instance
        """
        client = self.client
        url = '{}/{}/endpoints'.format(self._path, self.id)
        data = to_api(params)
        r = client.post(url, data=data)
        endpoint_id = get_location_id(r)
        data.update({'id': endpoint_id})
        return Endpoint(self.id, data)


class Endpoint(GenericResource):
    _fields = ('id', 'name', 'description', 'domain_id', 'application_id', 'enabled', 'credentials', 'sip_uri')

    def __init__(self, domain_id, data):
        self.client = get_client()

        self.id = None
        self.name = None
        self.description = None
        self.application_id = None
        self.enabled = True
        self.credentials = None
        self.sip_uri = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only endpoint-id or endpoint data as dictionary')

        self.domain_id = domain_id

    @classmethod
    def create(cls, domain_id, **data):
        """
        :param domain_id: domain in which the endpoint belongs to
        :param name: A name you choose for this endpoint
        :param description: A description you choose for this endpoint
        :param domain_id: A domain_id in which this endpoint will be created
        :param application_id: A application_id in which the endpoint will be related
        :param enabled: Used to indicate if this endpoing is enabled
        :param credentials: A set of credentials for this endpoints
        :return: Endpoint instance
        """
        client = cls.client or get_client()
        p_data = to_api(data)
        url = 'domains/{}/endpoints'.format(domain_id)
        resp = client.post(url, data=p_data)
        endpoint_id = get_location_id(resp)
        data.update({'id': endpoint_id})
        return cls(domain_id, data=data)

    @classmethod
    def list(cls, domain_id, page=0, size=25):
        """
        :param domain_id: domain in which the endpoint belongs to
        :param page: Used for pagination to indicate the page requested for querying a list of endpoints.
        If no value is specified the default is 1.
        :param size: Used for pagination to indicate the size of each page requested for querying a list of endpoints.
        If no value is specified the default value is 25. (Maximum value 1000).
        :return: List of Endpoints instances
        """
        client = cls.client or get_client()
        url = 'domains/{}/endpoints'.format(domain_id)
        data_as_list = client.get(url, params=dict(page=page, size=size)).json()
        return [cls(domain_id, data=from_api(v)) for v in data_as_list]

    @classmethod
    def get(cls, domain_id, endpoint_id):
        """
        :param domain_id: domain in which the endpoint belongs to
        :param endpoint_id: endpoint_id that you want to retrieve.
        Gets information about one of your endpoints. No query parameters are supported.
        :return: Endpoint instance
        """
        client = cls.client or get_client()
        url = 'domains/{}/endpoints/{}'.format(domain_id, endpoint_id)
        data_as_dict = client.get(url).json()
        endpoint = cls(domain_id, data=from_api(data_as_dict))
        return endpoint

    def patch(self, **data):
        """
        :param description: A description you choose for this endpoint
        :param application_id: A application_id in which the endpoint will be related
        :param enabled: Used to indicate if this endpoing is enabled
        :return: self if it's patched
        """
        client = self.client or get_client()
        url = 'domains/{}/endpoints/{}'.format(self.domain_id, self.id)
        cleaned_data = {k: v for k, v in data.items() if v is not None and k in self._fields}
        client.post(url, data=to_api(cleaned_data))
        if cleaned_data:
            self.data = cleaned_data
            self.set_up(self.data)
        return self

    def delete(self):
        """
        Delete endpoint instance on catapult side.
        :return: True if it's deleted
        """
        client = self.client or get_client()
        url = 'domains/{}/endpoints/{}'.format(self.domain_id, self.id)
        client.delete(url)
        return True

    def create_token(self, **params):
        """
        Create token to access the endpoint.
        :param expires: time for the token expires (milliseconds)
        :return: EndpointToken instance
        """
        client = self.client or get_client()
        url = 'domains/{}/endpoints/{}/tokens'.format(self.domain_id, self.id)
        data = to_api(params)
        resp = client.post(url, data=data)
        token_id = get_location_id(resp)
        data_as_dict = resp.json()
        data_as_dict['id'] = token_id
        return EndpointToken(self.domain_id, self.id, data=from_api(data_as_dict))

    def refresh(self):
        url = 'domains/{}/endpoints/{}'.format(self.domain_id, self.id)
        data = self.client.get(url).json()
        self.set_up(from_api(data))


class EndpointToken(GenericResource):
    _fields = ('id', 'token', 'expires')

    def __init__(self, domain_id, endpoint_id, data):
        self.client = get_client()

        self.id = None
        self.token = None
        self.expires = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only token data as dictionary')

        self.domain_id = domain_id
        self.endpoint_id = endpoint_id

    @classmethod
    def create(cls, domain_id, endpoint_id, **params):
        """
        Create token to access the endpoint.
        :param expires: time for the token expires (milliseconds)
        :return: EndpointToken instance
        """
        client = cls.client or get_client()
        url = 'domains/{}/endpoints/{}/tokens'.format(domain_id, endpoint_id)
        data = to_api(params)
        resp = client.post(url, data=data)
        token_id = get_location_id(resp)
        data_as_dict = resp.json()
        data_as_dict['id'] = token_id
        return cls(domain_id, endpoint_id, data=from_api(data_as_dict))

    def delete(self):
        """
        Delete endpoint token instance on catapult side.
        :return: True if it's deleted
        """
        client = self.client or get_client()
        url = 'domains/{}/endpoints/{}/tokens/{}'.format(self.domain_id, self.endpoint_id, self.id)
        client.delete(url)
        return True


class UserError(ListResource):
    """
    The User Errors resource lets you see information about errors that happened in your API calls
    and during applications callbacks. This error information can be very helpful
    when you're debugging an application.

    :param id: 	The user error ID
    :param time: 	The time the error ocurred
    :param category: The error category, one of:

        authentication
            The requestor could not be authenticated. Incorrect or disabled credentials are common causes
            of these errors.
        authorization
            The requestor does not have sufficient permissions to perform the operation or access the resource,
            or some other authorization error occurred.
        not-found
            The resource could not be found
        bad-request
            The request information sent could not be understood or contained values that are not allowed.
        conflict
            The resource could not be modified because it was already modified by a different request.
        unavailable
            The resource or service is currently unavailable. It may become available shortly, or the request may have
                to be modified to succeed.
        credit
            The requestor has insufficient credit to perform the operation or access the resource.
        limit
            A usage limit or rate limit for a resource or service has been exceeded.
        payment
            There was an error processing a payment.

    :param code: A specific error code string that identifies the type of error
    :param message: A message that describes the error condition in detail
    :param details: A list of additional details that may help you debug the error; see the User Error Detail
        Properties table
    """

    _fields = frozenset(('id', 'time', 'category', 'code', 'message', 'details', 'version', 'user'))

    # Additional details that may help you debug the error
    Detail = namedtuple('Detail', ['id', 'name', 'value'])
    User = namedtuple('UserInfo', ['id', 'account_non_expired', 'account_non_locked',
                                   'company_name', 'credentials_non_expired', 'email',
                                   'enabled', 'first_name', 'last_name', 'password', 'username'])

    _path = 'errors'
    CATEGORIES = enum('authentication', 'authorization', 'conflict', 'unavailable', 'credit', 'limit', 'payment',
                      not_found='not-found', bad_request='bad-request')

    def __init__(self, data):  # pragma: no cover
        self.client = get_client()

        self.id = None
        self.time = None
        self.category = None
        self.code = None
        self.message = None
        self.details = None
        self.version = None
        self.user = None

        if isinstance(data, dict):
            self.set_up(from_api(data))
        elif isinstance(data, six.string_types):
            self.id = data
        else:
            raise TypeError('Accepted only error-id or error data as dictionary')

    def __repr__(self):
        return 'UserError({}, message={})'.format(self.id, self.message)

    def set_up(self, data):
        details = data.pop('details', [])
        self.details = [self.Detail(**from_api(d)) for d in details]
        user = data.pop('user', None)
        if user:
            user.pop('@id', None)  # what is that?
            self.user = self.User(**from_api(user))
        super(UserError, self).set_up(data)

    @classmethod
    def list(cls, **query):
        """
        Gets the most recent user errors for the user.

        Since this operation uses HTTP GET, all the properties are specified as HTTP request parameters.
        :param page: Used for pagination to indicate the page requested for
                     querying a list of errors.
                     If no value is specified the default is 0.
        :param size: Used for pagination to indicate the size of each page
                     requested for querying a list of errors.
                     If no value is specified the default value is 25. (Maximum value 1000)
        """
        client = cls.client or get_client()
        query = to_api(query)
        data_as_list = client.get(cls._path, params=query).json()
        return [cls(v) for v in data_as_list]

    @classmethod
    def get(cls, error_id):
        """
        Gets information about one user error.
        :param error_id: id of error that you want to retrieve
        :return: new UserError instance with all provided fields.
        """
        client = cls.client or get_client()
        url = '{}/{}'.format(cls._path, error_id)
        data_as_dict = client.get(url).json()
        return cls(data_as_dict)
