import os
from urllib.parse import quote
import logging
import json

from .rest import RESTClientObject
from .errors import BandwithError

logger = logging.getLogger(__name__)

__all__ = ('_Client', 'Call')


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

    def create_application(self, name, timeout=None, **kwargs):

        json_data = {
            'name': name,
        }
        json_data.update(kwargs)
        return self._post('applications', data=json.dumps(json_data), timeout=timeout)

    def delete_application(self, app_id, timeout=None):
        url = 'applications/{}'.format(app_id)

        return self._delete(url, timeout=timeout)

    def list_applications(self, page=0, size=25, timeout=None):
        '''
        Gets a list of self.uid's applications.
        '''
        url = 'applications'

        http_get_params = {'page': page, 'size': size}

        return self._get(url, params=http_get_params, timeout=timeout)

    def get_application(self, application_id, timeout=None):
        '''
        Gets information about one application.
        '''
        url = 'applications/{}'.format(application_id)

        return self._get(url, timeout=timeout)

    def reserve_number(self, number, name='',
                       fallback_number='', timeout=None):
        '''
        Allocates a number so you can use it to make and receive calls
        and send and receive messages.
        '''
        json_data = {
            'number': number,
            'applicationId': self.application_id,
            'name': name,
            'fallbackNumber': fallback_number}

        return self._post('phoneNumbers', data=json.dumps(json_data), timeout=timeout)

    def delete_number(self, number_id, timeout=None):
        '''
        Deletes a phone number associated with the numberId
        '''

        url = 'phoneNumbers/{}'.format(number_id)

        return self._delete(url, timeout=timeout)

    def get_available_numbers_by_state(self, state, timeout=None):
        '''
        Performs a request to get the available
        '''
        url = '/v1/availableNumbers/local'

        return self._get(url, params={'state': state}, timeout=timeout)

    def get_number(self, number, timeout=None):
        '''
        GET /v1/users/{userId}/phoneNumbers/{numberString}
        Gets information about one of your numbers using the E.164 number string
        '''
        number = quote(number)
        url = 'phoneNumbers/{}'.format(number)

        return self._get(url, timeout=timeout)

    def patch_number(self, number, application_id, fallback_number='', timeout=None):
        """
        Makes changes to a number you have. POST a new JSON representation with the property values you desire to the URL
        that you got back in the "Location" header when you first allocated it.
        Properties you don't send will remain unchanged.
        """
        r = self.get_number(number)
        if not r.ok:
            return r
        phone_id = r.json()['id']
        url = 'phoneNumbers/{}'.format(phone_id)
        data = {'applicationId': application_id}

        return self._post(url, data=json.dumps(data),
                          timeout=timeout)

    def get_available_numbers_by_zip(self, zipcode, timeout=None):
        '''
        Performs a request to get the available
        '''
        url = '/v1/availableNumbers/local'

        return self._get(url, params={'zip': zipcode}, timeout=timeout)

    def list_numbers(self, application_id=None, page=None, size=None, timeout=None):
        '''
        Lists all of the numbers associated with applicationId,
        or all numbers owned by a user if appId=None
        '''
        url = 'phoneNumbers'

        http_get_params = {
            'applicationId': application_id,
            'page': page,
            'size': size}

        return self._get(url, params=http_get_params, timeout=timeout)

    def call_phone_into_bridge(self, from_number, to_number, bridge_id, tag=None,
                               record_call=False, timeout=None):
        '''
        Initiates a call
        '''
        json_data = {
            'from': from_number,
            'to': to_number,
            'bridgeId': bridge_id,
            'tag': tag}

        if record_call:
            json_data['recordingEnabled'] = 'true'

        self.log.debug('Making a call with the following data: {}'.format(json_data))

        url = 'calls'

        return self._post(url, data=json.dumps(json_data), timeout=timeout)

    def get_call_info(self, call_id):
        url = 'calls/{}'.format(call_id)
        return self._get(url).json()

    def get_calls(self, page=1, size=20):
        url = 'calls/'
        params = dict(page=page, size=size)
        return self._get(url, params=params).json()

    def get_bridge_info(self, bridge_id, timeout=None):
        '''
        Retrieves info about a bridge such as the call ID's associated with the bridge
        '''
        url = 'bridges/{}'.format(bridge_id)

        return self._get(url, timeout=timeout)

    def create_bridge(self, bridge_audio, call_ids, timeout=None):
        url = 'bridges/'

        json_data = {'bridgeAudio': bridge_audio,
                     'callIds': call_ids}
        data = json.dumps(json_data)
        return self._post(url, data=data, timeout=timeout)

    def create_call(self, caller, callee, timeout=None, **kwargs):
        url = 'calls/'

        json_data = {
            'from': caller,
            'to': callee,
            'callTimeout': 30,  # seconds
        }

        json_data.update(kwargs)
        data = self._post(url, data=json.dumps(json_data), timeout=timeout)
        location = data.headers['Location']
        call_id = location.split('/')[-1]
        return call_id

    def get_bridge_url(self, url, timeout=None):
        return self._get(url, timeout=timeout)

    def send_message(self, from_who, to_who, text, timeout=None, **kwargs):
        url = 'messages/'
        json_data = {'from': from_who,
                     'to': to_who,
                     'text': text
                     }
        json_data.update(kwargs)
        data = json.dumps(json_data)

        return self._post(url, data=data, timeout=timeout)

    def send_message_multy_v1(self, message_batch, timeout=None):
        url = 'messages/'

        if not all(isinstance(m, dict) and
                   m['from'] and
                   m['to'] and
                   m['text'] for m in message_batch):
            raise BandwithError('Invallid data to multi message {}'.format(message_batch))

        data = json.dumps(message_batch)

        return self._post(url, data=data, timeout=timeout)

    def send_message_multy_v2(self, from_who, to_who, params, timeout=None):
        '''

        @param from_who:
        @param to_who:
        @param params: list of (text, callbackUrl, tag) tuples.
        @param timeout:
        @return:
        '''
        url = 'messages/'

        def _composition(elem):
            text, cb_url, tag = elem
            entry = {'from': from_who,
                     'to': to_who,
                     'text': text
                     }
            if cb_url:
                entry['callbackUrl'] = cb_url
            if tag:
                entry['tag'] = tag
            return entry
        json_data = list(map(_composition, params))
        data = json.dumps(json_data)
        return self._post(url, data=data, timeout=timeout)

    def get_recording(self, rid, timeout=None):
        url = 'recordings/{}'.format(rid)
        return self._get(url, timeout=timeout)

    def delete_media(self, media_name, timeout=None):
        url = 'media/{}'.format(media_name)
        return self._delete(url, timeout=timeout)


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
        data = json.dumps({"bridgeAudio": bridge_audio, "callIds": [c.call_id for c in calls]})
        r = self.client._post('/bridges', data=data)
        location = r.headers['Location']
        bridge_id = location.split('/')[-1]
        return Bridge(bridge_id, *calls, bridge_audio=bridge_audio)

    def refresh(self):
        url = '/v1/users/calls/{}'.format(self.call_id)
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

        return self._post(url, data=json.dumps(json_data), timeout=timeout)

    def receive_dtmf(self, max_digits, terminating_digits,
                     inter_digit_timeout='1', timeout=None):
        url = 'calls/{}/gather'.format(self.call_id)

        http_get_params = {
            'maxDigits': max_digits,
            'terminatingDigits': terminating_digits,
            'interDigitTimeout': inter_digit_timeout}

        return self.client_get(url, params=http_get_params, timeout=timeout)

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

    def __init__(self, id, *calls, bridge_audio=True):
        self.calls = calls

    @property
    def call_ids(self):
        return [c.call_id for c in self.calls]
