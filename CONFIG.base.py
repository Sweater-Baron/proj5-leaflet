"""
Configuration of flask application.
Everything that could be different between running
on your development platform or on ix.cs.uoregon.edu
(or on a different deployment target) shoudl be here.
"""
DEBUG = True
PORT = 5000 # Replace with a randomly chosen port
#   Obtain a cookie key with 
#   import uuid
#   str(uuid.uuid4())
# We do it just once so that multiple processes
# will share the same key.
# Should look like COOKIE_KEY = 'xxxxxxxxxx-xxxx-xxxx'
COOKIE_KEY = '' # Replace with a new key
API_KEY = '' # Replace with a google API key that has the geocoding API enabled
             # in the Google Developer Console
             
CACHESIZE = 500000000 # The documentation wasn't clear what units this is in,
# but it's probably bytes