"""Created August 9th to get health insurance, Workers' comp expenditures for Boston PD
These numbers are from administration and finance budget"""

import pandas as pd


def BostonPD_Fringe(PD_fraction):
    """PD_fraction is series that maps year to % of total payroll that Boston PD makes up
    Updated Dec 18 to include benefits money in current chgs & obligations section of police budget
    Citywide numbers are from General Fund Appropriations by Cabinet & Department page in citywide budget
    which can be found under 'Operating Budget' at https://www.boston.gov/departments/budget
    Current thinking is that because worker's comp fund in citywide is under "admininistration and finance"
    that it's pointing to a separate expendituree than the 'Worker's Comp medical' in the Boston PD """
    citywide_fringe = pd.DataFrame(columns=list(range(2016, 2021)),
                          index=["Health Insurance Expenditures",
                                 "Workers' Comp Fund Expenditures"])

    # FY21 Document https://www.boston.gov/sites/default/files/file/2020/04/2-Volume%201%20-%20Operating%20Budget%20%281%29.pdf
    citywide_fringe.loc["Health Insurance Expenditures", 2018] = 210986298
    citywide_fringe.loc["Health Insurance Expendtiures", 2019] = 212029308

    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2018] = 1385669
    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2019] = 1618544

    # FY19 Document https://www.boston.gov/sites/default/files/embed/file/2019-04/v1_02-_19_a_summary-budget.pdf
    citywide_fringe.loc["Health Insurance Expenditures", 2016] = 191265768
    citywide_fringe.loc["Health Insurance Expenditures", 2017] = 205281017

    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2016] = 1328171
    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2017] = 1478685

    citywide_fringe.loc["Total"] = citywide_fringe.sum()

    PD_fringe = pd.DataFrame(columns=list(range(2016,2020)),
                             index = ["Worker's Comp Medical"])
    PD_fringe.loc["Worker's Comp Medical", 2016] = 0 #From FY18 Document
    PD_fringe.loc["Worker's Comp Medical", 2017] = 132926 # From FY19 Document
    PD_fringe.loc["Worker's Comp Medical", 2018] = 0 # From FY20 Document
    PD_fringe.loc["Worker's Comp Medical", 2019] = 101000 # From FY21 Document

    return citywide_fringe.loc["Total", 2016:2019] * PD_fraction + PD_fringe.loc["Worker's Comp Medical", :], PD_fringe.loc["Worker's Comp Medical", :]

def ChelseaPD_Fringe(PD_fraction):
    """No benefits listed separately on any budget document. Assign 0's to this category and say it's unclear
    Thought about some sort of correction where we assume the ratio of salary to benefit is the same as revere and use
    that to estimate but it's not worth it, just list it under missing data"""
    year_range = list(range(2016,2020))

    return pd.Series(index=year_range, data=0), pd.Series(index=year_range, data=0)

def ReverePD_Fringe(PD_fraction):
    """There is line-item for worker's comp, health insurance under 900-unclassified section of budget
    I will use total unclassified, which includes Workers Comp, Workers Comp Med, Workers Comp Unemp,
    Group Health, Medicare Taxes, Sick Leave Buy Back, Insurance"""
    year_range = list(range(2016,2020))
    benefits = pd.DataFrame(columns=year_range, index=["Total Unclassified Actual"])

    benefits.loc["Total Unclassified Actual", 2016] = 19240462 # FY18 Document missing a 2016 number so use recap estimated from
    benefits.loc["Total Unclassified Actual", 2017] = 19519748 # FY19 and FY18 Documents both missing 2017 number so used 2017 Mayor's Rec from FY17 Document
    benefits.loc["Total Unclassified Actual", 2018] = 20649256 #Page
    benefits.loc["Total Unclassified Actual", 2019] = 22635045.92 #On Page IX-7 From FY2021 Document

    return benefits.loc["Total Unclassified Actual"] * PD_fraction

def No_Fringe_Benefits(PD_fraction):
    """Called by Chelsea, can add fringe benefits later"""
    out = pd.Series(index=list(range(2016, 2021)), data=[0] * 5)

    return out
