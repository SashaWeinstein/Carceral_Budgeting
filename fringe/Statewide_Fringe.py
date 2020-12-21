"""Created August 14th to implement calculation of fringe benefits for statewide agencies.
Methodology is that we take health insurance payments through Group Insurance Commission (GIC) and then
estimation portion of those benefits that go to each agency as % of total payroll that an agency makes up"""

import pandas as pd

from Find_Data import find_data

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

def Total_Statewide_Fringe(client):
    """Implemented August 14. Note that GIC doesn't seem to have unemployment insurance payments
    Important: take out trust money.
    """
    GIC = pd.DataFrame(client.get("pegc-naaa",
                                  where="Department = 'GROUP INSURANCE COMMISSION (GIC)' \
                                  AND budget_fiscal_year >= 2016 AND budget_fiscal_year <= 2019",
                                  limit=999999))
    GIC.loc[:, "amount"] = GIC.loc[:, "amount"].astype(float)
    GIC.loc[:, "budget_fiscal_year"] = GIC.loc[:, "budget_fiscal_year"].astype(int)
    return GIC.groupby("budget_fiscal_year").sum()["amount"]