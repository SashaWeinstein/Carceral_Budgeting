"""Written by Sasha on July 10th to look at how much revenues these agencies collect
For cleaning: choose where to create client, when to open connection, and when to close."""

import pandas as pd
import seaborn as sns
from sodapy import Socrata
import matplotlib.pyplot as plt
import Initialize_Agencies
import budget_vs_expenditures
sns.set(rc={"figure.figsize": (20, 14), "lines.linewidth": 5})
sns.set_style("darkgrid")

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40


def visualize_revenues(year_range=list(range(2016,2020)), include_expenditures=False):
    """Written July 9th"""
    final_df = pd.DataFrame()
    for agency in Initialize_Agencies.get_state_agencies(year_range):
        if agency.alias != "MBT":
            if include_expenditures:
                agency.get_expenditures_by_year()
            agency.requery = True
            agency.add_budget_by_year()
            agency.budget_by_year.loc["All Appropriations Plus Revenues Minus 9c"] = \
                agency.budget_by_year.loc[["total enacted budget", "retained revenue collected"], :].sum()\
                - agency.budget_by_year.loc["planned savings 9c spending"]
            final_df = budget_vs_expenditures.visualize_state_agencies_pt2(agency, include_expenditures, final_df)
#            agency.budget_by_year.index = [agency.alias + " " + x for x in agency.budget_by_year.index]
    agency.client.close()


    final_df_melted = budget_vs_expenditures.melt_budget(final_df)

    budget_vs_expenditures.budgeted_vs_expenditures(final_df_melted,
                             "Difference between cthru budget columns for all state agencies")

def visualize_revenues_pt2(year_range=list(range(2016,2020)), include_expenditures=False):
    """Created July 13th for email to Bobby"""
    final_df = pd.DataFrame()
    for agency in Initialize_Agencies.get_state_agencies(year_range):
        if agency.alias != "MBT":
            if include_expenditures:
                agency.get_expenditures_by_year()

            agency.add_budget_by_year()
            agency.budget_by_year.loc["All Appropriations \nPlus Revenues Minus 9c"] = \
                agency.budget_by_year.loc[["total enacted budget", "retained revenue collected"], :].sum()\
                - agency.budget_by_year.loc["planned savings 9c spending"]
            final_df = budget_vs_expenditures.visualize_state_agencies_pt3(agency, final_df)
#            agency.budget_by_year.index = [agency.alias + " " + x for x in agency.budget_by_year.index]
    agency.client.close()


    final_df_melted = budget_vs_expenditures.melt_budget(final_df)

    budget_vs_expenditures.budgeted_vs_expenditures(final_df_melted,
                             "Difference between cthru budget columns for all state agencies")
    return final_df