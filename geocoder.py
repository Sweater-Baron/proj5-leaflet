"""
See documentation at https://developers.google.com/maps/documentation/geocoding
"""

import urllib.request
import urllib.parse
import json
import time
import CONFIG

API_KEY = CONFIG.API_KEY
API_URL = "https://maps.googleapis.com/maps/api/geocode/json?"


def get_ordinal_string(n):
    """
    Return the ordinal representation of a positive integer (e.g. 1 -> "1st")
    Code by CTT @ http://stackoverflow.com/a/739301
    """
    if 10 <= n % 100 < 20:
        return str(n) + 'th'
    else:
       return  str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, "th")

       
def make_google_api_request(request_url):
    result = json.loads(urllib.request.urlopen(request_url).read().decode())
    # Log the return status:
    print("Google API returned status: " + result["status"])
    if result["status"] == "OVER_QUERY_LIMIT" or result["status"] == "UNKNOWN_ERROR":
        # "OVER_QUERY_LIMIT" means that we've made too many requests in the
        # last second, and Google is throttling us. "UNKNOWN_ERROR" means
        # there was a problem on Google's end; in that case, their
        # documentation says to try again.
        # We'll only try again once, because if the second try doesn't work,
        # it's probably caused by a problem that will only be made worse by
        # trying over and over again
        time.sleep(1)
        result = json.loads(urllib.request.urlopen(request_url).read().decode())
        # Log the return status:
        print("Retrying. This time, API returned status: " + result["status"])
        
    return result
       
       
def geocode_intersection(intersection_string):
    """
    Get a tuple containing the latitude and longitude of the given address.
    """
    data = urllib.parse.urlencode({"address" : intersection_string,
                                  "key" : API_KEY})
    result = make_google_api_request(API_URL + data)
    if result["status"] == "OK":
        if "intersection" in result["results"][0]["types"]:
            lat = result["results"][0]["geometry"]["location"]["lat"]
            lng = result["results"][0]["geometry"]["location"]["lng"]
            return (lat, lng)
        else:
            return "Intersection does not exist"
    else:
        return "Status: " + result["status"]
    
    
def geocode_president(pres_number, pres_name, userLoc):
    """
    Look for the intersection of pres_name and pres_number in the town of
    userLoc
    userLoc is typically formatted like "City, State, Country", but Google will
    accept other formats
    
    """
    street_string = get_ordinal_string(pres_number) + " and " + pres_name
    full_address = street_string + ", " + userLoc
    #full_address should now look like "nth and President, City, State, USA"
    return (street_string, geocode_intersection(full_address))

    
def reverse_geocode(userCoords):
    """
    Returns the city, state (or equivalent administrative region), and country
    that the specified point is in
    userCoords is a tuple: (latitude, longitude)
    """
    lat, lng = userCoords
    latlng = "{0},{1}".format(lat, lng)
    data = urllib.parse.urlencode({"latlng" : latlng,
                                  "result_type" : "locality",
                                  "key" : API_KEY})
                                  
    result = make_google_api_request(API_URL + data)
    if result["status"] == "OK":
        return result["results"][0]["formatted_address"]
    else:
        return "Status: " + result["status"]
    
    
def main():
    print(reverse_geocode((44.051944, -123.086667)))
    print(geocode_intersection("1585 E. 13th Ave, Eugene, OR, 97403"))
    print(geocode_president(1, "Washington", "Eugene, Oregon, USA"))
    
if __name__ == "__main__":
    main()