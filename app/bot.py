from imfs import read_country, read_data, get_the_urls,scrap_organic_links,scrap_sponsored_links, headers_usa
import requests
from bs4 import BeautifulSoup
from operator import attrgetter
import requests
import regex as re
import pandas as pd
from datetime import datetime
import pymongo

# --- It will get all urls with pages
def mainScraper():
    print('running')
    country = read_country()
    url_list=get_the_urls(country=country)
    print(url_list)
    for url in url_list:
        advertised_asins = []
        sponsored_products = []
        organic_products = []
        for x in range(1,8):
            url_with_page = url[0] + str(x)
            print(url_with_page)
            r = requests.get(url_with_page,  headers=headers_usa)
            soup = BeautifulSoup(r.content, 'html.parser')
            products = soup.select('div[data-asin]')
            def product_info(products):
                for i in products:
                    try:
                        price = i.find('span', class_="a-offscreen").text
                    except:
                        price = None
                    if price:
                        try:    
                            review_count = i.find('span', class_='a-size-base s-underline-text').text
                        except:
                            review_count = 'N/A'
                        try:
                            tag = i.find('span', class_='a-color-secondary').text
                        except:
                            tag ='Organic'
                        try:
                            link = i.find('a', class_='a-link-normal s-no-outline', href=True)['href']
                        except:
                            link = '/RUBFAC-Assorted-Balloons-Decoration-Birthday/dp/B07WGXTKGY/ref=sr_1_2_sspa?crid=IK0V17JVE2DJ&keywords=balloons&qid=1659976353&s=toys-and-games&sprefix=ballo%2Ctoys-and-games%2C516&sr=1-2-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyQzYwWFNLVVlZM09BJmVuY3J5cHRlZElkPUEwMDM3MzczMzBXVlM1OEZPN0VKOSZlbmNyeXB0ZWRBZElkPUExMDM3ODQ3M0dQMTlJVFlEMU5HRCZ3aWRnZXROYW1lPXNwX2F0ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU='
                        try:
                            asin = re.findall(r"%2Fdp%2F(.+)%2Fre", link)[0]
                        except:
                                try:
                                    asin = re.findall(r"/dp/(.+)/", link)[0]
                                except:
                                    asin = 'N/A'
                        
                        try:    
                            title = i.find('h2', class_='a-size-mini a-spacing-none a-color-base s-line-clamp-4').text
                        except:
                            title = 'N/A'
                        date = datetime.today()
                        if tag == 'Sponsored':
                            sponsored_products.append([asin,title, price,review_count, 'Sponsored', date])
                        else:
                            organic_products.append([asin,title, price,review_count ,'Organic', date])
            product_info(products=products)
            scrap_sponsored_links(sponsored_products=sponsored_products, advertised_list=advertised_asins)
            scrap_organic_links(organic_products=organic_products, advertised_list=advertised_asins)
            all_products = organic_products + sponsored_products
            myclient = pymongo.MongoClient("mongodb://host.docker.internal:27017/")
            for i in all_products:
                mydb = myclient['AmazonProductData']
                mycol = mydb[url[1]]
                mydict = {'ASIN':i[0], 'Title':i[1], 'Price':i[2], 'ReviewCount':i[3], 'Category':i[4], 'Date':i[5], 'Country':i[6], 'Position':i[7], 'BSR':i[8], 'Details':i[9]}
                x = mycol.insert_one(mydict)
            for i in advertised_asins:
                mydb = myclient['AmazonProductData']
                mycol = mydb['Advertised Asins for : '+url[1]]
                x = mycol.insert_one(i)
        
if __name__ == '__main__':
    mainScraper()
            