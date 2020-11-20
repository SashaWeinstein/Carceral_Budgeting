"""Created on July 16th """

import pandas as pd
from sodapy import Socrata
import os
import sys

sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../..'))
import string
from Initialize_Agencies import get_state_agencies, get_PDs
from budget_vs_expenditures import visualize_state_agencies

year_range = list(range(2016, 2021))

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"

#New July 17th: Group the agencies into three catgories:
# legal system which is Trial court, DA, CPCS, DAAA
# jails which is DOC, sheriff
# cops which is state, local police


def get_big_df(by_category=False):
    """For first chart, which is % change in budget
    Another to do: allow both PD, agencies to be called from some wrapper or on init
    so this can collapsed to one loop"""
    state_agencies = get_state_agencies(year_range, True)
    PDs = get_PDs(True)
    big_df = pd.DataFrame(columns=["Category"]+year_range)
    for agency in state_agencies:
        agency.add_budget_by_year()
        agency.appropriations_rev_9c()
        temp_budget = agency.budget_by_year.loc[
            ["All Appropriations Plus Revenues Minus 9c", "total expenses"], year_range]. \
            rename(index={"All Appropriations Plus Revenues Minus 9c": "Total Budget",
                          "total expenses": "Total Expenditures"}).copy()
        temp_budget.loc["Percent Change in Budget Since 2016"] = [x / temp_budget.loc["Total Budget", 2016]
                                                                  for x in temp_budget.loc["Total Budget"]]
        temp_budget.loc["Percent of Budget Spent"] = temp_budget.loc["Total Expenditures"]/temp_budget.loc["Total Budget"]
        temp_budget.index = [agency.alias + " " + i for i in temp_budget.index]
        temp_budget["Category"] = agency.category
        big_df = big_df.append(temp_budget)

    for PD in PDs:
        if "Total Budget" not in PD.budget_summary.index:
            PD.budget_summary.rename(index={"Total Adopted": "Total Budget"}, inplace=True)
        temp_summary = PD.budget_summary.loc[["Total Budget", "Total Expenditures"], year_range].copy()

        temp_summary.loc["Percent Change in Budget Since 2016"] = [x / temp_summary.loc["Total Budget", 2016]
                                                                   for x in temp_summary.loc["Total Budget"]]
        temp_summary.loc["Percent of Budget Spent"] = temp_summary.loc["Total Expenditures"] / \
                                                      temp_summary.loc["Total Budget"]
        temp_summary.index = [PD.alias + " " + i for i in temp_summary.index]
        temp_summary["Category"] = agency.category
        big_df = big_df.append(temp_summary)
    if by_category:
        return group_by_category(big_df[big_df.index.str.contains("Percent")== False])
    else:
        big_df.drop(columns=["Category"], inplace = True)
        big_df.loc["Total Budget Across All Agencies"] = big_df[big_df.index.str.contains("Total Budget")].sum()

        big_df.loc["Percent Change in Total Budget From All Agencies Since 2016"] = [
            x / big_df.loc["Total Budget Across All Agencies", 2016]
            for x in big_df.loc["Total Budget Across All Agencies"]]
        big_df.loc["Total Expenditures Across All Agencies"] = big_df[big_df.index.str.contains("Total Expenditures")].sum()
        big_df.loc["Total Percent of Budget Spent Across All Agencies"] = \
            big_df.loc["Total Expenditures Across All Agencies"] / \
            big_df.loc["Total Budget Across All Agencies"]
    return big_df

def group_by_category(big_df):
    """Written by July 17th to use new category designation I just made up"""
    categories = list(big_df["Category"].unique())
    big_df.reset_index(inplace=True)
    big_df["index"] = big_df["Category"] + [x.split("Total")[1] for x in big_df["index"]]
    by_category = big_df.groupby("index").sum()
    for c in categories:
        by_category.loc["Percent Change in Budget Since 2016 for " + c] = [x / by_category.loc[c + " Budget", 2016]
                                                                           for x in by_category.loc[c + " Budget"]]
        by_category.loc["Percent of Budget Spent for" + c] =  by_category.loc[c+ " Expenditures"] / \
                                                              by_category.loc[c + " Budget"]
    return by_category