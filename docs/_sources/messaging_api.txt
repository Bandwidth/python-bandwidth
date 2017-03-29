Messaging API
=============

The Messaging API contains the methods to send sms and mms messages.

Client Initialization
^^^^^^^^^^^^^^^^^^^^^

Before using the sdk you must initialize a Client with your Bandwidth App
Platform API credentials::

    import bandwidth
    messaging_api = bandwidth.client('messaging', 'u-user', 't-token', 's-secret')

Example: Send Text Message::

    message_id = messaging_api.send_message(from_ = '+1234567980',
                                  to = '+1234567981',
                                  text = 'SMS message')
    print(message_id)
    # m-messageId

Example: Send Picture Message::

    message_id = messaging_api.send_message(from_ = '+1234567980',
                                  to = '+1234567981',
                                  text = 'MMS message',
                                  media=['http://cat.com/cat.png'])
    print(message_id)
    # m-messageId

Example: Bulk Send Picture or Text messages (or both)::

    results = messaging_api.send_messages([
        {'from': '+1234567980', 'to': '+1234567981', 'text': 'SMS message'},
        {'from': '+1234567980', 'to': '+1234567982', 'text': 'SMS message2'}
    ])

Example: Fetch information about single message::

    my_message = messaging_api.get_message('m-na6cpyjf2qcpz6l3drhcx7y')
    print(my_message)

    ## {
    ##     'callback_url'             :'https://yoursite.com/message',
    ##     'direction'               :'in',
    ##     'from'                    :'+19193047864',
    ##     'id'                      :'m-messageId',
    ##     'media'                   :[],
    ##     'message_id'               :'m-messageId',
    ##     'skip_mms_carrier_validation':True,
    ##     'state'                   :'received',
    ##     'text'                    :'Hey there',
    ##     'time'                    :'2017-02-01T21:10:32Z',
    ##     'to'                      :'+19191234567'
    ## }

Messaging Methods
^^^^^^^^^^^^^^^^^
.. toctree::
   :maxdepth: 4

   messages
