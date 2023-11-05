import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

list_brand = ["wardah", "make-over", "emina", "kahf"]
items = []

for brand in list_brand:
    url = f"https://reviews.femaledaily.com/brands/{brand}"
    driver = webdriver.Chrome()
    driver.get(url)
    
    next_page_available = True
    while next_page_available:
        time.sleep(1)
        
        for scroll in range(20):
            driver.execute_script("window.scrollBy(0, 250)")
            time.sleep(0.2)
        
        driver.execute_script("window.scrollBy(0, 50)")
        time.sleep(0.2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        column_format = {
            'brand_name'     : ['a', 'jsx-2059197805 product-card-catalog-brand'],
            'product_name'      : ['h2', 'jsx-2059197805 product-card-catalog-title'],
            'product_shade'     : ['p', 'jsx-2059197805 product-card-catalog-shade'],
            'product_rating'    : ['span', 'jsx-2059197805 product-card-catalog-rating-average'],
            'product_url'       : ['a', 'jsx-2059197805']
        }
        
        for item in soup.findAll('div', class_='jsx-2059197805 product-card-catalog'):
            item_info = []
            
            for key, value in column_format.items():
                element = item.find(value[0], class_=value[1])
                
                if key == "product_url":
                    url_key = element['href'] if element is not None and 'href' in element.attrs else ""
                    key_value = f"https://reviews.femaledaily.com{url_key}"
                else :
                    key_value = element.text if element is not None else ""
                    
                item_info.append(key_value)
                
            items.append(item_info)
        
        time.sleep(0.5)
    
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '#id_nextpage.paging-prev-text-active')
            next_button.click()
            time.sleep(5)
        except NoSuchElementException:
            print("This is the last page !")
            next_page_available = False
            driver.close()
            

product = pd.DataFrame(items, columns=column_format.keys())
product.to_csv("product_list.csv", index=False)