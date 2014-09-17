# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import os

from flask import Flask, request, jsonify
from flask.ext.rqify import init_rqify

from bandwith_sdk import Call

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
init_rqify(app)
# app.config.from_object('config')
CALLER = os.environ.get('CALLER_NUMBER')

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return 'Its works'


@app.route('/start/call', methods=['POST'])
def start_call():
    inc = request.get_json()
    call = Call.create(caller=CALLER, callee=inc['to'], recording_enabled=True)
    return jsonify(call.__dict__)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    return 'error occurred', 500


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
