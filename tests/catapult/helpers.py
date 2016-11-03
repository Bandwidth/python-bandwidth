from bandwidth.catapult import Client

def get_client():
    return Client('userId', 'apiToken', 'apiSecret')
