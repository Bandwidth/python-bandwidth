Account Api
===========

The account API contains the methods to interact with account features:

* Account
* Applications
* Search for numbers
* Register Domains and Endpoints
* Fetch Errors
* Upload/Download Media
* Order/update Phone Numbers

Client Initialization
^^^^^^^^^^^^^^^^^^^^^

Before using the sdk you must initialize a Client with your Bandwidth App
Platform API credentials::

    # Single import
    import bandwidth
    account_api = bandwidth.client('account', 'u-user', 't-token', 's-secret')

    # OR for IDE goodness with auto completes
    from bandwidth import account
    account_api = account.Client('u-user', 't-token', 's-secret')

Code Samples
^^^^^^^^^^^^

Each of these samples assumes you have already have a bandwidth account

Phone Numbers
-------------

Get available number via location search::

    from bandwidth import account
    account_api = account.Client('u-user', 't-token', 's-secret')

    numbers = account_api.search_available_local_numbers(area_code = '910', quantity = 3)

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

Account Methods
^^^^^^^^^^^^^^^
.. toctree::
   :maxdepth: 4

   account
   applications
   available_numbers
   domains
   endpoints
   errors
   media
   numbers
