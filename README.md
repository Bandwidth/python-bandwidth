# Bandwidth Python API

[![Build Status](https://travis-ci.org/bandwidthcom/python-bandwidth.svg?branch=master)](https://travis-ci.org/bandwidthcom/python-bandwidth)

[![Can I Use Python 3?](https://caniusepython3.com/project/bandwidth-sdk.svg)](https://caniusepython3.com/project/bandwidth-sdk)

Bandwidth SDK is Python library for working with [Bandwidth](https://catapult.inetwork.com/pages/home.jsf) platform API.
It should be integrated in your python web application easily.

Complete original documentation of API [here](https://catapult.inetwork.com/docs/)

## Getting started
You need to have

    - Git
    - Python (2.7, 3.3, 3.4)
    - Bandwidth Application Platform account
    - pip

## Installation
Simply use the following command to install the latest released version:
```console
pip install bandwidth_sdk
```

If you want the cutting edge version (that may be broken), use this:
```console
pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk
```
Note: This may have to be run as `root` or with `--user` flag if you are not using python virtual environment.


##  Usage
* [Set up](#the-sdk-setup)
* [Allocating a phone number ](#allocate-phone-number-basic)
* [Calls basic usage](#calls-basic-usage)
* [Uploading media](#uploading-the-media)
* [Sending text message](#sending-text-message)
* [Sending text message with receipt](#sending-text-message-with-receipt)
* [Getting number info](#getting-number-info)
* [Creating SIP domain](#creating-sip-domain)
* [Creating SIP endpoint](#creating-sip-endpoint)
* [Creating SIP endpoint token](#creating-sip-endpoint-token)


### The SDK setup


Default setup from environment variables in UNIX shell :

```console
export BANDWIDTH_USER_ID=u-your-user-id
export BANDWIDTH_API_TOKEN=t-your-token
export BANDWIDTH_API_SECRET=s-your-secret
```
Or explicitly set up in code:

```python
from bandwidth_sdk import Client
Client('u-user', 't-token', 's-secret')
```

Or using the config file `.bndsdkrc` that by default is getting from existing path 
or you can set up path to file using environment variable `BANDWIDTH_CONFIG_FILE`:
```file
[catapult]
user_id = u-your-user-id
token = t-your-token
secret = s-your-secret
```

### Allocate phone number basic

Import PhoneNumber from sdk
```python
from bandwidth_sdk import PhoneNumber
```
Get available number for yours search criteria (by location in the following example):

```python
available_numbers = PhoneNumber.list_local(city='Cary', state='NC')
available_numbers[0].allocate()
>>> PhoneNumber(number=+19198000000)
```

Search and allocate tool free numbers:

```python
available_numbers = PhoneNumber.list_tollfree(pattern='1844*')
available_numbers[0].allocate()
>>> PhoneNumber(number=+1844280000)
```

Get a list of allocated phone numbers:

```python
PhoneNumber.list()
>>> [PhoneNumber(number=+19198000000), PhoneNumber(number=+1844280000)]
```

Example of iteration over all of allocated numbers:

```python
fallback_number = '+19198000001'

for p in PhoneNumber.as_iterator():
	p.patch(fallback_number=fallback_number)

```
In the example, here we update the <code>fallback_number</code> attribute for all of allocated numbers.

You can also create Application before (or update current), to use your endpoint to handle events related to this Phonenumber.

```python
from bandwidth_sdk import Application
application = Application.create(name='new-application',
                                 incoming_call_url='http://test.callback.info')
# getting number that we allocated before
number = PhoneNumber.get_number_info(number=+19198000000)
number.patch(application=application)
```

Now this number is attached to your application, and all events will deliver to `incoming_call_url` that your point in Application.

###Calls basic usage

Import Call from sdk
```python
from bandwidth_sdk import Call
```

Creating a new call:
```python
call = Call.create("+1919000001", "+1919000002")
>>> Call(c-xxxxx, state=started)
```
Speaking a sentence in a phone call:
```python
call.speak_sentence("Hello", gender="female")
```
Transferring a call and saying something before bridging the calls:
```python
call.transfer('+1919000008', whisper_audio={"sentence": "Hello {number}, thanks for calling"})
>>> Call(c-yyyyy, state=started)
```
Retrieving list of calls:
```python
Call.list()
>>> [Call(c-xxxx, state=completed), Call(c-yyyyy, state=comleted), Call(c-zzzz, state=started)]
```
###Uploading the media
Make sure that you have media file. In this example we will use test file "dolphin.mp3", that exists in this repo:

```python
from bandwidth_sdk import Media
Media.upload('dolphin.mp3', file_path='./tests/fixtures/dolphin.mp3')
>>> Media(dolphin.mp3)
```

###Sending text message

Import Message from sdk:
```python
from bandwidth_sdk import Message
```
Send message by method "send":

```python
Message.send(sender='+19796543211', receiver='+19796543212', text='Good morning, this is a test message', tag='test tag')
>>> Message('m-id123213', state='sending')
```

###Sending text message with receipt

Import Message from sdk:
```python
from bandwidth_sdk import Message
```
Send message by method "send":

```python
Message.send(sender='+19796543211', receiver='+19796543212', text='Good morning, this is a test message', tag='test tag', receipt_requested='all')
>>> Message('m-id123213', state='sending', delivery_state='waiting')
```

###Getting number info

Import NumberInfo from sdk:
```python
from bandwidth_sdk import NumberInfo
```

Get number info by CNAM of the number:

```python
NumberInfo.get('+1900000001')
>>>NumberInfo(HIGHTSTOWN  NJ)
n_info = _
n_info.updated
>>>datetime.datetime(2014, 12, 19, 2, 14, 14, tzinfo=tzutc())
```

###Creating SIP domain

Import Domain from sdk:
```python
from bandwidth_sdk import Domain
```

Create Domain by method "create":
```python
>>>Domain.create(name='mydomain', description='My domain description')
Domain(rd-lrek7hie26iihjdja2iibji)
```

Delete Domain by method "delete":
```python
>>>domain = Domain.create(name='mydomain', description='My domain description')
>>>domain.delete()
True
```

###Creating SIP endpoint

Import Domain and Endpoint from sdk:
```python
from bandwidth_sdk import Domain
from bandwidth_sdk import Endpoint
```

Create Endpoind via Domain by method "add_endpoint":
```python
>>>domain = Domain.create(name='mydomain', description='My domain description')
>>>domain.add_endpoint(name='myendpoint', description='My endpoint description', credentials={'password':'123456'})
Endpoint(re-ywfvkvq7dbgfi4ld22d7qqi)
```

Delete Endpoint by method "delete":
```python
>>>domain = Domain.create(name='mydomain', description='My domain description')
>>>endpoint = domain.add_endpoint(name='myendpoint', description='My endpoint description', credentials={'password':'123456'})
>>>endpoint.delete()
True
```

###Creating SIP endpoint token

Import Domain and Endpoint from sdk:
```python
from bandwidth_sdk import Domain
from bandwidth_sdk import Endpoint
```

Create Endpoind token via Endpoint by method "create_token":
```python
>>>domain = Domain.create(name='mydomain', description='My domain description')
>>>endpoint = domain.add_endpoint(name='myendpoint', description='My endpoint description', credentials={'password':'123456'})
>>>endpoint.create_token()
EndpointToken(241ebe3ab1b884bb00f214c99dd83546c32d437c89156a05afc9c34043223915)
```

Delete Endpoint token by method "delete":
```python
>>>Domain.create(name='mydomain', description='My domain description')
Domain(rd-lrek7hie26iihjdja2iibji)
>>>Endpoint.create('rd-lrek7hie26iihjdja2iibji', name='myendpoint', description='My endpoint description', credentials={'password':'123456'})
Endpoint(re-ywfvkvq7dbgfi4ld22d7qqi)
>>>token = EndpointToken.create('rd-lrek7hie26iihjdja2iibji', 're-ywfvkvq7dbgfi4ld22d7qqi')
>>>token.delete()
True
```

###Generate Bandwidth XML

Import NumberInfo from sdk:
```python
    from bandwidth_sdk import xml
```

Create a Bandwidth XML response:
```python
    response = xml.Response()
    speak_sentence = xml.SpeakSentence("Transferring your call, please wait.", voice="paul", gender="male", locale="en_US")
    transfer = xml.Transfer(transfer_caller_id="private", transfer_to="+13032218749",
                            speak_sentence=xml.SpeakSentence("Inner speak sentence", voice="paul",
                                                             gender="male", locale="en_US"))
    hangup = xml.Hangup()

    response.push(speak_sentence)
    response.push(transfer)
    response.push(hangup)

    print(response.to_xml())
```

####More examples:

Take a look of [python bandwidth examples repository](https://github.com/bandwidthcom/python-bandwidth-examples).

## Running tests
```console
make req
make test
```
or
```console
make req
make local_test
```

## Contribution guidelines

Create a topic branch. Fix the issue. Cover with tests. Add documentation. Send pull request with a comment.
