"""Created July 31st"""

import pandas as pd
import numpy as np
from sodapy import Socrata
import os
import sys


sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../pensions'))
import string
from Initialize_Agencies_2Ver import get_agencies
from State_Pensions_2Ver import by_agency
from LocalPD_True_Payroll import True_Earnings
import State_Pensions_2Ver
import matplotlib.ticker as mtick
import Agency_Classes
import matplotlib.pyplot as plt
import seaborn as sns





year_range = list(range(2016, 2020))

agencies = get_agencies(year_range)
pensions_statewide_original = State_Pensions_2Ver.by_agency(False)

SCDAO_cases = {2016:30765,	2017:28264, 2018: 27818, 2019: 26576, 2020:None}
MA_GAA = {2016: 38438073000, 2017: 39249262000, 2018: 40196899000, 2019: 41883308000, 2020:43589937705}

plt.rcParams['legend.title_fontsize'] = 16

def yearly_operating_costs():
    """This is for summary of part 1, plot all non-pension costs for each agency"""
    df = state_agencies_budget()
    for alias in ["Boston PD", "Chelsea PD", "Revere PD", "Winthrop PD"]:
        PD = agencies[alias]
        if alias in ["Boston PD", "Chelsea PD"]:
            df.loc[PD.alias] = PD.budget_summary.loc["Final Yearly Operating Cost"]
        else:
            df.loc[PD.alias] = add_missing_data(PD)
        df.loc[PD.alias, "Category"] = "Local PD"
    df["Category"] = df["Category"].replace("Police", "State Police")
    return df

def visualize_yearly_operating_costs():
    df = yearly_operating_costs()
    display(df.applymap(lambda x: x / 10 ** 6 if isinstance(x, float) or isinstance(x, int) else x))
    by_category_gb = df.groupby("Category").sum()/10**6
    display(by_category_gb)
    plot_yearly_operating_costs(by_category_gb.reset_index())
    plot_SCDAO_case_cost(df.sum())
    return plot_pcnt_change_since_2016(by_category_gb)

def state_agencies_budget():
    out_df = pd.DataFrame(columns=["Category"] + year_range)
    for key, agency in agencies.items():
        if agency.alias == "MBTA":
            index_name = agency.alias + " Police"
            agency.get_payroll_by_year()
            MBTA_police_pay = agency.payroll_by_year.loc[["police_pay"]]
            MBTA_police_pay.loc["police_pay_final"] = [
                MBTA_police_pay.iloc[0, x] if not np.isnan(MBTA_police_pay.iloc[0, x])
                else MBTA_police_pay.iloc[0, x - 1]
                for x in range(MBTA_police_pay.shape[1])]

            out_df.loc[index_name, year_range] = agency.correction_function(
                MBTA_police_pay.loc["police_pay_final", year_range])
        elif isinstance(agency, Agency_Classes.StateAgency):
            index_name = agency.alias
            agency.add_budget_by_year()
            agency.appropriations_rev_9c()

            out_df.loc[index_name, year_range] = agency.correction_function(
                agency.budget_by_year.loc["All Appropriations Plus Revenues Minus 9c"])
        out_df.loc[index_name, "Category"] = agency.category
    return out_df

def plot_state_agencies_budget():
    df = state_agencies_budget()
    df.loc["Total of State Agencies", year_range] = df.loc[:, year_range].sum()
    display(df.applymap(lambda x: x / 10 ** 6 if isinstance(x, float) or isinstance(x, int) else x))
    plot_over_time(df.loc[:, year_range].reset_index(), "State Agencies Yearly Operating Costs")

def state_agencies_pensions():
    pensions_statewide = pensions_statewide_original.loc[:, year_range].copy()
    for key, agency in agencies.items():
        if agency.alias in pensions_statewide.index:
            pensions_statewide.loc[agency.alias] = agency.correction_function(pensions_statewide.loc[agency.alias])
    return pensions_statewide

def visualize_state_agencies_pensions():
    pensions_statewide = state_agencies_pensions()
    pensions_statewide.loc["Total Pension Cost\n of State Agencies"] = pensions_statewide.sum()
    print("Statewide Pension Costs")
    display(pensions_statewide.applymap(lambda x: x / 10 ** 6 if isinstance(x, float) or isinstance(x, int) else x))
    plot_over_time(pensions_statewide.reset_index(), "Calculated Pension Costs of Statewide Agencies",
                   ("agency_class", "Agency"))

