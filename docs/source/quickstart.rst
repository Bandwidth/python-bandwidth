Quickstart Guide
================

Installation
^^^^^^^^^^^^

To install the latest stable version with pip use the following command::

    pip install bandwidth_sdk

If you want to install the bleeding edge version of the SDK from our
`github repository <https://github.com/bandwidthcom/python-bandwidth>`_
use the following command::

    pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk

Note: This may have to be run as `root` or with `--user` flag if you are not
using python virtual environment.

Client Initialization
^^^^^^^^^^^^^^^^^^^^^

Before using the sdk you must initialize a Client with your Bandwidth App
Platform API credentials::

    from bandwidth_sdk import Client
    Client('u-user', 't-token', 's-secret')

For those who do not wish to hardcode their credentials in source code,
:meth:`bandwidth_sdk.client.Client` provides additional initialization methods
including environment variables and configuration files.

Code Samples
^^^^^^^^^^^^

Each of these code sample assumes that you have already initialized a client
as described above.

Phone Numbers
-------------

Get available number via location search::

    from bandwidth_sdk import PhoneNumber
    available_numbers = PhoneNumber.list_local(city='Cary', state='NC')
    available_numbers[0].allocate()
    # PhoneNumber(number=+19198000000)

Allocate a tollfree number::

    from bandwidth_sdk import PhoneNumber
    available_numbers = PhoneNumber.list_tollfree(pattern='1844*')
    available_numbers[0].allocate()
    # PhoneNumber(number=+1844280000)

Iterate over all allocated phone numbers::

    for p in PhoneNumber.as_iterator():
        print(p)

Get number info::

    from bandwidth_sdk import NumberInfo
    n_info = NumberInfo.get('+1900000001')
    n_info.updated
    # datetime.datetime(2014, 12, 19, 2, 14, 14, tzinfo=tzutc())

Calling
-------

Create a call::

    from bandwidth_sdk import Call
    call = Call.create("+1919000001", "+1919000002")
    # Call(c-xxxxx, state=started)

Speaking a sentence in a phone call::

    call.speak_sentence("Hello", gender="female")

Transferring a call and saying something before bridging the calls::

    call.transfer(
        '+1919000008',
         whisper_audio={"sentence": "Hello {number}, thanks for calling"}
     )
    # Call(c-yyyyy, state=started)

Retrieving list of calls::

    Call.list()
    # [Call(c-xxxx, state=completed), Call(c-yyyyy, state=comleted), Call(c-zzzz, state=started)]

Messaging
---------

Sending a text message::

    from bandwidth_sdk import Message
    Message.send(
        sender='+19796543211',
        receiver='+19796543212',
        text='Good morning, this is a test message',
        tag='test tag')
    # Message('m-id123213', state='sending')

Sending a text message with receipts::

    from bandwidth_sdk import Message
    Message.send(
        sender='+19796543211',
        receiver='+19796543212',
        text='Good morning, this is a test message',
        tag='test tag',
        receipt_requested='all'
    )
    # Message('m-id123213', state='sending', delivery_state='None')

Sending an MMS message::

    from bandwidth_sdk import Message
    from bandwidth_sdk import Media

    media = Media.upload('dolphin.mp3',
                         file_path='./tests/fixtures/dolphin.mp3')

    media_list = [media]

    Message.send(
        sender='+19796543211',
        receiver='+19796543212',
        text='Good morning, this is a test MMS message',
        media_list=media_list,
        tag='mms tag')

    # Message('m-id456654', state='sending')

SIP
---

Creating a SIP endpoint token::

    from bandwidth_sdk import Domain
    from bandwidth_sdk import Endpoint
    domain = Domain.create(name='mydomain', description='My domain description')
    endpoint = domain.add_endpoint(
        name='myendpoint',
        description='My endpoint description',
        credentials={'password':'123456'}
    )
    endpoint.create_token()
    # EndpointToken(241ebe3ab1b884bb00f214c99dd83546c32d437c89156a05afc9c34043223915)

Delete an endpoint token::

    from bandwidth_sdk import Domain
    from bandwidth_sdk import Endpoint
    Domain.create(name='mydomain', description='My domain description')
    # Domain('rd-lrek7hie26iihjdja2iibji')

    Endpoint.create(
        'rd-lrek7hie26iihjdja2iibji',
        name='myendpoint',
        description='My endpoint description',
        credentials={'password': '123456'})
    # Endpoint(re-ywfvkvq7dbgfi4ld22d7qqi)
    
    token = EndpointToken.create(
        'rd-lrek7hie26iihjdja2iibji',
        're-ywfvkvq7dbgfi4ld22d7qqi')
    
    token.delete()
    # True

Bandwidth XML
-------------

Create a Bandwidth XML response::

    from bandwidth_sdk import xml
    response = xml.Response()
    speak_sentence = xml.SpeakSentence(
        "Transferring your call, please wait.",
         voice="paul", gender="male",
         locale="en_US")

    transfer = xml.Transfer(
        transfer_caller_id="private",
        transfer_to="+13032218749",
        speak_sentence=xml.SpeakSentence(
            "Inner speak sentence",
             voice="paul",
             gender="male",
             locale="en_US"
        )
    )

    hangup = xml.Hangup()

    response.push(speak_sentence)
    response.push(transfer)
    response.push(hangup)

    print(response.to_xml())

More examples
-------------

Take a look at the
`python bandwidth examples repository <https://github.com/bandwidthcom/python-bandwidth-examples>`_
