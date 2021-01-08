"""Created August 9th to get health insurance, Workers' comp expenditures for Boston PD
These numbers are from administration and finance budget"""

import pandas as pd


def BostonPD_Fringe(agency):
    """PD_fraction is series that maps year to % of total payroll that Boston PD makes up
    Updated Dec 18 to include benefits money in current chgs & obligations section of police budget
    Citywide numbers are from General Fund Appropriations by Cabinet & Department page in citywide budget
    which can be found under 'Operating Budget' at https://www.boston.gov/departments/budget
    Current thinking is that because worker's comp fund in citywide is under "admininistration and finance"
    that it's pointing to a separate expendituree than the 'Worker's Comp medical' in the Boston PD """
    PD_fraction = agency.PD_fraction_total
    citywide_fringe = pd.DataFrame(columns=list(range(2016, 2021)),
                          index=["Health Insurance Expenditures",
                                 "Workers' Comp Fund Expenditures"])

    # FY21 Document https://www.boston.gov/sites/default/files/file/2020/04/2-Volume%201%20-%20Operating%20Budget%20%281%29.pdf
    citywide_fringe.loc["Health Insurance Expenditures", 2018] = 210986298
    citywide_fringe.loc["Health Insurance Expendtiures", 2019] = 212029308

    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2018] = 1385668
    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2019] = 1618544

    # FY19 Document https://www.boston.gov/sites/default/files/embed/file/2019-04/v1_02-_19_a_summary-budget.pdf
    citywide_fringe.loc["Health Insurance Expenditures", 2016] = 191265768
    citywide_fringe.loc["Health Insurance Expenditures", 2017] = 205281017

    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2016] = 1328171
    citywide_fringe.loc["Workers' Comp Fund Expenditures", 2017] = 1478695

    citywide_fringe.loc["Total"] = citywide_fringe.sum()

    # We now get commented out code in bostonPD non payroll operating
    # PD_fringe = pd.DataFrame(columns=list(range(2016,2020)),
    #                          index = ["Worker's Comp Medical"])
    # PD_fringe.loc["Worker's Comp Medical", 2016] = 120503 #From FY19 Document
    # PD_fringe.loc["Worker's Comp Medical", 2017] = 132926 # From FY19 Document
    # PD_fringe.loc["Worker's Comp Medical", 2018] = 123164 # From FY21 Document
    # PD_fringe.loc["Worker's Comp Medical", 2019] = 101000 # From FY21 Document

    return citywide_fringe.loc["Total", 2016:2019] * PD_fraction #+ PD_fringe.loc["Worker's Comp Medical", :]#, PD_fringe.loc["Worker's Comp Medical", :]

def ChelseaPD_Fringe(agency):
    """For Chelsea Use Health Insurance, worker's Comp"""
    year_range = list(range(2016,2020))
    citywide_fringe = pd.DataFrame(columns=year_range,
                                   index=["Health Insurance",
                                          "Workers Comp"])
    #From FY20 Budget Page 8
    citywide_fringe.loc["Health Insurance", 2016] = 6869046
    citywide_fringe.loc["Workers Comp", 2016] = 300000

    #From FY21 Budget

    citywide_fringe.loc["Health Insurance", 2017] = 8020886.55
    citywide_fringe.loc["Workers Comp", 2017] = 336888.50

    citywide_fringe.loc["Health Insurance", 2018] = 7321981.22
    citywide_fringe.loc["Workers Comp", 2018] = 464700.00

    citywide_fringe.loc["Health Insurance", 2019] = 7315861
    citywide_fringe.loc["Workers Comp", 2019] = 353120

    citywide_fringe.loc["Total"] = citywide_fringe.sum()

    return citywide_fringe.loc["Total"]*agency.PD_fraction_total

def ReverePD_Fringe(PD_fraction):
    """There is line-item for worker's comp, health insurance under 900-unclassified section of budget
   There isn't consistent information across budgets, use some budget and some expenditures based on
   what is available
   """
    year_range = list(range(2016,2020))
    citywide_fringe = pd.DataFrame(columns=year_range,
                                   index=["Health Insurance",
                                          "Workers Comp",
                                          "Workers Comp Medical",
                                          "Unemployment Insurance"])

    # Page 21 of FY17 Document. 2016 numbers are 2016 recap. 2017 numbers are Mayor's reco
    citywide_fringe.loc["Workers Comp", 2016] = 472145
    citywide_fringe.loc["Workers Comp Medical", 2016] = 120000
    citywide_fringe.loc["Unemployment Insurance", 2016] = 80000
    citywide_fringe.loc["Health Insurance", 2016] = 17200725

    citywide_fringe.loc["Workers Comp", 2017] = 472145
    citywide_fringe.loc["Workers Comp Medical", 2017] = 120000
    citywide_fringe.loc["Unemployment Insurance", 2017] = 80000
    citywide_fringe.loc["Health Insurance", 2017] = 17200725

    #Page II - 208 of FY19 Document. FY18 numbers are adopted, FY 19 numbers are requested
    citywide_fringe.loc["Workers Comp", 2018] = 302145
    citywide_fringe.loc["Workers Comp Medical", 2018] = 120000
    citywide_fringe.loc["Unemployment Insurance", 2018] = 80000
    citywide_fringe.loc["Health Insurance", 2018] = 17680225

    citywide_fringe.loc["Workers Comp", 2019] = 0
    citywide_fringe.loc["Workers Comp Medical", 2019] = 120000
    citywide_fringe.loc["Unemployment Insurance", 2019] = 80000
    citywide_fringe.loc["Health Insurance", 2019] = 20085645

    citywide_fringe.loc["Total"] = citywide_fringe.sum()

    return citywide_fringe.loc["Total"] * PD_fraction

def No_Fringe_Benefits(PD_fraction):
    """Called by Chelsea, can add fringe benefits later"""
    out = pd.Series(index=list(range(2016, 2021)), data=[0] * 5)

    return out
