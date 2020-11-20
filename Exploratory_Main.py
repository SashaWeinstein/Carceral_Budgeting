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

sys.path.insert(0, os.path.abspath('visualize/'))
import string
from Initialize_Agencies import get_state_agencies
from budget_vs_expenditures import visualize_state_agencies

year_range = list(range(2016, 2020))

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"



def by_fiscal_year(get_big_df=False, visualize=True, requery=False):
    """Last updated by Sasha on June 22nd
    This will produce the same plot for each agency: a plot of expenditures over time and payroll over time
    It will also save this info in a .csv somewhere
    Newest version allows for big_df to be passed in so data from different chtru datasets can be combined
    """
    agencies_list = get_state_agencies(year_range)
    client = Socrata("cthru.data.socrata.com", app_token)
    client.timeout = 40
    big_df = pd.DataFrame(columns=year_range)
    for agency in agencies_list:  # Goes backward so that if newer agencies throw bug it catches them sooner
        agency.requery = requery
        agency.get_expenditures_by_year()
        temp_expend = agency.expenditures_by_year.copy()
        temp_expend.index = [agency.alias + " " + i for i in temp_expend.index]
        big_df = big_df.append(temp_expend)
        if agency.alias == "MBT":  # MBT not in this budget dataset for some reason
            continue
        agency.add_budget_by_year()
        agency.appropriations_rev_9c()
        temp_budg = agency.budget_by_year.copy()
        temp_budg.loc["net transfer"] = temp_budg.loc["transfer in"] - temp_budg.loc["transfer out"]
        temp_budg.index = [agency.alias + " " + i for i in temp_budg.index]
        big_df = big_df.append(temp_budg)
        if visualize:
            visualize_state_agencies(agency)
    client.close()
    if get_big_df:
        return big_df


def by_calendar_year(total_OT_only=False):
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
            big_df = big_df.append(agency.add_payroll_by_year(client, total_OT_only))
    client.close()
    return big_df
