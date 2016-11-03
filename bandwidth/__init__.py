SUPPORTED_CLIENTS = ['catapult']

client_classes = {}

def client(client_name, *args, **kwargs):
    global client_classes
    name = client_name.lower()

    if name not in SUPPORTED_CLIENTS:
        client_names = map(lambda k: '"%s"' % k, SUPPORTED_CLIENTS)
        raise Exception('Invalid client name "%s". Valid values are %s' % [client_name, ', '.join(client_names)])
    client_class = client_classes.get(name)
    if client_class == None:
        client_class = getattr(__import__('bandwidth.%s' % name), name).Client
        client_classes[name] = client_class
    return client_class(*args, **kwargs)
