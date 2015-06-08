import os
import logging

from .utils import get_creds_from_file, file_exists
from .rest import RESTClientObject

logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')


_global_client = None


def Client(*args):
    """
    Proper way to define singleton
    """
    err_msg = None
    user_id, token, secret = (None, None, None)

    global _global_client
    if args:
        if len(args) != 3:
            err_msg = """
                Creating Client with arguments requires:
                Client(user_id, token, secret)
                where user_id, token, secret are from your Catapult account.
                """
        else:
            user_id, token, secret = args

    elif 'BANDWIDTH_USER_ID' in os.environ:
        user_id = os.environ.get('BANDWIDTH_USER_ID')
        token = os.environ.get('BANDWIDTH_API_TOKEN')
        secret = os.environ.get('BANDWIDTH_API_SECRET')

        if not all((user_id, token, secret)):
            err_msg = """
                If BANDWIDTH_USER_ID is defined in the environment,
                BANDWIDTH_API_TOKEN and BANDWIDTH_API_SECRET must also be defined
                """

    else:
        # get the credentials from a config file
        config_path = None
        if 'BANDWIDTH_CONFIG_FILE' in os.environ:
            config_path = os.environ.get('BANDWIDTH_CONFIG_FILE')
        else:
            config_path = '.bndsdkrc'
        if file_exists(config_path):
            user_id, token, secret = get_creds_from_file(config_path)
            if not all((user_id, token, secret)):
                err_msg = "\n \
                    file [{}] \n \
                    must have user_id, token and secret\n".format(config_path)
        else:
            err_msg = "\n \
                Credentials file <{}> \n \
                does not exist\n".format(config_path)

    if err_msg:
        raise ValueError('Credentials were improperly configured, ERROR MESSAGE: \n {}'.format(err_msg))

    _global_client = RESTClientObject(user_id, (token, secret))

    # from bandwidth_sdk import Account
    # acc = Account.get()
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
