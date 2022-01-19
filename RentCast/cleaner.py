import pandas as pd
import uuid
from datetime import date
from datetime import datetime
import numpy as np

col_list = ['abbreviation','unit_type','address','rent','date','distance','bed','bath','sqft','comp_type']
df = pd.read_csv('raw(rentcast).csv')
df = df.iloc[: , 1:]
today = (date.today().strftime("%Y-%m-%d"))
current_utc = datetime.utcnow()

dates = []
sqft_rent = []
distance = []
streets=[]
cities=[]
states=[]
zip_codes=[]
for_date=[]
ingest_time=[]
data_source=[]
comp_id=[]
sqft = []
rent= []
beds= []

for x in range(0, len(df)):
    ingest_time.append(current_utc)
    for_date.append(today)
    comp_id.append(uuid.uuid4())
    data_source.append('rentcast')
    streets.append((df['address'][x].splitlines())[0])
    cities.append(((df['address'][x].splitlines())[1]).split(',')[0])
    states.append(((df['address'][x].splitlines())[1]).split(',')[1].split()[0])
    zip_codes.append((df['address'][x])[-5:])
    if df['bed'][x] == 'Studio' or df['bed'][x] == 'studio' :
        beds.append(0)
    elif not str(df['bed'][x]):
        beds.append(0)
    else:
        beds.append(df['bed'][x])
    try:
        rent.append(((df['rent'][x]).splitlines()[0]).replace(',','').replace('$',''))
    except:
        rent.append((df['rent'][x]).splitlines()[0]).replace('$','')
    try:
        sqft.append((df['sqft'][x]).replace(',',''))
    except:
        sqft.append(df['sqft'][x])
    distance.append("".join(_ for _ in df['distance'][x] if _ in ".1234567890"))
    dates.append(datetime.strptime(((df['date'][x]).splitlines()[0].replace(',','')), '%b %d %Y').strftime('%Y-%m-%d'))    
    try:
        sqft_rent.append(("".join(_ for _ in (df['rent'][x]).splitlines()[1] if _ in ".1234567890")))
    except:
        sqft_rent.append('')
        
df2=pd.DataFrame()
df2['for_date']= for_date
df2['for_date'] = pd.to_datetime(df2['for_date'], format = "%Y-%m-%d" )
df2['comp_id'] = comp_id
df2['data_source'] = data_source
df2['abbreviation'] = df['abbreviation']
df2['unit_type'] = df['unit_type']
df2['address']=streets
df2['city']=cities
df2['state']=states
df2['zip_code']= zip_codes
df2['bedrooms'] = beds
df2['bathrooms'] = df['bath']
df2['listing_date']= dates
df2['listing_date'] = pd.to_datetime(df2['listing_date'], format = "%Y-%m-%d" )
df2['rent_monthly'] = rent
df2['sqft'] = sqft
df2['price_sqft']=sqft_rent
df2['distance']= distance
df2['ingest_time']=  ingest_time
df2['ingest_time'] = pd.to_datetime(df2['ingest_time'])
#df2['bathrooms'].astype(np.float).astype("int32")
#df2['bedrooms'].astype(np.float).astype("int32")
#df2['price_sqft'].astype('float64')
df2['zip_code'].astype('int64')
df2['distance'].astype('float64')
print(df2.dtypes)
df.drop(df.columns[[3,2,4,6,9]],axis=1,inplace=True)
df2.to_csv('rentcastcleaned.csv')
