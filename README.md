# Bandwidth Python API

[![Build Status](https://travis-ci.org/Bandwidth/python-bandwidth.svg?branch=master)](https://travis-ci.org/Bandwidth/python-bandwidth) [![Can I Use Python 3?](https://caniusepython3.com/project/bandwidth-sdk.svg)](https://caniusepython3.com/project/bandwidth-sdk)[![Documentation Status](https://readthedocs.org/projects/bandwidth-sdk/badge/?version=latest)](http://bandwidth-sdk.readthedocs.io/en/latest/?badge=latest)


Client library for the [Bandwidth App Platform](http://ap.bandwidth.com/docs/rest-api/)

## Full Reference
### [dev.bandwidth.com/python-bandwidth](http://dev.bandwidth.com/python-bandwidth)


## Requirements
* [Bandwidth Account](http://bandwidth.com/products/application-platform/?utm_medium=social&utm_source=github&utm_campaign=dtolb&utm_content=_)
* [At least Python 2.7](https://www.python.org/downloads/)


## Installation

```bash
pip install bandwidth-sdk
```

## Usage

### Client Initialization
```python
import bandwidth
voice_api = bandwidth.client('voice', 'u-user', 't-token', 's-secret')
messaging_api = bandwidth.client('messaging', 'u-user', 't-token', 's-secret')
account_api = bandwidth.client('account', 'u-user', 't-token', 's-secret')

## Or import each individually for better IDE integration::

from bandwidth import messaging, voice, account
messaging_api = messaging.Client('u-user', 't-token', 's-secret')
voice_api = voice.Client('u-user', 't-token', 's-secret')
account_api = account.Client('u-user', 't-token', 's-secret')
```

> Each of these code sample assumes that you have already initialized a client

### Search and order phone number

```python
numbers = account_api.search_available_local_numbers(area_code = '910', quantity = 3)
print(numbers[0]['number'])
## +19104440230

my_number = account_api.order_phone_number(numbers[0]['number'])

print(my_number)
#n-rnd5eag33safchqmrj3q
```

### Send Text Message
```python
message_id = api.send_message(from_ = '+1234567980',
                              to = '+1234567981',
                              text = 'SMS message')
print(message_id)
# m-messageId
```

### Send Picture Message

```python
message_id = api.send_message(from_ = '+1234567980',
                              to = '+1234567981',
                              text = 'MMS message',
                              media=['http://cat.com/cat.png'])
print(message_id)
# m-messageId
```


### Fetch information about single message
```python
my_message = api.get_message('m-messageId')
print(my_message[state])
## received
```

### Create an outbound call

```python
call_id = api.create_call(from_ = '+1234567890',
                          to = '+1234567891',
                          callback_url = "http://yoursite.com/calls")
print(call_id)
## c-abc123
 ```

### Get information on single call

```python
my_call = api.get_call('c-abc123')
print(my_call)
## {   'callback_url'         : 'http://yoursite.com/calls',
##     'direction'           : 'out',
##     'events'              : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/events',
##     'from'                : '+1234567890',
##     'id'                  : 'c-abc123',
##     'recording_enabled'    : False,
##     'recording_file_format' : 'wav',
##     'recordings'          : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/recordings',
##     'startTime'           : '2017-01-26T16:10:11Z',
##     'state'               : 'started',
##     'to'                  : '+1234567891',
##     'transcription_enabled': False,
##     'transcriptions'      : 'https://api.catapult.inetwork.com/v1/users/u-abc/calls/c-abc123/transcriptions'}
```

### Retrieving list of calls

```python
call_list = api.list_calls(to = '+19192223333', size = 2)
print(list(call_list))
```
