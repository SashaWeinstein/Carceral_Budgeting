"""This file essentially acts a pointer to code in Statewide_Pensions"""

import pandas as pd
from Statewide_Pensions import pensions_by_agency

by_agency, contributions_by_year = pensions_by_agency(requery=False)


def pensions_from_payouts_fraction(agency):
    alias, yr = agency.alias, agency.year_range
    if alias == "trial_court":
        return by_agency.loc["trial_court_statewide", yr], \
               by_agency.loc["trial_court_local", yr]
    elif alias == "Suffolk_Sheriff":
        """Added august 12th to account for City of Boston's obligations to retirees of suffolk sheriff's office. From
            Boston state budget:
                 State legislation converted all existing and future Suffolk County Sheriff employees to state employees
                 effective January 1, 2010. The State charges the City for Suffolk County through an assessment based on the
                residual unfunded pension liability for former Sherriff employees who retired prior to January 1, 2010.
                Once the unfunded pension liability is fully extinguished, the budget for Suffolk County
                will no longer be necessary.
        """
        return by_agency.loc[alias, yr] + 3.87 * (10 ** 6),  pd.Series(index=yr, data=0)
    elif alias not in by_agency.index:
        return pd.Series(index=yr, data=0), pd.Series(index=yr, data=0)

    return by_agency.loc[alias, yr],  pd.Series(index=yr, data=0)

def pensions_from_payroll_fraction(agency):
    """For any agency with incomplete data on which employees receive payouts"""
    yr, payroll_fraction = agency.year_range, agency.payroll_fraction
    return contributions_by_year[yr] * payroll_fraction, pd.Series(index=yr, data=0)