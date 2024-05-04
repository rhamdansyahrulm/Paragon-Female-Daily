import time
from datetime import datetime, timedelta, date
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def convert_date(date_info):
    date_today = datetime.now()
    
    today_list_info = ["second", "minute", "a day ago", "hour"]
    if any([x in date_info for x in today_list_info]):
        the_date =  date_today.strftime("%d/%m/%y")
    elif "days ago" in date_info :
        delta = "".join([x for x in date_info if x.isdigit()])
        delta_date = date_today - timedelta(days=int(delta))
        the_date = delta_date.strftime("%d/%m/%y")
    else :
        the_date = datetime.strptime(date_info, "%d %b %Y").strftime("%d/%m/%y")
        
    return the_date

def get_data_product_scrap(soup, card_attr):
    all_reviews_list = soup.findAll('div', class_='review-card')
    
    all_reviews = []
    for reviews_card in all_reviews_list:
        one_review_card = []
        
        for key_attr, val_attr in card_attr.items():
            element = reviews_card.find(val_attr[0], class_=val_attr[1])
            
            if key_attr == 'is_recommended':
                text = "yes" if element else "No"
                
            elif key_attr == 'rating_star':
                text = 0
                for star in element.find_all('i', class_='icon-ic_big_star_full'):
                    text += 1
            
            elif key_attr == "review_date":
                date_info = element.text
                text = convert_date(date_info)
            
            elif key_attr == "usage_and_shop":
                for info in element.find_all('b'):
                    text = info.text if info else ""
                    one_review_card.append(text)
                
            else :
                text = element.text if element else ""
            
            if key_attr != "usage_and_shop":
                one_review_card.append(text)
        
        all_reviews.append(one_review_card)
    
    return all_reviews

def scraping_product_run(product_url):
    card_attr = {
        'age' : ['p', 'profile-age'],
        'description' : ['p', 'profile-description'],
        'review' : ['p', 'text-content'],
        'is_recommended' : ['i', 'icon-ic_thumbs_up'],
        'rating_star' : ['span', 'cardrv-starlist'],
        'review_date' : ['p', 'review-date'],
        'usage_and_shop' : ['div', 'information-wrapper'],
    }
    
    page_now = 0
    on_scrap = True
    
    all_reviews_list = []
    try :
        while on_scrap:
            page_now += 1
            product_page_url = product_url + f"?page={page_now}"
            
            driver = webdriver.Chrome()
            driver.get(product_page_url)
            soup = BeautifulSoup(driver.page_source, "html.parser")    
        
            page_reviews_list = get_data_product_scrap(soup, card_attr)
            all_reviews_list.extend(page_reviews_list)
            
            if len(all_reviews_list) == 0:
                on_scrap = False
    
    except:
        on_scrap = False
    
    column_name = list(card_attr.keys())[:-1] + ["usage_period", "purchase_point"]
    product_reviews = pd.DataFrame(all_reviews_list, columns=column_name)
    
    return product_reviews

product_reviews = scraping_product_run("https://reviews.femaledaily.com/products/moisturizer/sun-protection-1/emina/sun-protection-spf-30-pa")
