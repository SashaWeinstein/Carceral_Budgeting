"""This file essentially acts a pointer to code in Statewide_Pensions"""

import pandas as pd
from Statewide_Pensions import pensions_by_agency

by_agency, contributions_by_year = pensions_by_agency(requery=False)

def pensions_from_payouts_fraction(agency):
    alias, yr = agency.alias, agency.year_range
    if alias == "trial_court":
        return by_agency.loc["trial_court_statewide", yr], \
               by_agency.loc["trial_court_local", yr]
    elif alias not in by_agency.index:
        return pd.Series(index=yr, data=0), pd.Series(index=yr, data=0)

    return by_agency.loc[alias, yr],  pd.Series(index=yr, data=0)

def pensions_from_payroll_fraction(agency):
    """For any agency with incomplete data on which employees receive payouts"""
    yr, payroll_fraction = agency.year_range, agency.payroll_fraction
    return contributions_by_year[yr] * payroll_fraction, pd.Series(index=yr, data=0)