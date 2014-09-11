import json
from rq import Queue
from flask import Flask
from flask import request
from bandwith_sdk.client_v4 import (Call,
                                    Bridge,
                                    Client,
                                    Event,
                                    AnswerCallEvent,
                                    PlaybackCallEvent,
                                    HangupEvent)

app = Flask(__name__)
# Client('u-**********', 't-******', 's-********')

NoSqlStorage = {}
queue = Queue('default')


@app.route('/v1/events', methods=['POST'])
def events_v1():
    event = json.loads(request.data.decode('ascii'))
    event = Event.create(**event)
    #event = Event.create(request.data)

    call = event.call  # Call('c-pkyusdpacfmvmopvd7p3dmi')
    if isinstance(event, AnswerCallEvent):
        queue.enqueue(call.play_audio, 'Thank_you_are_now_connected.mp3')
    elif isinstance(event, PlaybackCallEvent):
        #playback status: done
        if event.done:
            queue.enqueue(call.hangup)
    elif isinstance(event, HangupEvent):
        """
        Create a CDR
        """
        queue.enqueue(create_cdr, call)
    else:
        """
        Anything else ...
        """
    NoSqlStorage.update({event.callId: event})
    return b''


def create_cdr(call):
    call.refresh()
    cdr = {'caller': call.from_,
           'calee': call.to,
           'duration': call.endTime - call.activeTime,
           }
    #....
    # saving cdr somewhere

app.debug = True
app.run()