def localPD_pensions():
    localPD_pensions_df = pd.DataFrame(columns = year_range)
    for alias in ["Boston PD", "Chelsea PD", "Revere PD", "Winthrop PD"]:
        localPD_pensions_df.loc[alias] = agencies[alias].pension
    return localPD_pensions_df

def visualize_localPD_pensions():
    localPD_pensions_df = localPD_pensions()
    localPD_pensions_df.loc["Total Pension Costs for Municipal Police Forces"] = localPD_pensions_df.sum()
    display(localPD_pensions_df.applymap(lambda x: x / 10 ** 6 if isinstance(x, float) or isinstance(x, int) else x))
    plot_over_time(localPD_pensions_df.reset_index(), "Municipal Police Pensions Over Time")

def total_pensions():
    all_pensions = state_agencies_pensions()
    all_pensions = all_pensions.append(localPD_pensions())
    return all_pensions

def plot_total_pensions():
    all_pensions= total_pensions()
    all_pensions.loc["Total Pension Costs of Carceral State\n in Suffolk County"] = all_pensions.sum()
    plot_over_time(all_pensions.reset_index(), "All Pensions Over Time", ("index", "Agency"), (1, .4))


def final_summary():
    """Look at effect of adding pensions to cost per case. Start here tomorrow"""
    pre_pension = yearly_operating_costs()
    pre_pension["With Pension"] = [False]*pre_pension.shape[0]
    pre_pension.index = [x + " Without Pension" for x in pre_pension.index]

    pensions = total_pensions()
    total = yearly_operating_costs()

    for alias in pensions.index:
        total.loc[alias, year_range] = total.loc[alias, year_range] + pensions.loc[alias, year_range]
    total["With Pension"] = [True]*pre_pension.shape[0]
    # total["alias"] = total.index
    # total.index = [x + " Including Pension" for x in total.index]
    print("Final Totals Including Pension")
    display(total.loc[:, ["Category"] + year_range].applymap(lambda x: x / 10 ** 6 if isinstance(x, float) or
                                                                                      isinstance(x, int) else x))
    compare_pre_post_pension(total.append(pre_pension))
    compare_SCDAO_case_cost(total.append(pre_pension))

def compare_pre_post_pension(df):
    melted = df.melt(id_vars = ["Category", "With Pension"])
    melted["value_in_millions"] = (melted["value"] / 10 ** 6).astype(float)
    palette = sns.color_palette("Paired", melted["Category"].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="variable", y="value_in_millions", hue="Category", style ="With Pension", ci=False,
                     palette=palette, sort=False, data=melted)
    ax.legend(frameon=False, loc="center right", fontsize=16)
    p.set_title("Effect of Including Pensions", fontsize=24)
    plt.xticks(list(range(2016, 2020)))
    p.set_ylabel("Budgeted Dollars in Millions", fontsize=20)
    p.set_xlabel("")
    p.tick_params(labelsize=20)
    plt.show()

def compare_SCDAO_case_cost(df):
    gb = df.groupby("With Pension").sum()[year_range]
    SCDAO_cases_series = pd.Series(SCDAO_cases)[year_range]
    gb = gb/SCDAO_cases_series
    print("Yearly Cost of SCDAO Case With and Without Including Pension Costs (In Thousands)")
    display(gb)
    melted = gb.reset_index().melt(id_vars = ["With Pension"])
    palette = sns.color_palette("Paired", melted["With Pension"].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="variable", y="value", style ="With Pension", ci=False,
                     palette=palette, sort=False, data=melted)
    ax.legend(frameon=False, loc="lower right", fontsize=16)
    p.set_title("Effect of Including Pensions on Cost per SCDAO Case", fontsize=24)
    plt.xticks(list(range(2016, 2020)))
    p.set_ylabel("Dollars Per Case", fontsize=20)
    p.set_xlabel("")
    p.tick_params(labelsize=20)


