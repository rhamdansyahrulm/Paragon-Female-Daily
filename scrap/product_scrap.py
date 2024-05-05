import time
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from google.cloud import bigquery
import google.auth.transport.requests
import google.oauth2.credentials
import pandas_gbq
from google.oauth2 import service_account


list_brand = ["wardah", "make-over", "emina", "kahf"]

def open_all_page(driver, soup):
    button_next_item = soup.findAll('div', class_='jsx-2571374240 section-button-products')[0]
    total_product = button_next_item.find("button", class_="jsx-6b0b767667fbe712").text.split(" ")[-1]
    total_click_next = round(int(total_product) / 16)
    
    for _ in range(total_click_next):
        try:
            next_item = driver.find_element(By.CSS_SELECTOR, '#button-load-more-products')
            next_item.click()
            time.sleep(0.5)
        except NoSuchElementException:
            continue
        
def get_data_scrap(column_format, driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    items = []
    all_items_list = soup.findAll('div', class_='jsx-1897565266 info-product')
    url_element = soup.findAll('a', class_='jsx-3793288165', href=True)
    img_product_div = soup.findAll('div', class_="jsx-1897565266 image-container")
    
    for i_item, item in enumerate(all_items_list):
        url = url_element[i_item]['href']
        url_split = url.split("/")
        category, sub_category, brand = url_split[4:7]
        
        img = img_product_div[i_item].find('img')['src']
        
        item_info = [brand, category, sub_category]
        item_info = list(map(lambda raw_x: "".join([x for x in raw_x if x.isdigit() == False]).replace("-", " "), item_info))
        
        for key, value in column_format.items():
            element = item.find(value[0], class_=value[1])
            
            if key == "total_review":
                key_value = element.text if element is not None else ""
                key_value = "".join(x for x in key_value if x.isdigit())
            else :
                key_value = element.text if element is not None else ""
                
            item_info.append(key_value)
        
        item_info.extend([url, img])
        item_info.insert(0, f"{item_info[0]}-{i_item}")
        items.append(item_info)
    
    return items
    
def run_scraping(brand):
    column_format = {
        'product_name'      : ['p', 'jsx-1897565266 fd-body-md-regular text-ellipsis two-line word-break'],
        'product_shade'     : ['p', 'jsx-1897565266 fd-body-md-regular text-ellipsis grey']
    }
    
    url = f"https://reviews.femaledaily.com/brands/product/"
    url_brand = os.path.join(url, brand)
    url_order = url_brand + "?order=newest"
    
    driver = webdriver.Chrome()
    driver.get(url_order)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    open_all_page(driver, soup)
    all_data_items = get_data_scrap(column_format, driver)
    
    column_name = ["product_key", "brand", "category", "sub_category"] + list(column_format.keys()) + ["url", "img_url"]
    product = pd.DataFrame(all_data_items, columns=column_name)
    
    product.to_csv("product_items.csv", mode="a", index=False)
    
    return product

# for brand in ["emina", "wardah", "make-over", "kahf"]:
product_pd = run_scraping("kahf")









