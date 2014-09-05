import json

from flask import Flask
from flask import request

from bandwith_sdk.client import Client as ClientV1
from bandwith_sdk.client_v2 import Client as ClientV2


app = Flask(__name__)

creds = ('u-**********', ('t-******', '********'))
client_v1 = ClientV1(*creds)
client_v2 = ClientV2(*creds)

NoSqlStorage = {}


@app.route('/v1/events', methods=['POST'])
def events():
    event = json.loads(request.data)
    # Example of deserialized event:
    # {
    #     'time': '2014-07-23T13:04:39Z',
    #     'applicationId': 'a-73mq4rpnghrtbqprtr45zdy',
    #     'eventType': 'incomingcall',
    #     'callState': 'active',
    #     'callId': 'c-pkyusdpacfmvmopvd7p3dmi',
    #     'callUri': 'https://127.0.0.1/v1/users/u-2qep46jwram5oyyqqa5muli/calls/c-pkyusdpacfmvmopvd7p3dmi',
    #     'from': '+14084782637',
    #     'to': '+14082149398'
    # }

    event_type, call_id = event['eventType'], event['callId']

    if event_type == 'answer':
        client_v1.play_audio(call_id, fileUrl='hello.mp3')
    elif event_type == 'playback':
        client_v1.set_call_property(call_id, recordingEnabled=True)
    elif event_type == 'hangup':
        """
        Create a CDR
        """
    else:
        """
        Anything else ...
        """
    NoSqlStorage.update({call_id: event})
    return b''


@app.route('/v2/events', methods=['POST'])
def events():
    event = json.loads(request.data)
    # Example of deserialized event:
    # {
    #     'time': '2014-07-23T13:04:39Z',
    #     'applicationId': 'a-73mq4rpnghrtbqprtr45zdy',
    #     'eventType': 'incomingcall',
    #     'callState': 'active',
    #     'callId': 'c-pkyusdpacfmvmopvd7p3dmi',
    #     'callUri': 'https://127.0.0.1/v1/users/u-2qep46jwram5oyyqqa5muli/calls/c-pkyusdpacfmvmopvd7p3dmi',
    #     'from': '+14084782637',
    #     'to': '+14082149398'
    # }

    call = client_v2.Call(event)
    event_type = event['eventType']
    if event_type == 'answer':
        call.play_audio(fileUrl='hello.mp3')
    elif event_type == 'playback':
        call.set_call_property(recordingEnabled=True)
    elif event_type == 'hangup':
        """
        Create a CDR
        """
    else:
        """
        Anything else ...
        """
    # what do we need to save? Call or initial of event?
    NoSqlStorage.update({call.call_id: event})
    return b''


app.debug = True
app.run()
