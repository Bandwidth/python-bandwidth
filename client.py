from urllib.parse import quote
import logging
import json
import requests

log = logging.getLogger(__name__)

__all__ = ('Client', )


class Call(object):

    def __init__(self, client, kwargs):
        self.client = client
        self.kwargs = kwargs


class Client(object):
    endpoint = None
    uid = None
    auth = None
    log_hook = None
    default_timeout = 60
    headers = {'content-type': 'application/json'}

    def Call(self, kwargs):
        return Call(self, kwargs)

    class Error(Exception):
        pass

    def __init__(self, user_id: str, auth: tuple, endpoint='https://api.catapult.inetwork.com', log_hook=None):
        self.endpoint = endpoint
        self.log_hook = log_hook
        self.uid = user_id
        self.auth = auth
        self.application_id = None

    def _log_response(self, response):
        '''
        Perform logging actions with the response object returned
        by Client using self.log_hook.
        '''
        if self.log_hook:
            self.log_hook(response)

    def _join_endpoint(self, url):
        return '{}{}'.format(self.endpoint, url)

    def _delete(self, url, timeout=None, **kwargs):
        url = self._join_endpoint(url)

        if timeout is not None:
            kwargs['timeout'] = timeout

        response = requests.delete(url, auth=self.auth, headers=self.headers, **kwargs)

        self._log_response(response)

        return response

    def _get(self, url, timeout=None, **kwargs):
        url = self._join_endpoint(url)

        kwargs['timeout'] = timeout or self.default_timeout

        response = requests.get(url, auth=self.auth, headers=self.headers, **kwargs)

        self._log_response(response)

        return response

    def _post(self, url, timeout=None, **kwargs):
        url = self._join_endpoint(url)

        kwargs['timeout'] = timeout or self.default_timeout

        response = requests.post(url, auth=self.auth, headers=self.headers, **kwargs)

        self._log_response(response)

        return response

    def create_application(self, name, timeout=None, **kwargs):

        json_data = {
            'name': name,
        }
        json_data.update(kwargs)
        return self._post(
            '/v1/users/{}/applications'.format(self.uid),
            data=json.dumps(json_data),
            timeout=timeout)

    def delete_application(self, app_id, timeout=None):
        url = '/v1/users/{}/applications/{}'.format(self.uid, app_id)

        return self._delete(url, timeout=timeout)

    def list_applications(self, page=0, size=25, timeout=None):
        '''
        Gets a list of self.uid's applications.
        '''
        url = '/v1/users/{}/applications'.format(self.uid)

        http_get_params = {'page': page, 'size': size}

        return self._get(url, params=http_get_params, timeout=timeout)

    def get_application(self, application_id, timeout=None):
        '''
        Gets information about one application.
        '''
        url = '/v1/users/{}/applications/{}'.format(self.uid, application_id)

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

        return self._post(
            '/v1/users/{}/phoneNumbers'.format(self.uid),
            data=json.dumps(json_data),
            timeout=timeout)

    def delete_number(self, number_id, timeout=None):
        '''
        Deletes a phone number associated with the numberId
        '''

        url = '/v1/users/{}/phoneNumbers/{}'.format(self.uid, number_id)

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
        url = '/v1/users/{}/phoneNumbers/{}'.format(self.uid, number)

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
        url = '/v1/users/{}/phoneNumbers/{}'.format(self.uid, phone_id)
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
        url = '/v1/users/{}/phoneNumbers'.format(self.uid)

        http_get_params = {
            'applicationId': application_id,
            'page': page,
            'size': size}

        return self._get(url, params=http_get_params, timeout=timeout)

    def call_phone(self, from_number, to_number, record_call=False, timeout=None):
        '''
        Initiates a call
        '''
        json_data = {'from': from_number, 'to': to_number}

        if record_call:
            json_data['recordingEnabled'] = 'true'

        url = '/v1/users/{}/calls'.format(self.uid)

        return self._post(url, data=json.dumps(json_data), timeout=timeout)

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

        log.debug('Making a call with the following data: {}'.format(json_data))

        url = '/v1/users/{}/calls'.format(self.uid)

        return self._post(url, data=json.dumps(json_data), timeout=timeout)

    def get_call_info(self, call_id, timeout):
        url = '/v1/users/{}/calls/{}'.format(self.uid, call_id)

        return self._get(url, timeout=timeout)

    def get_bridge_info(self, bridge_id, timeout=None):
        '''
        Retrieves info about a bridge such as the call ID's associated with the bridge
        '''
        url = '/v1/users/{}/bridges/{}'.format(self.uid, bridge_id)

        return self._get(url, timeout=timeout)

    def create_bridge(self, bridge_audio, call_ids, timeout=None):
        url = '/v1/users/{}/bridges/'.format(self.uid)

        json_data = {'bridgeAudio': bridge_audio,
                     'callIds': call_ids}
        data = json.dumps(json_data)
        return self._post(url, data=data, timeout=timeout)

    def create_call(self, caller, callee, timeout=None, **kwargs):
        url = '/v1/users/{}/calls/'.format(self.uid)

        json_data = {
            'from': caller,
            'to': callee,
            'callTimeout': 30,  # seconds
        }

        json_data.update(kwargs)
        return self._post(url, data=json.dumps(json_data), timeout=timeout)

    def send_dtmf(self, call_id, dtmf, timeout=None):
        '''
        Sends a string of characters as DTMF on the given call_id
        Valid chars are '0123456789*#ABCD'
        '''
        url = '/v1/users/{}/calls/{}/dtmf'.format(self.uid, call_id)

        json_data = {'dtmfOut': dtmf}

        return self._post(url, data=json.dumps(json_data), timeout=timeout)

    def receive_dtmf(self, call_id, max_digits, terminating_digits,
                     inter_digit_timeout='1', timeout=None):
        url = '/v1/users/{}/calls/{}/gather'.format(self.uid, call_id)

        http_get_params = {
            'maxDigits': max_digits,
            'terminatingDigits': terminating_digits,
            'interDigitTimeout': inter_digit_timeout}

        return self._get(url, params=http_get_params, timeout=timeout)

    def end_call(self, call_id):
        '''
        Hangs up a call with the given call_id
        '''
        url = '/v1/users/{}/calls/{}/'.format(self.uid, call_id)

        return self._post(url, data=json.dumps({}), timeout=None)

    def play_audio(self, call_id, timeout=None, **kwargs):
        '''
        Plays audio form the given url to the call associated with call_id
        '''
        url = '/v1/users/{}/calls/{}/audio'.format(self.uid, call_id)

        # stops currently playing audio
        key = 'fileUrl' if 'fileUrl' in kwargs else 'sentence'
        if kwargs[key]:
            self._post(url, data=json.dumps({key: ''}), timeout=timeout)

        return self._post(url, data=json.dumps(kwargs), timeout=timeout)

    def get_bridge_url(self, url, timeout=None):
        return self._get(url, timeout=timeout)

    def get_recordings(self, call_id, timeout=None):
        '''
        Retrieves an array with all the recordings of the call_id
        '''
        url = '/v1/users/{}/calls/{}/recordings'.format(self.uid, call_id)

        return self._get(url, timeout=timeout)

    def set_call_property(self, call_id, timeout=None, **kwargs):
        url = '/v1/users/{}/calls/{}'.format(self.uid, call_id)
        json_data = json.dumps(kwargs)

        return self._post(url, data=json_data, timeout=timeout)

    def send_message(self, from_who, to_who, text, timeout=None, **kwargs):
        url = '/v1/users/{}/messages/'.format(self.uid)
        json_data = {'from': from_who,
                     'to': to_who,
                     'text': text
                     }
        json_data.update(kwargs)
        data = json.dumps(json_data)

        return self._post(url, data=data, timeout=timeout)

    def send_message_multy_v1(self, message_batch, timeout=None):
        url = '/v1/users/{}/messages/'.format(self.uid)

        if not all(isinstance(m, dict) and
                   m['from'] and
                   m['to'] and
                   m['text'] for m in message_batch):
            raise Client.Error('Invallid data to multi message {}'.format(message_batch))

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
        url = '/v1/users/{}/messages/'.format(self.uid)

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

    def activate_gathering(self, call_id, maxDigits, interDigitTimeout, terminatingDigits, timeout=None, **kwargs):
        url = '/v1/users/{}/calls/{}/gather'.format(self.uid, call_id)
        data = {'maxDigits': maxDigits,
                'interDigitTimeout': interDigitTimeout,
                'terminatingDigits': terminatingDigits,
                'prompt': kwargs.get('prompt')}
        data = {k: v for k, v in data.items() if v is not None}  # deleting keys with None values
        return self._post(url, data=json.dumps(data), timeout=timeout)

    def get_gather_info(self, call_id, gather_id, timeout=None):
        url = '/v1/users/{}/calls/{}/gather/{}'.format(self.uid, call_id, gather_id)
        return self._get(url, timeout=timeout)

    def get_recording(self, rid, timeout=None):
        url = '/v1/users/{}/recordings/{}'.format(self.uid, rid)
        return self._get(url, timeout=timeout)

    def delete_media(self, media_name, timeout=None):
        url = '/v1/users/{}/media/{}'.format(self.uid, media_name)
        return self._delete(url, timeout=timeout)

    def get(self, url, **kwargs):
        '''
        There are sevral places project where we need to GET request directly,
        without any urls or payloads construction.
        '''
        if url and url.startswith('https://localhost:8444/'):
            url = url.replace('localhost:8444', 'api.catapult.inetwork.com')
        response = requests.get(url, auth=self.auth, headers=self.headers, **kwargs)

        self._log_response(response)

        return response
