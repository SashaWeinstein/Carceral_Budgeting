"""Created September 8th, get statewide cost and details on agency corrections"""


import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
yr = list(range(2016,2020))
from Initialize_Agencies_2Ver import get_agencies
agencies = get_agencies(yr)

def by_type():
    total_cost = pd.Series()
    correction = pd.Series()
    ones = pd.Series(index=yr, data=1)
    for _, a in agencies.items():
        a.get_final_costs()
        total_cost.loc[a.alias] = (a.payroll_expenditures_by_year + a.non_payroll_operating_expenditures_by_year + \
            a.pensions + a.fringe + a.capital_expenditures).sum()/4
        correction.loc[a.alias] = a.correction_function(ones).sum()/4
    return total_cost, correction
