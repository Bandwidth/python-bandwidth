import os
import logging

from .utils import get_creds_from_file, file_exists
from .rest import RESTClientObject

logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')


_global_client = None

creds_help = """
There are three ways to set your crednetials.
These are listed in the order of precedence:

1) included as arguments when createing the client: 
    bw_cli = bandwidth_sdk.Client('u-your-user-id', 't-your-token', 'your-secret')
2) environment variables: 
    $ export BANDWIDTH_USER_ID=u-your-user-id
    $ export BANDWIDTH_API_TOKEN=t-your-token
    $ export BANDWIDTH_API_SECRET=your-secret
3) configuration file:
    The file can be specified with env var BANDWIDTH_CONFIG_FILE
    else .bndsdkrc is looked for in the current directory
    The config file has the following format:
[catapult]
user_id = u-your-user-id
token = t-your-token
secret = your-secret
"""

creds_missing_env_vars = """
If BANDWIDTH_USER_ID is defined in the environment,
BANDWIDTH_API_TOKEN and BANDWIDTH_API_SECRET must also be defined
"""

creds_missing_parms = """
Creating Client with arguments requires:
    Client(user_id, token, secret)
where user_id, token, secret are from your Catapult account.
"""

creds_config_file_format = """
The config file:
    <%s>
is either not formatted correctly or is missing values.
If that's the wrong config file, make sure BANDWIDTH_CONFIG_FILE
is set correctly or not set if you're trying to use .bndsdkrc.
"""

creds_config_file_missing = """
The config file specified:
    <%s>
could not be found.
If that's the wrong config file, make sure BANDWIDTH_CONFIG_FILE
is set correctly or not set if you're trying to use .bndsdkrc.
"""

creds_invalid_creds = """
The credentials you provided are not valid.
See the "API Information" section of the "Account" tab in the UI.
to check your credentails.
"""

def Client(*args):
    """
    Proper way to define singleton
    """
    err_msg = None
    user_id, token, secret = (None, None, None)

    global _global_client
    if args:
        if len(args) != 3:
            raise ValueError('{}{}'.format(creds_missing_parms, creds_help))
        else:
            user_id, token, secret = args

    elif 'BANDWIDTH_USER_ID' in os.environ:
        user_id = os.environ.get('BANDWIDTH_USER_ID')
        token = os.environ.get('BANDWIDTH_API_TOKEN')
        secret = os.environ.get('BANDWIDTH_API_SECRET')

        if not all((user_id, token, secret)):
            raise EnvironmentError('{}{}'.format(creds_missing_env_vars, creds_help))

    else:
        # get the credentials from a config file
        config_path = None
        if 'BANDWIDTH_CONFIG_FILE' in os.environ:
            config_path = os.environ.get('BANDWIDTH_CONFIG_FILE')
        else:
            config_path = '.bndsdkrc'

        if file_exists(config_path):
            try:
                user_id, token, secret = get_creds_from_file(config_path)
            except:
                raise ValueError('{}{}'.format(str(creds_config_file_format %config_path), creds_help))
        else:
            # would like to use FileNotFoundError here but that doesn't work in python 2.7
            # raise FileNotFoundError('{}{}'.format(str(creds_config_file_missing %config_path), creds_help))
            raise ValueError('{}{}'.format(str(creds_config_file_missing %config_path), creds_help))

    if err_msg:
        raise ValueError('Credentials were improperly configured, ERROR MESSAGE: \n {}'.format(err_msg))

    _global_client = RESTClientObject(user_id, (token, secret))

    from bandwidth_sdk import Account
    try: 
        acc = Account.get()
    except Exception: 
        raise ValueError('{}{}'.format(creds_invalid_creds, creds_help))

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
