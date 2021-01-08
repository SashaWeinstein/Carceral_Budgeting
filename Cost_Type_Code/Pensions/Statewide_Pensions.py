""" Last updated July 30th
New in 2Ver: a function to be called from Agency_Classes that returns pension payouts per year
Also just realized that there is fiscal year - calendar year mistmatch here, pension payouts are per calendar year
but state contributions to pension system are per fiscal year.
Methodology for trial court is extra complex so writing it all out here.
Trial court as a former employer shows up in many ways in the retirement benefits dataset. Sometimes as 'Trial Court Administration',
sometimes as 'South Boston District Court', sometimes as 'Juvneile Court Administration'.
If this column tells us that an employee worked in suffolk county when they were employed this gives us an extra piece of
information that is helpful to us. Our methodology assumes that the fraction of payouts across former employees of each
part of the government is equal to the fraction of the total pay-ins that are on behalf of current employees of that
part of the governemnt. So former employees of trial court in suffolk county are treated differently in our methodology:
trial court pension costs are split into statewide and local. The new local pension costs don't need to be corrected
for Suffolk County. They do still need to be corrected based on the assumption that a great deal of trial court
resources go to cases that aren't 'criminal.'
"""

#To do for refactor: one file that "serves" each payroll series. That file loads in functions from statewide and localPD,
# and then has functions that are called by the classes

import pandas as pd
import numpy as np
import sys
from sodapy import Socrata
sys.path.insert(0, "../")
sys.path.insert(0, "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory")

from Agency_Classes.Agency_Helpers.Find_Data import find_data
from Agency_Classes.Agency_Helpers.CY_To_FY import convert_CY_to_FY_df
carceral_departments = {"trial_court_local": ["Suffolk Superior Court",
                                  "Chelsea District Court", "Suffolk Cty. Juvenile Court",
                                  "South Boston District Court", "South Boston District  Court",
                                  "East Boston District Court", "Boston Municipal Court"],
                        "trial_court_statewide": ["Trial Court Justice", "Probation",
                                                  "Admin.office/district Court", "Office Of Court Management",
                                                  "General Court", "Superior Court Probation",
                                                  "Trial Court Administration",
                                                  "Juvenile Court Administration",
                                                  "Trial Court Cse Unit",
                                                  "Trial Court Law Libraries"],
                        "state_police": ["State Police"],
                        "Parole_Board": ["Parole Board"],
                        "Supreme_Judicial_Court": ["Supreme Judicial Court"],
                        "Appeals_Court": ["Appeals CourT-John Adams Court"]}

DOC_departments = ["Corrections - Transportation", "Corrections Reintr. Unit",
                                "Corrections Training Academy", "Dept Of Corrections",
                                "Department Corrections"]

app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)

big_path = "/Users/alexanderweinstein/Documents/Harris/Summer2020/Carceral_Budgeting/Exploratory/data/"

def pensions_by_agency(requery):
    cthru_pension_payouts = get_cthru_pension_payouts(requery)
    pcnt_of_total = as_pcnt_of_total(cthru_pension_payouts, requery)
    contributions_by_year = pension_contributions_by_year(requery)
    return pension_payments_statewide(pcnt_of_total, contributions_by_year), contributions_by_year




def get_cthru_pension_payouts(requery):
    """New July 30th"""
    cthru_pensions = find_data(requery, client, "pni4-392n", "year >=2015 AND year <= 2020",
                               "cthru_retirement_benefits.csv")
    cthru_pensions = clean_pensions(cthru_pensions)

    agency_classes = cthru_pensions.apply(lambda x: find_agency(x["department"]), axis=1)
    cthru_pensions["agency_class"] = agency_classes
    return cthru_pensions



def as_pcnt_of_total(cthru_pension_payouts, requery):

    yr = list(range(2016,2020))
    payouts_gb = cthru_pension_payouts.groupby(["agency_class", "year"]).agg({"annual_amount": "sum"}).unstack()
    payouts_gb.columns = [x[1] for x in payouts_gb.columns]
    payouts_gb.loc["DOC",:] = DOC_pensions(requery)

    total_by_year = cthru_pension_payouts.groupby("year").sum()["annual_amount"]

    payout_pct_calendar_year = payouts_gb/total_by_year
    payout_pct_FY = convert_CY_to_FY_df(payout_pct_calendar_year, yr)

    return payout_pct_FY

def pension_payments_statewide(payouts_fraction, contributions_by_year):
    """Takes fraction pf payout money to each entity (can be agency or umbrella dept right now) and caculates sum
    of total pension contributions"""
    pension_costs_statewide_calculated = pd.DataFrame(index=payouts_fraction.index, columns=payouts_fraction.columns)
    for year in list(range(2016,2020)):
        pension_costs_statewide_calculated[year] = payouts_fraction[year] * contributions_by_year[year]
    sheriff_extra(pension_costs_statewide_calculated)
    return pension_costs_statewide_calculated



