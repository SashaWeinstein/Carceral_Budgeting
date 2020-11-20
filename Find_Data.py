"""This py file is just to hold find_data which is such an important function it should have it's own file and
be imported each time"""

import pandas as pd
import os

big_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"

def find_data(requery, client, dataset, SOQL, file_name):
    """adopted from Agency class method"""
    path = big_path + file_name
    if not requery and os.path.exists(path):
        df = pd.read_csv(path)
    else:
        result_json = client.get(dataset, where=SOQL, limit=9999999)
        df = pd.DataFrame(result_json)
        assert df.shape[0] < 999999, "Dataset found with more than 999999 records, need to up limit"
        df.to_csv(path)
    return df