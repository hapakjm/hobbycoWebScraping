"""
Created on February 17, 2023

@Title: Web Scraping for Hobbyco
@author: Kelvin Hapa
@email: hapakjm@gmail.coml


Requirements:

async-generator==1.10
attrs==22.2.0
certifi==2022.12.7
cffi==1.15.1
charset-normalizer==3.0.1
clips==1.1.0
clipspy==1.0.0
colorama==0.4.6
h11==0.14.0
idna==3.4
numpy==1.24.1
outcome==1.2.0
packaging==23.0
pandas==1.5.2
pycparser==2.21
pyodbc==4.0.35
PySocks==1.7.1
python-dateutil==2.8.2
python-dotenv==0.21.0
pytz==2022.7
requests==2.28.2
selenium==3.141.0
six==1.16.0
sniffio==1.3.0
sortedcontainers==2.4.0
tqdm==4.64.1
trio==0.22.0
trio-websocket==0.9.2
urllib3==1.26.14
webdriver-manager==3.8.5
wsproto==1.2.0


Description:

Web scraping for https://www.hobbyco.com.au/

Extract:
1. Product name
2. SKU
3. Price
4. Rating
5. In-stock status

For Products:
1. Traxxas RC cars
2. Tamiya Model Kits


Note:
After the website completely loads its content,
there will be a 10 seconds delay and
wait for a popup (Subscription popup) to appear,
after the popup appeared,
click on a blank space in the website
to remove the popup.
You must do this to avoid error.
If you successfully remove the popup within the 10 seconds delay,
the code will run smoothly.
"""


#-------------------------------------------------------------------------------------#

## Python Libraries

from os import system
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import pandas as pd


#-------------------------------------------------------------------------------------#


## Functions

def clickBtnByXpath(xpath, sleep):
    btn = driver.find_element_by_xpath(xpath)
    text = btn.text
    btn.click()
    time.sleep(sleep)

    return text

def clickBtnByLinkText(text, sleep):
    btn = driver.find_element_by_link_text(text)
    text = btn.text
    btn.click()
    time.sleep(sleep)

    return text


def getProdTypeXpaths(collection_link, brand_xpath):
    prod_type_xpaths = []

    filter_btn_xpath = '//*[@id="CollectionAjaxContent"]/div/div/div[2]/div[2]/div/div[1]/div[1]/div[1]/button'
    brand_btn_xpath = '//*[@id="FilterDrawer"]/div/div[2]/form/div[1]/div/button'
    prod_type_btn_xpath = '//*[@id="FilterDrawer"]/div/div[2]/form/div[2]/div/button'
    prod_type_box_xpath = '//*[@id="SidebarDrawer-2-filter-product-type"]/div/ul/li[@class="tag"]'

    driver.get(collection_link)
    time.sleep(3)

    clickBtnByXpath(filter_btn_xpath, 1)
    clickBtnByXpath(brand_btn_xpath, 1)
    clickBtnByXpath(brand_xpath, 3)
    clickBtnByXpath(filter_btn_xpath, 1)
    clickBtnByXpath(prod_type_btn_xpath, 1)

    parent_element = driver.find_elements_by_xpath(prod_type_box_xpath)

    cntr = 1
    for list in parent_element:
        xpath = prod_type_box_xpath + f'[{cntr}]/label/span[2]/span'
        prod_type_xpaths.append(xpath)
        cntr += 1

    return prod_type_xpaths


def selectFilter(collection_link, brand_xpath, prod_type_btn):
    filter_btn_xpath = '//*[@id="CollectionAjaxContent"]/div/div/div[2]/div[2]/div/div[1]/div[1]/div[1]/button'
    brand_btn_xpath = '//*[@id="FilterDrawer"]/div/div[2]/form/div[1]/div/button'
    prod_type_btn_xpath = '//*[@id="FilterDrawer"]/div/div[2]/form/div[2]/div/button'
   
    driver.get(collection_link)
    time.sleep(3)

    clickBtnByXpath(filter_btn_xpath, 1)
    clickBtnByXpath(brand_btn_xpath, 1)
    brand = clickBtnByXpath(brand_xpath, 3)
    clickBtnByXpath(filter_btn_xpath, 1)
    clickBtnByXpath(prod_type_btn_xpath, 1)
    prod_type = clickBtnByXpath(prod_type_btn, 3)

    return brand, prod_type


def extractData(date, company, category, brand, type):
    # print(f'Page {page[0]}')
    products_box = driver.find_elements_by_xpath('//*[@id="CollectionAjaxContent"]/div/div/div[2]/div[2]/div/div[1]/div[2]/div')

    for div in products_box:
        id = div.get_attribute('data-product-id')
        url = div.find_element_by_xpath('./div/a').get_attribute('href')
        name = div.find_element_by_xpath('./div/a/div[2]/div[1]').text
        price_box = div.find_elements_by_xpath('./div/a/div[2]/div[3]/span')
        
        if price_box == []:
            sale_price = div.find_element_by_xpath('./div/a/div[2]/div[3]').text
            reg_price = sale_price
            disc = "$0"
        else:
            sale_price = price_box[2].text
            reg_price = price_box[1].text
            disc = price_box[3].text

        data['Date'].append(date)
        data['ID'].append(id)
        data['Name'].append(name)
        data['Sale_Price'].append(sale_price)
        data['Reg_Price'].append(reg_price)
        data['Discount'].append(disc)
        data['Collection'].append(category)
        data['Brand'].append(brand)
        data['Type'].append(type)
        data['Company'].append(company)
        data['URL'].append(url)

        data_count[0] += 1
        # print('Data: ', data_count[0])

    changePage(date, company, category, brand, type)


