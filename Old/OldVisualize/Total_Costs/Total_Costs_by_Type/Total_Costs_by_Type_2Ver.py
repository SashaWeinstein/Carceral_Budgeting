"""Created August 24, splits operating costs into payroll, non-labor operating costs"""


import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath('../../..'))
yr = list(range(2016,2020))
from Initialize_Agencies_2Ver import get_agencies
agencies = get_agencies(yr)

def by_type():
    by_agency = pd.DataFrame(columns=["Agency"]+ ["Cost Type"] + yr)
    overall = pd.DataFrame(columns=yr,
                           index=["Payroll Costs", "Non-Payroll Operating Costs","Pension Costs", "Fringe Benefit Costs",
                                  "Capital Costs"],
                           data=0)
    for _, a in agencies.items():
        a.get_final_costs()
        by_agency.loc[a.alias + " Payroll Costs", yr] = a.correction_function(a.payroll_expenditures_by_year)
        by_agency.loc[a.alias + " Payroll Costs", "Cost Type"] = "Payroll Costs"
        overall.loc["Payroll Costs"] += a.correction_function(a.payroll_expenditures_by_year)
        by_agency.loc[a.alias + " Non-Payroll Operating Costs", yr] = a.correction_function(
            a.non_payroll_operating_expenditures_by_year)
        by_agency.loc[a.alias + " Non-Payroll Operating Costs", "Cost Type"] = "Non-Payroll Operating Costs"
        overall.loc["Non-Payroll Operating Costs"] += a.correction_function(a.non_payroll_operating_expenditures_by_year)
        by_agency.loc[a.alias + " Pension Costs", yr] = a.correction_function(a.pensions)
        by_agency.loc[a.alias + " Pension Costs", "Cost Type"] = "Pension Costs"
        overall.loc["Pension Costs"] += a.correction_function(a.pensions)
        by_agency.loc[a.alias + " Fringe Benefit Costs"] = a.correction_function(a.fringe)
        by_agency.loc[a.alias + " Fringe Benefit Costs", "Cost Type"] = "Fringe Benefit Costs"
        overall.loc["Fringe Benefit Costs", yr] += a.correction_function(a.fringe)
        by_agency.loc[a.alias + " Capital Costs"] = a.correction_function(a.capital_expenditures)
        by_agency.loc[a.alias + " Capital Costs", "Cost Type"] = "Capital Costs"
        overall.loc["Capital Costs", yr] += a.correction_function(a.capital_expenditures)
        by_agency.iloc[-5:,:]["Agency"] = a.alias
    return overall, by_agency
