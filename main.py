import pandas as pd
import numpy as np
import streamlit as st

from scrap.scraping_review import scraping_product_run

st.set_page_config(page_title="Paragon Product Reviews", layout="wide")

def read_pandas_storage():
    df = pd.read_csv('scrap/product_items.csv')
    brand_list = df["brand"].unique().tolist()
    category_list = df["category"].unique().tolist()

    brand_list.sort()
    category_list.sort()
    
    return brand_list, df, category_list

def get_product(brand, category="", sub_category="", product=""):
    df = read_pandas_storage()[1]
    
    category_df = df[df["brand"] == brand]
    sub_category_df = category_df[category_df["category"] == category] if category else category_df
    product_df = sub_category_df[sub_category_df["sub_category"] == sub_category] if sub_category else sub_category_df
    
    product_df["isnull"] = product_df["product_shade"].isnull()
    product_shade_df = product_df[product_df["product_name"] == product] if product else product_df
    
    
    category_list = category_df["category"].unique().tolist()
    category_list.sort()
    
    sub_category_list = sub_category_df["sub_category"].unique().tolist()
    sub_category_list.sort()
    
    product_list = product_df["product_name"].unique().tolist()
    product_list.sort()
    
    product_shade_list = product_shade_df[product_shade_df["isnull"] == False]["product_shade"].unique().tolist()
    
    return category_list, sub_category_list, product_list, product_shade_list

def get_url(brand, category, sub_category, product_name, product_shade=""):
    data = read_pandas_storage()[1]
    data = data[(data["brand"] == brand) & 
                (data["category"] == category) & 
                (data["sub_category"] == sub_category) & 
                (data["product_name"] == product_name)]
    
    if product_shade:
        data = data[data["product_shade"] == "18 Majestic Marrakesh"]
    
    return data["url"].tolist()[0]
    
    

def update_df(df: pd.DataFrame) -> pd.DataFrame:   
    st.session_state["df"] = df
    st.session_state["fresh_data"] = False


brand_list, df, category_list = read_pandas_storage()

if "df" not in st.session_state:
    st.session_state.df = df
if "fresh_data" not in st.session_state:
    st.session_state.fresh_data = True
    
    
###############################################################################################################################
# STREAMLIT
###############################################################################################################################

st.markdown("""
<style>
   h1 {
      font-size: 24px;
      text-align: center;
      text-transform: uppercase;
   }
   h2 {
      font-size: 16px;
      font-weight: bold;
      text-align: center;
      text-transform: uppercase;
   }
</style>
""", unsafe_allow_html=True)


title = st.title("Scraping Data", )

form1, form2 = st.columns(2)

with form1.container():
    st.header("Get New Product List")
    
    df = st.session_state["df"]

    brand_options = df.brand.unique().tolist()
    category_options = df.category.unique().tolist()
    sub_category_options = df.sub_category.unique().tolist()
    product_options = df.product_name.unique().tolist()

    if st.session_state.fresh_data:
        sub_category_options.insert(0, "Please Select The Category First !")

    a = st.selectbox(
        "Brand",
        options=brand_options,
    )

with form2.container():
    st.header("Collect a New Review")
    
    df = st.session_state["df"]

    brand_options = brand_list
    category_options = category_list
    sub_category_options = df.sub_category.unique().tolist()

    if st.session_state.fresh_data:
        category_options.insert(0, "")
        sub_category_options.insert(0, "Please Select The Category First !")

    brand = st.selectbox(
        "Brand",
        options=brand_options,
        key="Brand"
    )
    category = st.selectbox(
        "category",
        options=get_product(brand)[0],
        on_change=update_df,
        kwargs={"df": df},
        key="category",
    )
    sub_category = st.selectbox(
        "Sub Category",
        options=get_product(brand, category)[1],
        on_change=update_df,
        kwargs={"df": df},
        key="sub_category",
        disabled=True if category == "" else False,
    )
    product_name = st.selectbox(
        "Product Name",
        options=get_product(brand, category, sub_category)[2],
        on_change=update_df,
        kwargs={"df": df},
        key="product_name",
        disabled=True if sub_category == "Please Select The Category First !" else False,
    )
    
    product_shade_list = get_product(brand, category, sub_category, product_name)[3]

    if len(product_shade_list) > 0:
        product_shade = st.selectbox(
            "Product Shade",
            options=get_product(brand, category, sub_category, product_name)[3],
            on_change=update_df,
            kwargs={"df": df},
            key="product_shade",
            disabled=True if sub_category == "Please Select The Category First !" else False,
        )
    
    submit_button = st.button("Submit")
    
    if submit_button:
        try :
            url_link_product = get_url(brand, category, sub_category, product_name, product_shade)
        except :
            url_link_product = get_url(brand, category, sub_category, product_name)
        st.write(url_link_product)
        scraping_product_run(url_link_product)