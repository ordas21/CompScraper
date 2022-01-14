import unidecode
import pandas as pd
import multiprocessing
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import requests
import json
import urllib

base_url= "https://maps.googleapis.com/maps/api/geocode/json?"
AUTH_KEY = "AIzaSyBWuXecwD1vwKyTova-qZBbJ8QKiesEMlg"


col_list = ["address"]
df = pd.read_csv('austin_tx.csv', usecols = col_list)
dirty_address = df['address']
updated_address = []


for add in dirty_address:
    badtext = str(add)
    stripped = badtext.encode('ascii', 'ignore').decode('ascii')
    stripped = stripped.split("  ")
    print(stripped[0])
    updated_address.append(stripped[0])


#Ignore for now WORK IN PROGRESS
"""
latitude = []
longitude = []
for address in updated_address:
    parameters = {"address": str(address),'key': AUTH_KEY}
    r = requests.get(f"{base_url}{urllib.parse.urlencode(parameters)}")
    if r.status_code not in range(200, 299):
        lat = None
        lng = None
    try:
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
        latitude.append(lat)
        longitude.append(lng)
    except:
        pass
df['lat'] = latitude
df['lon'] = longitude
"""

#THIS WORK OKAY FOR NOW
df['address']=updated_address
geolocator=Nominatim(user_agent='apptesdsvst1.1')
geocode = RateLimiter(geolocator.geocode,min_delay_seconds=.01)
pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

df['location'] = df['address'].pool.apply(geocode)
df['Lat'] = df['location'].apply(lambda x: x.latitude if x else None)
df['Lon'] = df['location'].apply(lambda x: x.longitude if x else None)
df.to_csv('austin_tx_lat_lon.csv')

