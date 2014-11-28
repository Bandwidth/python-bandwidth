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

## Usage

The SDK setup

Default setup from environment variables in UNIX shell:

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

###Allocate phone number basic

Import PhoneNumber from sdk
```python
from bandwidth_sdk import PhoneNumber
```
Get available number for yours search criteria:

```python
available_numbers = PhoneNumber.list_local(city='Cary', state='NC')
available_numbers[0].allocate()
>>> PhoneNumber(number=+19198000000)
```

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
make test_local
```

## Contribution guidelines

Create a topic branch. Fix the issue. Cover with tests. Add documentation. Send pull request with a comment.