def localPD_budget_pdfs():
    out_df = pd.DataFrame(columns=year_range)
    for alias in ["Boston PD", "Chelsea PD", "Revere PD", "Winthrop PD"]:
        PD = agencies[alias]
        out_df.loc[PD.alias] = add_missing_data(PD)
    display(out_df.applymap(lambda x: x / 10 ** 6 if isinstance(x, float) or isinstance(x, int) else x))
    plot_over_time(out_df.reset_index(), "Local Police Department Yearly Expenditures")
    return out_df

def add_missing_data(PD):
    out = PD.budget_summary.loc["Total Expenditures"]
    if PD.alias == "Chelsea PD":
        out[2016] = PD.budget_summary.loc["Total Budget", 2016]
    elif PD.alias == "Revere PD":
        out[2019] = PD.budget_summary.loc["Total Adopted", 2019]
    elif PD.alias == "Winthrop PD":
        out[2018] = PD.budget_summary.loc["Total Budget", 2018]
    return out


def plot_over_time(df, title, hue_tup=("index", "Agency"), legend_bbox_to_anchor=None):
    """New August 4th: hue mapper is tup where first val is name of hue column, second is name on legend"""
    df.rename(columns={hue_tup[0]:hue_tup[1]}, inplace=True)
    hue_column = hue_tup[1]
    melted = df.melt(id_vars=[hue_column])
    melted["value_in_millions"] = (melted["value"] / 10 ** 6).astype(float)
    palette = sns.color_palette("Paired", melted[hue_column].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="variable", y="value_in_millions", hue=hue_column, palette=palette, sort=False, data=melted)
    p.set_title(title, fontsize=24)
    if legend_bbox_to_anchor:
        ax.legend(frameon=False, fontsize=16, loc="center right", bbox_to_anchor=legend_bbox_to_anchor)
    else:
        ax.legend(frameon=False, loc="center right", fontsize=16)
    plt.xticks(list(range(2016, 2020)))
    p.set_ylabel("Budgeted Dollars in Millions", fontsize=20)
    p.set_xlabel("")
    p.tick_params(labelsize=20)
    plt.show()
    return fig


def compare_true_earnings():
    """Written August 3rd for True Earnings section"""
    examine_true_earnings = pd.DataFrame(columns=year_range)
    alias_list = ["Boston PD", "Chelsea PD"]
    for alias in alias_list:
        PD = agencies[alias]
        examine_true_earnings.loc[PD.alias + " Total Expenditures from Yearly Budget"] = add_missing_data(PD)
        examine_true_earnings.loc[PD.alias + " Payroll Expenditures from Yearly Budget"] =\
            PD.budget_summary.loc["Payroll Expenditures", PD.year_range]
        if examine_true_earnings.loc[PD.alias + " Payroll Expenditures from Yearly Budget", 2016] == 0:
            examine_true_earnings.loc[PD.alias + " Payroll Expenditures from Yearly Budget", 2016] =\
                PD.budget_summary.loc["Payroll Budget", 2016]
        true_earnings = True_Earnings(alias)[0]
        if 2016 not in true_earnings.index:
            true_earnings[2016] = None
        examine_true_earnings.loc[PD.alias + " True Payroll"] = true_earnings
        # examine_true_earnings.loc[PD.alias +\
        #                           " Difference btwn Earnings Dataset and Stated Payroll"] = \
        #     examine_true_earnings.loc[PD.alias + " True Payroll"]  - \
        #     examine_true_earnings.loc[PD.alias + " Payroll Expenditures from Yearly Budget"]

    bostonPD_difference = examine_true_earnings.loc["Boston PD True Payroll"] - \
                                    examine_true_earnings.loc["Boston PD Payroll Expenditures from Yearly Budget"]
    chelseaPD_difference = examine_true_earnings.loc["Chelsea PD True Payroll"] - \
                                    examine_true_earnings.loc["Chelsea PD Payroll Expenditures from Yearly Budget"]

    display(examine_true_earnings/10**6)
    # examine_true_earnings.drop(index=["Boston PD Difference btwn Earnings Dataset and Stated Payroll",
    #                                   "Chelsea PD Difference btwn Earnings Dataset and Stated Payroll"],
    #                            inplace=True)

    print("Difference between Earnings Dataset and Stated Yearly Payroll for Boston")
    display(bostonPD_difference/10**6)
    print("Difference between Earnings Dataset and Stated Yearly Payroll for Chelsea")
    display(chelseaPD_difference/10**6)


    examine_true_earnings = examine_true_earnings.reset_index()
    examine_true_earnings[['City', 'Budget Line Item']] = examine_true_earnings["index"].str.split(" PD ", expand=True)
    examine_true_earnings.drop(columns = ["index"], inplace=True)
    melted = examine_true_earnings.melt(id_vars=["City", "Budget Line Item"])

    for name in ["Boston", "Chelsea"]:
        plot_true_earnings_comparison(melted[melted["City"]==name], name)

