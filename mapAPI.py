import geocoding
from math import sin, cos, sqrt, atan2, radians
import place


def calculatedistance(x1, x2, y1, y2):
    R = 6373.0
    lat1 = radians(x1)
    lon1 = radians(y1)
    lat2 = radians(x2)
    lon2 = radians(y2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c * 1000
    return distance


placeResults = place.results
placeDetails = place.storeDetails

for i in range(len(placeResults)):
    placeLat = placeResults[i]["geometry"]["location"]["lat"]
    placeLong = placeResults[i]["geometry"]["location"]["lng"]
    dist = calculatedistance(geocoding.lat, placeLat, geocoding.long, placeLong)
    if dist < 1500:
        name = placeResults[i]["name"]
        formattedAddress = placeResults[i]["formatted_address"]
        placeDetails[name] = formattedAddress

for key in placeDetails:
    print("NAME: " + key + "   LOCATION: " + placeDetails[key])
