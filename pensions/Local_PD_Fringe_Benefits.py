"""Created August 9th to get health insurance, Workers' comp expenditures for Boston PD
These numbers are from administration and finance budget"""

import pandas as pd


def BostonPD_Fringe(PD_fraction):
    """PD_fraction is series that maps year to % of total payroll that Boston PD makes up"""
    fringe = pd.DataFrame(columns=list(range(2016, 2021)),
                          index=["Health Insurance Expenditures",
                                 "Workers' Comp Fund Expenditures"])

    # FY21 Document https://www.boston.gov/sites/default/files/file/2020/04/2-Volume%201%20-%20Operating%20Budget%20%281%29.pdf
    fringe.loc["Health Insurance Expenditures", 2018] = 210986298
    fringe.loc["Health Insurance Expendtiures", 2019] = 212029308

    fringe.loc["Workers' Comp Fund Expenditures", 2018] = 1385669
    fringe.loc["Workers' Comp Fund Expenditures", 2019] = 1618544

    # FY19 Document https://www.boston.gov/sites/default/files/embed/file/2019-04/v1_02-_19_a_summary-budget.pdf
    fringe.loc["Health Insurance Expenditures", 2016] = 191265768
    fringe.loc["Health Insurance Expenditures", 2017] = 205281017

    fringe.loc["Workers' Comp Fund Expenditures", 2016] = 1328171
    fringe.loc["Workers' Comp Fund Expenditures", 2017] = 1478685

    fringe.loc["Total"] = fringe.sum()
    return fringe.loc["Total", 2016:2019] * PD_fraction

def ChelseaPD_Fringe(PD_fraction):
    """Chelsea actually lists wages and benefits for each agency so we don't
    need this correction'"""
    year_range = list(range(2016,2021))
    return pd.Series(index=year_range, data=[0]*len(year_range))

def ReverePD_Fringe(PD_fraction):
    """There is line-item for worker's comp, health insurance under 900-unclassified section of budget
    I will use total unclassified, which includes Workers Comp, Workers Comp Med, Workers Comp Unemp,
    Group Health, Medicare Taxes, Sick Leave Buy Back, Insurance"""
    year_range = list(range(2016,2020))
    benefits = pd.DataFrame(columns=year_range, index=["Total Unclassified Actual"])

    benefits.loc["Total Unclassified Actual", 2016] = 19240462 # FY18 Document missing a 2016 number so use recap estimated from
    benefits.loc["Total Unclassified Actual", 2017] = 19519748 # FY19 and FY18 Documents both missing 2017 number so used 2017 Mayor's Rec from FY17 Document
    benefits.loc["Total Unclassified Actual", 2018] = 20649256
    benefits.loc["Total Unclassified Actual", 2019] = 22635045.92 #On Page IX-7 From FY2021 Document

    return benefits.loc["Total Unclassified Actual"] * PD_fraction

def No_Fringe_Benefits(PD_fraction):
    """Called by Chelsea, can add fringe benefits later"""
    out = pd.Series(index=list(range(2016, 2021)), data=[0] * 5)

    return out
