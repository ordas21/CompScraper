import unidecode
import pandas as pd
import requests
import json
import urllib
col_list = ["address"]
df = pd.read_csv('austin_tx_31_01_2022.csv', usecols = col_list)
dirty_address = df['address']
    
def clean_address(dirty_address):
    updated_address = []
    for add in dirty_address:
        badtext = str(add)
        stripped = badtext.encode('ascii', 'ignore').decode('ascii')
        stripped = stripped.split("  ")
        updated_address.append(stripped[0])
    return updated_address
#Ignore for now WORK IN PROGRESS
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
    cords = str(lat)+','+str(lng)
    print(cords)
    return cords
def main(dirty_address):
    coordinates = []
    updated_address = clean_address(dirty_address)
    for address in updated_address:
        lat_lon = get_coordinates(address)
        coordinates.append(lat_lon)
    df['lat_lon'] = coordinates
    df.to_csv('austin_tx_lat_lon.csv')

main(dirty_address)
