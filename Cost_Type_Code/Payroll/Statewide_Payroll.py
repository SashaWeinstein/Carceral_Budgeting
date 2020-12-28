"""Total statewide payroll is used for state-level agency fringe benefits calculation and some state-level pension"""

import pandas as pd
from sodapy import Socrata

from Find_Data import find_data

#Janky to hard-code client here but unsure of correct way to do it. Take another look later on in refactor
app_token = "2Qa1WiG8G4kj1vGVd2noK7zP0"
client = Socrata("cthru.data.socrata.com", app_token)
client.timeout = 40

def Total_Statewide_Payroll(client):

    yr = list(range(2016,2020)) # This should be passed from Initialize_Agencies where this will be called after refactor
    total_payroll = find_data(False, client, "rxhc-k6iz", "Year >=2015 AND Year<= 2019", "cthru_statewide_payroll.csv")
    total_payroll.loc[:, "pay_total_actual"] = total_payroll.loc[:, "pay_total_actual"].astype(float)
    total_payroll.loc[:, "year"] = total_payroll.loc[:, "year"].astype(int)
    total_payroll_by_calendar_year = total_payroll.groupby("year").sum()["pay_total_actual"]
    total_payroll_by_fiscal_year = pd.Series(index=yr)
    for y in yr:
        total_payroll_by_fiscal_year.loc[y] = .5 * total_payroll_by_calendar_year.loc[y-1] + \
                                              .5 * total_payroll_by_calendar_year.loc[y]

    return total_payroll_by_fiscal_year

total_payroll_by_FY = Total_Statewide_Payroll(client)

def Fraction_Statewide_Payroll(agency):
    return agency.payroll_by_year/total_payroll_by_FY