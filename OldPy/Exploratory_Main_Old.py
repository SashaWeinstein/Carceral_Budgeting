"""Created by Sasha on June 17th to re-create Bobby's analysis of total expenditures per year and
payroll expenditures per year for the following MA agencies: Trial Court, CPCS (public defenders),
Suffolk County DA's office, Suffolk County Sheriff's Office, MA State Police, MBTAP, MDAA,
Boston PD, Chelsea PD, Revere PD, Winthrop PD
Uses this dataset: https://cthru.data.socrata.com/dataset/Comptroller-of-the-Commonwealth-Spending/pegc-naaa
Last updated by Sasha on June 22nd"""

import pandas as pd
from sodapy import Socrata
import os
import sys
import string
from Initialize_Agencies import get_all_agencies

year_range = list(range(2016, 2021))

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
agencies_list = get_all_agencies(year_range)
def by_fiscal_year():
    """Last updated by Sasha on June 22nd
    This will produce the same plot for each agency: a plot of expenditures over time and payroll over time
    It will also save this info in a .csv somewhere
    Newest version allows for big_df to be passed in so data from different chtru datasets can be combined
    """
    client = Socrata("cthru.data.socrata.com", app_token)
    client.timeout = 20
    big_df = pd.DataFrame(columns=year_range)
    for agency in agencies_list[::-1]: #Goes backward so that if newer agencies throw bug it catches them sooner
        big_df = big_df.append(agency.get_expenditures_by_year(client))
        if agency.alias == "MBT": #MBT not in this budget dataset for some reason
            continue
        big_df = big_df.append(agency.add_budget_by_year(client))
    client.close()
    return big_df

def by_calendar_year():
    """Created by Sasha on June 22nd
    The payroll info on cthru seems to be by calendar year instead of fiscal year. I'll put it in separate csv,
    at least we can see the scale of overtime pay, like this agency devotes x % of it's payroll dollars towards
    overtime or whatever"""
    client = Socrata("cthru.data.socrata.com", app_token)
    client.timeout = 20

    big_df = pd.DataFrame(columns=year_range)
    for agency in agencies_list:
        # agency.add_payroll(client)
        # payroll_by_year = agency.payroll.groupby("year")[agency.pay_col].sum().T
        # clean_labels(payroll_by_year, agency)
        #
        # payroll_by_year = payroll_by_year[payroll_by_year.index.str.contains("To Date") == False]
        if agency.calender_year_data:
            big_df = big_df.append(agency.add_payroll_by_year(client))
    client.close()
    return big_df



