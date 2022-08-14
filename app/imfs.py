import pandas as pd
import regex as re
import csv
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pymongo
myclient = pymongo.MongoClient("mongodb://host.docker.internal:27017/")
sponsored_products = []
organic_products = []

# --- It  will read the country url
def read_country():
    x=pd.read_csv('country.csv')
    col=x['country']
    list = col.to_list()
    country = list[0]
    return country

# --- It will read all the data
def read_data():
    x=pd.read_csv('data.csv')
    col=x['keywords']
    keywords = col.to_list()
    return keywords

# --- It will get main urls for each keyword
def get_the_urls(country):
    keywords=read_data()
    url_list = []
    usa = 'com'
    cana = 'ca'
    if country == 'usa':
        for keyword in keywords:
            url = 'https://www.amazon.{0}/s?k={1}&page='.format(usa, keyword)
            url_list.append([url, keyword])
        return url_list
    if country == 'canada':
        for keyword in keywords:
            url = 'https://www.amazon.{0}/s?k={1}&page='.format(cana, keyword)
            url_list.append([url, keyword])
        return url_list

# --- get the information about products on each page
def scrap_sponsored_links(sponsored_products, advertised_list):
    country = read_country()
    for i in sponsored_products:
        url = 'https://www.amazon.com/dp/'+i[0]
        print(i[-2])
        r = requests.get(url, headers=headers_usa)
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            details = soup.find('div', id='feature-bullets').text
        except:
            details = 'N/A'
        try:    
            table = soup.find('table', id='productDetails_detailBullets_sections1')
        except:
            table = 'N/A'
        # To Grab best seller rank
        try:
            string =  re.findall(r"[<]\w+[>](#\d+.+</tr>)", str(table))
            BSR = '<tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Best Sellers Rank </th> <td> <span>  <span>'+ string[0] 
            BSR = BeautifulSoup(BSR, 'html.parser').find('td').find_all('span')
            bs_rank = ''
            for _ in BSR:
                list =  _.text.split('(')
                bs_rank += list[0] + ' '
        except:
            bs_rank = 'N/A'

        # Spnosered links on page
        sp_links = soup.find_all('a', class_='a-link-normal adReviewLink a-text-normal', href=True)
        for li in sp_links:
            asin = re.findall(r"url=%2Fdp%2F(.+)%2Fre", li['href'])[0]
            main_asin = i[0]
            record = {'MainASIN':main_asin, 'SponsoredASINs':asin}
            advertised_list.append(record)
        
            
        index = sponsored_products.index(i)+1
        details = details.replace('\n','   ')
        i.extend([country, index, bs_rank, details])

#--- get the information about products on each page 
def scrap_organic_links(organic_products, advertised_list):
        country = read_country()
        for i in organic_products:
            url = 'https://www.amazon.com/dp/'+i[0]
            print(i[-2])
            r = requests.get(url, headers=headers_usa)
            soup = BeautifulSoup(r.content, 'html.parser')
            try:
                details = soup.find('div', id='feature-bullets').text
            except:
                details = 'N/A'
            try:    
                table = soup.find('table', id='productDetails_detailBullets_sections1')
            except:
                table = 'N/A'
            # To Grab best seller rank
            try:
                string =  re.findall(r"[<]\w+[>](#\d+.+</tr>)", str(table))
                BSR = '<tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Best Sellers Rank </th> <td> <span>  <span>'+ string[0] 
                BSR = BeautifulSoup(BSR, 'html.parser').find('td').find_all('span')
                bs_rank = ''
                for _ in BSR:
                    list =  _.text.split('(')
                    bs_rank += list[0] + ' '
            except:
                bs_rank = 'N/A'

            # Spnosered links on page
            sp_links = soup.find_all('a', class_='a-link-normal adReviewLink a-text-normal', href=True)

            
            for li in sp_links:
                asin = re.findall(r"url=%2Fdp%2F(.+)%2Fre", li['href'])[0]
                main_asin = i[0]
                record = {'MainASIN':main_asin, 'SponsoredASINs':asin}
                advertised_list.append(record)
            
            index = organic_products.index(i)+1
            details = details.replace('\n','   ')
            i.extend([country, index, bs_rank, details])


headers_usa = {
    "Referer": "https://www.amazon.com/",
    "cookie": "session-id=135-0293763-9719807; ubid-main=135-3792879-6882303; av-timezone=America/Los_Angeles; sst-main=Sst1|PQHZJT2Vy3YlwS_Rud8Dzy0NB-wBZ_OcnOfH7swPrK2WXOOyHJigycwNeZcM7sDUrHySecSTHB82PgIuLmc_Kno1LxiMtxNIAhHKkmdeXgoXZaKUalCGBI5ZT4TNCZ7l5TEqB1iJsmOv7cmHRmD94tC3UX4NphkRkVU7PE5dQZuGeNKBlOe9IZHvfoj--mjSEFMpXQ6CJm2pN3fsnkkYWbf6eqBacZ1xw24QUeKYAYLlVUqIJGSaXkzSFjRn9domboL1; i18n-prefs=USD; session-id-time=2082787201l; skin=noskin; session-token=+JeiG65+COd/VFLD2CPSeBEGlnqKUm1VTNaqjCzDqIfRXe0VIAs7EhA9EZVBLjU+2kuMxdti4TPAXydevrcKVQpNOISROVFPxYmTN8fFMrK2EKhysHLMYmDhi+J+2tl57uFYQFXiqtwCAxI5SO4rpsrnBgWlbnI/m3qAGTp+YLNYmEf5ulWWT+TsljRJTolNwNFR0Ut+RPs+b3APVWZFBg6kktt1paDp; csm-hit=tb:s-W0AZ534E2BPQ3DFTB07C|1659767835188&t:1659767836937&adb:adblk_no",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}
