import os
import logging

from six.moves import configparser

import bandwidth_sdk
from .utils import get_creds_from_file, file_exists
from .rest import RESTClientObject


logger = logging.getLogger(__package__)

__all__ = ('_iris_client', 'get_client', 'set_client')

_global_client = None

_HELP_MISSING_IRIS_ENV_VARS = '' \
    'If BANDWIDTH_ACCOUNT_ID is defined in the environment, ' \
    'BANDWIDTH_USERNAME and BANDWIDTH_PASSWORD must also be defined'

_HELP_MISSING_IRIS_PARAMS = '' \
    'Creating iris_client with arguments requires: iris_client(account_id, username, password) ' \
    'where user_id, token, secret are from your Catapult account.'


def _iris_client(account_id='', username='', password=''):
    """
    Initialize the bandwidth sdk client for bandwidth dashboard (aka iris) api calls.  This function will attempt to
    gather credentials from one of several different locations in the
    following order:

    1) Included as arguments when creating the client::

        bandwidth = bandwidth_sdk.iris_client(
            account_id='your-bandwidth-dashboard-account_id',
            username='your-bandwidth-dashboard-username',
            password='your-bandwidth-dashboard-password')

    :type account_id: str
    :param account_id: dashboard account id
    :type username: str
    :param username: dashboard username
    :type password: str
    :param password: dashboard password
    :rtype: RESTClientObject
    :returns: bandwidth rest client
    """

    IRIS_ENDPOINT = 'https://dashboard.bandwidth.com:443/v1.0/'

    if any((account_id, username, password)):
        # at least one keyword argument was specified, require that all are
        # given or raise an error.
        if not all((account_id, username, password)):
            raise ValueError('{}{}'.format(
                _HELP_MISSING_PARAMS, _iris_client.__doc__
            ))

        bandwidth_sdk.account_id = account_id
        bandwidth_sdk.username = username
        bandwidth_sdk.password = password

    else:
        # could not locate configuration variables, raise an error
        raise ValueError('No configuration provided. {}'.format(_iris_client.__doc__))

    if bandwidth_sdk.iris_endpoint is not None:
        _endpoint = bandwidth_sdk.iris_endpoint
    else:
        _endpoint = IRIS_ENDPOINT

    return RESTClientObject(account_id, (username, password), endpoint=_endpoint, xml=True)


def get_iris_client():
    return _iris_client()


def set_client(client):
    """
    Set the global HTTP client for sdk.
    Returns previous client.
    """
    global _global_client
    previous = _global_client
    _global_client = client
    return previous