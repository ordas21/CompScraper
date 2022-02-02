import os
import sys
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from multiprocessing.dummy import Pool  # This is a thread-based Pool
from multiprocessing import cpu_count
from datetime import datetime
from pyzipcode import ZipCodeDatabase
import psycopg2

def prettify_text(data):
    """Given a string, replace unicode chars and make it prettier"""
    data = str(data)
    # format it nicely: replace multiple spaces with just one
    data = re.sub(' +', ' ', data)
    # format it nicely: 
    data = re.sub('<li class="specInfo"> <span>','', data)
    # format it nicely: 
    data = re.sub('</span> </li>','', data)
    # format it nicely: replace multiple new lines with just one
    data = re.sub('(\r?\n *)+', ' ', data)
    # format it nicely: replace bullet with *
    data = re.sub(u'\u2022', '* ', data)
    # format it nicely: replace registered symbol with (R)
    data = re.sub(u'\xae', ' (R) ', data)
    # format it nicely: remove trailing spaces
    data = data.strip()
    # format it nicely: encode it, removing special symbols
    data = data.encode('utf8', 'ignore')

    return data.decode('UTF-8')

def get_last_updates(soup, fields):
    fields['last-updated'] = ''
    obj = soup.find('span', class_='lastUpdated')
    if obj is not None:
        update = obj.getText()
        update = prettify_text(update)
        fields['last-updated'] = update


def get_property_name(soup, fields):
    fields['name'] = ''
    obj = soup.find('h1', class_='propertyName')
    if obj is not None:
        name = obj.getText()
        name = prettify_text(name)
        fields['name'] = name

def get_property_main_info(soup, fields):
    fields['rent'] = ''
    fields['bedrooms'] = ''
    fields['bathrooms'] = ''
    fields['size'] = ''
    obj = soup.find_all('p', class_='rentInfoDetail')
    if obj is not None:
        if len(obj) > 0:
          if obj[0] is not None:
            rent = obj[0].getText()
            rent = prettify_text(rent)
            rent = rent.strip('$')
            fields['rent'] = rent
          
          if obj[1] is not None:
            bedrooms = obj[1].getText()
            bedrooms = prettify_text(bedrooms)
            bedrooms = bedrooms.strip(' bd')
            fields['bedrooms'] = bedrooms
          
          if obj[2] is not None:
            bathrooms = obj[2].getText()
            bathrooms = prettify_text(bathrooms)
            bathrooms = bathrooms.strip(' ba')
            fields['bathrooms'] = bathrooms
    
          if obj[3] is not None:
            size = obj[3].getText()
            size = prettify_text(size)
            fields['size'] = size


def get_description(soup, fields):
    fields['description'] = ''
    obj = soup.find('section', id="descriptionSection")
    if obj is not None:
        description = obj.getText()
        description = prettify_text(description)
        fields['description'] = description


def get_property_address(soup, fields):
    fields['address'] = ''
    obj = soup.find('div', class_='propertyAddressContainer')
    if obj is not None:
        address = obj.getText()
        address = prettify_text(address)
    fields['address'] = address

def get_features(soup, fields):
    fields['features'] = []
    obj = soup.find_all('li', class_='specInfo')
    if obj is not None:
      for feature in obj:
        feat= feature.getText()
        feat = prettify_text(feat)
        fields['features'].append(feat)

def get_scores(soup, fields):
    fields['walk score'] = ''
    fields['transit score'] = ''
    fields['bike score'] = ''
    obj = soup.find_all('div', class_='score')
    
    if obj is not None:
      
      if obj[0] is not None:
        walk = obj[0].getText()
        walk = prettify_text(walk)
        fields['walk score'] = walk
      
      if obj[1] is not None:
        transit = obj[1].getText()
        transit = prettify_text(transit)
        fields['transit score'] = transit

      if obj[2] is not None:
        bike = obj[2].getText()
        bike = prettify_text(bike)
        fields['bike score'] = bike



