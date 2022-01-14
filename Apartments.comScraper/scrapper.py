# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 14:18:42 2021

@author: MarianaMaroto
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


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


def parse_different_links(url):
    
  fields = {}
  fields['data'] = []

  """For every city page, iterate over the number of pages the city has, UPDATE RANGE """
  
  for i in range(1,29):

    url_final = url+str(i)+'/'
    print(url_final)

    # read the current page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    page = requests.get(url_final, headers=headers, timeout = 10)

    # soupify the current page
    soup = BeautifulSoup(page.content, 'html.parser')

    all_links = soup.select('.property-title-wrapper')
    """For every page, iterate over every listing"""
    counter = 1
    for page in all_links:
        print(counter)
        counter = counter + 1
        link = page.find('a').attrs['href']
        fields['data'].append(parse_apartment_information(url = link))

  return fields

austin_zip_codes=[
78613,78617,78641,78653,
78660,78681,78701,78702,
78703,78704,78705,78712,
78717,78719,78721,78722,
78723,78724,78725,78726,
78727,78728,78729,78730,
78731,78732,78733,78734,
78735,78736,78738,78739,
78741,78742,78744,78745,
78746,78747,78748,78749,
78750,78751,78752,78753,
78754,78756,78757,78758,
78759]
frames = []
for zipcode in austin_zip_codes:
    zipcode = str(zipcode)
    run = parse_different_links(url = f'https://www.apartments.com/austin-tx-{zipcode}/')
    df = pd.DataFrame(run['data'])
    frames.append(df)
    result = pd.concat(frames)
    result.to_csv('austin_tx.csv')