def changePage(date, company, category, brand, type):
    next_btn = driver.find_elements_by_xpath('//a[@title="Next"]')

    if next_btn != []:
        next_btn[0].click()
        page[0] += 1
        time.sleep(3)
        extractData(date, company, category, brand, type)
    else:
        page[0] = 1


#-------------------------------------------------------------------------------------#


## Initialize data dictionary

data = {
    'Date': [],
    'ID': [],
    'Name': [],
    'Sale_Price': [],
    'Reg_Price': [],
    'Discount': [],
    'Collection': [],
    'Brand': [],
    'Type': [],
    'Company': [],
    'URL': [],
    'SKU': [],
    'SKU_Formatted': [],
    'Rating': [],
    'In_Stock': [],
    'In_Stock_Status': [],
    'Reviews': []
}

date = datetime.today()
company = 'Hobbyco'

page = [1]
data_count = [0]


#-------------------------------------------------------------------------------------#


## open browser

system('cls')

website = 'https://www.hobbyco.com.au'

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
driver.get(website)

system('cls')
print('Opening browser.')

time.sleep(10)


#-------------------------------------------------------------------------------------#


## extract Tamiya Model Kits data

print('Extracting data from Tamiya Model Kits')

model_kits_link = 'https://www.hobbyco.com.au/collections/model-kits'
tamiya_brand_xpath = '//*[@id="SidebarDrawer-1-filter-brand"]/div/ul/li[43]/label/span[2]'
tamiya_prod_type_xpaths = getProdTypeXpaths(model_kits_link, tamiya_brand_xpath)

for prod_type_xpath in tamiya_prod_type_xpaths:
    brand, prod_type = selectFilter(
        model_kits_link,
        tamiya_brand_xpath,
        prod_type_xpath
    )

    collection = 'MODEL KITS'
    brand = 'TAMIYA'

    print(brand, prod_type)

    extractData(date, company, collection, brand, prod_type)


#-------------------------------------------------------------------------------------#


## extract Traxxas Radio Control data

print('Extracting data from Traxxas Radio Control')

radio_control_link = 'https://www.hobbyco.com.au/collections/rc-slot-cars'
traxxas_brand_xpath = '//*[@id="SidebarDrawer-1-filter-brand"]/div/ul/li[30]/label/span[2]'
traxxs_prod_type_xpaths = getProdTypeXpaths(radio_control_link, traxxas_brand_xpath)

for prod_type_xpath in traxxs_prod_type_xpaths:
    brand, prod_type = selectFilter(
        radio_control_link,
        traxxas_brand_xpath,
        prod_type_xpath
    )

    collection = 'RADIO CARS'
    brand = 'TRAXXAS'

    print(brand, prod_type)

    extractData(date, company, collection, brand, prod_type)


#-------------------------------------------------------------------------------------#


## extract SKU, rating, in-stock status

url_visit = 0
for ind, url in enumerate(data['URL']):
    driver.get(url)
    url_visit += 1
    print(f'Data {url_visit}/{data_count[0]}')
    time.sleep(3)

    sku = driver.find_element_by_xpath('//p[@class="product-single__sku"]').text
    rating = 0
    in_stock = driver.find_element_by_xpath('//span[@data-product-inventory=""]').text

    sku_temp = ''
    if data['Brand'][ind] == 'TRAXXAS':
        for ind2, char in enumerate(sku):
            if ind2 == 2:
                sku_temp += 'A'
            elif ind2 == 8:
                sku_temp += '-'
                sku_temp += char
            else:
                sku_temp += char
    else:
        sku_temp = sku

    data['SKU'].append(sku)
    data['SKU_Formatted'].append(sku_temp)
    data['Rating'].append(rating)
    data['In_Stock'].append(in_stock)
    data['In_Stock_Status'].append('YES')
    data['Reviews'].append('No reviews')
    print(sku, sku_temp, rating, in_stock)


#-------------------------------------------------------------------------------------#


## exit browser

print('Closing browser.')
driver.quit()


#-------------------------------------------------------------------------------------#


## save data into a dataframe

print('Saving data to a dataframe.')
df = pd.DataFrame(data)


#-------------------------------------------------------------------------------------#


## save dataframe into a csv file the initial data

print('Saving initial data to a CSV file.')
df.to_csv('Hobbyco_'+str(date)[0:10]+'_initial'+'.csv', index=False, encoding='utf-8')


#-------------------------------------------------------------------------------------#


## drop uneccessary columns and duplicated data

print('Cleaning data.')
df_hobbyco = df[['Date',  'Company', 'Name', 'Sale_Price', 'SKU_Formatted', 'Rating', 'In_Stock_Status', 'Reviews']]
df_hobbyco.rename(columns = {'Sale_Price':'Price', 'SKU_Formatted':'SKU', 'In_Stock_Status':'In_Stock'}, inplace = True)
df_hobbyco.drop_duplicates()


#-------------------------------------------------------------------------------------#


## save dataframe into a csv file the final data

print('Saving final data to a CSV file.')
df_hobbyco.to_csv('Hobbyco_'+str(date)[0:10]+'.csv', index=False, encoding='utf-8')