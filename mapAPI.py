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


def getFoodPlaces(search, type, lat, lng):
    placeResults = place.getPlaces(search, type, lat, lng)
    placeDetails = {}

    for i in range(len(placeResults)):
        placeLat = placeResults[i]["geometry"]["location"]["lat"]
        placeLong = placeResults[i]["geometry"]["location"]["lng"]
        dist = calculatedistance(lat, placeLat, lng, placeLong)
        if dist < 1500:
            name = placeResults[i]["name"]
            formattedAddress = placeResults[i]["formatted_address"]
            placeDetails[name] = formattedAddress
    return placeDetails

