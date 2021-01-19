"""For January Slidedeck, need  effect of adding Hidden Costs on:
1) BPD for cost per call
2) Legal System overall
3) Jail System Overall
4) Total Yearly Numbers
Want these numbers as fractional increase
Maybe also want effect of hidden costs on Police generally
"""

import pandas as pd
import sys
sys.path.insert(0, "../../Final_Results")
from Final_Results_Helpers import get_Result
yr = list(range(2016,2020))

def avg_fractional_increase(filename, query, yr=list(range(2016, 2020))):
    raw = get_Result(filename)
    if query is not None:
        relevant = raw.query(query)
    else:
        relevant = raw
    gb = relevant.groupby("Hidden")[yr].sum().mean(axis=1)
    gb.rename(index={True:"Hidden", False:"Stated"}, inplace=True)
    gb["Total"] = gb.sum()
    return gb["Hidden"]/gb["Stated"], gb["Hidden"]/gb["Total"], gb

def yearly_fractional_increase_overall():
    raw = get_Result("Final_by_Year_splitHidden.csv")
    raw.rename(index={True: "Hidden", False: "Stated"}, inplace=True)
    fractional_increase = raw.loc["Hidden"]/raw.loc["Stated"]
    return fractional_increase, raw