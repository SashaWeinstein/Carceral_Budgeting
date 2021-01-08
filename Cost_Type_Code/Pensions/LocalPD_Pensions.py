"""Created July 30th to take code from jupyter notebooks in pensions folder and put into callable functions"""

import pandas as pd

big_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"

def BostonPD_Pensions(agency):
    """PD_fraction is series that maps year to % of non-teacher payroll that Boston PD makes up"""
    PD_fraction = agency.PD_fraction_non_teacher
    pension_contributions = pd.DataFrame(columns=list(range(2016, 2021)),
                                         index=["Pension Budget",
                                                "Pension Expenditures"])
    #From FY21 Document page 10
    pension_contributions.loc["Pension Expenditure", 2019] = 263.08 * (10**6)

    #From FY20 Document page 24
    pension_contributions.loc["Pension Budgeted", 2020] = 265.6 * (10**6)
    pension_contributions.loc["Pension Budgeted", 2019] = 242.08 * (10**6)
    pension_contributions.loc["Pension Expenditure", 2018] = 233.3 * (10**6)
    pension_contributions.loc["Pension Expenditure", 2017] = 199.28 * (10**6)

    #From FY19 Document page 25
    pension_contributions.loc["Pension Budgeted", 2018] = 221.3 * (10**6)
    pension_contributions.loc["Pension Expenditure", 2016] = 196.55 * (10**6)

    #From FY18 Document
    pension_contributions.loc["Pension Budgeted", 2017] = 199.28 * (10**6)

    #From FY17 Document
    pension_contributions.loc["Pension Budgeted", 2016] = 184.55 * (10**6)

    return pension_contributions.loc["Pension Expenditure", 2016:2019] * PD_fraction


def ChelseaPD_Pensions(agency):
    """PD_fraction is from true earnings module, has fraction of non-teacher payroll that goes to cops each year"""
    pension_costs = pd.DataFrame(columns=list(range(2016, 2021)),
                                 index=["Chelsea Pension Contribution Budget",
                                        "Chelsea Pension Contribution Expenditure"])
    #From FY20 Document page 7 Total Direct Expenses for Retirement Program Budget
    pension_costs.loc["Chelsea Pension Contribution Budget", 2016] = 6764818
    pension_costs.loc["Chelsea Pension Contribution Budget", 2017] = 7076524
    pension_costs.loc["Chelsea Pension Contribution Budget", 2018] = 7411936
    pension_costs.loc["Chelsea Pension Contribution Budget", 2019] = 8046650
    pension_costs.loc["Chelsea Pension Contribution Budget", 2020] = 8546184

    #From FY21 Document page 53
    pension_costs.loc["Chelsea Pension Contribution Expenditure", 2017] = 7076376.6
    pension_costs.loc["Chelsea Pension Contribution Expenditure", 2018] = 7341603.95
    pension_costs.loc["Chelsea Pension Contribution Expenditure", 2019] = 7961415.83
    pension_costs.loc["Chelsea Pension Contribution Budget", 2021] = 9080939

    pension_costs.loc["Final Pension Contribution", 2016] = pension_costs.loc["Chelsea Pension Contribution Budget",
                                                                              2016]
    pension_costs.loc["Final Pension Contribution",
                      [2017, 2018, 2019]] = pension_costs.loc["Chelsea Pension Contribution Expenditure",
                                                              [2017, 2018, 2019]]
    return pension_costs.loc["Final Pension Contribution", agency.year_range] * agency.PD_fraction_non_teacher


