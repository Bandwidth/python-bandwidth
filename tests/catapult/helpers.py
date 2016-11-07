import requests
from bandwidth.catapult import Client

def get_client():
    return Client('userId', 'apiToken', 'apiSecret')

def create_response(status_code = 200, content = '', content_type = 'application/json'):
        response = requests.Response()
        response.status_code = status_code
        response.headers['content-type'] = content_type
        response._content = content
        return response

AUTH = ('apiToken', 'apiSecret')
