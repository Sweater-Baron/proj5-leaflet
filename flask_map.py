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
                           "CACHE_DEFAULT_TIMEOUT":1000})

app.secret_key = CONFIG.COOKIE_KEY  # Should allow using session variables

@cache.memoize() # Cached so we can avoid the 4+ second API lookup time
def geocode_presidents(town):
    """
    Returns a list of all intersections where a numbered street crosses a street
    named after the corresponding president ("1st and Washington", etc.)
    
    Each item in the resulting list is a tuple, with item[0] holding the name
    of the intersection ("1st and Washington"), and item[1] holding a tuple
    containing the latitude and longitude of the intersection.
    
    Args:
    town is typically formatted like "City, State, Country", but Google will
    accept other formats
    
    """
    points = []
    
    for i in PRESIDENTS:
        streets = geocoder.get_ordinal_string(i) + " and " + PRESIDENTS[i]
        
        intersections = geocoder.geocode_intersection(streets, town)
        for point in intersections:
            points.append((streets, point))
            
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
    The user gave us their city. We must return a list of points marking
    places where a numbered street intersects a street named after the president
    corresponding to that number (e.g. 1st and Washington)
    
    The points are formatted as tuples, where point[0] is a description of the
    intersection ("1st and Washington"), and point[1] is a tuple containing the
    latitude and longitude of the point.
    """
    app.logger.debug("Entering getPoints")
    rslt = {}
    points = []
    
    user_city = request.args.get("city", type=str)
    points = geocode_presidents(user_city)
    
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

