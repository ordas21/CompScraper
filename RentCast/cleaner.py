import pandas as pd 
from datetime import date
from datetime import datetime

df = pd.read_csv('out.csv')
df = df.iloc[: , 1:]

dates = []
sqft_rent = []
distance = []
streets=[]
cities=[]
states=[]
zip_codes=[]
for_date=[]

dirty_rent = df.iloc[:,3]
dirty_address = df.iloc[:,2]
dirty_dates = df.iloc[:,4]
dirty_miles = df.iloc[:,6]
dirty_sqft = df.iloc[:,9]

for x in range(0, len(df)):
    for_date.append(date.today().strftime("%d/%m/%Y"))
    streets.append((dirty_address[x].splitlines())[0])
    cities.append(((dirty_address[x].splitlines())[1]).replace(',','').split()[0])
    states.append(((dirty_address[x].splitlines())[1]).replace(',','').split()[1])
    zip_codes.append(((dirty_address[x].splitlines())[1]).replace(',','').split()[2])
    distance.append("".join(_ for _ in dirty_miles[x] if _ in ".1234567890"))
    dates.append(datetime.strptime(((dirty_dates[x]).splitlines()[0].replace(',','')), '%b %d %Y').strftime('%Y-%m-%d'))    
    try:
        sqft_rent.append(("".join(_ for _ in (dirty_rent[x]).splitlines()[1] if _ in ".1234567890")))
    except:
        sqft_rent.append('')
        
df2=pd.DataFrame()
df2['for_date']=for_date
df2['abbreviation'] = df.iloc[:,1]
df2['unit_type'] = df.iloc[:,2]
df2['address']=streets
df2['city']=cities
df2['state']=states
df2['zip_code']= zip_codes
df2['bedrooms'] = df.iloc[:,8]
df2['bathrooms'] = df.iloc[:,9]
df2['listing_date']=dates
df2['price_sqft']=sqft_rent
df2['distance']= distance
#df.drop(df.columns[[3,2,4,6,9]],axis=1,inplace=True)
df2.to_csv('cleaned(rentcast).csv')