def ReverePD_Pensions(reverePD_payroll):
    """ReverePD_Payroll comes from budget pdfs
    Based on section for Revere public schools, they have their own system of health insurance and pensions so it's correct
    to exclude. "Total" here really means total non-public schools
    """
    pension_contributions = pd.DataFrame(columns=list(range(2016, 2021)),
                                         index=["Pension Expenditure",
                                                "Pension Appropriation",
                                                "Pension Recap Estimated"
                                                "Pension Recommended"])
    total_payroll = pd.DataFrame(columns=list(range(2016, 2021)),
                                 index=["Total Payroll Appropriation",
                                        "Total Payroll Request"])

    #From FY16 document
    pension_contributions.loc["Pension Recommended", 2016] = 10492643

    #From FY17 Document page 21
    pension_contributions.loc["Pension Recap Estimated", 2016] = 10492643
    pension_contributions.loc["Pension Recommended", 2017] = 11033908

    #On page 29
    total_payroll.loc["Total Payroll Appropriation", 2016] = 27190424
    total_payroll.loc["Total Payroll Request", 2017] = 26970488

    #From FY18 Document Page 18
    pension_contributions.loc["Pension Recommended", 2018] = 11566412
    pension_contributions.loc["Pension Recap Estimated", 2017] = 11033908
    pension_contributions.loc["Pension Expenditure", 2016] = 10492643

    #On page 25
    total_payroll.loc["Total Payroll Appropriation", 2017] = 26989489
    total_payroll.loc["Total Payroll Request", 2018] = 27909365

    #From FY19 Document Page 213
    pension_contributions.loc["Pension Expenditure", 2016] = 10492643
    pension_contributions.loc["Pension Expenditure", 2017] = 11033908

    pension_contributions.loc["Pension Appropriation", 2018] = 11566412
    pension_contributions.loc["Pension Recommended", 2019] = 11914874

    #From FY20 Document
    pension_contributions.loc["Pension Appropriation", 2019] = 11914874
    pension_contributions.loc["Pension Recommended", 2020] = 12655956
    #Page 203
    pension_contributions.loc["Pension Expenditure", 2018] = 11566412

    # FROM FY21 Document page IX - 8
    pension_contributions.loc["Pension Expenditure", 2019] = 12057685.15

    final_total_payroll = total_payroll.loc["Total Payroll Appropriation", [2016, 2017]]
    final_total_payroll[2018] = total_payroll.loc["Total Payroll Request", 2018]

    shortened_yr = list(range(2016,2019))
    reverePD_fraction = reverePD_payroll.loc[shortened_yr]/final_total_payroll.loc[shortened_yr]
    reverePD_fraction.loc[2019] = reverePD_fraction.loc[2018]

    pension_final = pension_contributions.loc["Pension Expenditure", list(range(2016,2020))]

    return reverePD_fraction * pension_final, reverePD_fraction

def WinthropPD_Pensions_Benefits(ReverePD_fraction):
    """Found winthrop pension contributions, so will change code to use Revere's PD fraction for pension and total
    benefits. Will save this for later because it's trivial in the big scheme of things
    In FY18 document pensions are under the same sub-header as other benefits, in FY19 document they get thier own
    section. In FY21 they get their own sub-header. I'll put both pensions and fringe benefits in the same
    function for simplicity.
    I use the following fringe benefits: Workers Comp, Unemployment, Group Insurance - Retirees,
    Group Insurance - Town, Police Fire Medical
    """

    year_range = list(range(2016,2020))
    pensions = pd.DataFrame(columns = year_range,
                            index = ["Fringe Benefit Expenditures",
                                     "Pension Expenditures"])
    #From FY18 Document get 2016 actual. Page 129 by Preview app's counting
    pensions.loc["Fringe Benefit Expenditures", 2016] = 124275 + 99149 + 2148066 + 17829
    pensions.loc["Pension Expenditures", 2016] = 2741050

    #From FY 19 Document get 2017 Actual page 101
    pensions.loc["Fringe Benefit Expenditures", 2017] = 30633 + 25657 + 3440277 + 34061
    pensions.loc["Pension Expenditures", 2017] = 2087906

    # From FY 21 document get 2018, 2019 actual on page 121
    pensions.loc["Fringe Benefit Expenditures", 2018] = 27010 + 14308 + 1789570 + 1454919 + 20387
    pensions.loc["Pension Expenditures", 2018] = 2222798

    pensions.loc["Fringe Benefit Expenditures", 2019] = 32219 + 57839 + 1882978 + 1327242 + 28424
    pensions.loc["Pension Expenditures", 2019] = 2232037

    return pensions.loc["Fringe Benefit Expenditures"]*ReverePD_fraction, \
           pensions.loc["Pension Expenditures"]*ReverePD_fraction