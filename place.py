import os

import requests

# search = ""
radius = 1000
# type = "bar"


def getPlaces(search, type, lat, lng):
    API_KEY = os.getenv("API_KEY")
    query_url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={search}&sensor=true&location={lat},{lng}&radius={radius}&type={type}&key={API_KEY}'

    place_payload = {}
    place_headers = {}
    jsonResponse = requests.request("GET", query_url, headers=place_headers, data=place_payload).json()
    return jsonResponse["results"]

# dict to store name and location of the nearby restaurants
# storeDetails = {}

