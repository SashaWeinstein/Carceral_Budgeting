"""This file was created for January Slidedeck for Rollins
Get payroll fractions for each state agency and Boston, Chelsea PD"""

import pandas as pd
import sys

home_dir = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory"
sys.path.insert(0, home_dir)
from Initialize_Agencies import get_agencies

misc_viz_helpers_dir = "/Visualize/Misc_Viz_Helpers"
sys.path.insert(0, misc_viz_helpers_dir)
from Pretty_Names import Prettify_AN

agencies = get_agencies()

def get_Payroll_Fraction():
    out = pd.Series()
    state_agencies = pd.Series()
    for _, agency in agencies.items():
        if agency.alias in ["Boston PD", "Chelsea PD", "Revere PD"]:
            out.loc[Prettify_AN(agency.alias)] = agency.PD_fraction_total.mean()
            if agency.alias in ["Boston PD", "Chelsea PD"]:
                out.loc[Prettify_AN(agency.alias) + " Non-MTRS"] = agency.PD_fraction_non_teacher.mean()
        elif agency.alias not in ["Winthrop PD"]:
            state_agencies.loc[Prettify_AN(agency.alias)] = agency.payroll_fraction.mean()

    out.loc["State Agencies Total"] = state_agencies.sum()
    return out, state_agencies
