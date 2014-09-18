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
    event_type = None
    call_id = None
    call_uri = None
    time = None
    dtmf_digit = None
    dtmf_duration = None
    tag = None
    _fields = frozenset(('event_type', 'call_id', 'call_uri', 'time', 'dtmf_digit', 'dtmf_duration', 'tag'))


class SpeakCallEvent(EventType):
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


_events = {"hangup": HangupCallEvent,
           "answer": AnswerCallEvent,
           "incomingcall": IncomingCallEvent,
           "gather": GatherCallEvent,
           "speak": SpeakCallEvent,
           "playback": PlaybackCallEvent,
           "dtmf": DtmfCallEvent}
