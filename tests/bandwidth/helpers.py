import requests
from bandwidth.voice import Client as VoiceClient
from bandwidth.account import Client as AccountClient
from bandwidth.messaging import Client as MessagingClient
from bandwidth.version import __version__ as version

headers = {
    'User-Agent': 'PythonSDK_' + version
}


def get_account_client():
    return AccountClient('userId', 'apiToken', 'apiSecret')


def get_voice_client():
    return VoiceClient('userId', 'apiToken', 'apiSecret')


def get_messaging_client():
    return MessagingClient('userId', 'apiToken', 'apiSecret')


def create_response(status_code=200, content='', content_type='application/json'):
    response = requests.Response()
    response.status_code = status_code
    if content is not None and len(content) > 0:
        response.headers['content-type'] = content_type
        response._content = content.encode('utf-8')
    return response

AUTH = ('apiToken', 'apiSecret')
