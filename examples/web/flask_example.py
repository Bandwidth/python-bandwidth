# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os
import logging

from flask import Flask, request, jsonify

from bandwith_sdk import Call, Event, Bridge, AnswerCallEvent, PlaybackCallEvent, HangupCallEvent, GatherCallEvent

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
# app.config.from_object('config')
CALLER = os.environ.get('CALLER_NUMBER')
BRIDGE_CALLEE = os.environ.get('CALLER_NUMBER')

DOMAIN = os.environ.get('DOMAIN')


logger = logging.getLogger(__name__)
# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return 'Its works'


@app.route('/start/call', methods=['POST'])
def start_call():
    inc = request.get_json()
    callee = inc.get('to')
    if not callee:
        return jsonify('number field is required'), 400
    Call.create(CALLER, callee, recording_enabled=True)
    return jsonify('Created'), 201


@app.route('/events', methods=['POST'])
def handle_event():
    event = Event.create(**request.get_json())
    call = event.call
    logger.debug('Processing %s', event)
    if isinstance(event, AnswerCallEvent):
        call.speak_sentence('Hello from test application', gender='female', tag='greeting')
    elif isinstance(event, PlaybackCallEvent):
        logger.debug('Playback received')
        if event.done:
            if event.tag == 'greeting':
                logger.debug('Starting dtmf gathering')
                call.gather.create(max_digits='5',
                                   terminating_digits='*',
                                   inter_digit_timeout='7',
                                   prompt={'sentence': 'Please enter your 5 digit code', 'loop_enabled': True})
            elif event.tag == 'gather_complete':
                bridge = Bridge.create(call)
                app_url = 'http://{}{}'.format(DOMAIN, '/events/bridged')
                bridge.call_party(CALLER, BRIDGE_CALLEE, call_back_url=app_url, tag='bridge-id:{}'.format(bridge.id))

    elif isinstance(event, GatherCallEvent):
        call.speak_sentence('Thank you, your input was {}, this call will be bridged'.format(event.dtmf_digits),
                            gender='male',
                            tag='gather_complete')

    elif isinstance(event, HangupCallEvent):
        logger.debug('Call ended')
    else:
        """
        Anything else ...
        """
    return '', 200


@app.route('/events/bridged', methods=['POST'])
def handle_bridged_leg():
    event = Event.create(**request.get_json())
    call = event.call
    if isinstance(event, HangupCallEvent):
        logger.debug('Call ended')
        bridge_id = event.tag.split(':')[-1]
        bridge = Bridge(bridge_id)
        calls = bridge.fetch_calls()
        for c in calls:
            if call.call_id != c.call_id:
                c.hangup()
    return '', 200


# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    return 'error occurred', 500


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404

# ----------------------------------------------------------------------------#
# Delayed jobs
# ----------------------------------------------------------------------------#

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)
