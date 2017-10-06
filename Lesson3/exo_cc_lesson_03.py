#!/usr/bin/python3.5

import json
import requests
import numpy as np
import pandas as pd

major_cities = ['Lyon', 'Paris', 'Marseille', 'Dijon']
cities_len = len(major_cities)

key = "AIzaSyC810c9HsAD_RpyrhBThgZmtiOnRB1Jvyw"
url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={0}&destinations={1}&key={2}"

results = np.zeros((cities_len, cities_len))
for index1, city1 in enumerate(major_cities):
    for index2, city2 in enumerate(major_cities):
        if city1 == city2:
            continue
        response = requests.get(url.format(city1, city2, key))
        json_response = json.loads(response.text)
        distance = json_response['rows'][0]['elements'][0]['distance']['value']
        results[index1, index2] = int(distance)

df = pd.DataFrame(results)
df.columns = major_cities
df.to_csv("distances.csv")
