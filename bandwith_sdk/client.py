import os
import logging

from .rest import RESTClientObject

logger = logging.getLogger(__package__)

__all__ = ('Client', '_Client')


_global_client = None


def Client(**kwargs):
    """
    Proper way to define singleton
    """
    #todo: todo implement setup from kwargs
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

    def __init__(self, user_id, auth, endpoint='https://api.catapult.inetwork.com',
                 log=None, log_hook=None):
        self.endpoint = endpoint + '/v1/users/{}/'.format(user_id)
        self.log_hook = log_hook
        self.uid = user_id
        self.auth = auth
        self.application_id = None
        self.log = log or logger
