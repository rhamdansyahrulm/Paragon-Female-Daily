import time
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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
    
    return total_click_next
    
def get_data_scrap(column_format, driver, total_click_next):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    items = []
    for item in soup.findAll('div', class_='jsx-1897565266 info-product'):
        item_info = []
        
        for key, value in column_format.items():
            element = item.find(value[0], class_=value[1])
            key_value = element.text if element is not None else ""
            item_info.append(key_value)
            
        items.append(item_info)
    
    return items
    
def run_scrapping(brand):
    column_format = {
        'product_name'      : ['p', 'jsx-1897565266 fd-body-md-regular text-ellipsis two-line word-break'],
        'product_shade'     : ['p', 'jsx-1897565266 fd-body-md-regular text-ellipsis grey'],
        'product_rating'    : ['span', 'jsx-1897565266 fd-body-sm-regular'],
        'total_review'      : ['span', 'jsx-1897565266 fd-body-sm-regular grey']
    }
    
    url = f"https://reviews.femaledaily.com/brands/product/"
    url_brand = os.path.join(url, brand)
    
    driver = webdriver.Chrome()
    driver.get(url_brand)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    total_click_next = open_all_page(driver, soup)
    all_data_items = get_data_scrap(column_format, driver, total_click_next)
    
    product = pd.DataFrame(all_data_items, columns=column_format.keys())
    product.to_csv("product_list.csv", index=False)
    
    print(product)

run_scrapping("emina")











