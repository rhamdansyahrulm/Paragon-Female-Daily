import json
import pandas as pd

storage_class_dict = json.load(open('data.json'))["storage_class"]

list_storage_df = []
for category, sub_category_list in storage_class_dict["category"].items():
    for sub_category in sub_category_list:
        list_storage_df.append([category, sub_category])

df = pd.DataFrame(list_storage_df, columns=["category", "sub_category"])

print(df)
