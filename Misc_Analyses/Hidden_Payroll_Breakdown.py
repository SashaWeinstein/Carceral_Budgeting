"""Important to point out that nearly all hidden payroll is paid to cops. Quantify that here"""

import pandas as pd
import sys
sys.path.insert(0, "../../Final_Results")
df = pd.read_csv("../../Final_Results/Final_by_Agency_Type_SP.csv", index_col=0)

yr = list(range(2016,2020))
df.rename(columns = {str(x):x for x in yr}, inplace=True)

def breakdown_hidden_payroll():
    """Where is hidden payroll paid?"""
    hidden_payroll = df[df["Cost Type"] == "Hidden Payroll Costs"][yr].mean(axis=1)
    hidden_payroll = hidden_payroll[hidden_payroll >= 1000]
    print("the following agencies have more than 1k in hidden payroll")
    print(hidden_payroll.index)