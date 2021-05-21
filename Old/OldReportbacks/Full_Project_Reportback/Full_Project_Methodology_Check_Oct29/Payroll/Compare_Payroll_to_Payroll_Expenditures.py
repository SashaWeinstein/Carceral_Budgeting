import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath('../../..'))
yr = list(range(2016,2020))
from Initialize_Agencies_2Ver import get_agencies
agencies = get_agencies(yr)
from Agency_Classes import StateAgency

def difference_between_payroll_and_payroll_expenditures():
    raw_differences_df = pd.DataFrame(columns=yr)
    percent_differences_df = pd.DataFrame(columns=yr)

    for name, agency in agencies.items():
        if (isinstance(agency, StateAgency)) and name !="MBTA":
            agency.get_final_costs()
            agency.add_payroll_by_year(False)
            alternative_payroll_by_year = agency.expenditures[agency.expenditures["vendor"].str.contains("(?i)payroll")]\
                .groupby("budget_fiscal_year").sum()["amount"]
            # print(agency.payroll_by_year[yr])
            # print(agency.payroll_expenditures_by_year[yr])
            raw_differences_df.loc[name + " total difference"] = agency.payroll_by_year.loc["pay total actual", yr] - alternative_payroll_by_year
            percent_differences_df.loc[name + " % difference"] = (agency.payroll_by_year.loc["pay total actual", yr] - alternative_payroll_by_year)/alternative_payroll_by_year

    return raw_differences_df, percent_differences_df