def pension_contributions_by_year(requery=False):
    """This queries API for state expenditures on contributions to state pension system
    returns series that has total pension contributions 2016-2020"""
    pension_SOQL = "appropriation_name = '(06121020) STATE RETIREMENT BD COMMONWEALTH PENSION'"
    pension_SOQL += "AND budget_fiscal_year >= 2016 AND budget_fiscal_year <= 2020"
    pension_contributions = find_data(requery, client, "pegc-naaa", pension_SOQL, "cthru_pension_contributions.csv")
    pension_contributions["amount"] = pension_contributions["amount"].astype(float)
    pension_contributions["budget_fiscal_year"] = pension_contributions["budget_fiscal_year"].astype(int)
    pension_contributions = pension_contributions[pension_contributions["object_class"] == "(DD) PENSION & INSURANCE RELATED EX"]
    return pension_contributions.groupby("budget_fiscal_year").sum()["amount"]

def DOC_pensions(requery):
    """DOC requires it's own separate methodology because a bookkeeping error forces us to make some estimations
    Bookkeepping error is that 160 million dollars of retirement money was paid out in 2020, whereas previous 10 years
    has 6-11 million in retirement benefits paid out. So plan is to assume the 160 million is spread out over the
    previous ten years, following the same trend the other money does"""
    DOC_SOQL = "(department_last_worked_in LIKE '%Corrections%')"
    DOC_pensions = find_data(requery, client, "pni4-392n", DOC_SOQL, "cthru_DOC_retirement_benefits.csv")
    DOC_pensions = clean_pensions(DOC_pensions)
    DOC_pensions = DOC_pensions[DOC_pensions["department"].isin(DOC_departments)]
    lump_sum = DOC_pensions[DOC_pensions["department"] == "Department Corrections"]["annual_amount"].sum()
    by_year = DOC_pensions[DOC_pensions["department"] != "Department Corrections"]\
                        .groupby("year").sum()["annual_amount"]
    by_year_fraction = by_year/DOC_pensions[DOC_pensions["department"] != "Department Corrections"]\
                       ["annual_amount"].sum()
    return by_year + by_year_fraction * lump_sum

def sheriff_extra(df):
    """Added august 12th to account for City of Boston's obligations to retirees of suffolk sheriff's office. From
    Boston state budget:
         State legislation converted all existing and future Suffolk County Sheriff employees to state employees
         effective January 1, 2010. The State charges the City for Suffolk County through an assessment based on the
        residual unfunded pension liability for former Sherriff employees who retired prior to January 1, 2010.
        Once the unfunded pension liability is fully extinguished, the budget for Suffolk County
        will no longer be necessary.
    """
    df.loc["Suffolk_Sheriff",:] = df.loc["Suffolk_Sheriff",:] + 3.87*(10**6)


def clean_pensions(cthru_pensions):
    cthru_pensions.loc[:,"annual_amount"] = cthru_pensions.loc[:,"annual_amount"].astype(float)
    cthru_pensions = cthru_pensions[cthru_pensions["retirement_system"] == "MSERS"]
    cthru_pensions.rename(columns={"department_last_worked_in": "department"}, inplace=True)
    cthru_pensions["department"].fillna("None", inplace=True)
    cthru_pensions["year"] = cthru_pensions["year"].astype(int)
    cthru_pensions["title_at_retirement"].fillna("None", inplace=True)
    return cthru_pensions


def find_umbrella(val, title):
    for umbrella, depts in carceral_departments.items():
        if val in depts:
            return umbrella
        elif "State Police" in title and "Dispatcher" not in title:
            return "state_police"
    return np.NaN

def find_agency(dept):
    """Created in Version 2 to get agency class for each payment
    Should be made prettier in refactor """
    if dept == "Suffolk Sheriff's Office":
        return "Suffolk_Sheriff"
    if dept == "District Att.,suffolk District":
        return "Suffolk_DA"
    if dept == "Public Counsel Services":
        return "CPCS"
    if dept == "District Attorney's Assoc.":
        return "DAA"
    if dept == "Parole Board":
        return "Parole_Board"
    if dept == "Supreme Judicial Court":
        return "Supreme_Judicial_Court"
    if dept =="Appeals CourT-John Adams Court":
        return "Appeals_Court"
    if dept in carceral_departments["trial_court_statewide"]:
        return "trial_court_statewide"
    if dept in carceral_departments["trial_court_local"]:
        return "trial_court_local"
    if dept in carceral_departments["state_police"]:
        return "State_Police"
    return None

#To do: see if there is nice way for user to pass in requery variable
#also to do: give this it's own file?
