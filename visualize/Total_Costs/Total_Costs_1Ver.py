"""Created July 21st to take first crack at getting a total cost of the carceral state in Suffolk County.
Jupyter notebook has better description of methodology"""

import pandas as pd
from sodapy import Socrata
import os
import sys

sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../..'))
import string
from Initialize_Agencies import get_state_agencies, get_PDs

SCDAO_cases = {2016:30765,	2017:28264, 2018: 27818, 2019: 26576, 2020:None}
MA_GAA = {2016: 38438073000, 2017: 39249262000, 2018: 40196899000, 2019: 41883308000, 2020:43589937705}

def get_total_cost(year_range):
    """Created July 21st"""
    final_df = pd.DataFrame(columns=year_range)
    for agency in get_state_agencies(year_range) + get_PDs():
        final_df.loc[agency.alias + " Budget"] = agency.get_final_costs(False, None)
        final_df.loc[agency.alias + " Fractional Change"] = [x / final_df.loc[agency.alias + " Budget", 2016]
                                                                  for x in final_df.loc[agency.alias + " Budget"]]
    final_df.loc["Total Budget"] = final_df.sum(axis=0)
    final_df.loc["Total Fractional Change"] = [x/final_df.loc["Total Budget", 2016]
                                               for x in final_df.loc["Total Budget"]]
    final_df.loc["Number of SCDAO Cases"] = [SCDAO_cases[y] for y in year_range]
    final_df.loc["Number of SCDAO Cases Fractional Change"] = [x/final_df.loc["Number of SCDAO Cases", 2016]
                                                               for x in final_df.loc["Number of SCDAO Cases"]]
    final_df.loc["Cost per SCDAO Case"] =[final_df.loc["Total Budget", y]/SCDAO_cases[y] if SCDAO_cases[y] else None
                                          for y in year_range]
    final_df.loc["Cost per SCDAO Case Fractional Change"] = [x/final_df.loc["Cost per SCDAO Case", 2016]
                                                             for x in final_df.loc["Cost per SCDAO Case"]]
    final_df.loc["MA GAA"] = [MA_GAA[x] for x in MA_GAA.keys() if x in year_range]
    final_df.loc["MA GAA Fractional Change"] =[MA_GAA[x]/MA_GAA[2016] for x in MA_GAA.keys() if x in year_range]

    return final_df