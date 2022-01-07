import googlemaps
import requests

API_KEY = "AIzaSyDbd8nrqxr6y4ys59aXVDxYZLcSNH8EOG8";
map_client = googlemaps.Client(API_KEY)

# nus location for testing
lat = 1.2966
long = 103.7764

radius = 1000
type = "restaurant"
url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius={radius}&type={type}&key={API_KEY}'

payload={}
headers = {}

jsonResponse = requests.request("GET", url, headers=headers, data=payload).json()
results = jsonResponse["results"]

# dict to store name and location of the nearby restaurants
storeDetails = {}

for i in range(len(results)):
    name = results[i]["name"]
    vicinity = results[i]["vicinity"]
    storeDetails[name] = vicinity

# for key in storeDetails:
#     print("NAME: " + key + "   LOCATION: " + storeDetails[key])



