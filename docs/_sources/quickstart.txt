Quickstart Guide
================

Installation
^^^^^^^^^^^^

To install the latest stable version with pip use the following command::

    pip install bandwidth_sdk

If you want to install the bleeding edge version of the SDK from our
`github repository <https://github.com/bandwidth/python-bandwidth>`_
use the following command::

    pip install -e git+https://github.com/bandwidth/python-bandwidth.git#egg=bandwidth_sdk

Note: This may have to be run as `root` or with `--user` flag if you are not
using python virtual environment.

Client Initialization
^^^^^^^^^^^^^^^^^^^^^

Before using the sdk you must initialize a Client with your Bandwidth App
Platform API credentials::

    import bandwidth
    api = bandwidth.client('catapult', 'u-user', 't-token', 's-secret')

Code Samples
^^^^^^^^^^^^

Each of these code sample assumes that you have already initialized a client
as described above.

Phone Numbers
-------------

Get available number via location search::

    import Bandwidth
    api = bandwidth.client('catapult', 'u-user', 't-token', 's-secret')
    numbers = api.search_available_local_numbers(area_code = '910', quantity = 3)
    print(numbers)
    ## [   {   'city'          : 'WILMINGTON',
    ##         'nationalNumber': '(910) 444-0230',
    ##         'number'        : '+19104440230',
    ##         'price'         : '0.35',
    ##         'rateCenter'    : 'WILMINGTON',
    ##         'state'         : 'NC'},
    ##     {   'city'          : 'WILMINGTON',
    ##         'nationalNumber': '(910) 444-0263',
    ##         'number'        : '+19104440263',
    ##         'price'         : '0.35',
    ##         'rateCenter'    : 'WILMINGTON',
    ##         'state'         : 'NC'},
    ##     {   'city'          : 'WILMINGTON',
    ##         'nationalNumber': '(910) 444-0268',
    ##         'number'        : '+19104440268',
    ##         'price'         : '0.35',
    ##         'rateCenter'    : 'WILMINGTON',
    ##         'state'         : 'NC'}
    ## ]

    my_number = api.create_phone_number(numbers[0]['number'])

    print(my_number)
    #+19104440230

Calling
-------

Create a call::

    import Bandwidth
    api = bandwidth.client('catapult', 'u-user', 't-token', 's-secret')
    call_id = api.create_call(from_ = '+1234567890', to = '+1234567891', callback_url = "http://yoursite.com/calls")
    print(call_id)
    ## c-abc123

    my_call = api.get_call(call_id)
    print(my_call)
    ## {   'callbackUrl'         : 'http://yoursite.com/calls',
    ##     'direction'           : 'out',
    ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
    ##     'from'                : '+1234567890',
    ##     'id'                  : 'c-abc123',
    ##     'recordingEnabled'    : False,
    ##     'recordingFileFormat' : 'wav',
    ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
    ##     'startTime'           : '2017-01-26T16:10:11Z',
    ##     'state'               : 'started',
    ##     'to'                  : '+1234567891',
    ##     'transcriptionEnabled': False,
    ##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/transcriptions'}

Retrieving list of calls::

    import Bandwidth
    api = bandwidth.client('catapult', 'u-user', 't-token', 's-secret')
    call_list = api.list_calls(to = '+19192223333', size = 2)
    print(list(call_list))
    ## [
    ##   {
    ##     'activeTime'          : '2017-01-26T16:10:23Z',
    ##     'callbackUrl'         : 'http://yoursite.com/calls',
    ##     'chargeableDuration'  : 60,
    ##     'direction'           : 'out',
    ##     'endTime'             : '2017-01-26T16:10:33Z',
    ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/events',
    ##     'from'                : '+17079311113',
    ##     'id'                  : 'c-abc123',
    ##     'recordingEnabled'    : False,
    ##     'recordingFileFormat' : 'wav',
    ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/recordings',
    ##     'startTime'           : '2017-01-26T16:10:11Z',
    ##     'state'               : 'completed',
    ##     'to'                  : '+19192223333',
    ##     'transcriptionEnabled': False,
    ##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/transcriptions'
    ##   },
    ##   {
    ##     'activeTime'          : '2016-12-29T23:50:35Z',
    ##     'chargeableDuration'  : 60,
    ##     'direction'           : 'out',
    ##     'endTime'             : '2016-12-29T23:50:41Z',
    ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/events',
    ##     'from'                : '+19194443333',
    ##     'id'                  : 'c-xyz987',
    ##     'recordingEnabled'    : False,
    ##     'recordingFileFormat' : 'wav',
    ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/recordings',
    ##     'startTime'           : '2016-12-29T23:50:15Z',
    ##     'state'               : 'completed',
    ##     'to'                  : '+19192223333',
    ##     'transcriptionEnabled': False,
    ##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/transcriptions'
    ##   }
    ## ]

Messaging
---------

Example: Send Text Message::

    message_id = api.send_message(from_ = '+1234567980',
                                  to = '+1234567981',
                                  text = 'SMS message')
    print(message_id)
    # m-messageId

Example: Send Picture Message::

    message_id = api.send_message(from_ = '+1234567980',
                                  to = '+1234567981',
                                  text = 'MMS message',
                                  media=['http://cat.com/cat.png'])
    print(message_id)
    # m-messageId

Example: Bulk Send Picture or Text messages (or both)::

    results = api.send_message([
        {'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'},
        {'from': '+1234567980', 'to': '+1234567982', 'text': 'SMS message2'}
    ])

Example: Fetch information about single message::

    my_message = api.get_message('m-na6cpyjf2qcpz6l3drhcx7y')
    print(my_message)

    ## {
    ##     'callbackUrl'             :'https://yoursite.com/message',
    ##     'direction'               :'in',
    ##     'from'                    :'+19193047864',
    ##     'id'                      :'m-messageId',
    ##     'media'                   :[],
    ##     'messageId'               :'m-messageId',
    ##     'skipMMSCarrierValidation':True,
    ##     'state'                   :'received',
    ##     'text'                    :'Hey there',
    ##     'time'                    :'2017-02-01T21:10:32Z',
    ##     'to'                      :'+19191234567'
    ## }
