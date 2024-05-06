import pandas as pd

def read_pandas_storage():
    df = pd.read_csv('scrap/product_items.csv')
    brand_list = df["brand"].unique().tolist()
    category_list = df["category"].unique().tolist()

    brand_list.sort()
    category_list.sort()
    
    return brand_list, df, category_list

data = read_pandas_storage()[1]
data = data[(data["brand"] == "wardah") & 
            (data["category"] == "lips") & 
            (data["sub_category"] == "lipstick") & 
            (data["product_name"] == "Colorfit Last All Day Lip Paint Around The World") &
            (data["product_shade"] == "18 Majestic Marrakesh")]

def get_url(brand, category, sub_category, product_name, product_shade):
    data = read_pandas_storage()[1]
    data = data[(data["brand"] == brand) & 
                (data["category"] == category) & 
                (data["sub_category"] == sub_category) & 
                (data["product_name"] == product_name)]
    
    if product_shade:
        data = data[data["product_shade"] == "18 Majestic Marrakesh"]
    
    return data["url"].tolist()[0]

df = get_url("wardah", "lips", "lipstick", "Colorfit Last All Day Lip Paint Around The World", "18 Majestic Marrakesh")