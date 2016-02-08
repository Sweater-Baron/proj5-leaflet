"""
A simple Flask website that displays a map of the user's city and indicates
each intersection where a street named after a president intersects with a
numbered street whose number is that president's number - e.g. '1st and 
Washington', '2nd and Adams', etc.
"""

import flask
from flask import render_template
from flask import request  # Data from a submitted form
from flask import url_for
from flask import jsonify # For AJAX transactions
from flask.ext.cache import Cache

import json
import logging
import argparse  # For the vocabulary list
import sys

###
# Our own modules
###
import geocoder

###
# Globals
###
import CONFIG
from presidents import PRESIDENTS
CACHESIZE = CONFIG.CACHESIZE

app = flask.Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE":"filesystem",
                           "CACHE_THRESHOLD":CACHESIZE,
                           "CACHE_DIR":".flaskCache",
                           "CACHE_DEFAULT_TIMEOUT":5000}) #timeout is 2 seconds

#cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.secret_key = CONFIG.COOKIE_KEY  # Should allow using session variables

@cache.memoize() # Cached so we can avoid the 4+ second API lookup time
def get_president_points(user_city):
    points = []
    for pres_num in PRESIDENTS:
        point = geocoder.geocode_president(pres_num, PRESIDENTS[pres_num], user_city)
        if isinstance(point[1], tuple):
            # If the 2nd value in point is a tuple, we found a valid spot.
            points.append(point)
            # Note that these tuples will become arrays when jsonified
    return points

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  return flask.render_template('presidents.html')


  
###############
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
###############

@app.route("/_getPoints")
def getPoints():
    """
    User's location has been found. We need to return a list of
    points. TODO: more details
    """
    app.logger.debug("Entering getPoints")
    rslt = {}
    points = []
    
    user_city = request.args.get("city", type=str)
    points = get_president_points(user_city)
    
    rslt["points"] = points
    rslt["did_find_points"] = bool(points) # Empty lists are False
        
    return jsonify(result=rslt)

  
  
###################
#   Error handlers
###################
@app.errorhandler(404)
def error_404(e):
  app.logger.warning("++ 404 error: {}".format(e))
  return render_template('404.html'), 404

@app.errorhandler(500)
def error_500(e):
   app.logger.warning("++ 500 error: {}".format(e))
   assert app.debug == False #  I want to invoke the debugger
   return render_template('500.html'), 500

@app.errorhandler(403)
def error_403(e):
  app.logger.warning("++ 403 error: {}".format(e))
  return render_template('403.html'), 403



#############

# Set up to run from cgi-bin script, from
# gunicorn, or stand-alone.
#

if __name__ == "__main__":
    # Standalone. 
    app.debug = True
    app.logger.setLevel(logging.DEBUG)
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
else:
    # Running from cgi-bin or from gunicorn WSGI server, 
    # which makes the call to app.run.  Gunicorn may invoke more than
    # one instance for concurrent service.
    #FIXME:  Debug cgi interface 
    app.debug=False

