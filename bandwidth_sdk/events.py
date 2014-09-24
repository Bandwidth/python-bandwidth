import json
from six import iteritems
from .utils import from_api
# Event abstraction


class Event(object):

    @staticmethod
    def create(data=None, **kwargs):
        """
        Factory method
        :param data: optional byte string of data
        :param kwargs: params dictionary
        :return: EventType instance or throw an error
        """
        if data is not None:
            api_data = json.loads(data.decode('utf-8'))
            event_as_dict = from_api(api_data)
        else:
            event_as_dict = from_api(kwargs)
        event_cls = _events.get(event_as_dict.get('event_type', ''))
        if not event_cls:
            raise ValueError('Unknown event {}'.format(event_as_dict))
        return event_cls(**event_as_dict)


class EventType(object):
    call_id = None
    _fields = frozenset(('call_id',))

    def __init__(self, **kwargs):
        from_ = kwargs.pop('from', None)
        if from_:
            kwargs['from_'] = from_
        for attr, val in iteritems(kwargs):
            if attr in self._fields:
                setattr(self, attr, val)

    @property
    def call(self):
        # avoid cyclic imports
        from .models import Call
        return Call(self.call_id)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.call_id)


class IncomingCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when an incoming call arrives.
    For incoming call the callback set is the one related to the Application associated with the called number.
    """
    event_type = None
    from_ = None
    to = None
    call_uri = None
    call_state = None
    application_id = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time',
                         'application_id', 'tag'))


class AnswerCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when the call is answered.
    """
    event_type = None
    from_ = None
    to = None
    call_uri = None
    call_state = None
    application_id = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time',
                         'application_id', 'tag'))


class HangupCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when the call ends.
    """
    event_type = None
    from_ = None
    to = None
    call_uri = None
    call_state = None
    cause = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time', 'cause', 'tag'))


class PlaybackCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when audio file playback starts or stops.
    """
    event_type = None
    call_id = None
    call_uri = None
    status = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'tag', 'time'))

    @property
    def done(self):
        return self.status == 'done'


class GatherCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when the gather dtmf is completed or an error occurs.
    """
    event_type = None
    call_id = None
    time = None
    reason = None
    gather_id = None
    state = None
    digits = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'state', 'digits', 'tag', 'time', 'gather_id', 'reason'))

    @property
    def gather(self):
        return self.call.gather.get(self.gather_id)


class DtmfCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when audio file playback starts or stops.
    """
    event_type = None
    call_id = None
    call_uri = None
    time = None
    dtmf_digit = None
    dtmf_duration = None
    tag = None
    _fields = frozenset(('event_type', 'call_id', 'call_uri', 'time', 'dtmf_digit', 'dtmf_duration', 'tag'))


class SpeakCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when text-to-speech starts or stops.
    """
    event_type = None
    call_id = None
    call_uri = None
    status = None
    state = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'status', 'state', 'call_uri', 'tag', 'time'))

    @property
    def done(self):
        return self.status == 'done'


class ErrorCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when an error occurs.
    """
    event_type = None
    from_ = None
    to = None
    call_id = None
    call_uri = None
    call_state = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'call_state', 'time', 'tag'))


class TimeoutCallEvent(EventType):
    """
    Bandwidth API sends this message to the application when the call is not answered until the specified timeout.
    """
    event_type = None
    from_ = None
    to = None
    call_id = None
    call_uri = None
    time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'from_', 'to', 'call_uri', 'time', 'tag'))


class RecordingCallEvent(EventType):
    """
    Bandwidth API sends this event to the application when an the recording media file is saved or an error occurs
    while saving it.
    """
    event_type = None
    call_id = None
    recording_id = None
    recording_uri = None
    state = None
    status = None
    start_time = None
    end_time = None
    tag = None
    _fields = frozenset(('call_id', 'event_type', 'recording_id', 'recording_uri', 'state', 'status', 'start_time',
                         'end_time', 'tag'))


_events = {"hangup": HangupCallEvent,
           "answer": AnswerCallEvent,
           "incomingcall": IncomingCallEvent,
           "gather": GatherCallEvent,
           "speak": SpeakCallEvent,
           "playback": PlaybackCallEvent,
           'error': ErrorCallEvent,
           'timeout': TimeoutCallEvent,
           'recording': RecordingCallEvent,
           "dtmf": DtmfCallEvent}
