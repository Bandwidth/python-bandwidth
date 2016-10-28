# flake8: noqa
from .errors import *
from .client import *
from .models import *
from .events import *
from .rest import RESTClientObject, ENDPOINT
from .version import __version__

# credentials for App Platform (aka catapult)
user_id = None
api_token = None
api_secret = None

# credentials for Bandwidth Dashboard (aka iris)
account_id = None
username = None
password = None
iris_endpoint = None