from google.cloud import bigquery
from google.oauth2 import service_account
from scraping_review import get_reviews

# Initialize BigQuery client
credentials = service_account.Credentials.from_service_account_file("../../voltaic-reducer-399714-87eda49329ec.json")
project_id = "voltaic-reducer-399714"
client = bigquery.Client(credentials=credentials, project=project_id)

# Retrieve product data
table_id_product = "paragon.products_list"
table_id_reviews = "paragon.reviews"
query_product = f"""
   SELECT *
   FROM {table_id_product}
   ORDER BY brand_id
   """
product_list_df = client.query(query_product).to_dataframe()

# Retrieve unique brand data
unique_brand = product_list_df[['brand_id', 'brand_name']].drop_duplicates().reset_index(drop=True)

# Function to select items
def select_items(prompt, column_name, df, selected_brand_list=[]):
    if column_name == "brand_id":
        print("=" * 75)
        print(("\t" * 6) + "LIST OF PARAGON BRAND NAMES")
        print("=" * 75)
        print("0. All (Select all brands)")
        for i, row in unique_brand.iterrows():
            print(f"{row['brand_id']}. {row['brand_name']}")
        print("=" * 75)
    elif column_name == "product_id":
        for i, row_1 in unique_brand.iterrows():
            if str(row_1['brand_id']) in selected_brand_list:
                print("=" * 75)
                print(("\t" * 6) + f"LIST OF PARAGON PRODUCT NAMES ({row_1['brand_name']})")
                print("=" * 75)
                print("0. All (Select all products for this brand)")
                for i, row_2 in product_list_df.iterrows():
                    if row_1["brand_id"] == row_2["brand_id"]:
                        print(f"{row_2['product_id']}. {row_2['product_name']}")
                print("=" * 75)

    selected_items = []
    selected_names = []

    while True:
        selected_item = input(prompt)
        if selected_item == "0":
            # Select all items
            selected_brand_list = [int(item) for item in selected_brand_list]
            selected_items = [item for item in df[df["brand_id"].isin(selected_brand_list)]['product_id'].tolist()]
            selected_names = product_list_df[product_list_df["product_id"].isin(selected_items)][["brand_name", "product_name", "product_shade", "product_url"]].values.tolist()
            break
        else:
            selected_items.append(selected_item)
            selected_names.extend(product_list_df.loc[product_list_df['product_id'] == int(selected_item), ["brand_name", "product_name", "product_shade", "product_url"]].values.tolist())
        choose = input("Do you want to add another item? [Y/N]: ").strip().lower()
        if choose != "y":
            break

    print("=" * 75)
    print(("\t" * 6) + f"YOUR SELECTED {column_name.upper()}")
    print("=" * 75)

    for i, row in df.iterrows():
        if str(row[column_name]) in selected_items:
            print(f"{row[column_name]}. {row[column_name.replace('id', 'name')]}")

    print("=" * 75)
    return selected_items, selected_names


def time_interval():
    interval_list = ["today", "1 Week Ago", "1 Month Ago", "1 Year Ago", "All"]
    print("=" * 75)
    print(("\t" * 6) + "TIME INTERVAL")
    print("=" * 75)
    for i in range(len(interval_list)):
        print(f"{i+1}. {interval_list[i]}")
    print("=" * 75)
    
    selected_interval = input("What time interval you want to take ? : ")
    return interval_list[int(selected_interval)-1]
    

# Select brands
brand, _ = select_items("Select the brand you want to search for: ", "brand_id", unique_brand)

# Select products
product_id, product_info = select_items("Select the Product you want to search for: ", "product_id", product_list_df, brand)

interval = time_interval()
    
for info in product_info:
    get_reviews(info, project_id, table_id_reviews, interval)
    
    
    
    