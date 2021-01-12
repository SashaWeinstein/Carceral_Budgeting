"""Created August 20th now that I have operating costs, pensions, fringe benefits and capital expenditures for each
agency. Leave off settlements for now as they are not yet complete"""


import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
yr = list(range(2016,2020))
from Initialize_Agencies_2Ver import get_agencies
agencies = get_agencies(yr)

def by_type():
    by_agency = pd.DataFrame(columns=yr)
    overall = pd.DataFrame(columns=yr,
                           index=["Operating Costs", "Pension Costs", "Fringe Benefit Costs", "Capital Costs"],
                           data=0)
    for _, a in agencies.items():
        a.get_final_costs()
        print("got to", a.alias, " total costs 1 ver")
        print("operating costs are")
        display(a.operating_costs)
        by_agency.loc[a.alias + " Operating Costs"] = a.correction_function(a.operating_costs)
        overall.loc["Operating Costs"] += a.correction_function(a.operating_costs)
        by_agency.loc[a.alias + " Pension Costs"] = a.correction_function(a.pensions)
        overall.loc["Pension Costs"] += a.correction_function(a.pensions)
        by_agency.loc[a.alias + " Fringe Benefit Costs"] = a.correction_function(a.fringe)
        overall.loc["Fringe Benefit Costs"] += a.correction_function(a.fringe)
        by_agency.loc[a.alias + " Capital Costs"] = a.correction_function(a.capital_expenditures)
        overall.loc["Capital Costs"] += a.correction_function(a.capital_expenditures)
        print("overall at this point is")
        display(overall)
        print()

    return overall, by_agency
