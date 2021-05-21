"""For January slidedeck for DA Rollins"""

import pandas as pd
import sys
final_results_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/Final_Results/"
sys.path.insert(0, final_results_dir)
from Effect_of_Hidden_Costs import avg_fractional_increase, yearly_fractional_increase_overall
yr = list(range(2016,2020))

#Caseflow/efficiency metrics
#Calls
calls_BPD_response = 538000
total_calls = 695000
fraction_police_incidents_violent = .06
BPD_response_violent_incidents = calls_BPD_response*fraction_police_incidents_violent

#Incidents suffolk wide - 2016
total_reported_incidents_2016 = 158610
total_reported_criminal_incidents_2016 = 131960
total_estimated_incidents_including_unreported_2016 = 334075
total_case_filings_2016 = 25036
case_filings_2016_leading_to_conviction = 7427

#BPD Incidents
BPD_reported_incidents_2016 = 99430
BPD_reported_criminal_incidents_2016 = 72510

#BPD Reports/Clearances
BPD_total_reported_crime = 22676
BPD_total_cleared_crime = 2756
BPD_total_reported_violent_crime = 4767
BPD_cleared_violent_crime = 1431

#These are numbers Bobby sent over a while back, will need to double check
SCDAO_cases_dict = {2016:30765,	2017:28264, 2018: 27818, 2019: 26576, 2020:None}
SCDAO_cases = pd.Series(SCDAO_cases_dict).loc[yr]




def BPD_cost_per_call():
    BPD_fractional_increase, BPD_fraction_hidden, BPD_gb = avg_fractional_increase(
        "Final_by_Agency_Type_splitHidden.csv",
        "Agency == 'Boston PD'")
    out = cost_per(calls_BPD_response, BPD_gb)
    out.rename({"Stated": "Stated Cost per Call",
                "Total": "Total Cost per Call including Hidden Costs"}, inplace=True)
    return out

def legal_cost_per_case_filing_2016():
    legal_fractional_increase, legal_fraction_hidden, legal_gb = avg_fractional_increase(
        "Final_by_Category_splitHidden.csv",
        "Category == 'Legal'", [2016])
    out = cost_per(total_case_filings_2016, legal_gb)
    out.rename({"Stated": "Stated Legal Cost per Case Filing",
                "Total": "Total Legal Cost per Case Filing including Hidden Costs"},
               inplace=True)
    return out

def legal_plus_police_cost_per_case_filing_2016():
    fractional_increase, fraction_hidden, gb, = avg_fractional_increase("Final_by_Category_splitHidden.csv",
                                                                        "Category == 'Police' or Category =='Legal'",
                                                                        [2016])
    out = cost_per(total_case_filings_2016, gb)
    out.rename({"Stated": "Stated Legal+Police Cost per Case Filing",
                "Total": "Total Legal+Police Cost per Case Filing including Hidden Costs"},
                inplace=True)
    return out

def systemwide_cost_per_case_filing_2016():
    fractional_increase, fraction_hidden, gb, = avg_fractional_increase("Final_by_Year_splitHidden.csv",
                                                                        None,
                                                                        [2016])
    out = cost_per(total_case_filings_2016, gb)
    out.rename({"Stated":"Stated Systemwide Cost per Conviction (2016)",
                "Total":"Total Systemwide Cost per Conviction (2016)"})
    return out

def systemwide_cost_per_conviction_2016():
    fractional_increase, fraction_hidden, gb, = avg_fractional_increase("Final_by_Year_splitHidden.csv",
                                                                        None,
                                                                        [2016])
    out = cost_per(case_filings_2016_leading_to_conviction, gb)
    out.rename({"Stated":"Stated Systemwide Cost per Conviction (2016)",
                "Total":"Total Systemwide Cost per Conviction (2016)"})
    return out, gb


def cost_per(count, gb):
    return gb/count
