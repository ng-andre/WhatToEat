import requests
import geocoding

API_KEY = "AIzaSyDbd8nrqxr6y4ys59aXVDxYZLcSNH8EOG8"
search = "Vegan"
radius = 1000
type = "Restaurant"

query_url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={search}&sensor=true&location={geocoding.lat},{geocoding.long}&radius={radius}&type={type}&key={API_KEY}'

place_payload = {}
place_headers = {}
jsonResponse = requests.request("GET", query_url, headers=place_headers, data=place_payload).json()
results = jsonResponse["results"]

# dict to store name and location of the nearby restaurants
storeDetails = {}