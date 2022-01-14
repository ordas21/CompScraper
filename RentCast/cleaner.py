import pandas as pd 

col_list=['abbreviation','unit-type','comp-address','rent','listing-date','similarity','distance','beds','baths','sqft','type']
df = pd.read_csv('rencast(data).csv', usecols =col_list)

days = []
dates = []
monthly = []
sqft_rent = []
distance = []
for x in range(0, len(df)):
    
    rent_list = (df['rent'][x]).splitlines()
    date_list =  (df['listing-date'][x]).splitlines()
    print(rent_list)
    #listing_date = date_list[0]
    dist = "".join(_ for _ in df['distance'][x] if _ in ".1234567890")
    monthly_rent = "".join(_ for _ in rent_list[0] if _ in ".1234567890")
    try:
        sqftrent = "".join(_ for _ in rent_list[1] if _ in ".1234567890")
    except:
        sqftrent = ''
    days_ago = "".join(_ for _ in date_list[1] if _ in ".1234567890")
    days.append(days_ago)
    sqft_rent.append(sqftrent)
    monthly.append(monthly_rent)
    distance.append(dist)

df['monthly-rent']=monthly
df['days-ago']=days
df['price-sqft']=sqft_rent
df['dist']= distance
df.drop(columns=['rent','listing-date','distance'])

df.to_csv('cleaned(rentcast).csv')
