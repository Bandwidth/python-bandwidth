import json
from six import iteritems
from .utils import from_api
# Event abstraction


class Event(object):

    @staticmethod
    def create(data=None, **kwargs):
        if data is not None:
            event_as_dict = json.loads(data.decode('utf-8'))
        else:
            event_as_dict = from_api(kwargs)
        event_cls = _events.get(event_as_dict['eventType'])
        if not event_cls:
            raise ValueError('Unknown event {}'.format(event_as_dict))
        return event_cls(**kwargs)


class BaseEvent(object):
    callId = None

    def __init__(self, **kwargs):
        for attr, val in iteritems(kwargs):
            if not hasattr(self, attr):
                raise ValueError('Malformed')
            setattr(self, attr, val)

    @property
    def call(self):
        # avoid cyclic imports
        from .models import Call
        return Call(self.callId)


class IncomingCallEvent(BaseEvent):
    eventType = None
    from_ = None
    to = None
    callUri = None
    callState = None
    applicationId = None
    time = None


class AnswerCallEvent(BaseEvent):
    eventType = None
    from_ = None
    to = None
    callUri = None
    callState = None
    applicationId = None
    time = None


class HangupEvent(BaseEvent):
    eventType = None
    from_ = None
    to = None
    callUri = None
    callState = None
    cause = None
    time = None


class PlaybackCallEvent(BaseEvent):
    eventType = None
    callId = None
    callUri = None
    status = None
    time = None
    tag = None

    @property
    def done(self):
        return self.status == 'done'


_events = {"hangup": HangupEvent,
           "answer": AnswerCallEvent,
           "incomingcall": IncomingCallEvent,
           "playback": PlaybackCallEvent}
