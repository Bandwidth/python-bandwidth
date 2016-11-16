_SUPPORTED_CLIENTS = ['catapult']

_client_classes = {}


def client(client_name, *args, **kwargs):
    """
    Initialize the bandwidth sdk client.
    :type client_name: str
    :param client_name: required client name (catapult or iris only)
    :type user_id: str
    :param user_id: catapult user id (for 'catapult' only)
    :type api_token: str
    :param api_token: catapult api token (for 'catapult' only)
    :type api_secret: str
    :param api_secret: catapult api secret (for 'catapult' only)
    :type api_endpoint: str
    :param api_endpoint: catapult api endpoint (optional, default value is https://api.catapult.inetwork.com,
    for 'catapult' only)
    :type api_version: str
    :param api_version: catapult api version (optional, default value is v1, for 'catapult' only)

    :rtype: bandwidth.catapult.Client
    :returns: bandwidth client

    :Example:
    api = bandwidth.client('catapult', 'YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
    """
    global _client_classes
    name = client_name.lower()
    if name not in _SUPPORTED_CLIENTS:
        client_names = ', '.join(map(lambda k: '"%s"' % k, _SUPPORTED_CLIENTS))
        raise ValueError('Invalid client name "%s". Valid values are %s' % (client_name, client_names))
    client_class = _client_classes.get(name)
    if client_class is None:
        client_class = getattr(__import__('bandwidth.%s' % name), name).Client
        _client_classes[name] = client_class
    return client_class(*args, **kwargs)
