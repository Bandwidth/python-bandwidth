Voice API
=========

The Voice API contains all the methods to create and manage:

* Phone Calls
* Conferences
* Recordings
* Transcriptions

Client Initialization
^^^^^^^^^^^^^^^^^^^^^

Before using the sdk you must initialize a Client with your Bandwidth App
Platform API credentials::

    # single import
    import bandwidth
    voice_api = bandwidth.client('voice', 'u-user', 't-token', 's-secret')

    # OR for IDE goodness with auto completes
    from bandwidth import voice
    voice_api = voice.Client('u-user', 't-token', 's-secret')


Create a call::

    import bandwidth
    voice_api = bandwidth.client('voice', 'u-user', 't-token', 's-secret')
    call_id = voice_api.create_call(from_ = '+1234567890', to = '+1234567891', callback_url = "http://yoursite.com/calls")
    print(call_id)
    ## c-abc123

    my_call = api.get_call(call_id)
    print(my_call)
    ## {   'callback_url'         : 'http://yoursite.com/calls',
    ##     'direction'           : 'out',
    ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
    ##     'from'                : '+1234567890',
    ##     'id'                  : 'c-abc123',
    ##     'recording_enabled'    : False,
    ##     'recording_file_format' : 'wav',
    ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
    ##     'start_time'           : '2017-01-26T16:10:11Z',
    ##     'state'               : 'started',
    ##     'to'                  : '+1234567891',
    ##     'transcription_enabled': False,
    ##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/transcriptions'}

Retrieving list of calls::

    import bandwidth
    voice_api = bandwidth.client('voice', 'u-user', 't-token', 's-secret')
    call_list = voice_api.list_calls(to = '+19192223333', size = 2)
    print(list(call_list))
    ## [
    ##   {
    ##     'active_time'          : '2017-01-26T16:10:23Z',
    ##     'callback_url'         : 'http://yoursite.com/calls',
    ##     'chargeable_duration'  : 60,
    ##     'direction'           : 'out',
    ##     'endTime'             : '2017-01-26T16:10:33Z',
    ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/events',
    ##     'from'                : '+17079311113',
    ##     'id'                  : 'c-abc123',
    ##     'recording_enabled'    : False,
    ##     'recording_file_format' : 'wav',
    ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/recordings',
    ##     'start_time'           : '2017-01-26T16:10:11Z',
    ##     'state'               : 'completed',
    ##     'to'                  : '+19192223333',
    ##     'transcription_enabled': False,
    ##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-abc123/transcriptions'
    ##   },
    ##   {
    ##     'active_time'          : '2016-12-29T23:50:35Z',
    ##     'chargeable_duration'  : 60,
    ##     'direction'           : 'out',
    ##     'endTime'             : '2016-12-29T23:50:41Z',
    ##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/events',
    ##     'from'                : '+19194443333',
    ##     'id'                  : 'c-xyz987',
    ##     'recording_enabled'    : False,
    ##     'recording_file_format' : 'wav',
    ##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/recordings',
    ##     'start_time'           : '2016-12-29T23:50:15Z',
    ##     'state'               : 'completed',
    ##     'to'                  : '+19192223333',
    ##     'transcription_enabled': False,
    ##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc123/calls/c-xyz987/transcriptions'
    ##   }
    ## ]

Voice Methods
^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 4

   calls
   conferences
   bridges
   recordings
   transcriptions
