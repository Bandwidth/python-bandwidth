# Bandwidth Python API

[![Build Status](https://travis-ci.org/bandwidthcom/python-bandwidth.svg?branch=master)](https://travis-ci.org/bandwidthcom/python-bandwidth)

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

    pip install bandwidth_sdk

If you want the cutting edge version (that may be broken), use this:

    pip install -e git+https://github.com/bandwidthcom/python-bandwidth.git#egg=bandwidth_sdk

## Usage

The SDK setup

    * Default setup from environment variables in UNIX shell:

        export BANDWIDTH_USER_ID=u-your-user-id
        export BANDWIDTH_TOKEN=t-your-token
        export BANDWIDTH_SECRET=s-your-secret

    * Explicitly set up in code:

        from bandwidth_sdk import Client
        Client('u-user', 't-token', 's-secret')

Calls basic usage

    Import
        from bandwidth_sdk import Call

    * Creating a new call:

        call = Call.create("+1919000001", "+1919000002")
        >>> Call(c-xxxxx, state=started)

    * Speaking a sentence in a phone call:

        call.speak_sentence("Hello", gender="female")

    * Transferring a call and saying something before bridging the calls:

        call.transfer('+1919000008', whisper_audio={"sentence": "Hello {number}, thanks for calling"})
        >>> Call(c-yyyyy, state=started)

    * Retrieving list of calls:

        Call.list()
        >>> [Call(c-xxxx, state=completed), Call(c-yyyyy, state=comleted), Call(c-zzzz, state=started)]

## Running tests

    make req
    make test
or

    make test_local


## Contribution guidelines

Create a topic branch. Fix the issue. Cover with tests. Add documentation. Send pull request with a comment.
