import os
import logging

from .rest import RESTClientObject

logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')


_global_client = None


def Client(*args):
    """
    Proper way to define singleton
    """
    global _global_client
    if args:
        assert len(args) == 3, 'Not enough args'
        user_id, token, secret = args
    else:
        user_id = os.environ.get('BANDWIDTH_USER_ID')
        token = os.environ.get('BANDWIDTH_API_TOKEN')
        secret = os.environ.get('BANDWIDTH_API_SECRET')
    if not all((user_id, token, secret)):
        raise ValueError('Credentials were improperly configured')
    _global_client = RESTClientObject(user_id, (token, secret))
    return _global_client


def get_client():
    global _global_client
    if not _global_client:
        return Client()
    return _global_client


def set_client(client):
    """
    Set the global HTTP client for sdk.
    Returns previous client.
    """
    global _global_client
    previous = _global_client
    _global_client = client
    return previous
