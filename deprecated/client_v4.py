import os
from urllib.parse import quote
import logging
import json

from .rest import RESTClientObject
from .errors import BandwidthError
from .events import *

logger = logging.getLogger(__name__)

__all__ = ('_Client', 'Call', )


_global_client = None


def Client(**kwargs):
    """
    Proper way to definition singleton
    """
    global _global_client
    if _global_client is None:
        user_id = os.environ.get('BANDWITH_USER_ID')
        token = os.environ.get('BANDWITH_TOKEN')
        secret = os.environ.get('BANDWITH_SECRET')
        if not all((user_id, token, secret)):
            raise ValueError('Improperly configured')
        _global_client = _Client(user_id, (token, secret))
    return _global_client


class _Client(RESTClientObject):
    endpoint = None
    uid = None
    auth = None
    log_hook = None
    default_timeout = 60
    headers = {'content-type': 'application/json'}

    def __init__(self, user_id: str, auth: tuple, endpoint='https://api.catapult.inetwork.com',
                 log=None, log_hook=None):
        self.endpoint = endpoint + '/v1/users/{}/'.format(user_id)
        self.log_hook = log_hook
        self.uid = user_id
        self.auth = auth
        self.application_id = None
        self.log = log or logger


UNEVALUATED = object()


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
        data = client._post(url, data=json.dumps(json_data))
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

    def play_audio(self, timeout=None, **kwargs):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = 'calls/{}/audio'.format(self.call_id)

        # stops currently playing audio
        key = 'fileUrl' if 'fileUrl' in kwargs else 'sentence'
        if kwargs[key]:
            self.client._post(url, data=json.dumps({key: ''}), timeout=timeout)

        return self.client._post(url, data=json.dumps(kwargs), timeout=timeout)

    def set_call_property(self, timeout=None, **kwargs):
        url = 'calls/{}'.format(self.call_id)
        json_data = json.dumps(kwargs)
        return self.client._post(url, data=json_data, timeout=timeout)

    def bridge(self, *calls, bridge_audio=True):
        _calls = (self,) + calls
        return Bridge.create(*_calls, bridge_audio=bridge_audio)

    def refresh(self):
        url = 'calls/{}'.format(self.call_id)
        data = self.client._get(url).json()
        self.data.update(data)
        self.set_up()

    def __repr__(self):
        return 'Call({})'.format(repr(self.data) if self.data is not UNEVALUATED else self.call_id)

    def send_dtmf(self, dtmf, timeout=None):
        '''
        Sends a string of characters as DTMF on the given call_id
        Valid chars are '0123456789*#ABCD'
        '''
        url = 'calls/{}/dtmf'.format(self.call_id)

        json_data = {'dtmfOut': dtmf}

        return self.client._post(url, data=json.dumps(json_data), timeout=timeout)

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

        return self.client._post(url, data=json.dumps({}), timeout=None)

    def activate_gathering(self, maxDigits, interDigitTimeout, terminatingDigits, timeout=None, **kwargs):
        url = 'calls/{}/gather'.format(self.call_id)
        data = {'maxDigits': maxDigits,
                'interDigitTimeout': interDigitTimeout,
                'terminatingDigits': terminatingDigits,
                'prompt': kwargs.get('prompt')}
        data = {k: v for k, v in data.items() if v is not None}  # deleting keys with None values
        return self.client._post(url, data=json.dumps(data), timeout=timeout)

    def get_gather_info(self, gather_id, timeout=None):
        url = 'calls/{}/gather/{}'.format(self.call_id, gather_id)
        return self.client._get(url, timeout=timeout)

    def get_recordings(self, timeout=None):
        '''
        Retrieves an array with all the recordings of the call_id
        '''
        url = 'calls/{}/recordings'.format(self.call_id)

        return self.client._get(url, timeout=timeout).json()

    def __getstate__(self):
        return self.call_id

    def __setstate__(self, state):
        self.call_id = state
        self.data = UNEVALUATED
        self.client = Client()
        return True


class Applications(object):
    pass


class Bridge(object):
    id = None
    state = None
    call_ids = None
    calls = None
    bridge_audio = None
    completed_time = None
    created_time = None
    activated_time = None
    client = None

    def __init__(self, id, *calls, bridge_audio=True):
        self.calls = calls
        self.client = Client()
        self.bridge_audio = bridge_audio
        self.id = id

    @classmethod
    def create(cls, *calls, bridge_audio=True):
        client = cls.client or Client()
        data = json.dumps({"bridgeAudio": bridge_audio, "callIds": [c.call_id for c in calls]})
        r = client._post('bridges', data=data)
        location = r.headers['Location']
        bridge_id = location.split('/')[-1]
        return cls(bridge_id, *calls, bridge_audio=bridge_audio)

    @property
    def call_ids(self):
        return [c.call_id for c in self.calls]

    def call(self, caller, callee):
        new_call = Call.create(caller, callee, bridgeId=self.id)
        self.calls += (new_call,)
        return new_call

    def add_call(self, call):
        return

    def fetch_calls(self):
        url = 'bridges/{}/calls'.format(self.id)
        r = self.client._get(url)
        return [Call(v) for v in r.json()]

    def play_audio(self, file):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = 'bridges/{}/audio'.format(self.id)

        self.client._post(url, data=json.dumps({'fileUrl': file}))

    def stop_audio(self, file):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = 'bridges/{}/audio'.format(self.id)

        self.client._post(url, data=json.dumps({'fileUrl': ''}))
