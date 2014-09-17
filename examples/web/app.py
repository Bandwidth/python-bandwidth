#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, request
from flask.ext.rq import RQ

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
# app.config.from_object('config')

RQ(app)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return 'Its works'

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    return 'error occurred', 500


@app.errorhandler(404)
def not_found_error(error):
    return 'Not found', 404

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
