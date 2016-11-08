# proj5-leaflet
Author: Alex Brandenfels

Project 5 for CIS 399: A web app that displays intersections where numbered streets meet streets named after the president corresponding to that number (e.g. 1st and Washington, 2nd and Adams, ...)

## Overview
This app displays a Leaflet map centered on the user's location. It then uses Google's JavaScript geocoding API to reverse geocode the user's location, in order to find out the user's city, which is sent to the server. The server finds the relevant "presidential intersections" in that city, and sends their locations to the user, so that they can be displayed on the user's map. If the user mouses-over one of the presidential pins, a pop-up will display the intersection's name (e.g. "1st and Washington")

## Behind the scenes
The server uses Google's non-JavaScript geocoding API to find the locations of all the intersections. Google limits geocoding requests to 10 per second, so doing all 44 geocoding requests via the API takes a while. To get around this, all locations are cached, so that if the site has ever been used in a particular city before, the server doesn't have to use the slow geocoding API.

## Limitations
Due to the request rate limitations of the Google API, concurrent users could break the system if neither of their cities are already in the cache (also I'm not 100% sure the cache is thread safe). This could be solved by running all API requests in a single, separate thread, but that would be even more outside the scope of the assignment than I have already gone.

## Setup
Run "make install". Create a CONFIG.py from the CONFIG.base.py. Run flask_map.py.

## Working example
http://pres-streets.herokuapp.com/

Note that the above example can be very slow because it's running on the free tier.
