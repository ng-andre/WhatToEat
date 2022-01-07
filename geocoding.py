import requests

postal_code = 542308

API_KEY = "AIzaSyDbd8nrqxr6y4ys59aXVDxYZLcSNH8EOG8"
geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={postal_code}&key={API_KEY}'
geocode_payload = {}
geocode_headers = {}
jsonResponse = requests.request("GET", geocode_url, headers=geocode_headers, data=geocode_payload).json()

lat = jsonResponse["results"][0]["geometry"]["location"]["lat"]
long = jsonResponse["results"][0]["geometry"]["location"]["lng"]