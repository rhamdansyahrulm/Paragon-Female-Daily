import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Paragon Product Reviews", layout="wide")

def read_pandas_storage():
    storage_class_dict = json.load(open('data.json'))["storage_class"]

    list_storage_df = []
    category_list = []
    for category, sub_category_list in storage_class_dict["category"].items():
        category_list.append(category)
        for sub_category in sub_category_list:
            list_storage_df.append([category, sub_category])

    return storage_class_dict["brand"], pd.DataFrame(list_storage_df, columns=["category", "sub_category"]), category_list


def update_df(df: pd.DataFrame) -> pd.DataFrame:
    category = st.session_state["category"]

    if category != "":
        df = read_pandas_storage()[1]
        df = df.query(f"category == '{category}'")
    
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

    brand_options = brand_list
    category_options = category_list
    sub_category_options = df.sub_category.unique().tolist()

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
        options=category_options,
        on_change=update_df,
        kwargs={"df": df},
        key="category",
    )
    sub_category = st.selectbox(
        "Sub Category",
        options=sub_category_options,
        on_change=update_df,
        kwargs={"df": df},
        key="sub_category",
        disabled=True if category == "" else False,
    )