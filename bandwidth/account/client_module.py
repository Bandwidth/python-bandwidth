import requests
import six
import urllib
import json
import itertools
from bandwidth.voice.lazy_enumerable import get_lazy_enumerator
from bandwidth.convert_camel import convert_object_to_snake_case
from bandwidth.voice.decorators import play_audio
from bandwidth.version import __version__ as version

from .api_exception_module import BandwidthAccountAPIException

quote = urllib.parse.quote if six.PY3 else urllib.quote
lazy_map = map if six.PY3 else itertools.imap


class Client:

    """
    Account API client
    """

    def __init__(self, user_id=None, api_token=None, api_secret=None, **other_options):
        """
        Initialize the catatpult client.
        :type user_id: str
        :param user_id: catapult user id
        :type api_token: str
        :param api_token: catapult api token
        :type api_secret: str
        :param api_secret: catapult api secret
        :type api_endpoint: str
        :param api_endpoint: catapult api endpoint (optional, default value is https://api.catapult.inetwork.com)
        :type api_version: str
        :param api_version: catapult api version (optional, default value is v1)

        :rtype: bandwidth.catapult.Client
        :returns: bandwidth client

        Init the catapult client::

            api = bandwidth.catapult.Client('YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
            # or
            api = bandwidth.client('catapult', 'YOUR_USER_ID', 'YOUR_API_TOKEN', 'YOUR_API_SECRET')
        """
        if not all((user_id, api_token, api_secret)):
            raise ValueError('Arguments user_id, api_token and api_secret are required. '
                             'Use bandwidth.client("catapult", "YOUR-USER-ID", "YOUR-API-TOKEN", "YOUR-API-SECRET")')
        self.user_id = user_id
        self.api_endpoint = other_options.get(
            'api_endpoint', 'https://api.catapult.inetwork.com')
        self.api_version = other_options.get('api_version', 'v1')
        self.auth = (api_token, api_secret)

    def _request(self, method, url, *args, **kwargs):
        user_agent = 'PythonSDK_' + version
        headers = kwargs.pop('headers', None)
        if headers:
            headers['User-Agent'] = user_agent
        else:
            headers = {
                'User-Agent': user_agent
            }
        if url.startswith('/'):
            # relative url
            url = '%s/%s%s' % (self.api_endpoint, self.api_version, url)
        return requests.request(method, url, auth=self.auth, headers=headers, *args, **kwargs)

    def _check_response(self, response):
        if response.status_code >= 400:
            if response.headers.get('content-type') is not None and \
                    response.headers.get('content-type').startswith("application/json"):
                data = response.json()
                raise BandwidthAccountAPIException(
                    response.status_code, data['message'], code=data.get('code'))
            else:
                raise BandwidthAccountAPIException(
                    response.status_code, response.content.decode('utf-8')[:79])

    def _make_request(self, method, url, *args, **kwargs):
        response = self._request(method, url, *args, **kwargs)
        self._check_response(response)
        data = None
        id = None
        if response.headers.get('content-type') is not None and \
                response.headers.get('content-type').startswith("application/json"):
            data = convert_object_to_snake_case(response.json())
        location = response.headers.get('location')
        if location is not None:
            id = location.split('/')[-1]
        return (data, response, id)

    """
    Account API
    """

    def get_account(self):
        """
        Get an Account object

        :rtype: dict
        :returns: account data

        Example::

            data = api.get_account()
        """
        return self._make_request('get', '/users/%s/account' % self.user_id)[0]

    def list_account_transactions(self,
                                  max_items=None,
                                  to_date=None,
                                  from_date=None,
                                  trans_type=None,
                                  size=None,
                                  number=None,
                                  **kwargs):
        """
        Get the transactions from the user's account

        :param str max_items: Limit the number of transactions that will be returned.
        :param str to_date: Return only transactions that are newer than the parameter. \
            Format: "yyyy-MM-dd'T'HH:mm:ssZ"
        :param str from_date: Return only transactions that are older than the parameter. \
            Format: "yyyy-MM-dd'T'HH:mm:ssZ"
        :param str trans_type: Return only transactions that are this type.
        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items. \
            If no value is specified the default value is 25. (Maximum value 1000)
        :param str number: Search transactions by phone number
        :rtype: types.GeneratorType
        :returns: list of transactions

        Example: Get transactions::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions by date::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions filtering by date::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions limiting result::

            list = api.get_account_transactions(type = 'charge')

        Example: Get transactions of payment type::

            list = api.get_account_transactions(type = 'charge')
        """
        kwargs["maxItems"] = max_items
        kwargs["toDate"] = to_date
        kwargs["fromDate"] = from_date
        kwargs["type"] = trans_type
        kwargs["size"] = size
        kwargs["number"] = number

        path = '/users/%s/account/transactions' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def list_applications(self, size=None, **kwargs):
        """
        Get a list of user's applications

        :param int size: Used for pagination to indicate the size of each page requested for querying a list
                of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of applications

        Example: Fetch and print all applications::

            apps = api.list_applications()
            print(list(apps))

        Example: Iterate over all applications to find specific name::

            apps = api.list_applications(size=20)

            app_name = ""
            while app_name != "MyAppName":
                my_app = next(apps)
                app_name = my_app["name"]

            print(my_app)


            ## {   'auto_answer': True,
            ##     'callback_http_method': 'get',
            ##     'id': 'a-asdf',
            ##     'incoming_call_url': 'https://test.com/callcallback/',
            ##     'incoming_message_url': 'https://test.com/msgcallback/',
            ##     'name': 'MyAppName'
            ## }

        """
        kwargs["size"] = size
        path = '/users/%s/applications' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_application(self,
                           name,
                           incoming_call_url=None,
                           incoming_call_url_callback_timeout=None,
                           incoming_call_fallback_url=None,
                           incoming_message_url=None,
                           incoming_message_url_callback_timeout=None,
                           incoming_message_fallback_url=None,
                           callback_http_method=None,
                           auto_answer=None,
                           **kwargs):
        """
        Creates an application that can handle calls and messages for one of your phone number.

        :param str name: A name you choose for this application (required).
        :param str incoming_call_url: A URL where call events will be sent for an inbound call.
        :param str incoming_call_url_callback_timeout: Determine how long should the platform wait for
            inconmingCallUrl's response before timing out in milliseconds.
        :param str incoming_call_fallback_url: The URL used to send the callback event
            if the request to incomingCallUrl fails.
        :param str incoming_message_url: A URL where message events will be sent for an inbound SMS message
        :param str incoming_message_url_callback_timeout: Determine how long should the platform wait for
            incomingMessageUrl's response before timing out in milliseconds.
        :param str incoming_message_fallback_url: The URL used to send the callback event if the request to
            incomingMessageUrl fails.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.\
            (If not set the default is HTTP POST)
        :param str auto_answer: Determines whether or not an incoming call should be automatically answered. \
            Default value is 'true'.

        :rtype: str
        :returns: id of created application

        Example: Create Application::

            my_app_id = api.create_application( name                 = "MyFirstApp",
                                                incoming_call_url    = "http://callback.com/calls",
                                                incoming_message_url  = "http://callback.com/messages",
                                                callback_http_method = "GET")

            print(my_app_id)
            ## a-1232asf123

            my_app = api.get_application(my_app_id)
            print(my_app)
            ## {   'auto_answer'        : True,
            ##     'callback_http_method': 'get',
            ##     'id'                : 'a-1232asf123',
            ##     'incoming_call_url'   : 'http://callback.com/calls',
            ##     'incoming_message_url': 'http://callback.com/messages',
            ##     'incoming_sms_url'    : 'http://callback.com/messages',
            ##     'name'              : 'MyFirstApp2'
            ## }

            print(my_app["id"])
            ## a-1232asf123

        """
        kwargs["name"] = name
        kwargs["incomingCallUrl"] = incoming_call_url
        kwargs[
            "incomingCallUrlCallbackTimeout"] = incoming_call_url_callback_timeout
        kwargs["incomingCallFallbackUrl"] = incoming_call_fallback_url
        kwargs["incomingMessageUrl"] = incoming_message_url
        kwargs[
            "incomingMessageUrlCallbackTimeout"] = incoming_message_url_callback_timeout
        kwargs["incomingMessageFallbackUrl"] = incoming_message_fallback_url
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["autoAnswer"] = auto_answer

        return self._make_request('post', '/users/%s/applications' % self.user_id, json=kwargs)[2]

    def get_application(self, app_id):
        """
        Gets information about an application

        :type app_id: str
        :param app_id: id of an application

        :rtype: dict
        :returns: application information

        Example: Fetch single application::

            my_app = api.get_application(my_app_id)
            print(my_app)
            ## {   'auto_answer': True,
            ##     'callback_http_method': 'get',
            ##     'id': 'a-1232asf123',
            ##     'incoming_call_url': 'http://callback.com/calls',
            ##     'incoming_message_url': 'http://callback.com/messages',
            ##     'incoming_sms_url': 'http://callback.com/messages',
            ##     'name': 'MyFirstApp2'
            ## }

            print(my_app["id"])
            ## a-1232asf123
        """
        return self._make_request('get', '/users/%s/applications/%s' % (self.user_id, app_id))[0]

    def update_application(self, app_id,
                           name=None,
                           incoming_call_url=None,
                           incoming_call_url_callback_timeout=None,
                           incoming_call_fallback_url=None,
                           incoming_message_url=None,
                           incoming_message_url_callback_timeout=None,
                           incoming_message_fallback_url=None,
                           callback_http_method=None,
                           auto_answer=None,
                           **kwargs):
        """
        Updates an application that can handle calls and messages for one of your phone number.

        :param str app_id: The Id of the application to upate (a-123)
        :param str name: A name you choose for this application (required).
        :param str incoming_call_url: A URL where call events will be sent for an inbound call.
        :param str incoming_call_url_callback_timeout: Determine how long should the platform wait for
            inconmingCallUrl's response before timing out in milliseconds.
        :param str incoming_call_fallback_url: The URL used to send the callback event
            if the request to incomingCallUrl fails.
        :param str incoming_message_url: A URL where message events will be sent for an inbound SMS message
        :param str incoming_message_url_callback_timeout: Determine how long should the platform wait for
            incomingMessageUrl's response before timing out in milliseconds.
        :param str incoming_message_fallback_url: The URL used to send the callback event if the request to
            incomingMessageUrl fails.
        :param str callback_http_method: Determine if the callback event should be sent via HTTP GET or HTTP POST.\
            (If not set the default is HTTP POST)
        :param str auto_answer: Determines whether or not an incoming call should be automatically answered. \
            Default value is 'true'.

        :rtype: str
        :returns: id of created application

        Example: Update Existing Application::

            my_app_id = api.create_application( name                 = "MyFirstApp",
                                                incoming_call_url    = "http://callback.com/calls",
                                                incoming_message_url  = "http://callback.com/messages",
                                                callback_http_method = "GET")

            print(my_app_id)
            ## a-1232asf123

            my_app = api.get_application(my_app_id)
            print(my_app)
            {   'auto_answer'        : True,
                'callbackHttpMethod': 'get',
                'id'                : 'a-1232asf123',
                'incomingCallUrl'   : 'http://callback.com/calls',
                'incomingMessageUrl': 'http://callback.com/messages',
                'incomingSmsUrl'    : 'http://callback.com/messages',
                'name'              : 'MyFirstApp'
            }

            api.update_application(my_app_id, name = "My Updated App")

            my_app = api.get_application(my_app_id)
            print(my_app)
            {   'autoAnswer'        : True,
                'callbackHttpMethod': 'get',
                'id'                : 'a-1232asf123',
                'incomingCallUrl'   : 'http://callback.com/calls',
                'incomingMessageUrl': 'http://callback.com/messages',
                'incomingSmsUrl'    : 'http://callback.com/messages',
                'name'              : 'My Updated App'
            }

        """
        kwargs["name"] = name
        kwargs["incomingCallUrl"] = incoming_call_url
        kwargs[
            "incomingCallUrlCallbackTimeout"] = incoming_call_url_callback_timeout
        kwargs["incomingCallFallbackUrl"] = incoming_call_fallback_url
        kwargs["incomingMessageUrl"] = incoming_message_url
        kwargs[
            "incomingMessageUrlCallbackTimeout"] = incoming_message_url_callback_timeout
        kwargs["incomingMessageFallbackUrl"] = incoming_message_fallback_url
        kwargs["callbackHttpMethod"] = callback_http_method
        kwargs["autoAnswer"] = auto_answer

        self._make_request('post', '/users/%s/applications/%s' % (self.user_id, app_id), json=kwargs)

    def delete_application(self, app_id):
        """
        Remove an application

        :type app_id: str
        :param app_id: id of an application

        Example: Delete single application::

            api.delete_application('a-appId')

            try :
                api.get_application('a-appId')
            except CatapultException as err:
                print(err.message)
            ## The application a-appId could not be found

        """
        self._make_request(
            'delete', '/users/%s/applications/%s' % (self.user_id, app_id))

    def search_available_local_numbers(self,
                                       city=None,
                                       state=None,
                                       zip_code=None,
                                       area_code=None,
                                       local_number=None,
                                       in_local_calling_area=None,
                                       quantity=None,
                                       pattern=None,
                                       **kwargs):
        """
        Searches for available local or toll free numbers.

        :param str city: A city name
        :param str state: A two-letter US state abbreviation
        :param str zip_code: A 5-digit US ZIP code
        :param str area_code: A 3-digit telephone area code
        :param str local_number: It is defined as the first digits of a telephone number inside an area code for
            filtering the results. It must have at least 3 digits and the areaCode field must be filled.
        :param str in_local_calling_area: Boolean value to indicate that the search for available numbers
            must consider overlayed areas.
        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)
        :param str pattern: A number pattern that may include letters, digits, and the wildcard characters

        :rtype: list
        :returns: list of numbers

        Example: Search for 3 910 numbers::

            numbers = api.search_available_local_numbers(area_code = '910', quantity = 3)

            print(numbers)

            ## [   {   'city'          : 'WILMINGTON',
            ##         'national_number': '(910) 444-0230',
            ##         'number'        : '+19104440230',
            ##         'price'         : '0.35',
            ##         'rate_center'    : 'WILMINGTON',
            ##         'state'         : 'NC'},
            ##     {   'city'          : 'WILMINGTON',
            ##         'national_number': '(910) 444-0263',
            ##         'number'        : '+19104440263',
            ##         'price'         : '0.35',
            ##         'rate_center'    : 'WILMINGTON',
            ##         'state'         : 'NC'},
            ##     {   'city'          : 'WILMINGTON',
            ##         'national_number': '(910) 444-0268',
            ##         'number'        : '+19104440268',
            ##         'price'         : '0.35',
            ##         'rate_center'    : 'WILMINGTON',
            ##         'state'         : 'NC'}
            ## ]

            print(numbers[0]["number"])
            ## +19104440230

        """
        kwargs["city"] = city
        kwargs["state"] = state
        kwargs["zip"] = zip_code
        kwargs["areaCode"] = area_code
        kwargs["localNumber"] = local_number
        kwargs["inLocalCallingArea"] = in_local_calling_area
        kwargs["quantity"] = quantity
        kwargs["pattern"] = pattern
        return self._make_request('get', '/availableNumbers/local', params=kwargs)[0]

    def search_available_toll_free_numbers(self, quantity=None, pattern=None, **kwargs):
        """
        Searches for available local or toll free numbers.

        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)
        :param str pattern:  A number pattern that may include letters, digits, and the wildcard characters

        :rtype: list
        :returns: list of numbers

        Example: Search for 3 toll free numbers with pattern 456::

            numbers = api.search_available_toll_free_numbers(pattern = '*456', quantity = 3)

            print(numbers)

            ## [   {   'national_number': '(844) 489-0456',
            ##         'number'        : '+18444890456',
            ##         'pattern_match'  : '           456',
            ##         'price'         : '0.75'},
            ##     {   'national_number': '(844) 498-2456',
            ##         'number'        : '+18444982456',
            ##         'pattern_match'  : '           456',
            ##         'price'         : '0.75'},
            ##     {   'national_number': '(844) 509-4566',
            ##         'number'        : '+18445094566',
            ##         'pattern_match'  : '          456 ',
            ##         'price'         : '0.75'}]

            print(numbers[0]["number"])
            ## +18444890456


        """
        kwargs["quantity"] = quantity
        kwargs["pattern"] = pattern
        return self._make_request('get', '/availableNumbers/tollFree', params=kwargs)[0]

    def search_and_order_local_numbers(self,
                                       city=None,
                                       state=None,
                                       zip_code=None,
                                       area_code=None,
                                       local_number=None,
                                       in_local_calling_area=None,
                                       quantity=None,
                                       **kwargs):
        """
        Searches and orders for available local numbers.

        :param str city: A city name
        :param str state: A two-letter US state abbreviation
        :param str zip_code: A 5-digit US ZIP code
        :param str area_code: A 3-digit telephone area code
        :param str local_number: It is defined as the first digits of a telephone number inside an area code for
            filtering the results. It must have at least 3 digits and the areaCode field must be filled.
        :param str in_local_calling_area: Boolean value to indicate that the search for available numbers
            must consider overlayed areas.
        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)

        :rtype: list
        :returns: list of ordered numbers

        Example: Search _and_ order a single number::

            ordered_numbers = api.search_and_order_available_numbers(zip = '27606', quantity = 1)

            print(ordered_numbers)

            ## [   {   'city'          : 'RALEIGH',
            ##         'id'            : 'n-abc',
            ##         'location'      : 'https://api.catapult.inetwork.com/v1/users/u-12/phoneNumbers/n-abc',
            ##         'national_number': '(919) 222-4444',
            ##         'number'        : '+19192224444',
            ##         'price'         : '0.35',
            ##         'state'         : 'NC'}]


        """
        kwargs["city"] = city
        kwargs["state"] = state
        kwargs["zip"] = zip_code
        kwargs["areaCode"] = area_code
        kwargs["localNumber"] = local_number
        kwargs["inLocalCallingArea"] = in_local_calling_area
        kwargs["quantity"] = quantity
        number_list = self._make_request(
            'post', '/availableNumbers/local', params=kwargs)[0]
        for item in number_list:
            item['id'] = item.get('location', '').split('/')[-1]
        return number_list

    def search_and_order_toll_free_numbers(self, quantity, **kwargs):
        """
        Searches for available local or toll free numbers.

        Query parameters for toll free numbers
        :param int quantity: The maximum number of numbers to return (default 10, maximum 5000)

        :rtype: list
        :returns: list of numbers

        Example: Search then order a single toll-free number::

            numbers = api.search_and_order_toll_free_numbers(quantity = 1)

            print(numbers)

            ## [   {   'location'      : 'https://api.catapult.inetwork.com/v1/users/u-123/phoneNumbers/n-abc',
            ##         'national_number': '(844) 484-1048',
            ##         'number'        : '+18444841048',
            ##         'price'         : '0.75'}]

            print(numbers[0]["number"])
            ## +18444841048

        """
        kwargs["quantity"] = quantity
        list = self._make_request(
            'post', '/availableNumbers/tollFree', params=kwargs)[0]
        for item in list:
            item['id'] = item.get('location', '').split('/')[-1]
        return list

    def list_domains(self, size=None, **kwargs):
        """
        Get a list of domains

        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items. \
            If no value is specified the default value is 25. (Maximum value 100)
        :rtype: types.GeneratorType
        :returns: list of domains

        Example: Fetch domains and print::

            domain_list = api.list_domains(size=10)
            print(list(domain_list))

            ## [{   'endpoints_url': 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/endpoints',
            ##     'id'           : 'rd-domainId',
            ##     'name'         : 'siplearn1'},
            ## {   'endpoints_url' : 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/endpoints',
            ##     'id'           : 'rd-domainId2',
            ##     'name'         : 'siplearn2'}]

        Example: Search for domain based on name::

            domain_list = api.list_domains(size=100)

            domain_name = ''

            while domain_name != 'My Prod Site':
                my_domain = next(domain_list)
                domain_name = my_domain['name']

            print(my_domain)
            ## {   'description' : 'Python Docs Example',
            ##     'endpoints_url': 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/rd-domainId/endpoints',
            ##     'id'          : 'rd-domainId',
            ##     'name'        : 'My Prod Site'}


        """
        kwargs['size'] = size
        path = '/users/%s/domains' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_domain(self, name, description=None, **kwargs):
        """
        Create a domain

        :param str name: The name is a unique URI to be used in DNS lookups
        :param str description: String to describe the domain

        :rtype: str
        :returns: id of created domain

        Example: Create Domain::

            domain_id = api.create_domain(name='qwerty', description='Python Docs Example')

            print(domain_id)
            # rd-domainId
        """
        kwargs['name'] = name
        kwargs['description'] = description
        return self._make_request('post', '/users/%s/domains' % self.user_id, json=kwargs)[2]

    def get_domain(self, domain_id):
        """
        Get information about a domain

        :type domain_id: str
        :param domain_id: id of the domain

        :rtype: dict
        :returns: domain information

        Example: Create then fetch domain::

            domain_id = api.create_domain(name='qwerty', description='Python Docs Example')

            print(domain_id)
            # rd-domainId

            my_domain = api.get_domain(domain_id)

            print(my_domain)
            ## {   'description' : 'Python Docs Example',
            ##     'endpoints_url': 'https://api.catapult.inetwork.com/v1/users/u-abc123/domains/rd-domainId/endpoints',
            ##     'id'          : 'rd-domainId',
            ##     'name'        : 'qwerty'}
        """
        return self._make_request('get', '/users/%s/domains/%s' % (self.user_id, domain_id))[0]

    def delete_domain(self, domain_id):
        """
        Delete a domain

        :type domain_id: str
        :param domain_id: id of a domain

        Example: Delete domain 'domainId'::

            api.delete_domain('domainId')
        """
        self._make_request('delete', '/users/%s/domains/%s' %
                           (self.user_id, domain_id))

    def list_domain_endpoints(self, domain_id, size=None, **kwargs):
        """
        Get a list of domain's endpoints

        :type domain_id: str
        :param domain_id: id of a domain
        :param int size: Used for pagination to indicate the size of each page requested for querying a list of items.\
            If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of endpoints

        Example: List and iterate over::

            endpoint_list = api.list_domain_endpoints('rd-domainId', size=1000)

            for endpoint in endpoint_list:
                print(endpoint['id'])
            ##re-endpointId1
            ##re-endpointId2

        Example: List and print all::

            endpoint_list = api.list_domain_endpoints('rd-domainId', size=1000)

            print(list(endpoint_list))

            ## [
            ##     {
            ##         'application_id':'a-appId',
            ##         'credentials'  :{
            ##             'realm'    :'creds.bwapp.bwsip.io',
            ##             'username' :'user1'
            ##         },
            ##         'description'  :"Your SIP Account",
            ##         'domain_id'     :'rd-domainId',
            ##         'enabled'      :True,
            ##         'id'           :'re-endpointId1',
            ##         'name'         :'User1_endpoint',
            ##         'sip_uri'       :'sip:user1@creds.bwapp.bwsip.io'
            ##     },
            ##     {
            ##         'application_id':'a-appId',
            ##         'credentials'  :{
            ##             'realm'    :'creds1.bwapp.bwsip.io',
            ##             'username' :'user2'
            ##         },
            ##         'description'  :"Your SIP Account",
            ##         'domain_id'     :'rd-domainId',
            ##         'enabled'      :True,
            ##         'id'           :'re-endpointId2',
            ##         'name'         :'User2_endpoint',
            ##         'sip_uri'       :'sip:user2@creds.bwapp.bwsip.io'
            ##     }
            ## ]

        """
        kwargs['size'] = size
        path = '/users/%s/domains/%s/endpoints' % (self.user_id, domain_id)
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def create_domain_endpoint(
            self,
            domain_id,
            name,
            password,
            description=None,
            application_id=None,
            enabled=True,
            **kwargs):
        """
        Create a domain endpoint

        :param str domain_id: id of a domain
        :param str name: The name of endpoint
        :param str description: String to describe the endpoint
        :param str application_id: Id of application which will handle calls and messages of this endpoint
        :param bool enabled: When set to true, SIP clients can register as this device to receive and make calls. \
            When set to false, registration, inbound, and outbound calling will not succeed.
        :param str password: Password of created SIP account

        :rtype: str
        :returns: id of endpoint

        Example: Create Endpoint on Domain 'rd-domainId'::

            endpoint_id = api.create_domain_endpoint('rd-domainId',
                                                     endpoint_name='User3_endpoint',
                                                     password='AtLeast6Chars')
            print(endpoint_id)
            # re-endpointId3

            my_endpoint = api.get_domain_endpoint(endpoint_id)
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'User3_endpoint'
            ##     },
            ##     'domain_id'    :'rd-domainId',
            ##     'enabled'     :True,
            ##     'id'          :'re-endpointId3',
            ##     'name'        :'User3_endpoint',
            ##     'sip_uri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }

        """
        kwargs['name'] = name
        kwargs['description'] = description
        kwargs['applicationId'] = application_id
        kwargs['enabled'] = enabled
        kwargs['credentials'] = dict(password=password)
        return self._make_request('post', '/users/%s/domains/%s/endpoints' % (self.user_id, domain_id), json=kwargs)[2]

    def get_domain_endpoint(self, domain_id, endpoint_id):
        """
        Get information about an endpoint

        :type domain_id: str
        :param domain_id: id of a domain

        :type endpoint_id: str
        :param endpoint_id: id of a endpoint

        :rtype: dict
        :returns: call information

        Example: Create Endpoint on Domain 'rd-domainId' then fetch the endpoint::

            endpoint_id = api.create_domain_endpoint('rd-domainId',
                                                     endpoint_name='User3_endpoint',
                                                     password='AtLeast6Chars')
            print(endpoint_id)
            # re-endpointId3

            my_endpoint = api.get_domain_endpoint(endpoint_id)
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'User3_endpoint'
            ##     },
            ##     'domain_id'    :'rd-domainId',
            ##     'enabled'     :True,
            ##     'id'          :'re-endpointId3',
            ##     'name'        :'User3_endpoint',
            ##     'sip_uri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }
        """
        return self._make_request('get', '/users/%s/domains/%s/endpoints/%s' % (self.user_id,
                                                                                domain_id, endpoint_id))[0]

    def update_domain_endpoint(self,
                               domain_id,
                               endpoint_id,
                               password=None,
                               description=None,
                               application_id=None,
                               enabled=None,
                               **kwargs):
        """
        Update information about an endpoint

        :param str domain_id: id of a domain
        :param str endpoint_id: id of a endpoint
        :param str description: String to describe the endpoint
        :param str application_id: Id of application which will handle calls and messages of this endpoint
        :param bool enabled: When set to true, SIP clients can register as this device to receive and make calls. \
            When set to false, registration, inbound, and outbound calling will not succeed.
        :param str password: Password of created SIP account

        Example: Update password and disable the endpoint::


            my_endpoint = api.get_domain_endpoint('rd-domainId', 're-endpointId')
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'user5'
            ##     },
            ##     'domain_id'    :'rd-domainId',
            ##     'enabled'     :True,
            ##     'id'          :'re-endpointId',
            ##     'name'        :'user3',
            ##     'sip_uri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }

            api.update_domain_endpoint('rd-domainId', 're-endpointId', enabled=False, password='abc123')
            my_endpoint = api.get_domain_endpoint('rd-domainId', 're-endpointId')
            print(my_endpoint)

            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'user5'
            ##     },
            ##     'domain_id'    :'rd-domainId',
            ##     'enabled'     :False,
            ##     'id'          :'re-endpointId',
            ##     'name'        :'user3',
            ##     'sip_uri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }
        """

        kwargs['description'] = description
        kwargs['applicationId'] = application_id
        kwargs['enabled'] = enabled
        kwargs['credentials'] = dict(password=password)

        self._make_request('post', '/users/%s/domains/%s/endpoints/%s' %
                           (self.user_id, domain_id, endpoint_id), json=kwargs)

    def delete_domain_endpoint(self, domain_id, endpoint_id):
        """
        Remove an endpoint

        :param str domain_id: id of a domain
        :param str endpoint_id: id of a endpoint

        Example: Delete and try to fetch endpoint::

            my_endpoint = api.get_domain_endpoint('rd-domainId', 're-endpointId')
            print(my_endpoint)
            ## {
            ##     'credentials' :{
            ##         'realm'   :'qwerty.bwapp.bwsip.io',
            ##         'username':'user5'
            ##     },
            ##     'domain_id'    :'rd-domainId',
            ##     'enabled'     :False,
            ##     'id'          :'re-endpointId3ndpointId',
            ##     'name'        :'user3',
            ##     'sip_uri'      :'sip:user5@qwerty.bwapp.bwsip.io'
            ## }
            api.delete_domain_endpoint(d, e)

            try:
                my_endpoint = api.get_domain_endpoint(d, e)
            except Exception as e:
                print(e)
            ## CatapultException(404, "The endpoint 're-endpointId' could not be found")

        """
        self._make_request(
            'delete', '/users/%s/domains/%s/endpoints/%s' % (self.user_id, domain_id, endpoint_id))

    def create_domain_endpoint_auth_token(self, domain_id, endpoint_id, expires=3600, **kwargs):
        """
        Create auth token for an endpoint

        :param str domain_id: id of a domain
        :param str endpoint_id: id of a endpoint
        :param int expires: Duration of valid token.

        Example: Create token::

            token = api.create_domain_endpoint_auth_token('domainId', 'endpointId', 5000)
        """
        kwargs['expires'] = expires
        path = '/users/%s/domains/%s/endpoints/%s/tokens' % (
            self.user_id, domain_id, endpoint_id)
        return self._make_request('post', path, json=kwargs)[0]

    def list_errors(self, size=None, **kwargs):
        """
        Get a list of errors

        :param int size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of calls

        Example: List all errors::

            error_list = api.list_errors()

            print(list(error_list))

            # [{
            #     'category':'unavailable',
            #     'code'    :'number-allocator-unavailable',
            #     'details':[
            #         {
            #             'id'   :'ued-eh3zn3dxgiin4y',
            #             'name' :'requestPath',
            #             'value':'availableNumbers/local'
            #         },
            #         {
            #             'id'   :'ued-3fsdqiq',
            #             'name' :'remoteAddress',
            #             'value':'216.82.234.65'
            #         },
            #         {
            #             'id'   :'ued-2r4t47bwi',
            #             'name' :'requestMethod',
            #             'value':'GET'
            #         }
            #     ],
            #     'id'     :'ue-upvfv53xzca',
            #     'message':'Cannot connect to the number allocator',
            #     'time'   :'2016-03-28T18:31:33Z'
            # },
            # {
            #     'category':'unavailable',
            #     'code':'number-allocator-unavailable',
            #     'details':[
            #         {
            #             'id':'ued-kntwx7vyotalci',
            #             'name':'requestPath',
            #             'value':'availableNumbers/local'
            #         },
            #         {
            #             'id':'ued-b24vxpfskldq',
            #             'name':'remoteAddress',
            #             'value':'216.82.234.65'
            #         },
            #         {
            #             'id':'ued-ww5rcgl7zm2ydi',
            #             'name':'requestMethod',
            #             'value':'GET'
            #         }
            #     ],
            #     'id':'ue-pok2vg7kyuzaqq',
            #     'message':'Cannot connect to the number allocator',
            #     'time':'2016-03-28T18:31:33Z'
            # }]
        """
        kwargs['size'] = size
        path = '/users/%s/errors' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def get_error(self, error_id):
        """
        Get information about an error

        :type error_id: str
        :param id: id of an error
        :rtype: dict
        :returns: error information

        Example: Get information of specific error::

            error = api.get_error('ue-errorId')
            print(error)

            ## {
            ##     'category':'unavailable',
            ##     'code'    :'number-allocator-unavailable',
            ##     'details' :[
            ##         {
            ##            'id'      :'ued-kntvyotalci',
            ##            'name'    :'requestPath',
            ##            'value'   :'availableNumbers/local'
            ##         },
            ##         {
            ##            'id'      :'ued-b2dq',
            ##            'name'    :'remoteAddress',
            ##            'value'   :'216.82.234.65'
            ##         },
            ##         {
            ##            'id'      :'ued-wzm2ydi',
            ##            'name'    :'requestMethod',
            ##            'value'   :'GET'
            ##         }
            ##     ],
            ##     'id'      :'ue-errorId',
            ##     'message' :'Cannot connect to the number allocator',
            ##     'time'    :'2016-03-28T18:31:33Z'
            ## }
        """
        return self._make_request('get', '/users/%s/errors/%s' % (self.user_id, error_id))[0]

    def list_media_files(self):
        """
        Gets a list of user's media files.

        :rtype: types.GeneratorType
        :returns: list of media files

        Example: list media files and save any with the name `dog` in file name::

            media_list = api.list_media_files()
            for media in media_list:
                if 'dog' in media['media_name'].lower():
                    stream, content_type = api.download_media_file(media['media_name'])
                    with io.open(media['media_name'], 'wb') as file:
                        file.write(stream.read())

        """
        path = '/users/%s/media' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path))

    def upload_media_file(self, media_name, content=None, content_type='application/octet-stream', file_path=None):
        """
        Upload a file

        :type media_name: str
        :param media_name: name of file on bandwidth server

        :type content: str|buffer|bytearray|stream|file
        :param content: content of file to upload (file object, string or buffer).
            Don't use together with file_path

        :type content_type: str
        :param content_type: mime type of file

        :type file_path: str
        :param file_path: path to file to upload. Don't use together with content

        Example: Upload text file::

            api.upload_media_file('file1.txt', 'content of file', 'text/plain')

            # with file path
            api.upload_media_file('file1.txt', file_path='/path/to/file1.txt')

        """
        is_file_path = False
        if file_path is not None and content is None:
            content = open(file_path, 'rb')
            is_file_path = True
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        try:
            return self._make_request('put', path, data=content, headers={'content-type': content_type})
        finally:
            if is_file_path:
                content.close()

    def download_media_file(self, media_name):
        """
        Download a file

        :type media_name: str
        :param media_name: name of file on bandwidth server

        :rtype (stream, str)
        :returns stream to file to download and mime type

        Example: list media files and save any with the name `dog` in file name::

            media_list = api.get_media_files()
            for media in media_list:
                if 'dog' in media['media_name'].lower():
                    stream, content_type = api.download_media_file(media['media_name'])
                    with io.open(media['media_name'], 'wb') as file:
                        file.write(stream.read())
        """
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        response = self._request('get', path, stream=True)
        response.raise_for_status()
        return response.raw, response.headers['content-type']

    def delete_media_file(self, media_name):
        """
        Remove a file from the server

        :type media_name: str
        :param media_name: name of file on bandwidth server

        Example: Delete a file from server::

            api.delete_media_file('file1.txt')
        """
        path = '/users/%s/media/%s' % (self.user_id, quote(media_name))
        self._make_request('delete', path)

    def get_number_info(self, number):
        """
        Gets CNAM information about phone number

        :type number: str
        :param number: phone number to get information

        :rtype: dict
        :returns: CNAM information

        Example: Get Number information::

            data = api.get_number_info('+1234567890')
            print(data)
            ## {   'created': '2017-02-10T09:11:50Z',
            ##     'name'       : 'RALEIGH, NC',
            ##     'number'     : '+1234567890',
            ##     'updated'    : '2017-02-10T09:11:50Z'}

        """
        path = '/phoneNumbers/numberInfo/%s' % quote(number)
        return self._make_request('get', path)[0]

    def list_phone_numbers(
            self,
            application_id=None,
            state=None,
            name=None,
            city=None,
            number_state=None,
            size=None,
            **kwargs):
        """
        Get a list of user's phone numbers

        :param str application_id: Used to filter the retrieved list of numbers by an associated application ID.
        :param str state: Used to filter the retrieved list of numbers allocated for the authenticated
            user by a US state.
        :param str name: Used to filter the retrieved list of numbers allocated for the authenticated
            user by it's name.
        :param str city: Used to filter the retrieved list of numbers allocated for the authenticated user
            by it's city.
        :param str number_state: Used to filter the retrieved list of numbers allocated for the authenticated user
            by the number state.
        :param str size: Used for pagination to indicate the size of each page requested for querying a list
            of items. If no value is specified the default value is 25. (Maximum value 1000)
        :rtype: types.GeneratorType
        :returns: list of phone numbers

        Example: List all phone numbers::

            number_list = api.list_phone_numbers(size=1000)
            print(list(number_list))
            ## [
            ##     {
            ##         'city'          :'RALEIGH',
            ##         'created_time'   :'2017-02-06T18:41:37Z',
            ##         'id'            :'n-n123',
            ##         'name'          :'demo name',
            ##         'national_number':'(919) 555-5346',
            ##         'number'        :'+19195555346',
            ##         'number_state'   :'enabled',
            ##         'price'         :'0.35',
            ##         'state'         :'NC'
            ##     },
            ##     {
            ##         'city'          :'RALEIGH',
            ##         'created_time'   :'2017-02-06T18:41:56Z',
            ##         'id'            :'n-n1234',
            ##         'name'          :'demo name',
            ##         'national_number':'(919) 555-5378',
            ##         'number'        :'+19195555378',
            ##         'number_state'   :'enabled',
            ##         'price'         :'0.35',
            ##         'state'         :'NC'
            ##     }
            ## ]
        """

        kwargs['applicationId'] = application_id
        kwargs['state'] = state
        kwargs['name'] = name
        kwargs['city'] = city
        kwargs['numberState'] = number_state
        kwargs['size'] = size

        path = '/users/%s/phoneNumbers' % self.user_id
        return get_lazy_enumerator(self, lambda: self._make_request('get', path, params=kwargs))

    def order_phone_number(self,
                           number=None,
                           name=None,
                           application_id=None,
                           fallback_number=None,
                           **kwargs):
        """
        Allocates a number so user can use it to make and receive calls and send
        and receive messages.

        :param str number: An available telephone number you want to use
        :param str name: A name you choose for this number.
        :param str application_id: The unique id of an Application you want to associate with this number.
        :param str fallback_number: Number to transfer an incoming call when the callback/fallback events can't
            be delivered.

        :rtype: str
        :returns: id of created phone number

        Example: Order Number::

            number_id = api.order_phone_number(number='+1234567890')
            print(number_id)
            # n-asdf123
        """

        kwargs['number'] = number
        kwargs['name'] = name
        kwargs['applicationId'] = application_id
        kwargs['fallbackNumber'] = fallback_number

        return self._make_request('post', '/users/%s/phoneNumbers' % self.user_id, json=kwargs)[2]

    def get_phone_number(self, number_id):
        """
        Get information about a phone number

        :type number_id: str
        :param number_id: id of a phone number

        :rtype: dict
        :returns: number information

        Example: Search, order, and fetch Number information::

            available_numbers = api.search_available_local_numbers(city='Raleigh', state='NC')

            number_id = api.order_phone_number(available_numbers[0]['number'])
            print(number_id)
            # n-123

            my_number = api.get_phone_number(number_id)
            print(my_number)
            ## {
            ##     'city'          :'RALEIGH',
            ##     'created_time'   :'2017-02-06T18:27:14Z',
            ##     'id'            :'n-123',
            ##     'national_number':'(919) 561-5039',
            ##     'number'        :'+19195615039',
            ##     'number_state'   :'enabled',
            ##     'price'         :'0.35',
            ##     'state'         :'NC'
            ## }

        """
        return self._make_request('get', '/users/%s/phoneNumbers/%s' % (self.user_id, number_id))[0]

    def update_phone_number(self, number_id,
                            name=None,
                            application_id=None,
                            fallback_number=None,
                            **kwargs):
        """
        Update information about a phone number

        :param str number_id: id of a phone number
        :param str name: A name you choose for this number.
        :param str application_id: The unique id of an Application you want to associate with this number.
        :param str fallback_number: Number to transfer an incoming call when the callback/fallback events can't
            be delivered.

        Example: Update number information::

            my_number = api.get_phone_number(number_id)
            print(my_number)
            ## {
            ##     'city'          :'RALEIGH',
            ##     'created_time'   :'2017-02-06T18:27:14Z',
            ##     'id'            :'n-123',
            ##     'national_number':'(919) 561-5039',
            ##     'number'        :'+19195615039',
            ##     'number_state'   :'enabled',
            ##     'price'         :'0.35',
            ##     'state'         :'NC'
            ## }

            api.update_phone_number(number_id, name='demo name')

            my_number = api.get_phone_number(number_id)
            print(my_number)
            ## {
            ##     'id'            :'n-123',
            ##     'number'        :'+19195615039',
            ##     'national_number':'(919) 561-5039',
            ##     'name'          :'demo name',
            ##     'created_time'   :'2017-02-06T18:41:56Z',
            ##     'city'          :'RALEIGH',
            ##     'state'         :'NC',
            ##     'price'         :'0.35',
            ##     'number_state'   :'enabled'
            ## }
        """
        kwargs['name'] = name
        kwargs['applicationId'] = application_id
        kwargs['fallbackNumber'] = fallback_number

        self._make_request(
            'post', '/users/%s/phoneNumbers/%s' % (self.user_id, number_id), json=kwargs)

    def delete_phone_number(self, number_id):
        """
        Remove a phone number

        :type number_id: str
        :param number_id: id of a phone number

        Example: Delete phone number (release) from account::

            api.delete_phone_number('numberId')
        """
        self._make_request(
            'delete', '/users/%s/phoneNumbers/%s' % (self.user_id, number_id))
