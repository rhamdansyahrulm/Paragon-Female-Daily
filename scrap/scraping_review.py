import time
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_reviews(product_info, project_id, table_id_reviews, interval):
    brand_name, product_name, product_shade, url = product_info
    
    driver = webdriver.Chrome()
    driver.get(url)
    
    next_page_available = True
    continue_scrap = True
    while next_page_available and continue_scrap:
        page_review = []
        time.sleep(1)
        
        for scroll in range(25):
            driver.execute_script("window.scrollBy(0, 250)")
            time.sleep(0.2)
        
        driver.execute_script("window.scrollBy(0, 50)")
        time.sleep(0.2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        if soup.find('div', class_='jsx-2016320139 jsx-2462230538 no-review-holder'):
            break
        
        column_format = {
            'age' : ['p', 'profile-age'],
            'description' : ['p', 'profile-description'],
            'date' : ['p', 'review-date'],
            'review' : ['p', 'text-content'],
            'rating' : ['span', 'cardrv-starlist'],
            'recommend' : ['p', 'recommend'],
            'usage_period' : ['div', 'information-wrapper'],
            'purchase_point' : ['div', 'information-wrapper']
        }
        
        for item in soup.findAll('div', class_='jsx-2016320139 jsx-2462230538 item'):
            item_info = [brand_name, product_name, product_shade]
            
            for key, value in column_format.items():
                element = item.find(value[0], class_=value[1])
                
                if key == "review":
                    span_element = element.find('span') if element else None
                    key_value = span_element.text if span_element is not None else ""
                elif key == "usage_period":
                    b_tags = element.find_all('b')
                    key_value = b_tags[0].text if len(b_tags) > 0 else ""
                elif key == "rating":
                    score = element.find_all('i', class_="icon-ic_big_star_full margin-right")
                    key_value = len(score)
                elif key == "recommend":
                    user_recommend = element.find('b').text if element is not None else ""
                    key_value = 0 if "doesn't recommend" in user_recommend else 1
                elif key == "purchase_point":
                    b_tags = element.find_all('b')
                    key_value = b_tags[1].text if len(b_tags) > 1 else ""
                elif key == "date":
                    date_value = element.text if element is not None else ""
                    if "hours ago" in date_value:
                        key_value = datetime.now()
                    elif "days ago" in date_value:
                        days_ago = int(date_value.split()[0])
                        key_value = datetime.now() - timedelta(days=days_ago)
                    else:
                        key_value = datetime.strptime(date_value, '%d %b %Y')
                else:
                    key_value = element.text if element is not None else ""
                    
                item_info.append(key_value)
        
            page_review.append(item_info)
        
        column_names = ["brand_name", "product_name", "product_shade", "age", "description", "date", "review", "rating", "recommend", "usage_period", "purchase_point"]
        review_df = pd.DataFrame(page_review, columns=column_names)
        
        if interval == "today":
            fix_df = review_df[review_df["date"] == datetime.now()]
        elif interval == "1 Week Ago":
            date_range = (datetime.now() - timedelta(days=6))
            fix_df = review_df[review_df["date"] >= date_range]
        elif interval == "1 Month Ago":
            date_range = (datetime.now() - timedelta(days=30))
            fix_df = review_df[review_df["date"] >= date_range]
        elif interval == "1 Year Ago":
            date_range = (datetime.now() - timedelta(days=365))
            fix_df = review_df[review_df["date"] >= date_range]
        elif interval == "All":
            fix_df = review_df
        
        fix_df["date"] = fix_df["date"].dt.strftime('%Y-%m-%d')
        fix_df.to_gbq(table_id_reviews, project_id=project_id, if_exists="append")
                        
        time.sleep(0.5)
    
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '#id_next_page.paging-prev-text-active')
            next_button.click()
            time.sleep(5)
        except NoSuchElementException:
            print("This is the last page !")
            next_page_available = False
        
        if len(fix_df) < 10:
            continue_scrap = False
    
    driver.close()