def plot_yearly_operating_costs(gb):
    """For summary of part 1"""
    melted = gb.melt(id_vars = ["Category"])
    palette = sns.color_palette("Paired", melted["Category"].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="variable", y="value", palette=palette,
                     hue="Category", sort=False, data=melted)
    p.set_title("Yearly Operating Costs", fontsize=24)
    ax.legend(frameon=False, loc="upper left", fontsize=16)
    plt.xticks(year_range)
    p.set_ylabel("Dollars in Millions", fontsize=20)
    p.set_xlabel("")
    p.tick_params(labelsize=20)
    plt.show()

def plot_true_earnings_comparison(melted, name):
    melted.rename(columns = {"Budget Line Item": "Source of Data"}, inplace=True)
    melted.loc[:, "value_in_millions"] = (melted["value"] / 10 ** 6).astype(float)
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="variable", y="value_in_millions",
                     style="Source of Data", sort=False, data=melted)
    p.set_title("Compare Stated Expenditures to True Earnings for " + name, fontsize=24)
    ax.legend(frameon=False, loc="upper left", fontsize=16)
    plt.xticks(year_range)
    p.set_ylabel("Dollars in Millions", fontsize=20)
    p.set_xlabel("")
    p.tick_params(labelsize=20)

def plot_SCDAO_case_cost(cost_per_year):
    """First called for summary of part 1"""
    SCDAO_cases_series = pd.Series(SCDAO_cases)
    cost_per_case = (cost_per_year.loc[year_range]/SCDAO_cases_series[year_range]).astype(float)
    fig, ax = plt.subplots(1, 1)
    print("Cost per SCDAO Case (In Thousands)")
    display(cost_per_case)
    plt.ticklabel_format(style='plain', axis='y')
    p2 = sns.lineplot(x=cost_per_case.index , y = cost_per_case.values)
    p2.set_title("Yearly Operating Expenses per SCDAO Case", fontsize=24)
    plt.xticks(year_range)
    p2.set_ylabel("Dollars", fontsize=20)
    p2.set_xlabel("")
    p2.tick_params(labelsize=20)
    plt.show()

def plot_pcnt_change_since_2016(df):
    """First written for Summary of Part 1"""
    SCDAO_cases_series = pd.Series(SCDAO_cases)[year_range]
    df.loc["Total Cost of Carceral State in Suffolk"] = df.sum()
    df.loc["Cost Per SCDAO Case"] = df.sum()/SCDAO_cases_series
    df.loc["Number of SCDAO Cases"] = SCDAO_cases_series
    df.loc["MA GAA"] = pd.Series(MA_GAA)[year_range]/10**6
    for row in df.index:
        df.loc[row + " Fractional Change"] = [x / df.loc[row, 2016] for x in df.loc[row]]
    melted = df[df.index.str.contains("Fractional")].reset_index().melt(id_vars=["Category"])
    palette = sns.color_palette("Paired", melted["Category"].nunique())
    fig, ax = plt.subplots(1, 1)
    plt.ticklabel_format(style='plain', axis='y')
    p = sns.lineplot(x="variable", y="value", palette=palette,
                     hue="Category", sort=False, data=melted)
    p.set_title("Percent Change Since 2016", fontsize=24)
    ax.legend(frameon=False, loc="upper left", fontsize=16)
    plt.xticks(year_range)
    p.set_ylabel("Percent Change", fontsize=20)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    p.set_xlabel("")
    p.tick_params(labelsize=20)
    plt.show()

