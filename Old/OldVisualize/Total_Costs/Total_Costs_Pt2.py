"""Updated July 30 to add pension costs, updated payroll calculations"""

import pandas as pd
from sodapy import Socrata
import os
import sys

sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../pensions'))
from Initialize_Agencies_2Ver import get_agencies


SCDAO_cases = {2016: 30765, 2017: 28264, 2018: 27818, 2019: 26576, 2020: None}
MA_GAA = {2016: 38438073000, 2017: 39249262000, 2018: 40196899000, 2019: 41883308000, 2020: 43589937705}


agencies = get_agencies(list(range(2016, 2020)))

def get_total_cost(year_range):
    """Created July 21st"""
    final_df = pd.DataFrame(columns=year_range)
    for agency_name, agency in agencies.items():
        final_df.loc[agency.alias + " Expenditures"] = agency.get_final_costs(True)
        final_df.loc[agency.alias + " Fractional Change"] = [x / final_df.loc[agency.alias + " Expenditures", 2016]
                                                             for x in final_df.loc[agency.alias + " Expenditures"]]
    final_df.loc["Total Expenditures"] = final_df.sum(axis=0)
    final_df.loc["Total Fractional Change"] = [x / final_df.loc["Total Expenditures", 2016]
                                               for x in final_df.loc["Total Expenditures"]]
    final_df.loc["Number of SCDAO Cases"] = [SCDAO_cases[y] for y in year_range]
    final_df.loc["Number of SCDAO Cases Fractional Change"] = [x / final_df.loc["Number of SCDAO Cases", 2016]
                                                               for x in final_df.loc["Number of SCDAO Cases"]]
    final_df.loc["Cost per SCDAO Case"] = [final_df.loc["Total Expenditures", y] / SCDAO_cases[y] if SCDAO_cases[y]
                                           else None for y in year_range]
    final_df.loc["Cost per SCDAO Case Fractional Change"] = [x / final_df.loc["Cost per SCDAO Case", 2016]
                                                             for x in final_df.loc["Cost per SCDAO Case"]]
    final_df.loc["MA GAA"] = [MA_GAA[x] for x in MA_GAA.keys() if x in year_range]
    final_df.loc["MA GAA Fractional Change"] = [MA_GAA[x] / MA_GAA[2016] for x in MA_GAA.keys() if x in year_range]

    return final_df
