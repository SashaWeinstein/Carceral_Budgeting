"""For January slidedeck for DA Rollins"""

import pandas as pd
import sys
final_results_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Final_Results/"
sys.path.insert(0, final_results_dir)
from Effect_of_Hidden_Costs import avg_fractional_increase, yearly_fractional_increase_overall
yr = list(range(2016,2020))

def BPD_cost_per_call():
    BPD_fractional_increase, BPD_fraction_hidden, BPD_gb = avg_fractional_increase(
        "Final_by_Agency_Type_splitHidden.csv",
        "Agency == 'Boston PD'")
    calls_BPD_response = 538000
    out = cost_per(calls_BPD_response, BPD_gb)
    out.rename({"Stated": "Stated Cost per Call",
                "Total": "Total Cost per Call including Hidden Costs"}, inplace=True)
    return out

disposed_cases_filed_2016 = 6096
def legal_cost_per_disposed_case_2016():
    legal_fractional_increase, legal_fraction_hidden, legal_gb = avg_fractional_increase(
        "Final_by_Category_splitHidden.csv",
        "Category == 'Legal'", [2016])

    out = cost_per(disposed_cases_filed_2016, legal_gb)
    out.rename({"Stated": "Stated Legal Cost per Disposed Case",
                "Total": "Total Legal Cost per Disposed Case including Hidden Costs"},
               inplace=True)
    return out

def legal_plus_police_cost_per_disposed_case_2016():
    fractional_increase, fraction_hidden, gb, = avg_fractional_increase("Final_by_Category_splitHidden.csv",
                                                                        "Category == 'Police' or Category =='Legal'",
                                                                        [2016])
    out = cost_per(disposed_cases_filed_2016, gb)
    out.rename({"Stated": "Stated Legal+Police Cost per Disposed Case",
                "Total": "Total Legal+Police Cost per Disposed Case including Hidden Costs"},
                inplace=True)
    return out

success = 1654*.65
def jails_cost_per_success():
    fractional_increase, fraction_hidden, gb = avg_fractional_increase("Final_by_Category_splitHidden.csv",
                                                                       "Category == 'Jails'")
    out = cost_per(success, gb)
    out.rename({"Stated": "Stated Jails Cost per Success",
                "Total":"Total Jails Cost per Success including Hidden Costs"},
               inplace=True)
    return out

def systemwide_cost_per_success():
    fractional_increase, fraction_hidden, gb = avg_fractional_increase("Final_by_Category_splitHidden.csv",
                                                                       None)
    out = cost_per(success, gb)
    out.rename({"Stated":"Stated Systemwide Yearly Cost per Success",
                "Total": "Total Systemwide Yearly Cost per Success including Hidden Costs"},
               inplace=True)
    return out

def cost_per(count, gb):
    return gb/count