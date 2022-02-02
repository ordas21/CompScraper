import pandas as pd
import requests
import json
import urllib
from art import tprint
from geopy.distance import geodesic
import re
import numpy as np
col_list = ['rent','address','bedrooms','bathrooms','size','lat','lon']
df = pd.read_csv('data/austin_tx_16_01_2022.csv', usecols =col_list)


tprint('COMPS')
address = input('Enter Address: ')
bed_count = input('Enter Beds: ')
bath_count = input('Enter Baths: ')
sqft_input = float(input('Enter Squarefootage: '))


def get_coordinates(address):
    base_url= "https://maps.googleapis.com/maps/api/geocode/json?"
    AUTH_KEY = "AIzaSyBWuXecwD1vwKyTova-qZBbJ8QKiesEMlg"
    parameters = {"address": str(address),'key': AUTH_KEY}
    r = requests.get(f"{base_url}{urllib.parse.urlencode(parameters)}")
    if r.status_code not in range(200, 299):
        lat = None
        lng = None
    try:
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
    except:
        pass
    return lat, lng

def get_distance(lat1,lon1,lat2,lon2):
    R = 6373.0
    lat1 = radians(52.2296756) #home    
    lon1 = radians(21.0122287) #home
    lat2 = radians(52.406374) #target
    lon2 = radians(16.9251681) #target
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    miles = distance * 0.621371
    return miles

comps = []
lat1, lon1 = get_coordinates(address)
lat2 = df['lat']
lon2 = df['lon']

for x in range(0,len(df)):
    origin=(lat1,lon1)
    dist=(lat2[x],lon2[x])
    if bed_count == df['bedrooms'][x] and bath_count == df['bathrooms'][x]:
        high_sqft = int(sqft_input * 1.2)
        low_sqft = int(sqft_input * .8)
        target_size = re.sub("[^\d\.]", "", str(df['size'][x]))
        if target_size:
            if int(target_size) in range(low_sqft,high_sqft):
                distance = geodesic(origin, dist).miles
                if distance < 1:
                    comp = [[df['address'][x]],[int((df['rent'][x]).replace(',',''))],["{:.2f}".format(distance)],[df['bedrooms'][x]],[df['bathrooms'][x]],[df['size'][x]]]
                    comps.append(comp)

rents= []
for x in range(0,len(comps)):
    rents.append(comps[x][1])
print('Average Rent for Comparable: ', np.mean(rents))

for comp in comps:
    print(comp)

