"""
Created on 1/13/2022
Author: @sebastianordas
"""
import time
import psycopg2
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
#Postgres Connection
start = time.time()
conn = psycopg2.connect(
   database="postgres", user='propdata_user', password='propdata_password', host='propdatadb.cmea3vckvopo.us-east-1.rds.amazonaws.com', port= '5432')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('''
                SELECT DISTINCT ON (unit_type) 
                    prop.address,
                    prop.city,
                    prop.state,
                    o.abbreviation as abb,
                    unit_number as unit,
                    unit_type,
                    sqft,
                    bedrooms as bed ,
                    bathrooms as bath,
                    market_rent as mkt,
                    actual_rent as act
                FROM dev.occupancy_unit_description o 
                JOIN dev.properties prop ON prop.abbreviation = o.abbreviation
                WHERE unit_type IN 
                    (
                    SELECT unit_type
                    FROM dev.occupancy_unit_description
                    GROUP BY unit_type
                    HAVING COUNT(*) >= 5
                            )
                AND prop.property_type = 'Multi-Family'
                AND o.for_date = '2022-01-12'
                AND o.actual_rent > 0
                ''')
result = cursor.fetchall();
conn.close()
#Initialize Driver and Test Chrome
options = Options()
options.add_argument("--headless")
#options.add_experimental_option("debuggerAddress","localhost:9014")
driver = webdriver.Chrome(executable_path="chromedriver.exe",chrome_options=options)
driver.get('https://app.rentcast.io/login')
time.sleep(2)
driver.find_element_by_id("signInEmail").send_keys('fbasca@rex.com')
driver.find_element_by_id("signInPassword").send_keys('pimpincomps')
driver.find_element_by_xpath("/html/body/ngb-modal-window/div/div/rc-auth-modal/div/div/form/div[2]/rc-button-spinner/button").click()
col_list = ["address","city","state","abb","unit","unit_type","sqft","bed","bath","mkt","act"]
df = pd.DataFrame.from_records(result, columns=col_list)
table_data = []
address_string = ''
address = []
rentcast = []
comp_list = []
count = 0
for x in range(0, len(df)):
    address_split = str(df['address'][x]).split()
    for word in range(1, len(address_split)):
        fixed_word = '%20'+str(address_split[word])
        address.append(fixed_word)
    address.insert(0,address_split[0])
    address_string=''.join(address)
    address =[]
    abbreviation = df['abb'][x]
    unit = df['unit'][x]
    unit_type = df['unit_type'][x]
    city = df['city'][x]
    state = df['state'][x]
    bed = str(df['bed'][x])
    bath = str(df['bath'][x])
    sqft = str(df['sqft'][x])
    mkt = df['mkt'][x]
    act = df['act'][x]
    url = f'https://app.rentcast.io/app?address={address_string},%20{city},%20{state}&bedrooms={bed}&bathrooms={bath}&area={sqft}'
    #Table Extract
    connected = False
    while not connected:
        try:
            time.sleep(.5)
            driver.refresh()
            driver.get(url)
            WebDriverWait(driver, 70).until(EC.presence_of_element_located((By.XPATH,"/html/body/rc-root/rc-app-layout/main/div/div/div/div/div/rc-property-search/rc-property-data/div/div/div[1]/div[2]/rc-property-data-comps-table/div/div[2]/table/tbody/tr")))
            connected = True
        except:
            print("Timeout: Trying Again")
            pass
    count += 1
    print(count)
    rows = len(driver.find_elements(By.XPATH,"/html/body/rc-root/rc-app-layout/main/div/div/div/div/div/rc-property-search/rc-property-data/div/div/div[1]/div[2]/rc-property-data-comps-table/div/div[2]/table/tbody/tr"))
    cols = 10
    for r in range(1, rows+1):
        comp = []
        comp.append(abbreviation)
        comp.append(unit_type)
        for p in range(2, cols+1):
            # obtaining the text from each column of the table
            value = driver.find_element(By.XPATH,"/html/body/rc-root/rc-app-layout/main/div/div/div/div/div/rc-property-search/rc-property-data/div/div/div[1]/div[2]/rc-property-data-comps-table/div/div[2]/table/tbody/tr["+str(r)+"]/td["+str(p)+"]").text
            comp.append(value)
        comp_list.append(comp)
        #print(comp_list)
        comp_df = pd.DataFrame(comp_list)
        comp_df.to_csv('out.csv')
    if count%11==0:
        print("sleeping...Zzzz")
        time.sleep(70)
end = time.time()
comp_df = pd.DataFrame(comp_list)
comp_df.to_csv('Comparables.csv')
runtime = end-start
print("Runtime: ",str(runtime))
