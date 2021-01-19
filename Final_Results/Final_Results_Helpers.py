"""For properly reading in .csv's"""

import pandas as pd
import sys
final_results_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Final_Results/"
sys.path.insert(0, final_results_path)

def get_Result(filename):
    df = pd.read_csv(final_results_path + filename, index_col=0)

    yr = list(range(2016, 2020))
    df.rename(columns={str(x): x for x in yr}, inplace=True)
    return df
