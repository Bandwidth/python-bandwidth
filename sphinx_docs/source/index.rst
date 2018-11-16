Bandwidth SDK
==========================

bandwidth_sdk is a python library for working with
`Bandwidth Voice And Messaging APIs <http://dev.bandwidth.com>`_.

Complete original documentation of the API can be found
`here <http://dev.bandwidth.com>`_

Install the SDK with pip::

    pip install bandwidth-sdk

The Bandwidth-Python API is broken up into logical pieces:

* Voice API
* Account API
* Messaging API

Before using the sdk you must initialize at least one client with your Bandwidth App
Platform API credentials::

    import bandwidth
    voice_api = bandwidth.client('voice', 'u-user', 't-token', 's-secret')
    messaging_api = bandwidth.client('messaging', 'u-user', 't-token', 's-secret')
    account_api = bandwidth.client('account', 'u-user', 't-token', 's-secret')

Or import each individually for better IDE integration::

    from bandwidth import messaging, voice, account
    messaging_api = messaging.Client('u-user', 't-token', 's-secret')
    voice_api = voice.Client('u-user', 't-token', 's-secret')
    account_api = account.Client('u-user', 't-token', 's-secret')

Voice API
~~~~~~~~~
* Phone Calls
* Conferences
* Recordings
* Transcriptions

Messaging API
~~~~~~~~~~~~~
* Send MMS
* Send SMS
* Fetch Messages

Account API
~~~~~~~~~~~
* Account
* Applications
* Search for numbers
* Register Domains and Endpoints
* Fetch Errors
* Upload/Download Media
* Order/update Phone Numbers

Contents:
~~~~~~~~~

.. toctree::
   :maxdepth: 3

   quickstart
   messaging_api
   voice_api
   account_api
   tests
   contribute

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