# setting up pet policy 
def get_pet_policy(soup, fields):
    fields['dogs_allowed'] = ''
    fields['cats_allowed'] = ''
    obj = soup.find_all('h4', class_='header-column')
    if obj is not None:
        obj  = [i.getText() for i in obj]
        if 'Dogs Allowed' in obj :
            fields['dogs_allowed'] = 'yes'
        if 'Cats Allowed' in obj :
            fields['cats_allowed'] = 'yes'


  
def parse_apartment_information(url):

    # read the current page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    page = requests.get(url, headers=headers)

    # soupify the current page
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.prettify()

    # the information we need to return as a dict
    fields = {}
    fields['id'] = url[-8:-1]
    fields['link'] = url

    # get the name of the property
    get_property_name(soup, fields)

    # get the main info
    get_property_main_info(soup, fields)

    # get the latest updates
    get_last_updates(soup, fields)

    # get the description section
    get_description(soup, fields)

    # get the address of the property
    get_property_address(soup, fields)

    # get the apt features
    get_features(soup, fields)
    
    # get walk score
    get_scores(soup, fields)

    # get pet policy
    get_pet_policy(soup, fields)

    return fields



#YOU FINSIHED HERE< COMPLETE WORK WITH PAGE RANGE
#
def parse_different_links(url):
    
  fields = {}
  fields['data'] = []
  links = []
  

  """For every city page, iterate over the number of pages the city has, UPDATE RANGE """
  try:
      headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
      page = requests.get(url, headers=headers, timeout = 10)
      soup = BeautifulSoup(page.content, 'html.parser')
      paging = soup.find("div",{"id":"placardContainer"}).find("span",{"class":"pageRange"}).text
      pg_len = [int(i) for i in paging.split() if i.isdigit()]
      start_page = pg_len[0]
      last_page = pg_len[1]
  except:
      start_page = 1
      last_page = 0

  for i in range(int(start_page),int(last_page) + 1):

    url_final = url+str(i)+'/'
    
    # read the current page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    page = requests.get(url_final, headers=headers, timeout = 10)

    # soupify the current page
    soup = BeautifulSoup(page.content, 'html.parser')

    all_links = soup.select('.property-title-wrapper')
    """For every page, iterate over every listing"""
    counter = 1
    
    for page in all_links:
        counter = counter + 1
        link = page.find('a').attrs['href']
        links.append(link)
        fields['data'].append(parse_apartment_information(url = link))
  return fields

def GetURL():
    conn = psycopg2.connect(
       database="postgres", user='propdata_user', password='propdata_password', host='propdatadb.cmea3vckvopo.us-east-1.rds.amazonaws.com', port= '5432')
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f'''
    SELECT Distinct city, p.state, zip
    FROM dev.resman_properties p 
    where for_date = '2022-01-20'
                    ''')
    result = cursor.fetchall();
    conn.close()

    locationsdf = pd.DataFrame.from_records(result, columns = ['city','state','zip'])
    zcdb = ZipCodeDatabase()
    zips = []
    url = []
    cities = []
    for x in range(0,len(locationsdf)):
        target_zip = locationsdf['zip'][x]
        for z in zcdb.get_zipcodes_around_radius(f'{target_zip}', 4):
            zips.append(z.zip)

    for z in zips:
        city = zcdb[z].city.replace(" ", "_").lower()
        cities.append(city)
        state = zcdb[z].state.lower()
        url.append(f'https://www.apartments.com/{city}-{state}-{z}/')
        
    return url

frames = []
urls= GetURL()
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y")
count = 0

for url in urls:
    count += 1
    progress = str(count)+'/'+str(len(urls))
    print(progress)
    run = parse_different_links(url)
    df = pd.DataFrame(run['data'])
    frames.append(df)
    result = pd.concat(frames)
    result.to_csv(f'austin_tx_{dt_string}.csv')
    
